# IOPaint Docker 部署指南

本目录包含 IOPaint 的 Docker 配置文件，支持 CPU 和 GPU 两种模式。

## 📦 可用镜像

### CPU 版本
适用于没有 NVIDIA GPU 的环境。

### GPU 版本
适用于有 NVIDIA GPU 的环境，性能更好。

## 🚀 快速开始

### 使用预构建的镜像（推荐）

**CPU 模式：**
```bash
docker pull let5sne/iopaint:cpu-latest
docker run -d -p 8080:8080 let5sne/iopaint:cpu-latest
```

**GPU 模式：**
```bash
docker pull let5sne/iopaint:gpu-latest
docker run --gpus all -d -p 8080:8080 let5sne/iopaint:gpu-latest
```

访问 `http://localhost:8080` 使用 IOPaint。

### 从源码构建

**构建所有镜像：**
```bash
# 在项目根目录执行
bash build_docker.sh 1.0.0  # 替换为版本号
```

**构建单个镜像：**

CPU 版本：
```bash
docker build -f docker/CPUDockerfile -t let5sne/iopaint:cpu-latest .
```

GPU 版本：
```bash
docker build -f docker/GPUDockerfile -t let5sne/iopaint:gpu-latest .
```

## 🔧 运行配置

### 基础运行

```bash
# CPU 模式
docker run -d -p 8080:8080 let5sne/iopaint:cpu-latest

# GPU 模式（需要 nvidia-docker）
docker run --gpus all -d -p 8080:8080 let5sne/iopaint:gpu-latest
```

### 挂载数据目录

```bash
docker run -d \
  -p 8080:8080 \
  -v /path/to/input:/app/input \
  -v /path/to/output:/app/output \
  -v /path/to/models:/root/.cache \
  let5sne/iopaint:gpu-latest
```

### 自定义启动参数

```bash
docker run -d -p 8080:8080 let5sne/iopaint:gpu-latest \
  python3 main.py start \
  --model runwayml/stable-diffusion-inpainting \
  --device cuda \
  --port 8080 \
  --host 0.0.0.0
```

### 使用不同模型

```bash
# 使用 SD Inpainting 模型
docker run -d -p 8080:8080 let5sne/iopaint:gpu-latest \
  python3 main.py start --model runwayml/stable-diffusion-inpainting --device cuda --port 8080 --host 0.0.0.0

# 使用 SDXL 模型（低内存模式）
docker run -d -p 8080:8080 let5sne/iopaint:gpu-latest \
  python3 main.py start --model diffusers/stable-diffusion-xl-1.0-inpainting-0.1 --device cuda --low-mem --port 8080 --host 0.0.0.0
```

## 📊 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  iopaint-gpu:
    image: let5sne/iopaint:gpu-latest
    ports:
      - "8080:8080"
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./models:/root/.cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  iopaint-cpu:
    image: let5sne/iopaint:cpu-latest
    ports:
      - "8081:8080"
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./models:/root/.cache
    restart: unless-stopped
```

启动：
```bash
# 启动 GPU 服务
docker-compose up -d iopaint-gpu

# 启动 CPU 服务
docker-compose up -d iopaint-cpu
```

## 🛠️ 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HF_HOME` | HuggingFace 模型缓存目录 | `/root/.cache` |
| `PYTORCH_CUDA_ALLOC_CONF` | CUDA 内存分配配置 | - |

设置环境变量：
```bash
docker run -d \
  -p 8080:8080 \
  -e HF_HOME=/models \
  -v /path/to/models:/models \
  let5sne/iopaint:gpu-latest
```

## 📋 系统要求

### CPU 版本
- RAM: 至少 4GB
- 磁盘: 至少 10GB 可用空间

### GPU 版本
- NVIDIA GPU（支持 CUDA）
- VRAM: 
  - LaMa 模型: 至少 2GB
  - SD Inpainting: 至少 8GB
  - SDXL: 至少 12GB
- 磁盘: 至少 20GB 可用空间
- nvidia-docker 或 Docker 19.03+（支持 --gpus）

## 🔍 故障排查

### GPU 无法使用

检查 nvidia-docker 是否正确安装：
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 端口冲突

修改端口映射：
```bash
docker run -d -p 8888:8080 let5sne/iopaint:gpu-latest
```

### 模型下载慢

使用 HuggingFace 镜像：
```bash
docker run -d \
  -p 8080:8080 \
  -e HF_ENDPOINT=https://hf-mirror.com \
  let5sne/iopaint:gpu-latest
```

### 内存不足

对于 SDXL 等大模型，使用低内存模式：
```bash
docker run -d -p 8080:8080 let5sne/iopaint:gpu-latest \
  python3 main.py start --model diffusers/stable-diffusion-xl-1.0-inpainting-0.1 --device cuda --low-mem --cpu-offload --port 8080 --host 0.0.0.0
```

## 📖 更多信息

- 项目主页：https://github.com/let5sne/IOPaint
- 文档：查看项目根目录的 README.md
- 问题反馈：https://github.com/let5sne/IOPaint/issues

## 🔐 安全建议

1. **不要暴露到公网**：默认配置仅用于本地使用
2. **使用代理**：如需公网访问，建议使用 Nginx 反向代理并配置 HTTPS
3. **限制资源**：使用 Docker 资源限制避免过度占用系统资源

```bash
docker run -d \
  -p 8080:8080 \
  --memory="4g" \
  --cpus="2.0" \
  let5sne/iopaint:cpu-latest
```

## 📝 更新日志

### Version 1.0.0 (2025-11-28)
- 更新为 IOPaint 项目
- 使用最新依赖版本
- 支持 CUDA 12.1
- 从源码构建而非 PyPI 安装
- 添加详细的使用文档
