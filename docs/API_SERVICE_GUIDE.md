# IOPaint 去水印 API 服务设计方案

## 📋 目录
1. [MVP 最小可行产品](#mvp-最小可行产品)
2. [商业化架构设计](#商业化架构设计)
3. [部署方案对比](#部署方案对比)
4. [成本与扩展性分析](#成本与扩展性分析)

---

## 🚀 MVP 最小可行产品

### 设计原则（KISS）
- **单一功能**：只提供去水印API，不包含WebUI
- **单一模型**：只使用LaMa模型（快速、低资源）
- **简单认证**：API Key认证
- **本地存储**：无需对象存储
- **单机部署**：Docker Compose即可

### 核心改造

#### 1. 精简API服务 (`api_service.py`)
```python
# 只保留核心功能：
# - POST /api/v1/remove-watermark - 去水印接口
# - GET /api/v1/health - 健康检查
# - GET /api/v1/usage - 使用统计（可选）

# 移除功能：
# - WebUI相关路由
# - 多模型支持
# - 插件系统
# - 文件浏览器
# - Socket.IO实时通信
```

#### 2. API接口设计

**去水印接口**
```bash
POST /api/v1/remove-watermark
Headers:
  X-API-Key: your_api_key_here
  Content-Type: multipart/form-data

Body:
  image: file (必需) - 原始图片
  mask: file (可选) - 水印遮罩，不提供则自动检测

Response:
  - 200: 返回处理后的图片（image/png）
  - 401: API Key无效
  - 400: 参数错误
  - 500: 处理失败
```

**健康检查**
```bash
GET /api/v1/health
Response: {"status": "ok", "model": "lama"}
```

#### 3. MVP部署架构

```
┌─────────────────────────────────────┐
│          Nginx (反向代理)            │
│   - SSL终止                          │
│   - 限流 (rate limiting)             │
│   - 日志记录                         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      IOPaint API Service            │
│   - FastAPI                          │
│   - LaMa模型                         │
│   - API Key认证                      │
│   - 本地存储                         │
└─────────────────────────────────────┘
```

#### 4. MVP Docker配置

**单容器方案**：适合月处理量 < 10万张
```yaml
# docker-compose.mvp.yml
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: docker/APIDockerfile
    ports:
      - "8080:8080"
    environment:
      - API_KEY=your_secret_key_here
      - MAX_IMAGE_SIZE=4096
      - ENABLE_METRICS=true
    volumes:
      - ./models:/root/.cache
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

**成本估算（MVP阶段）**：
- **云服务器**：2核4G，约￥200-300/月（阿里云、腾讯云）
- **存储**：100GB SSD，约￥50/月
- **流量**：100GB/月，约￥50/月
- **总计**：约￥300-400/月

**性能预估**：
- 处理速度：约1-2秒/张（1024x1024）
- 并发能力：2-4个请求
- 月处理量：~5-10万张

---

## 🏢 商业化架构设计

### 设计原则
- **横向扩展**：支持动态增减实例
- **高可用**：无单点故障
- **异步处理**：支持批量和队列
- **监控完善**：实时监控和告警
- **成本优化**：按需扩展

### 商业化架构图

```
                   ┌─────────────────┐
                   │   CDN / CloudFlare  │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │  Load Balancer   │  (Nginx/HAProxy/ALB)
                   │  - SSL终止       │
                   │  - 限流          │
                   │  - WAF           │
                   └────────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │API Pod 1│        │API Pod 2│        │API Pod N│
   │ (GPU)   │        │ (GPU)   │        │ (GPU)   │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │  Redis  │        │PostgreSQL│        │   S3    │
   │ (队列)  │        │ (元数据) │        │ (存储)  │
   └─────────┘        └──────────┘        └─────────┘
        │
   ┌────▼────┐
   │ Celery  │
   │ Worker  │
   └─────────┘
        │
   ┌────▼────┐
   │Prometheus│
   │ Grafana │
   └─────────┘
```

### 核心组件

#### 1. API层（Kubernetes部署）

**api-deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iopaint-api
spec:
  replicas: 3  # 根据负载自动扩展
  template:
    spec:
      containers:
      - name: api
        image: let5sne/iopaint-api:latest
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1
        env:
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: S3_BUCKET
          value: "iopaint-images"
```

#### 2. 异步任务队列（Redis + Celery）

**好处**：
- 避免API超时
- 支持批量处理
- 可重试失败任务
- 平滑处理流量峰值

**工作流程**：
```
1. 用户上传图片 → API返回任务ID
2. 图片存入S3 → 任务推入Redis队列
3. Celery Worker异步处理
4. 处理完成 → 更新数据库 → 触发回调/Webhook
```

#### 3. 数据库设计（PostgreSQL）

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    plan VARCHAR(20) NOT NULL,  -- free, basic, pro, enterprise
    quota_monthly INT NOT NULL,
    quota_used INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 任务表
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id INT REFERENCES users(id),
    status VARCHAR(20) NOT NULL,  -- pending, processing, completed, failed
    image_url TEXT NOT NULL,
    result_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    processing_time_ms INT
);

-- 使用统计表（按日汇总）
CREATE TABLE usage_stats (
    date DATE NOT NULL,
    user_id INT REFERENCES users(id),
    requests_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    avg_processing_time_ms INT,
    PRIMARY KEY (date, user_id)
);
```

#### 4. 监控与告警

**Prometheus指标**：
```python
# 核心业务指标
requests_total = Counter('api_requests_total', 'Total API requests', ['status', 'endpoint'])
processing_time = Histogram('image_processing_seconds', 'Image processing time')
model_inference_time = Histogram('model_inference_seconds', 'Model inference time')
queue_size = Gauge('redis_queue_size', 'Current queue size')
gpu_utilization = Gauge('gpu_utilization', 'GPU utilization %')
```

**告警规则**：
- API错误率 > 5%
- 队列积压 > 1000
- GPU利用率 > 90%（持续5分钟）
- 响应时间 > 10秒（P95）

#### 5. 成本优化策略

**弹性伸缩**：
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: iopaint-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: iopaint-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: nvidia.com/gpu
      target:
        type: Utilization
        averageUtilization: 80
```

**Spot实例**：
- 使用云厂商Spot/抢占式实例，成本降低60-80%
- 配合优先级队列，重要任务用按需实例

---

## 🔄 部署方案对比

| 方案 | 适用场景 | 优点 | 缺点 | 月成本估算 |
|------|---------|------|------|-----------|
| **Docker单机** | 个人/小团队<br>月< 10万张 | • 部署简单<br>• 成本低<br>• 维护容易 | • 无法扩展<br>• 单点故障<br>• 性能有限 | ￥300-500 |
| **Docker Compose多容器** | 小型商业<br>月10-50万张 | • 支持多实例<br>• 负载均衡<br>• 成本可控 | • 手动扩展<br>• 监控有限<br>• 高可用差 | ￥1000-3000 |
| **Kubernetes** | 中大型商业<br>月50万张+ | • 自动扩展<br>• 高可用<br>• 完善监控<br>• 多云部署 | • 复杂度高<br>• 学习成本<br>• 初期成本高 | ￥5000-20000+ |
| **Serverless (Lambda/云函数)** | 不规则流量<br>峰谷明显 | • 按用付费<br>• 无需运维<br>• 无限扩展 | • 冷启动慢<br>• GPU支持差<br>• 单次限制 | 按用量计费 |

---

## 💰 成本与扩展性分析

### MVP阶段（月处理10万张）

**方案：单机Docker**
```
硬件：
  - 云服务器 2核4G（CPU版本）：￥200/月
  或
  - GPU服务器 4核16G + T4（GPU版本）：￥800/月

存储：
  - 系统盘 100GB SSD：￥50/月
  - 模型缓存：~5GB（LaMa）

带宽：
  - 假设平均每张图500KB，10万张 = 50GB
  - 上传 + 下载 = 100GB，约￥60/月

总计：
  - CPU版本：约￥310/月
  - GPU版本：约￥910/月（推荐，处理速度快10倍）
```

### 商业化阶段（月处理100万张）

**方案：Kubernetes + GPU节点池**
```
计算资源（3个GPU节点，自动扩展）：
  - 3 x (4核16G + T4 GPU)：￥2400/月
  - 高峰期额外2个节点（Spot实例）：￥400/月

数据库：
  - PostgreSQL云数据库（2核4G）：￥300/月
  - Redis云实例（2G）：￥150/月

存储：
  - 对象存储 500GB：￥100/月
  - 数据库存储 100GB：￥50/月

CDN + 流量：
  - CDN加速：￥200/月
  - 带宽流量（1TB）：￥600/月

监控 + 日志：
  - 日志服务：￥100/月
  - 监控告警：￥100/月

负载均衡：￥100/月

总计：约￥4500-5000/月
```

**收益模型（参考）**：
```
定价方案：
  - Free: 10张/天，免费
  - Basic: ￥99/月，3000张
  - Pro: ￥399/月，20000张
  - Enterprise: ￥1999/月，150000张，优先处理

假设用户分布：
  - Free用户：1000人 = 0元（引流）
  - Basic用户：200人 = ￥19,800
  - Pro用户：50人 = ￥19,950
  - Enterprise：10人 = ￥19,990

月收入：约￥59,740
月成本：约￥5,000
月利润：约￥54,740
```

---

## 📝 推荐实施路线

### 阶段1：MVP验证（1-2个月）
**目标**：验证市场需求，获取前100个付费用户

**技术栈**：
- Docker单机部署
- FastAPI + LaMa模型
- 简单API Key认证
- SQLite本地数据库

**投入**：
- 开发时间：1周
- 服务器成本：￥300-500/月
- 域名+SSL：￥100/年

**里程碑**：
- [ ] API服务上线
- [ ] 文档和示例代码
- [ ] 支付集成（微信/支付宝）
- [ ] 获取前10个付费用户
- [ ] 收集用户反馈

### 阶段2：产品优化（2-4个月）
**目标**：优化体验，扩展到1000付费用户

**技术栈**：
- Docker Compose多容器
- PostgreSQL数据库
- Redis缓存
- 简单监控（Prometheus）

**投入**：
- 开发时间：2周
- 服务器成本：￥1000-2000/月

**里程碑**：
- [ ] 批量处理API
- [ ] Webhook回调
- [ ] 使用Dashboard
- [ ] 自动检测水印（可选）
- [ ] API SDK（Python/Node.js）

### 阶段3：规模化（4-6个月）
**目标**：支持月百万级处理，稳定盈利

**技术栈**：
- Kubernetes集群
- 对象存储
- 完整监控体系
- 多模型支持（可选）

**投入**：
- 开发时间：4周
- 基础设施成本：￥5000-10000/月

**里程碑**：
- [ ] 自动扩展
- [ ] 多区域部署
- [ ] SLA保证（99.9%）
- [ ] 企业级支持

---

## 🎯 关键建议

### 1. MVP阶段重点
✅ **做**：
- 专注核心功能（去水印）
- 简单可靠的API
- 完善的文档和示例
- 快速迭代

❌ **不做**：
- 复杂的功能（多模型、插件）
- 过度设计的架构
- 过早优化性能
- WebUI界面

### 2. Docker vs Kubernetes

**用Docker如果**：
- 月处理量 < 50万张
- 团队 < 3人
- 预算有限
- 流量相对稳定

**用Kubernetes如果**：
- 月处理量 > 50万张
- 需要高可用（99.9%+）
- 流量波动大
- 计划多区域部署

### 3. 技术债务控制

**从一开始就做好**：
- API版本控制（/api/v1/）
- 完善的错误处理和日志
- API限流和认证
- 数据备份策略

**可以后续优化**：
- 监控系统（先简单后完善）
- 自动扩展（先手动后自动）
- 多模型支持（先单模型验证）
- 高级功能（批量、回调等）

### 4. 安全建议

**必须**：
- HTTPS强制
- API Key认证
- 请求限流
- 输入验证（文件大小、格式）
- 敏感信息加密

**推荐**：
- WAF防护
- DDoS防护
- 审计日志
- 定期安全扫描

---

## 📚 参考资源

- [FastAPI最佳实践](https://fastapi.tiangolo.com/tutorial/)
- [Kubernetes生产实践](https://kubernetes.io/docs/setup/production-environment/)
- [AWS架构最佳实践](https://aws.amazon.com/architecture/well-architected/)
- [API设计指南](https://github.com/microsoft/api-guidelines)
