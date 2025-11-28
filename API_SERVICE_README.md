# IOPaint 去水印 API 服务

专注于提供去水印功能的精简API服务，适合商业化部署。

## 🎯 项目特点

- **单一职责**：专注去水印功能，移除WebUI和其他复杂功能
- **高性能**：使用LaMa模型，1-2秒处理一张1024x1024图片
- **易部署**：Docker一键部署，支持CPU和GPU
- **低成本**：MVP阶段月成本约￥300-500
- **可扩展**：提供完整的商业化架构方案

## 📚 文档

- [完整设计方案](./API_SERVICE_GUIDE.md) - MVP到商业化的完整路线图
- [客户端示例](./API_CLIENT_EXAMPLES.md) - Python、JavaScript、cURL等多语言调用示例

## 🚀 快速开始

### 方式1：Docker Compose部署（推荐）

```bash
# 1. 设置API密钥
export API_KEY="your_secret_key_here"

# 2. 启动服务（GPU版本）
docker-compose -f docker-compose.mvp.yml up -d

# 3. 检查服务状态
curl http://localhost:8080/api/v1/health

# 4. 测试去水印
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: $API_KEY" \
  -F "image=@test.jpg" \
  -o result.png
```

### 方式2：直接运行Python脚本

```bash
# 1. 安装依赖
pip3 install -r requirements.txt
pip3 install -e .

# 2. 设置环境变量
export API_KEY="your_secret_key_here"

# 3. 启动服务
python3 api_service_mvp.py

# 4. 访问 http://localhost:8080/docs 查看API文档
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_KEY` | API访问密钥 | `your_secret_key_change_me` |
| `MAX_IMAGE_SIZE` | 最大图片边长（像素） | `4096` |
| `ENABLE_METRICS` | 启用统计指标 | `true` |

### 硬件要求

**最低配置（CPU版本）**：
- CPU: 2核
- 内存: 4GB
- 磁盘: 20GB
- 性能: ~10-15秒/张

**推荐配置（GPU版本）**：
- CPU: 4核
- 内存: 8GB
- GPU: NVIDIA T4或更好（2GB+ VRAM）
- 磁盘: 30GB
- 性能: ~1-2秒/张

## 📖 API文档

### 核心接口

#### 1. 去水印接口

```http
POST /api/v1/remove-watermark
```

**请求头**：
- `X-API-Key`: API密钥（必需）
- `Content-Type`: multipart/form-data

**请求体**：
- `image`: 图片文件（必需）
- `mask`: 遮罩图片（可选，白色区域将被修复）

**响应**：
- 成功：返回处理后的PNG图片
- 失败：返回JSON错误信息

**示例**：
```bash
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: your_key" \
  -F "image=@input.jpg" \
  -o result.png
```

#### 2. 健康检查

```http
GET /api/v1/health
```

**响应**：
```json
{
  "status": "healthy",
  "model": "lama",
  "device": "cuda",
  "gpu_available": true
}
```

#### 3. 使用统计

```http
GET /api/v1/stats
```

**请求头**：
- `X-API-Key`: API密钥（必需）

**响应**：
```json
{
  "total": 1000,
  "success": 980,
  "failed": 20,
  "avg_processing_time": 1.5
}
```

## 💡 使用示例

### Python

```python
import requests

def remove_watermark(image_path, api_key):
    url = "http://localhost:8080/api/v1/remove-watermark"
    headers = {"X-API-Key": api_key}
    files = {"image": open(image_path, "rb")}

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        with open("result.png", "wb") as f:
            f.write(response.content)
        print("✓ 处理成功！")
    else:
        print(f"✗ 失败: {response.json()}")

remove_watermark("test.jpg", "your_api_key")
```

更多语言示例请查看 [API_CLIENT_EXAMPLES.md](./API_CLIENT_EXAMPLES.md)

## 📊 性能基准

基于NVIDIA T4 GPU测试：

| 图片尺寸 | 处理时间 | 内存占用 | 每秒处理 |
|----------|---------|----------|---------|
| 512x512 | ~0.8秒 | ~1.5GB | ~1.25张/秒 |
| 1024x1024 | ~1.5秒 | ~2GB | ~0.67张/秒 |
| 2048x2048 | ~4秒 | ~3.5GB | ~0.25张/秒 |
| 4096x4096 | ~15秒 | ~6GB | ~0.07张/秒 |

## 🏗️ 架构方案

### MVP阶段（月处理10万张）
- **部署方式**：Docker单机
- **成本**：约￥300-500/月
- **支持用户**：100-500人

### 商业化阶段（月处理100万张）
- **部署方式**：Kubernetes + GPU节点池
- **成本**：约￥5000-10000/月
- **支持用户**：5000+人
- **特性**：
  - 自动扩展
  - 异步队列（Redis + Celery）
  - 对象存储（S3/OSS）
  - 完整监控（Prometheus + Grafana）

详细架构请查看 [API_SERVICE_GUIDE.md](./API_SERVICE_GUIDE.md)

## 💰 定价建议（参考）

| 套餐 | 价格 | 额度 | 适用场景 |
|------|------|------|---------|
| **Free** | ¥0/月 | 10张/天 | 个人测试 |
| **Basic** | ¥99/月 | 3000张 | 小型工作室 |
| **Pro** | ¥399/月 | 20000张 | 中型企业 |
| **Enterprise** | ¥1999/月 | 150000张 | 大型企业 |

## 🔒 安全建议

1. **生产环境务必修改默认API密钥**
2. **使用HTTPS**（配置Nginx SSL）
3. **启用限流**（防止滥用）
4. **定期备份数据库**
5. **监控异常访问**

## 🐛 故障排查

### 常见问题

**1. API返回401错误**
- 检查X-API-Key header是否正确
- 确认API_KEY环境变量已设置

**2. 处理速度慢**
- CPU模式：考虑升级到GPU
- GPU模式：检查显存是否充足
- 检查图片是否过大

**3. Docker容器无法启动**
- GPU版本：确认nvidia-docker已安装
- 检查端口8080是否被占用
- 查看日志：`docker-compose logs api`

**4. 返回500错误**
- 查看服务日志：`tail -f logs/api_*.log`
- 检查磁盘空间是否充足
- 确认模型文件已下载

## 📈 监控指标

推荐监控以下指标：

- **业务指标**：
  - 请求总数
  - 成功率
  - 平均处理时间
  - 队列长度

- **系统指标**：
  - CPU使用率
  - GPU使用率
  - 内存使用
  - 磁盘I/O

- **告警阈值**：
  - 错误率 > 5%
  - 响应时间P95 > 10秒
  - GPU利用率 > 90%（持续5分钟）

## 🚦 实施路线图

### 第1周：MVP上线
- [ ] 部署API服务
- [ ] 编写使用文档
- [ ] 集成支付系统
- [ ] 获取前10个用户反馈

### 第2-4周：产品优化
- [ ] 优化处理速度
- [ ] 添加批量处理API
- [ ] 实现Webhook回调
- [ ] 创建使用Dashboard

### 第2-3个月：规模化
- [ ] 迁移到Kubernetes
- [ ] 添加自动扩展
- [ ] 实现异步队列
- [ ] 完善监控系统

## 📞 技术支持

- **文档**: [API_SERVICE_GUIDE.md](./API_SERVICE_GUIDE.md)
- **示例**: [API_CLIENT_EXAMPLES.md](./API_CLIENT_EXAMPLES.md)
- **问题反馈**: https://github.com/let5sne/IOPaint/issues
- **在线文档**: `http://localhost:8080/docs` (Swagger UI)

## 📄 许可证

本项目基于 Apache-2.0 许可证开源。

---

**⚡ 立即开始：**
```bash
git clone https://github.com/let5sne/IOPaint.git
cd IOPaint
export API_KEY="your_secret_key"
docker-compose -f docker-compose.mvp.yml up -d
```

访问 http://localhost:8080/docs 查看完整API文档！
