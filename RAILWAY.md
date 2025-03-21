# Railway部署指南 - 数据指标平台

## 部署前准备

本项目已配置好所有必要的Railway部署文件：

- `requirements.txt`: 包含所有项目依赖
- `Procfile`: 定义应用启动命令
- `runtime.txt`: 指定Python版本
- `railway.json`: Railway部署配置
- `railway.async.json`: 异步任务服务配置

## 部署步骤

### 1. 主应用部署

1. 登录Railway平台 (https://railway.app/)
2. 创建新项目，选择"Deploy from GitHub repo"
3. 选择本代码仓库
4. Railway将自动识别并使用我们的配置文件
5. 等待部署完成

### 2. 环境变量配置

在Railway控制台中，前往"Variables"选项卡，设置以下环境变量：

```
DATA_INSIGHT_HOST=0.0.0.0
DATA_INSIGHT_PORT=$PORT
DATA_INSIGHT_DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=<生成一个安全的密钥>
```

> 注意：Railway会自动提供$PORT环境变量，您的应用必须监听此端口。

### 3. 异步任务服务部署（可选）

如果需要部署异步任务服务：

1. 在同一项目中添加新服务（Add New）
2. 选择"Deploy from GitHub repo"
3. 选择同一仓库
4. 在"Settings"中，将"Root Directory"保持为空
5. 将"Start Command"设置为：`python -m data_insight.async_task_service`
6. 配置与主应用相同的环境变量，并添加：
   ```
   REDIS_URL=<您的Redis连接URL>
   TASK_QUEUE=data_insight_tasks
   ```

## 验证部署

部署完成后，您可以访问以下端点验证应用是否正常运行：

- `/api/health` - 应返回健康状态信息
- `/api/docs` - 应显示API文档

## 常见问题排查

- **应用无法启动**: 检查日志，确认环境变量是否正确设置
- **无法访问应用**: 确认应用正在监听$PORT环境变量
- **异步任务不工作**: 验证Redis连接是否正确

## 相关资源

- [Railway官方文档](https://docs.railway.app/)
- [Gunicorn配置文档](https://docs.gunicorn.org/en/stable/configure.html) 