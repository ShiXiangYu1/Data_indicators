# 数据指标分析系统部署文档

## 目录

- [概述](#概述)
- [部署前准备](#部署前准备)
- [本地部署](#本地部署)
- [Docker部署](#Docker部署)
- [Kubernetes部署](#Kubernetes部署)
  - [基础环境部署](#基础环境部署)
  - [生产环境部署](#生产环境部署)
  - [监控与日志](#监控与日志)
- [环境配置](#环境配置)
- [扩展配置](#扩展配置)
- [安全配置](#安全配置)
- [性能调优](#性能调优)
- [常见问题](#常见问题)

## 概述

数据指标分析系统提供了多种部署方式，以满足不同的环境需求和规模要求。本文档详细介绍了系统的部署过程，包括本地部署、Docker部署和Kubernetes部署，以及相关的配置和优化建议。

## 部署前准备

在开始部署前，请确保满足以下要求：

### 基础要求

- Python 3.9+
- Redis (可选，用于缓存)
- MySQL/PostgreSQL (可选，用于数据存储)
- 至少2GB内存和4GB磁盘空间

### Docker部署额外要求

- Docker 20.10+
- Docker Compose 2.0+

### Kubernetes部署额外要求

- Kubernetes 1.19+
- kubectl 命令行工具
- Helm 3.0+ (可选，用于部署依赖服务)

### 网络要求

- 开放 8000 端口（API服务）
- 如使用Redis，开放 6379 端口
- 如使用数据库，开放相应数据库端口

## 本地部署

本地部署适合开发、测试或小规模使用场景。

### 1. 获取代码

```bash
git clone https://github.com/yourusername/data-insight.git
cd data-insight
```

### 2. 环境准备

创建并激活Python虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建`.env`文件：

```bash
cp .env.example .env
```

编辑`.env`文件，设置必要的配置参数：

```
# 基础配置
PORT=8000
WORKERS=4
LOG_LEVEL=info
ENVIRONMENT=development

# Redis配置 (可选)
REDIS_URL=redis://localhost:6379/0

# 安全配置
SECRET_KEY=your-secret-key  # 请更改为随机字符串
API_TOKEN=your-api-token    # 请更改为随机字符串
```

### 4. 启动服务

使用uvicorn启动服务：

```bash
uvicorn data_insight.app:app --host 0.0.0.0 --port 8000
```

或使用提供的启动脚本：

```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### 5. 验证部署

访问`http://localhost:8000/health`验证服务是否正常运行。您应该看到类似以下的响应：

```json
{
  "status": "ok",
  "api_service": "healthy",
  "cache_service": "healthy",
  "task_service": "healthy",
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

## Docker部署

Docker部署适合开发、测试和小型生产环境。

### 1. 获取代码

```bash
git clone https://github.com/yourusername/data-insight.git
cd data-insight
```

### 2. 配置环境变量

创建`.env`文件：

```bash
cp .env.example .env
```

编辑`.env`文件，设置必要的配置参数（与本地部署类似）。

### 3. 构建并启动容器

使用Docker Compose启动服务：

```bash
docker-compose up -d
```

这将启动API服务和Redis缓存服务。

### 4. 验证部署

访问`http://localhost:8000/health`验证服务是否正常运行。

### 5. 查看日志

```bash
docker-compose logs -f
```

### 6. 停止服务

```bash
docker-compose down
```

### 7. 更新部署

```bash
git pull
docker-compose build
docker-compose up -d
```

## Kubernetes部署

Kubernetes部署适合大型生产环境和高可用部署场景。

### 基础环境部署

#### 1. 准备Kubernetes配置

确保已正确配置`kubectl`并可以访问Kubernetes集群。

```bash
kubectl cluster-info
```

#### 2. 创建命名空间

```bash
kubectl create namespace data-insight
```

#### 3. 创建配置和密钥

创建ConfigMap：

```bash
kubectl apply -f kubernetes/configmap.yaml -n data-insight
```

创建Secret（请先修改示例文件，添加实际密钥）：

```bash
kubectl apply -f kubernetes/secret-example.yaml -n data-insight
```

#### 4. 部署Redis（如需）

```bash
kubectl apply -f kubernetes/redis.yaml -n data-insight
```

#### 5. 部署应用

使用Kustomize部署基础环境：

```bash
kubectl apply -k kubernetes/bases -n data-insight
```

### 生产环境部署

生产环境部署基于基础环境，添加了额外的配置和资源。

#### 1. 修改生产环境特定配置

编辑`kubernetes/overlays/production/kustomization.yaml`和相关补丁文件，设置生产环境特定的配置。

#### 2. 部署生产环境

```bash
kubectl apply -k kubernetes/overlays/production -n data-insight-production
```

#### 3. 配置Ingress

```bash
kubectl apply -f kubernetes/production/ingress.yaml -n data-insight-production
```

#### 4. 验证部署

```bash
kubectl get pods -n data-insight-production
kubectl get services -n data-insight-production
kubectl get ingress -n data-insight-production
```

### 监控与日志

#### 1. 部署Prometheus和Grafana（可选）

如果需要监控系统性能和健康状态，可以部署Prometheus和Grafana：

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

#### 2. 配置Prometheus抓取数据

在Prometheus配置中添加数据指标分析系统的抓取配置：

```yaml
scrape_configs:
  - job_name: 'data-insight'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - data-insight-production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

#### 3. 日志收集

使用Elasticsearch、Fluentd和Kibana（EFK）收集和查看日志：

```bash
helm repo add elastic https://helm.elastic.co
helm repo update
helm install elasticsearch elastic/elasticsearch -n logging
helm install kibana elastic/kibana -n logging
kubectl apply -f kubernetes/fluentd-config.yaml -n logging
```

## 环境配置

系统支持通过环境变量和配置文件进行配置，主要配置选项如下：

### 基础配置

| 环境变量 | 描述 | 默认值 | 示例 |
|---------|------|-------|------|
| PORT | 服务监听端口 | 8000 | 8000 |
| WORKERS | 工作进程数 | 4 | 4 |
| LOG_LEVEL | 日志级别 | info | info, debug, warning, error |
| ENVIRONMENT | 运行环境 | production | development, testing, production |

### 缓存配置

| 环境变量 | 描述 | 默认值 | 示例 |
|---------|------|-------|------|
| REDIS_URL | Redis连接URL | - | redis://localhost:6379/0 |
| CACHE_TTL | 缓存过期时间(秒) | 3600 | 3600 |
| CACHE_BACKEND | 缓存后端类型 | memory | memory, redis, file |
| FILE_CACHE_DIR | 文件缓存目录 | tmp/cache | /data/cache |

### 安全配置

| 环境变量 | 描述 | 默认值 | 示例 |
|---------|------|-------|------|
| SECRET_KEY | 系统密钥 | - | random-string |
| API_TOKEN | API认证令牌 | - | random-string |
| RATE_LIMIT | API请求限制 | 100 | 100 |
| ALLOWED_ORIGINS | 允许的跨域来源 | * | http://example.com,https://example.com |

### 性能配置

| 环境变量 | 描述 | 默认值 | 示例 |
|---------|------|-------|------|
| MAX_WORKERS | 并行处理最大工作线程 | 4 | 8 |
| TASK_TIMEOUT | 任务超时时间(秒) | 300 | 600 |
| MAX_REQUESTS | 进程最大请求数 | 1000 | 1000 |
| MAX_REQUESTS_JITTER | 请求数随机抖动 | 50 | 50 |

## 扩展配置

### 水平扩展

在Kubernetes环境中，可以通过HorizontalPodAutoscaler自动扩展服务实例数：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: data-insight-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-insight
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 第三方服务集成

如需集成第三方服务（如数据库、对象存储等），可通过环境变量进行配置：

```
# 数据库配置
DB_CONNECTION_STRING=postgresql://username:password@host:port/dbname

# 对象存储配置
STORAGE_TYPE=s3
S3_ENDPOINT=s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=your-bucket-name
```

## 安全配置

### TLS配置

在生产环境中，建议启用TLS加密。可以通过Ingress Controller或负载均衡器配置TLS终结。

Ingress示例：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: data-insight-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.data-insight.example.com
    secretName: data-insight-tls
  rules:
  - host: api.data-insight.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: data-insight
            port:
              number: 80
```

### API访问控制

系统支持多种API访问控制机制：

1. **API令牌认证**：通过环境变量`API_TOKEN`设置

2. **IP白名单**：通过环境变量`ALLOWED_IPS`设置允许的IP地址列表

3. **JWT认证**：配置JWT密钥和验证参数

### 敏感信息保护

所有敏感信息（如密钥、密码）应存储在Kubernetes Secrets中，而不是ConfigMap中。

创建Secret示例：

```bash
kubectl create secret generic data-insight-secrets \
  --from-literal=api-key=your-api-key \
  --from-literal=secret-key=your-secret-key \
  --from-literal=redis-password=your-redis-password
```

## 性能调优

### 资源分配

根据系统负载和规模调整资源分配：

```yaml
resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    cpu: "1000m"
    memory: "1Gi"
```

### 缓存优化

1. **启用Redis缓存**：对于高负载环境，建议使用Redis缓存替代内存缓存
2. **调整缓存TTL**：根据数据更新频率调整缓存过期时间
3. **优化缓存键**：使用特定前缀和命名空间隔离不同类型的缓存数据

### 异步任务处理

对于长时间运行的分析任务，建议使用异步处理：

1. 调整任务队列大小：`TASK_QUEUE_SIZE=100`
2. 设置合理的任务超时时间：`TASK_TIMEOUT=600`
3. 配置任务重试策略：`TASK_RETRY_COUNT=3`

## 常见问题

### 1. 服务无法启动

**问题**：部署后服务无法正常启动

**排查步骤**：
1. 检查日志文件中的错误信息
2. 验证环境变量是否正确设置
3. 确认数据库和Redis连接是否正常
4. 检查服务依赖是否已启动

**解决方案**：
- 修正配置错误
- 确保依赖服务可访问
- 检查磁盘空间和权限

### 2. API响应缓慢

**问题**：系统API响应时间过长

**排查步骤**：
1. 检查服务器负载情况
2. 监控数据库和缓存性能
3. 分析请求日志，识别慢查询
4. 检查网络延迟

**解决方案**：
- 增加服务实例数量
- 优化数据库查询
- 调整缓存策略
- 考虑使用CDN或边缘缓存

### 3. 内存使用过高

**问题**：服务内存占用不断增长

**排查步骤**：
1. 使用内存分析工具识别内存泄漏
2. 检查大型请求处理是否释放内存
3. 监控缓存大小增长情况

**解决方案**：
- 优化内存使用，增加垃圾回收频率
- 设置内存缓存大小限制
- 使用数据分块处理大型请求

### 4. Kubernetes Pod重启

**问题**：Kubernetes环境中Pod频繁重启

**排查步骤**：
1. 检查Pod日志和事件
2. 验证资源请求和限制设置
3. 检查就绪探针和存活探针配置

**解决方案**：
- 调整资源配置，确保足够的CPU和内存
- 优化探针设置，避免误判
- 检查容器启动命令和参数

### 5. Redis连接失败

**问题**：无法连接到Redis服务

**排查步骤**：
1. 验证Redis服务是否运行
2. 检查网络连接和防火墙设置
3. 确认连接字符串格式是否正确
4. 检查认证信息是否正确

**解决方案**：
- 确保Redis服务正常运行
- 检查网络策略配置
- 更新连接配置
- 验证密码是否正确 