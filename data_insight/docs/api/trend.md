# 趋势分析 API

## 概述

趋势分析 API 用于分析时间序列数据的变化趋势，识别上升、下降、周期性和季节性模式。API 支持多种分析方法，包括移动平均线、指数平滑、线性回归等。

## API 端点

### 趋势分析

**端点:** `/api/v1/trend/analyze`

**方法:** `POST`

**描述:** 分析时间序列数据的变化趋势，并返回趋势类型、斜率、波动性等信息。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `data_points` | array | 是 | 要分析的时间序列数据点 | - | 数组长度至少为10 |
| `time_period` | string | 否 | 数据点的时间周期 | "day" | 可选值: "minute", "hour", "day", "week", "month", "quarter", "year" |
| `method` | string | 否 | 分析方法 | "auto" | 可选值: "auto", "moving_average", "exponential_smoothing", "linear_regression", "polynomial_regression", "decomposition" |
| `window_size` | integer | 否 | 移动窗口大小 | 5 | 取值范围: 3 ~ 数据点长度的一半 |
| `sensitivity` | number | 否 | 趋势变化的灵敏度 | 0.05 | 取值范围: 0.01 ~ 0.2 |
| `include_details` | boolean | 否 | 是否包含详细的分析数据 | false | - |

**请求示例:**

```json
{
  "data_points": [102, 105, 108, 111, 117, 120, 123, 125, 128, 131, 135, 142, 146, 150, 153],
  "time_period": "day",
  "method": "linear_regression",
  "include_details": true
}
```

#### 响应参数

**成功响应 (200 OK):**

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 响应消息 |
| `status_code` | integer | HTTP 状态码 |
| `data` | object | 分析结果 |
| `data.trend_type` | string | 趋势类型，可能值: "increasing", "decreasing", "fluctuating", "stable", "cyclical", "seasonal" |
| `data.slope` | number | 趋势斜率（对于线性趋势） |
| `data.confidence` | number | 趋势判断的置信度 (0-1) |
| `data.volatility` | number | 数据波动性 |
| `data.breakpoints` | array | 趋势转折点 |
| `data.forecast` | array | 未来趋势预测（如有） |
| `data.details` | object | 详细分析数据（仅当 include_details=true 时） |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "趋势分析成功",
  "status_code": 200,
  "data": {
    "trend_type": "increasing",
    "slope": 3.45,
    "confidence": 0.92,
    "volatility": 0.08,
    "breakpoints": [5, 11],
    "forecast": [157, 161, 164, 168, 172],
    "details": {
      "regression_stats": {
        "r_squared": 0.97,
        "p_value": 0.0001,
        "std_error": 1.2
      },
      "processed_data": [102, 105, 108, 111, 117, 120, 123, 125, 128, 131, 135, 142, 146, 150, 153],
      "trend_line": [103.2, 106.7, 110.1, 113.6, 117.0, 120.5, 123.9, 127.4, 130.8, 134.3, 137.7, 141.2, 144.6, 148.1, 151.5]
    }
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

### 异步趋势分析

**端点:** `/api/v1/trend/analyze-async`

**方法:** `POST`

**描述:** 异步分析时间序列数据的变化趋势。立即返回任务ID，可以通过任务ID查询分析结果。

#### 请求参数

与同步分析端点相同。

#### 响应参数

**成功响应 (202 Accepted):**

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 响应消息 |
| `status_code` | integer | HTTP 状态码 |
| `data` | object | 任务信息 |
| `data.task_id` | string | 任务ID |
| `data.status` | string | 任务状态 |
| `data.check_url` | string | 查询任务结果的URL |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "趋势分析任务已创建",
  "status_code": 202,
  "data": {
    "task_id": "12345678-1234-5678-1234-567812345678",
    "status": "pending",
    "check_url": "/api/v1/tasks/12345678-1234-5678-1234-567812345678"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

### 获取趋势分析任务结果

**端点:** `/api/v1/tasks/{task_id}`

**方法:** `GET`

**描述:** 获取异步趋势分析任务的结果。

#### 路径参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `task_id` | string | 任务ID |

#### 响应参数

**任务进行中 (200 OK):**

```json
{
  "success": true,
  "message": "任务正在处理中",
  "status_code": 200,
  "data": {
    "task_id": "12345678-1234-5678-1234-567812345678",
    "status": "processing",
    "progress": 45,
    "estimated_completion": "2023-07-25T12:35:56.789Z"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

**任务完成 (200 OK):**

响应格式与同步分析接口相同，但包含额外的任务信息。

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 无权限访问 |
| 404 | 任务不存在 |
| 429 | 请求频率超过限制 |
| 500 | 服务器内部错误 |

## 使用示例

### Python

```python
import requests
import json

url = "https://api.data-insight.example.com/api/v1/trend/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}
data = {
    "data_points": [102, 105, 108, 111, 117, 120, 123, 125, 128, 131, 135, 142, 146, 150, 153],
    "time_period": "day",
    "method": "linear_regression",
    "include_details": True
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    trend_type = result["data"]["trend_type"]
    slope = result["data"]["slope"]
    confidence = result["data"]["confidence"]
    print(f"趋势类型: {trend_type}, 斜率: {slope}, 置信度: {confidence}")
else:
    print(f"分析失败: {result['message']}")
```

### JavaScript

```javascript
const url = "https://api.data-insight.example.com/api/v1/trend/analyze";
const headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
};
const data = {
    data_points: [102, 105, 108, 111, 117, 120, 123, 125, 128, 131, 135, 142, 146, 150, 153],
    time_period: "day",
    method: "linear_regression",
    include_details: true
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        const trendType = result.data.trend_type;
        const slope = result.data.slope;
        const confidence = result.data.confidence;
        console.log(`趋势类型: ${trendType}, 斜率: ${slope}, 置信度: ${confidence}`);
    } else {
        console.error(`分析失败: ${result.message}`);
    }
})
.catch(error => {
    console.error("请求错误:", error);
});
``` 