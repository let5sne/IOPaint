# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

IOPaint 是一个免费开源的图像修复(inpainting)和扩展(outpainting)工具,基于最先进的 AI 模型。项目包括 Python 后端(FastAPI)和 React TypeScript 前端(Vite)。

**关键特性:**
- 支持多种 AI 模型:LaMa、Stable Diffusion、SDXL、BrushNet、PowerPaint、AnyText 等
- 插件系统:Segment Anything、RemoveBG、RealESRGAN、GFPGAN 等
- 批处理功能
- WebUI 界面和命令行界面
- 支持 CPU、GPU、Apple Silicon

## 常用命令

### 开发环境设置

**前端开发:**
```bash
cd web_app
npm install
npm run dev  # 开发服务器运行在 http://localhost:5173
```

**前端构建:**
```bash
cd web_app
npm run build
cp -r dist/ ../iopaint/web_app
```

**后端开发:**
```bash
pip install -r requirements.txt
python3 main.py start --model lama --port 8080 --device cpu
```

**安装插件依赖:**
```bash
iopaint install-plugins-packages
```

### 生产环境

**安装并启动:**
```bash
pip3 install iopaint
iopaint start --model=lama --device=cpu --port=8080
```

**批处理图像:**
```bash
iopaint run --model=lama --device=cpu \
  --image=/path/to/image_folder \
  --mask=/path/to/mask_folder \
  --output=output_dir
```

**下载模型:**
```bash
iopaint download --model runwayml/stable-diffusion-inpainting
```

**列出已下载的模型:**
```bash
iopaint list
```

### 构建与发布

**构建 Python 包:**
```bash
bash publish.sh
# 会构建前端并打包成 wheel
```

**构建 Docker 镜像:**
```bash
bash build_docker.sh <version_tag>
```

## 架构概览

### 后端架构 (iopaint/)

**入口点流程:**
1. `__init__.py::entry_point()` - 主入口,处理 Windows PyTorch 修复
2. `cli.py::typer_app` - Typer CLI 应用,定义所有命令(start, run, download, list)
3. `api.py::Api` - FastAPI 应用,处理 WebUI 和 REST API
4. `model_manager.py::ModelManager` - 核心模型管理器,负责加载和切换模型

**模型系统:**
- `model/base.py::InpaintModel` - 所有模型的抽象基类
- 模型实现分为两类:
  - **擦除模型** (erase models): LaMa, MAT, MI-GAN, OpenCV2, Manga 等 - 用于移除物体、水印
  - **扩散模型** (diffusion models): SD, SDXL, ControlNet, BrushNet, PowerPaint, AnyText 等 - 用于替换物体或扩展图像
- 每个模型实现 `forward()` 方法,接收图像、mask 和 InpaintRequest 配置

**插件架构:**
- `plugins/base_plugin.py::BasePlugin` - 插件抽象基类
- 插件独立于主模型运行,可以启用/禁用
- 主要插件: InteractiveSeg, RemoveBG, AnimeSeg, RealESRGAN, GFPGAN, RestoreFormer

**文件管理:**
- `file_manager/` - 处理图像浏览、存储后端(本地文件系统)

**批处理:**
- `batch_processing.py::batch_inpaint()` - 批量处理图像的主函数

### 前端架构 (web_app/)

- React + TypeScript + Vite
- 使用 Recoil/Zustand 进行状态管理
- TailwindCSS + Radix UI 组件
- Socket.IO 用于实时通信
- React Query 用于数据获取

### 数据流

**WebUI 模式:**
1. 用户在浏览器中操作(绘制 mask、选择模型、调整参数)
2. 前端通过 HTTP API 发送 InpaintRequest 到 FastAPI 后端
3. `api.py` 接收请求,调用 `ModelManager`
4. `ModelManager.__call__()` 预处理图像,调用模型的 `forward()`
5. 模型返回修复后的图像
6. 后端将结果返回给前端显示

**批处理模式:**
1. CLI 命令触发 `batch_processing.py`
2. 遍历输入目录中的图像和 mask
3. 为每个图像调用 ModelManager
4. 保存结果到输出目录

### 模型加载与管理

- `download.py::scan_models()` - 扫描本地和 HuggingFace 可用模型
- `ModelManager.init_model()` - 根据模型类型初始化相应的模型类
- 支持动态模型切换(通过 `/api/v1/switch_model` 端点)
- 模型文件缓存在 `~/.cache` (可通过 `--model-dir` 修改)

### 关键配置模式

**模型配置:**
- SD/SDXL 模型使用 `model/original_sd_configs/` 中的 YAML 配置
- AnyText 使用专门的 `model/anytext/anytext_sd15.yaml`

**设备管理:**
- 支持 CPU、CUDA、MPS(Apple Silicon)
- `helper.py::switch_mps_device()` - 处理 MPS 不兼容的模型
- `model/utils.py::torch_gc()` - 清理 GPU/CPU 内存

**HD 策略:**
- `schema.py::HDStrategy` - 处理高分辨率图像的策略(CROP, RESIZE, ORIGINAL)
- 大图像会被分块处理或调整大小

## 重要注意事项

### 添加新模型

1. 在 `model/` 目录创建新的模型文件
2. 继承 `InpaintModel` 基类
3. 实现 `init_model()` 和 `forward()` 方法
4. 在 `model/__init__.py` 注册模型
5. 更新 `const.py` 中的 `AVAILABLE_MODELS` 或 `DIFFUSION_MODELS`

### 前端开发

- 前端代码修改后自动热重载
- 后端代码修改需要重启服务
- 创建 `web_app/.env.local` 文件配置后端地址:
  ```
  VITE_BACKEND=http://127.0.0.1:8080
  ```

### 性能优化选项

- `--low-mem`: 低内存模式,减少 VRAM 使用
- `--cpu-offload`: CPU 卸载,将部分模型移到 CPU
- `--no-half`: 禁用半精度(FP16),提高精度但增加内存使用
- `--cpu-textencoder`: 将文本编码器放在 CPU 上

### 环境变量

项目在 `__init__.py` 中设置了关键的 PyTorch 环境变量:
- `PYTORCH_ENABLE_MPS_FALLBACK=1` - 启用 MPS 回退
- `TORCH_CUDNN_V8_API_LRU_CACHE_LIMIT=1` - 防止 GPU 上的 CPU 内存泄漏

### Docker 支持

- `docker/CPUDockerfile` - CPU 版本
- `docker/GPUDockerfile` - GPU 版本(需要 NVIDIA GPU)
- 使用 `build_docker.sh` 构建镜像

## 依赖管理

- `requirements.txt` - 生产依赖（已更新到最新兼容版本）
- `requirements-dev.txt` - 开发依赖(wheel, twine, pytest-loguru)
- `web_app/package.json` - 前端依赖
- PyTorch 版本: >= 2.0.0
- Python 版本: >= 3.7

### 包版本更新 (2025-11-28)

项目依赖已更新到最新稳定版本：
- `diffusers`: 0.27.2 → 0.35.2+
- `huggingface_hub`: 0.25.2 → 0.26.0+
- `peft`: 0.7.1 → 0.13.0+
- `transformers`: 4.39.1+ → 4.45.0+
- `controlnet-aux`: 0.0.3 → 0.0.9+
- `fastapi`: 0.108.0 → 0.115.0+
- `gradio`: 4.21.0 → 5.0.0+ (限制 < 6.0.0)
- `python-socketio`: 5.7.2 → 5.11.0+
- `Pillow`: 9.5.0 → 10.0.0+

**代码修改:**
- 修复了 `iopaint/model/ldm.py:279` 中 `torch.cuda.amp.autocast()` 的弃用警告，改为 `torch.amp.autocast('cuda')`

**安装建议:**
- 优先使用国内镜像源加速安装：
  ```bash
  pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
  ```

## 常见模式

### 图像处理流程

1. `helper.py::load_img()` - 加载图像
2. `helper.py::decode_base64_to_image()` - 解码 base64 图像
3. `helper.py::adjust_mask()` - 调整 mask 大小和格式
4. `helper.py::pad_img_to_modulo()` - 填充图像到模型要求的倍数
5. 模型处理
6. `helper.py::pil_to_bytes()` / `numpy_to_bytes()` - 转换输出格式

### WebSocket 通信

- 使用 Socket.IO 进行实时通信
- 主要用于长时间运行的任务进度更新
- 定义在 `api.py` 的 Socket.IO 服务器中
