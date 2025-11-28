#!/usr/bin/env bash
set -e

GIT_TAG=$1
IMAGE_DESC="IOPaint - Free and open-source inpainting & outpainting tool powered by SOTA AI models"
GIT_REPO="https://github.com/let5sne/IOPaint"

echo "Building CPU docker image..."

docker buildx build \
--platform linux/amd64 \
--file ./docker/CPUDockerfile \
--label org.opencontainers.image.title=IOPaint \
--label org.opencontainers.image.description="$IMAGE_DESC" \
--label org.opencontainers.image.url=$GIT_REPO \
--label org.opencontainers.image.source=$GIT_REPO \
--label org.opencontainers.image.version=$GIT_TAG \
--build-arg version=$GIT_TAG \
--tag let5sne/iopaint:cpu-$GIT_TAG .


echo "Building NVIDIA GPU docker image..."

docker buildx build \
--platform linux/amd64 \
--file ./docker/GPUDockerfile \
--label org.opencontainers.image.title=IOPaint \
--label org.opencontainers.image.description="$IMAGE_DESC" \
--label org.opencontainers.image.url=$GIT_REPO \
--label org.opencontainers.image.source=$GIT_REPO \
--label org.opencontainers.image.version=$GIT_TAG \
--build-arg version=$GIT_TAG \
--tag let5sne/iopaint:gpu-$GIT_TAG .
