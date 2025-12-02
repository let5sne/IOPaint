#!/usr/bin/env bash
# 构建适用于 T4 显卡的 API 服务 Docker 镜像
# NVIDIA T4 支持 CUDA Compute Capability 7.5
# 使用 CUDA 12.1 基础镜像，完全兼容 T4

set -e

VERSION=${1:-latest}
IMAGE_NAME="let5see/iopaint"
TAG="api-t4-${VERSION}"

echo "=========================================="
echo "  IOPaint API Service - T4 GPU Image"
echo "=========================================="
echo "版本: ${VERSION}"
echo "镜像: ${IMAGE_NAME}:${TAG}"
echo ""

echo "[1/3] 构建 Docker 镜像..."
docker build \
    --platform linux/amd64 \
    --file ./docker/APIDockerfile \
    --label org.opencontainers.image.title="IOPaint API Service" \
    --label org.opencontainers.image.description="IOPaint API Service for T4 GPU" \
    --label org.opencontainers.image.version="${VERSION}" \
    --tag "${IMAGE_NAME}:${TAG}" \
    .

echo ""
echo "[2/3] 镜像构建完成!"
echo "本地镜像: ${IMAGE_NAME}:${TAG}"
echo ""

# 询问是否推送
read -p "是否推送到 Docker Hub? (y/N): " PUSH_CONFIRM
if [[ "$PUSH_CONFIRM" =~ ^[Yy]$ ]]; then
    echo "[3/3] 推送镜像到 Docker Hub..."
    docker push "${IMAGE_NAME}:${TAG}"
    echo ""
    echo "推送完成: ${IMAGE_NAME}:${TAG}"
else
    echo "[3/3] 跳过推送"
fi

echo ""
echo "=========================================="
echo "  完成!"
echo "=========================================="
echo ""
echo "运行命令:"
echo "  docker run --gpus all -p 8080:8080 ${IMAGE_NAME}:${TAG}"
echo ""
