# IOPaint 依赖包升级说明

## 升级日期
2025-11-28

## 升级概述

本次升级将项目的主要依赖包更新到了最新的稳定版本，以获得更好的性能、更多功能和安全性改进。

## 包版本变化

### 核心 AI 库

| 包名 | 原版本 | 新版本 | 说明 |
|------|--------|--------|------|
| diffusers | 0.27.2 | ≥0.35.0 | Hugging Face 扩散模型库，支持更多新模型 |
| huggingface_hub | 0.25.2 | ≥0.26.0 | 模型下载和管理 |
| peft | 0.7.1 | ≥0.13.0 | 参数高效微调库 |
| transformers | ≥4.39.1 | ≥4.45.0 | Transformer 模型库 |
| controlnet-aux | 0.0.3 | ≥0.0.9 | ControlNet 预处理工具 |

### Web 框架

| 包名 | 原版本 | 新版本 | 说明 |
|------|--------|--------|------|
| fastapi | 0.108.0 | ≥0.115.0 | Web API 框架 |
| gradio | 4.21.0 | ≥5.0.0,<6.0.0 | Web UI 框架（限制<6.0以避免破坏性变更） |
| python-socketio | 5.7.2 | ≥5.11.0 | WebSocket 支持 |

### 工具库

| 包名 | 原版本 | 新版本 | 说明 |
|------|--------|--------|------|
| Pillow | 9.5.0 | ≥10.0.0 | 图像处理库 |
| piexif | 1.1.3 | ≥1.1.3 | EXIF 处理 |
| typer-config | 1.4.0 | ≥1.4.0 | CLI 配置 |

## 代码修改

### 1. 修复 PyTorch 弃用警告

**文件:** `iopaint/model/ldm.py:279`

**修改前:**
```python
@torch.cuda.amp.autocast()
def forward(self, image, mask, config: InpaintRequest):
```

**修改后:**
```python
@torch.amp.autocast('cuda')
def forward(self, image, mask, config: InpaintRequest):
```

**原因:** PyTorch 2.x 更新了 autocast API，旧版本已被弃用。

## 兼容性测试

✅ **所有测试通过:**
- ✓ 核心模块导入
- ✓ Diffusers API 兼容性
- ✓ Gradio 5.x API 兼容性
- ✓ FastAPI 兼容性
- ✓ CLI 命令正常工作
- ✓ 服务器启动正常

## 安装说明

### 使用国内镜像源（推荐）

```bash
# 使用阿里云镜像源
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 或使用清华镜像源
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 使用官方源

```bash
pip3 install -r requirements.txt
```

### 验证安装

```bash
# 测试基础导入
python3 -c "from iopaint import entry_point; print('✓ IOPaint 安装成功')"

# 测试 CLI
python3 main.py --help

# 启动服务器测试
python3 main.py start --model lama --device cpu --port 8080
```

## 潜在影响

### 向后兼容性
- ✅ 所有现有功能保持兼容
- ✅ API 接口无变化
- ✅ 配置文件格式无变化

### 性能改进
- 🚀 Diffusers 0.35.x 提供了更快的推理速度
- 🚀 Gradio 5.x 改进了 UI 响应性能
- 🚀 FastAPI 新版本提升了并发处理能力

### 新功能支持
- ✨ 支持更多最新的 Stable Diffusion 模型
- ✨ ControlNet 预处理支持更多模型
- ✨ Gradio 5.x 提供更好的用户体验

## 已知问题

### 警告信息（可忽略）
运行时可能看到以下警告，不影响功能：
- `controlnet_aux` 关于 mediapipe 的警告（除非使用相关功能）
- `timm` 模块导入路径的 FutureWarning

### 解决方案
这些是依赖包的警告，不影响 IOPaint 核心功能。如需消除警告：
```bash
pip3 install mediapipe  # 如果使用 MediaPipe 相关功能
```

## 回滚方案

如果遇到问题需要回滚到旧版本：

```bash
# 恢复旧版本
git checkout <previous_commit>
pip3 install -r requirements.txt --force-reinstall
```

或手动安装旧版本：
```bash
pip3 install diffusers==0.27.2 gradio==4.21.0 fastapi==0.108.0 peft==0.7.1 Pillow==9.5.0
```

## 测试建议

升级后建议进行以下测试：

1. **基础功能测试**
   ```bash
   python3 main.py start --model lama --device cpu
   ```

2. **Diffusion 模型测试**
   ```bash
   python3 main.py start --model runwayml/stable-diffusion-inpainting --device cuda
   ```

3. **批处理测试**
   ```bash
   python3 main.py run --model lama --device cpu --image <path> --mask <path> --output <path>
   ```

4. **插件功能测试**
   ```bash
   python3 main.py start --enable-interactive-seg --enable-remove-bg
   ```

## 联系与反馈

如果在升级过程中遇到问题，请：
1. 检查本文档的"已知问题"部分
2. 查看 GitHub Issues
3. 提交新的 Issue 并附上错误日志

## 更新日志

- 2025-11-28: 首次发布，更新所有主要依赖到最新稳定版本
