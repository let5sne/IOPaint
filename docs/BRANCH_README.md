# IOPaint API Service Branch

这是 **IOPaint 去水印 API 服务** 的独立分支，专注于提供商业化的 REST API 服务。

## 🌿 分支说明

### 主要分支对比

| 分支 | 用途 | 特点 | 适用场景 |
|------|------|------|---------|
| **main/master** | 完整版 IOPaint | • WebUI 界面<br>• 多种模型<br>• 插件系统<br>• 批处理功能 | 个人使用、本地工具 |
| **feature/api-service** | API 服务版 | • 纯 REST API<br>• 单一模型（LaMa）<br>• 商业化就绪<br>• 易于部署 | 企业集成、SaaS 服务 |

## 📦 本分支内容

### 核心文件

**服务代码**:
- `api_service_mvp.py` - 精简的 API 服务实现
- `docker/APIDockerfile` - API 服务 Docker 镜像
- `docker-compose.mvp.yml` - MVP 部署配置
- `nginx/nginx.conf` - Nginx 反向代理配置

**完整文档**:
- `API_DOCS_INDEX.md` - 📑 文档导航（从这里开始）
- `RESTFUL_API_DOCUMENTATION.md` - 📖 完整 REST API 文档
- `API_SERVICE_README.md` - 🚀 快速开始指南
- `API_CLIENT_EXAMPLES.md` - 💻 多语言客户端示例
- `API_SERVICE_GUIDE.md` - 🏗️ 商业化部署方案
- `openapi.yaml` - 🔧 OpenAPI 3.0.3 规范
- `IOPaint_API.postman_collection.json` - 🧪 Postman 测试集合

### 与主分支的差异

**移除的功能**:
- ❌ WebUI 界面（前端代码仍在，但不使用）
- ❌ 多模型支持（只保留 LaMa）
- ❌ 插件系统
- ❌ 文件浏览器
- ❌ Socket.IO 实时通信

**新增的功能**:
- ✅ RESTful API 服务
- ✅ API Key 认证
- ✅ 使用统计
- ✅ 完整的 API 文档
- ✅ 多语言客户端示例
- ✅ 商业化部署方案

## 🚀 快速开始

### 1. 克隆并切换到 API 分支

```bash
# 克隆仓库
git clone https://github.com/let5sne/IOPaint.git
cd IOPaint

# 切换到 API 服务分支
git checkout feature/api-service

# 查看分支
git branch
# * feature/api-service
#   main
#   master
```

### 2. 启动服务

```bash
# 设置 API 密钥
export API_KEY="your_secret_key_here"

# 启动服务（GPU 版本）
docker-compose -f docker-compose.mvp.yml up -d

# 或者直接运行 Python（需要先安装依赖）
python3 api_service_mvp.py
```

### 3. 测试 API

```bash
# 健康检查
curl http://localhost:8080/api/v1/health

# 去水印
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: $API_KEY" \
  -F "image=@test.jpg" \
  -o result.png
```

### 4. 查看在线文档

访问 http://localhost:8080/docs（Swagger UI）

## 📚 文档导航

**新手必读**:
1. [📑 文档总览](./API_DOCS_INDEX.md) - 从这里开始
2. [🚀 快速开始](./API_SERVICE_README.md) - 10分钟上手

**开发者集成**:
1. [📖 REST API 完整文档](./RESTFUL_API_DOCUMENTATION.md)
2. [💻 多语言客户端示例](./API_CLIENT_EXAMPLES.md)
3. [🔧 OpenAPI 规范](./openapi.yaml)

**商业化部署**:
1. [🏗️ 完整部署方案](./API_SERVICE_GUIDE.md)
2. [💰 成本与收益分析](./API_SERVICE_GUIDE.md#成本与扩展性分析)

## 🔄 分支切换指南

### 切换到主分支（WebUI 版本）

```bash
# 切换到 main 分支
git checkout main

# 启动 WebUI 版本
python3 main.py start --model lama --device cuda --port 8080
```

### 切换回 API 分支

```bash
# 切换到 API 服务分支
git checkout feature/api-service

# 启动 API 服务
docker-compose -f docker-compose.mvp.yml up -d
```

### 保持两个版本同时运行

```bash
# 方法1：使用不同端口
# 主分支（WebUI）使用 8080
git checkout main
python3 main.py start --model lama --port 8080

# API 分支使用 8081
git checkout feature/api-service
docker-compose -f docker-compose.mvp.yml up -d
# 修改 docker-compose.mvp.yml 中的端口为 8081

# 方法2：使用不同目录
mkdir -p ~/iopaint-webui ~/iopaint-api
git clone https://github.com/let5sne/IOPaint.git ~/iopaint-webui
git clone https://github.com/let5sne/IOPaint.git ~/iopaint-api

cd ~/iopaint-webui && git checkout main
cd ~/iopaint-api && git checkout feature/api-service
```

## 🎯 使用场景

### 使用主分支（main）如果你需要：
- ✅ 本地使用图形界面
- ✅ 尝试不同的 AI 模型
- ✅ 使用插件（RemoveBG、RealESRGAN 等）
- ✅ 批处理本地图片
- ✅ 个人/团队内部工具

### 使用 API 分支（feature/api-service）如果你需要：
- ✅ 集成到自己的应用
- ✅ 提供在线服务
- ✅ 商业化部署
- ✅ 自动化处理
- ✅ 远程调用 API

## 📊 性能对比

| 项目 | 主分支 | API 分支 |
|------|--------|----------|
| **启动时间** | ~30秒 | ~10秒 |
| **内存占用** | ~3-4GB | ~2-3GB |
| **镜像大小** | ~8GB | ~6GB |
| **API 响应** | 需要 WebUI | 原生 REST API |
| **并发支持** | 有限 | 良好（可扩展）|
| **部署难度** | 简单 | 中等（但文档齐全）|

## 🔐 安全建议

### API 分支特有的安全考虑

1. **API Key 管理**
   ```bash
   # 生产环境必须修改默认密钥
   export API_KEY=$(openssl rand -hex 32)
   ```

2. **HTTPS 强制**
   ```bash
   # 使用 Nginx 配置 SSL
   # 参考 nginx/nginx.conf
   ```

3. **限流保护**
   ```nginx
   # Nginx 已配置限流
   # 每秒 10 个请求，突发 20 个
   ```

4. **日志监控**
   ```bash
   # 查看日志
   tail -f logs/api_*.log
   ```

## 🛠️ 维护指南

### 更新依赖

```bash
# 切换到 API 分支
git checkout feature/api-service

# 更新 Python 依赖
pip install -r requirements.txt --upgrade

# 重建 Docker 镜像
docker-compose -f docker-compose.mvp.yml build --no-cache
```

### 同步主分支的修复

```bash
# 如果主分支有重要修复，可以选择性合并
git checkout feature/api-service

# 只合并特定文件
git checkout main -- iopaint/model/
git checkout main -- iopaint/helper.py

# 提交
git commit -m "sync: 同步主分支的模型修复"
```

### 版本标签

```bash
# 创建版本标签
git tag -a api-v1.0.0 -m "API Service v1.0.0 - MVP Release"
git push origin api-v1.0.0

# 查看所有 API 版本
git tag -l "api-v*"
```

## 📈 发展路线图

### 当前版本（v1.0.0）
- ✅ 基础 REST API
- ✅ LaMa 模型支持
- ✅ API Key 认证
- ✅ 完整文档
- ✅ Docker 部署

### 计划中（v1.1.0）
- 🔜 批量处理 API
- 🔜 Webhook 回调
- 🔜 自动检测水印
- 🔜 使用 Dashboard

### 未来版本（v2.0.0）
- 🔮 多模型支持（SD、SDXL）
- 🔮 异步处理队列
- 🔮 对象存储集成
- 🔮 Kubernetes Helm Chart

## 🤝 贡献指南

### API 分支的贡献

如果你想为 API 服务分支做贡献：

```bash
# 1. Fork 仓库
# 2. 创建功能分支
git checkout -b feature/api-new-feature feature/api-service

# 3. 开发并测试
# 4. 提交 Pull Request 到 feature/api-service
```

### 文档改进

```bash
# 改进文档
git checkout -b docs/improve-api-docs feature/api-service

# 编辑文档
vim RESTFUL_API_DOCUMENTATION.md

# 提交
git commit -m "docs: 改进 API 认证说明"
git push origin docs/improve-api-docs
```

## 📞 获取帮助

### API 分支特定问题

- **GitHub Issues**: https://github.com/let5sne/IOPaint/issues
  - 标签：`api-service`, `documentation`, `deployment`

- **分支地址**: https://github.com/let5sne/IOPaint/tree/feature/api-service

### 常见问题

**Q: 为什么要独立分支？**
A: 主分支专注于 WebUI 体验，API 分支专注于服务化和商业化，两者目标不同。

**Q: API 分支会合并到主分支吗？**
A: 不会。两个分支将独立发展，但会同步重要的 bug 修复。

**Q: 如何选择使用哪个分支？**
A: 个人使用选主分支（WebUI），企业集成选 API 分支。

**Q: API 分支可以使用其他模型吗？**
A: 当前只支持 LaMa，未来版本会添加更多模型。

**Q: API 分支支持批量处理吗？**
A: v1.0 不支持，v1.1 计划添加批量 API。

## 📄 许可证

本项目（包括 API 服务分支）基于 Apache-2.0 许可证开源。

## 🎉 总结

### API 服务分支的优势

- ✅ **专注**：只做 API 服务，代码更精简
- ✅ **高效**：启动快，资源占用少
- ✅ **专业**：完整的商业化文档和部署方案
- ✅ **灵活**：易于集成到任何应用
- ✅ **可靠**：生产就绪，经过优化

### 立即开始

```bash
# 1. 克隆并切换分支
git clone https://github.com/let5sne/IOPaint.git
cd IOPaint
git checkout feature/api-service

# 2. 阅读文档
cat API_DOCS_INDEX.md

# 3. 启动服务
export API_KEY="your_secret_key"
docker-compose -f docker-compose.mvp.yml up -d

# 4. 访问文档
open http://localhost:8080/docs
```

---

**分支**: `feature/api-service`
**版本**: v1.0.0
**更新**: 2025-11-28
**维护者**: [@let5sne](https://github.com/let5sne)

**快速链接**:
- [📑 文档导航](./API_DOCS_INDEX.md)
- [🚀 快速开始](./API_SERVICE_README.md)
- [📖 完整 API 文档](./RESTFUL_API_DOCUMENTATION.md)
- [🏗️ 部署方案](./API_SERVICE_GUIDE.md)
