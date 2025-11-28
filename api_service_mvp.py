"""
IOPaint 去水印 API 服务 - MVP版本
专注于单一功能：去除图片水印

遵循KISS原则：
- 只支持LaMa模型
- 简单的API Key认证
- 同步处理（无需队列）
- 本地存储
"""

import os
import time
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime

import torch
import uvicorn
import numpy as np
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from PIL import Image

from iopaint.model_manager import ModelManager
from iopaint.schema import InpaintRequest, HDStrategy
from iopaint.helper import (
    decode_base64_to_image,
    numpy_to_bytes,
    load_img,
)


# ==================== 配置 ====================
class Config:
    """服务配置"""
    # API密钥（生产环境应从环境变量读取）
    API_KEY = os.getenv("API_KEY", "your_secret_key_change_me")

    # 模型配置
    MODEL_NAME = "lama"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # 限制配置
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "4096"))  # 最大边长
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # 日志配置
    LOG_DIR = Path("./logs")
    LOG_DIR.mkdir(exist_ok=True)

    # 指标统计
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"


# ==================== 应用初始化 ====================
app = FastAPI(
    title="IOPaint 去水印 API",
    description="基于LaMa模型的图片去水印API服务",
    version="1.0.0-MVP",
    docs_url="/docs",  # Swagger文档
    redoc_url="/redoc",  # ReDoc文档
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 全局变量 ====================
model_manager: Optional[ModelManager] = None
request_stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "total_processing_time": 0.0,
}


# ==================== 认证中间件 ====================
async def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """验证API密钥"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key. Please provide X-API-Key header."
        )

    if x_api_key != Config.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return x_api_key


# ==================== 启动/关闭事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时加载模型"""
    global model_manager

    logger.info("=" * 60)
    logger.info("IOPaint API Service - MVP Version")
    logger.info("=" * 60)
    logger.info(f"Device: {Config.DEVICE}")
    logger.info(f"Model: {Config.MODEL_NAME}")
    logger.info(f"Max Image Size: {Config.MAX_IMAGE_SIZE}")
    logger.info(f"API Key: {'*' * 20}{Config.API_KEY[-4:]}")
    logger.info("=" * 60)

    try:
        # 直接初始化模型管理器，不使用 ApiConfig
        model_manager = ModelManager(
            name=Config.MODEL_NAME,
            device=torch.device(Config.DEVICE),
            no_half=False,
            low_mem=False,
            cpu_offload=False,
            disable_nsfw=True,
            sd_cpu_textencoder=False,
            local_files_only=False,
            cpu_textencoder=False,
        )

        logger.success(f"✓ Model {Config.MODEL_NAME} loaded successfully on {Config.DEVICE}")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理工作"""
    logger.info("Shutting down API service...")

    if Config.ENABLE_METRICS:
        logger.info("=" * 60)
        logger.info("Final Statistics:")
        logger.info(f"  Total Requests: {request_stats['total']}")
        logger.info(f"  Successful: {request_stats['success']}")
        logger.info(f"  Failed: {request_stats['failed']}")
        if request_stats['success'] > 0:
            avg_time = request_stats['total_processing_time'] / request_stats['success']
            logger.info(f"  Avg Processing Time: {avg_time:.2f}s")
        logger.info("=" * 60)


# ==================== API路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "IOPaint Watermark Removal API",
        "version": "1.0.0-MVP",
        "status": "running",
        "model": Config.MODEL_NAME,
        "device": Config.DEVICE,
        "docs": "/docs",
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model": Config.MODEL_NAME,
        "device": Config.DEVICE,
        "gpu_available": torch.cuda.is_available(),
    }


@app.get("/api/v1/stats")
async def get_stats(api_key: str = Header(None, alias="X-API-Key")):
    """获取使用统计（需要API Key）"""
    await verify_api_key(api_key)

    if not Config.ENABLE_METRICS:
        raise HTTPException(status_code=404, detail="Metrics disabled")

    stats = request_stats.copy()
    if stats['success'] > 0:
        stats['avg_processing_time'] = stats['total_processing_time'] / stats['success']
    else:
        stats['avg_processing_time'] = 0

    return stats


@app.post("/api/v1/remove-watermark")
async def remove_watermark(
    request: Request,
    image: UploadFile = File(..., description="原始图片"),
    mask: Optional[UploadFile] = File(None, description="水印遮罩（可选）"),
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    去除图片水印

    参数：
    - image: 原始图片文件（必需）
    - mask: 水印遮罩图片（可选，黑色区域会被保留，白色区域会被修复）

    返回：
    - 处理后的图片（PNG格式）
    """
    # 验证API Key
    await verify_api_key(api_key)

    start_time = time.time()
    request_stats["total"] += 1

    try:
        # 1. 读取图片
        image_bytes = await image.read()
        if len(image_bytes) > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Max size: {Config.MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # 验证图片格式
        try:
            pil_image = Image.open(image.file).convert("RGB")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image format: {str(e)}"
            )

        # 检查图片尺寸
        width, height = pil_image.size
        if max(width, height) > Config.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Max dimension: {Config.MAX_IMAGE_SIZE}px"
            )

        logger.info(f"Processing image: {width}x{height}")

        # 2. 读取遮罩（如果提供）
        mask_pil = None
        if mask:
            mask_bytes = await mask.read()
            try:
                mask_pil = Image.open(mask.file).convert("L")
                # 确保遮罩尺寸与原图一致
                if mask_pil.size != pil_image.size:
                    mask_pil = mask_pil.resize(pil_image.size, Image.LANCZOS)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid mask format: {str(e)}"
                )
        else:
            # 如果没有提供遮罩，创建全白遮罩（修复整张图）
            logger.info("No mask provided, will process entire image")
            mask_pil = Image.new("L", pil_image.size, 255)

        # 3. 将 PIL 图像转换为 numpy 数组
        image_np = np.array(pil_image)
        mask_np = np.array(mask_pil)

        # 4. 构建请求配置
        inpaint_request = InpaintRequest(
            image="",  # 不需要 base64
            mask="",
            hd_strategy=HDStrategy.ORIGINAL,
            hd_strategy_crop_margin=128,
            hd_strategy_crop_trigger_size=800,
            hd_strategy_resize_limit=2048,
        )

        # 5. 调用模型进行处理
        logger.info("Running model inference...")
        inference_start = time.time()

        result_image = model_manager(
            image=image_np,
            mask=mask_np,
            config=inpaint_request,
        )

        inference_time = time.time() - inference_start
        logger.info(f"Inference completed in {inference_time:.2f}s")

        # 6. 转换结果为字节
        output_bytes = numpy_to_bytes(
            result_image,
            ext="png",
        )

        # 7. 更新统计
        processing_time = time.time() - start_time
        request_stats["success"] += 1
        request_stats["total_processing_time"] += processing_time

        logger.success(
            f"✓ Request completed in {processing_time:.2f}s "
            f"(inference: {inference_time:.2f}s)"
        )

        # 8. 返回结果
        return Response(
            content=output_bytes,
            media_type="image/png",
            headers={
                "X-Processing-Time": f"{processing_time:.3f}",
                "X-Image-Size": f"{width}x{height}",
            }
        )

    except HTTPException:
        request_stats["failed"] += 1
        raise

    except Exception as e:
        request_stats["failed"] += 1
        logger.error(f"Error processing request: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


# ==================== 主函数 ====================
def main():
    """启动服务"""
    # 配置日志
    logger.add(
        Config.LOG_DIR / "api_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
    )

    # 启动服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )


if __name__ == "__main__":
    main()
