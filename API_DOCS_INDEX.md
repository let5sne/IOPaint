# IOPaint API 文档导航

本项目提供完整的 API 文档，适用于不同场景和需求。

## 📚 文档总览

| 文档 | 用途 | 适合人群 |
|------|------|---------|
| [API_SERVICE_README.md](./API_SERVICE_README.md) | 快速开始指南 | 所有用户 ⭐ |
| [RESTFUL_API_DOCUMENTATION.md](./RESTFUL_API_DOCUMENTATION.md) | 完整 REST API 文档 | 开发者 ⭐⭐⭐ |
| [API_CLIENT_EXAMPLES.md](./API_CLIENT_EXAMPLES.md) | 多语言客户端示例 | 集成开发者 ⭐⭐ |
| [API_SERVICE_GUIDE.md](./API_SERVICE_GUIDE.md) | 商业化部署方案 | 架构师/CTO ⭐⭐⭐ |
| [openapi.yaml](./openapi.yaml) | OpenAPI 规范 | 工具/自动化 ⭐⭐ |
| [IOPaint_API.postman_collection.json](./IOPaint_API.postman_collection.json) | Postman 集合 | API 测试 ⭐⭐ |

---

## 🎯 按场景选择文档

### 场景 1: 我想快速开始使用 API

**推荐文档**: [API_SERVICE_README.md](./API_SERVICE_README.md)

**内容包括**:
- 3 步启动服务
- API 使用示例
- 常见问题解决

**快速开始**:
```bash
# 1. 设置 API 密钥
export API_KEY="your_secret_key"

# 2. 启动服务
docker-compose -f docker-compose.mvp.yml up -d

# 3. 测试 API
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: $API_KEY" \
  -F "image=@test.jpg" \
  -o result.png
```

---

### 场景 2: 我需要集成 API 到我的应用

**推荐文档**:
1. [RESTFUL_API_DOCUMENTATION.md](./RESTFUL_API_DOCUMENTATION.md) - 完整 API 参考
2. [API_CLIENT_EXAMPLES.md](./API_CLIENT_EXAMPLES.md) - 代码示例

**支持的语言**:
- ✅ Python
- ✅ JavaScript/Node.js
- ✅ PHP
- ✅ Go
- ✅ Java
- ✅ cURL/Bash

**关键内容**:
- 认证方式
- 所有 API 端点
- 请求/响应格式
- 错误处理
- 限流规则
- 完整代码示例

---

### 场景 3: 我想测试 API

**推荐工具**:
1. [Postman Collection](./IOPaint_API.postman_collection.json) - 一键导入测试
2. Swagger UI - 在线交互式文档

**Postman 使用**:
1. 打开 Postman
2. Import → 选择 `IOPaint_API.postman_collection.json`
3. 设置环境变量 `api_key`
4. 发送请求测试

**Swagger UI 使用**:
```bash
# 启动服务后访问
http://localhost:8080/docs
```

---

### 场景 4: 我要自动生成客户端代码

**推荐文档**: [openapi.yaml](./openapi.yaml)

**支持的工具**:
- OpenAPI Generator
- Swagger Codegen
- Postman (导入 OpenAPI)

**示例**:
```bash
# 使用 OpenAPI Generator 生成 Python 客户端
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./python-client

# 生成 JavaScript 客户端
openapi-generator-cli generate \
  -i openapi.yaml \
  -g javascript \
  -o ./js-client
```

---

### 场景 5: 我要规划商业化部署

**推荐文档**: [API_SERVICE_GUIDE.md](./API_SERVICE_GUIDE.md)

**内容包括**:
- MVP 最小可行产品方案
- 商业化架构设计（单机 → K8s）
- 成本分析和收益模型
- 实施路线图
- 部署方案对比

**关键决策参考**:

| 月处理量 | 推荐方案 | 成本/月 |
|---------|---------|---------|
| < 10万张 | Docker 单机 | ￥300-500 |
| 10-50万张 | Docker Compose | ￥1000-3000 |
| 50万+张 | Kubernetes | ￥5000-20000 |

---

## 📖 文档详细说明

### 1. API_SERVICE_README.md

**快速开始指南** - 10分钟上手

```
内容：
✓ 快速部署（3步）
✓ API 基础使用
✓ 配置说明
✓ 性能基准
✓ 故障排查
✓ 实施路线图

适合：
• 第一次使用的用户
• 需要快速验证的团队
• POC 阶段
```

---

### 2. RESTFUL_API_DOCUMENTATION.md

**完整 REST API 文档** - OpenAI 风格专业文档

```
内容：
✓ 所有 API 端点详细说明
✓ 认证和安全
✓ 请求/响应示例
✓ 错误代码和处理
✓ 限流规则
✓ 最佳实践
✓ 性能优化建议
✓ 多语言代码示例

适合：
• API 集成开发者
• 需要完整技术参考
• 生产环境部署
```

**章节导航**:
- [Introduction](#introduction) - API 介绍
- [Authentication](#authentication) - 认证方式
- [API Endpoints](#api-endpoints) - 所有端点
- [Error Handling](#error-handling) - 错误处理
- [Rate Limiting](#rate-limiting) - 限流规则
- [Best Practices](#best-practices) - 最佳实践

---

### 3. API_CLIENT_EXAMPLES.md

**多语言客户端示例** - 复制粘贴即可用

```
内容：
✓ Python（基础 + 高级）
✓ JavaScript/Node.js
✓ PHP
✓ Go
✓ Java
✓ cURL + Bash 脚本
✓ 完整客户端类实现
✓ 批量处理示例
✓ 错误处理和重试

适合：
• 需要快速集成的开发者
• 学习如何调用 API
• 参考最佳实践
```

**每种语言包含**:
- 基础示例（最简单用法）
- 高级示例（错误处理、重试、批量）
- 完整客户端类
- 生产级代码

---

### 4. API_SERVICE_GUIDE.md

**商业化部署完整方案** - MVP 到规模化

```
内容：
✓ MVP 最小可行产品设计
✓ 商业化架构（单机→K8s）
✓ 成本分析（详细预算）
✓ 收益模型（定价建议）
✓ 部署方案对比
✓ 实施路线图
✓ 技术栈选择
✓ 监控和告警

适合：
• 创业者/产品经理
• 技术负责人
• 架构师
• CTO
```

**核心章节**:
- MVP 阶段（1-2个月）
- 产品优化（2-4个月）
- 规模化（4-6个月）
- Docker vs Kubernetes 对比
- 成本与扩展性分析

---

### 5. openapi.yaml

**OpenAPI 3.0.3 规范** - 机器可读的 API 定义

```
用途：
✓ Swagger UI 自动渲染
✓ Redoc 文档生成
✓ 客户端代码生成
✓ API 测试工具
✓ Mock 服务器

工具支持：
• Swagger UI
• Redoc
• Postman
• Insomnia
• OpenAPI Generator
• Swagger Codegen
```

**在线查看**:
```bash
# 启动服务后访问
http://localhost:8080/docs      # Swagger UI
http://localhost:8080/redoc     # ReDoc
```

**验证规范**:
```bash
# 安装 OpenAPI 验证工具
npm install -g @apidevtools/swagger-cli

# 验证文件
swagger-cli validate openapi.yaml
```

---

### 6. IOPaint_API.postman_collection.json

**Postman Collection V2.1** - API 测试集合

```
包含：
✓ 所有 API 端点
✓ 预配置的测试脚本
✓ 环境变量模板
✓ 示例请求/响应
✓ 自动化测试

功能：
• 一键导入
• 快速测试
• 自动化测试
• 团队分享
```

**导入步骤**:
1. 打开 Postman
2. File → Import
3. 选择 `IOPaint_API.postman_collection.json`
4. 设置变量：
   - `base_url`: `http://localhost:8080`
   - `api_key`: `your_secret_key_change_me`
5. 开始测试

---

## 🔗 相关资源

### 在线资源

- **项目仓库**: https://github.com/let5sne/IOPaint
- **API 分支**: https://github.com/let5sne/IOPaint/tree/feature/api-service
- **在线文档**: http://localhost:8080/docs (需先启动服务)

### 开发工具

| 工具 | 用途 | 链接 |
|------|------|------|
| Postman | API 测试 | https://www.postman.com/ |
| Swagger UI | API 文档 | https://swagger.io/tools/swagger-ui/ |
| Redoc | API 文档 | https://github.com/Redocly/redoc |
| OpenAPI Generator | 代码生成 | https://openapi-generator.tech/ |

### 推荐阅读

- [RESTful API 设计指南](https://github.com/microsoft/api-guidelines)
- [OpenAPI 规范](https://swagger.io/specification/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)

---

## 💡 使用建议

### 新手路径

```
1. 阅读 API_SERVICE_README.md（了解基础）
   ↓
2. 启动服务并访问 /docs（在线测试）
   ↓
3. 导入 Postman Collection（实际测试）
   ↓
4. 参考 API_CLIENT_EXAMPLES.md（集成到应用）
```

### 开发者路径

```
1. 阅读 RESTFUL_API_DOCUMENTATION.md（理解 API）
   ↓
2. 使用 openapi.yaml 生成客户端代码
   ↓
3. 参考 Best Practices 优化集成
   ↓
4. 阅读 API_SERVICE_GUIDE.md（了解架构）
```

### 决策者路径

```
1. 阅读 API_SERVICE_GUIDE.md（了解方案）
   ↓
2. 评估成本和收益模型
   ↓
3. 选择合适的部署方案
   ↓
4. 制定实施路线图
```

---

## 📞 获取帮助

### 问题排查

1. **API 无法访问** → 查看 [API_SERVICE_README.md - 故障排查](./API_SERVICE_README.md#故障排查)
2. **认证失败** → 查看 [RESTFUL_API_DOCUMENTATION.md - Authentication](./RESTFUL_API_DOCUMENTATION.md#authentication)
3. **性能问题** → 查看 [RESTFUL_API_DOCUMENTATION.md - Best Practices](./RESTFUL_API_DOCUMENTATION.md#best-practices)
4. **部署问题** → 查看 [API_SERVICE_GUIDE.md - 部署方案](./API_SERVICE_GUIDE.md#部署方案对比)

### 联系方式

- **GitHub Issues**: https://github.com/let5sne/IOPaint/issues
- **文档反馈**: 在对应文档提 Issue

---

## 📝 文档更新日志

### 2025-11-28

**新增**:
- ✨ API_SERVICE_README.md - 快速开始指南
- ✨ RESTFUL_API_DOCUMENTATION.md - 完整 REST API 文档
- ✨ API_CLIENT_EXAMPLES.md - 多语言客户端示例
- ✨ API_SERVICE_GUIDE.md - 商业化部署方案
- ✨ openapi.yaml - OpenAPI 3.0.3 规范
- ✨ IOPaint_API.postman_collection.json - Postman 测试集合
- ✨ API_DOCS_INDEX.md - 文档导航（本文档）

**特点**:
- 符合 OpenAPI 标准
- OpenAI 风格专业文档
- 多语言代码示例
- 完整的部署方案
- 生产级最佳实践

---

**快速开始**: 阅读 [API_SERVICE_README.md](./API_SERVICE_README.md) 👈

**完整 API 参考**: 阅读 [RESTFUL_API_DOCUMENTATION.md](./RESTFUL_API_DOCUMENTATION.md) 👈

**商业化方案**: 阅读 [API_SERVICE_GUIDE.md](./API_SERVICE_GUIDE.md) 👈
