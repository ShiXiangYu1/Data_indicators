# 数据指标分析API文档

## 简介

Data Insight API 是一个功能强大的数据指标分析服务，提供了多种高级分析功能，帮助用户深入理解数据指标的变化趋势、相关性和潜在原因。API采用RESTful设计风格，支持JSON格式的请求和响应，并提供了完善的认证、访问控制和速率限制机制。

## API基础信息

- **基础URL**: `https://api.data-insight.example.com` (或本地开发环境 `http://localhost:5000`)
- **API版本**: v1
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 认证与安全

所有API请求都需要进行认证。目前支持以下认证方式：

1. **令牌认证**: 在请求头中添加 `X-API-Token` 字段
2. **HMAC签名认证**: 使用 `X-API-Key` 和 `X-Signature` 请求头

详情请参阅[认证文档](./auth.md)。

## 请求速率限制

为了保障服务的稳定性，API实施了请求速率限制。限制策略包括：

- 基于IP的限制：默认每小时100次
- 基于令牌的限制：默认每小时1000次

详情请参阅[速率限制文档](./rate-limit.md)。

## 响应格式

所有API响应都使用统一的JSON格式：

```json
{
  "success": true,
  "message": "操作成功",
  "status_code": 200,
  "data": { ... },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

错误响应：

```json
{
  "success": false,
  "message": "错误消息",
  "status_code": 400,
  "error_type": "ValidationError",
  "error_detail": { ... },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

## API模块

API功能按模块组织，每个模块提供不同的分析功能：

- [健康检查API](./health.md) - 检查服务的健康状态
- [趋势分析API](./trend.md) - 分析时间序列数据的变化趋势
- [原因分析API](./reason.md) - 分析指标变化的可能原因
- [归因分析API](./attribution.md) - 分析指标变化的归因因素
- [根因分析API](./root-cause.md) - 分析指标变化的根本原因
- [相关性分析API](./correlation.md) - 分析指标之间的相关性
- [预测分析API](./prediction.md) - 预测指标的未来走势
- [指标分析API](./metric.md) - 分析单个指标和指标对比
- [图表分析API](./chart.md) - 分析图表数据

## 异步处理

对于某些可能需要较长处理时间的分析请求，API提供了异步处理模式。异步处理通过以下步骤实现：

1. 发送分析请求到对应的异步API端点（通常以`-async`结尾）
2. API立即返回一个任务ID
3. 使用任务ID查询任务状态和结果

详情请参阅[异步处理文档](./async.md)。

## 错误处理

API使用标准HTTP状态码表示请求的处理结果：

- 2xx: 请求成功
- 4xx: 客户端错误（如参数错误、认证失败）
- 5xx: 服务器错误

详情请参阅[错误处理文档](./errors.md)。

## SDK与代码示例

我们提供了多种语言的SDK和代码示例，帮助开发者快速集成API：

- [Python SDK](../sdk/python.md)
- [JavaScript SDK](../sdk/javascript.md)
- [代码示例](../examples/index.md)

## 变更日志

API的变更历史记录在[变更日志](./changelog.md)中。 