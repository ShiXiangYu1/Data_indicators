# 归因分析 API

## 概述

归因分析 API 用于分析指标变化的归因因素，确定哪些因素对指标变化贡献最大，并量化每个因素的影响程度。API 支持多种归因分析方法，适用于不同的业务场景和数据类型。

## API 端点

### 归因分析

**端点:** `/api/v1/attribution`

**方法:** `POST`

**描述:** 分析指标变化的归因因素，计算各因素的贡献率和影响程度。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `metric_name` | string | 是 | 需要分析的指标名称 | - | 长度: 1-100 |
| `metric_value` | number | 是 | 当前指标值 | - | - |
| `previous_value` | number | 是 | 上一期指标值 | - | - |
| `time_period` | string | 否 | 时间周期 | "day" | 可选值: "minute", "hour", "day", "week", "month", "quarter", "year" |
| `factors` | array | 是 | 可能影响指标的因素列表 | - | 数组长度: 1-20 |
| `factors[].name` | string | 是 | 因素名称 | - | 长度: 1-100 |
| `factors[].current_value` | number/string | 是 | 因素当前值 | - | - |
| `factors[].previous_value` | number/string | 是 | 因素上一期值 | - | - |
| `factors[].type` | string | 否 | 因素数据类型 | "numeric" | 可选值: "numeric", "categorical", "boolean" |
| `factors[].weight` | number | 否 | 因素权重 | 1.0 | 取值范围: 0.1-10.0 |
| `data_points` | array | 否 | 历史数据点 | [] | 数组长度: 0-1000 |
| `data_points[].metric_value` | number | 是 | 历史指标值 | - | - |
| `data_points[].factors` | object | 是 | 各因素历史值 | - | - |
| `data_points[].timestamp` | string | 否 | 数据点时间戳 | - | ISO 8601 格式 |
| `attribution_method` | string | 否 | 归因方法 | "auto" | 可选值: "auto", "last_touch", "first_touch", "linear", "time_decay", "position_based", "shapley_value", "markov_chain" |
| `confidence_level` | number | 否 | 置信水平 | 0.95 | 取值范围: 0.8-0.99 |

**请求示例:**

```json
{
  "metric_name": "总转化率",
  "metric_value": 8.5,
  "previous_value": 7.2,
  "time_period": "week",
  "factors": [
    {
      "name": "网站访问量",
      "current_value": 15000,
      "previous_value": 12000,
      "type": "numeric"
    },
    {
      "name": "平均停留时间",
      "current_value": 120,
      "previous_value": 95,
      "type": "numeric",
      "weight": 1.5
    },
    {
      "name": "广告投放",
      "current_value": "高",
      "previous_value": "中",
      "type": "categorical"
    },
    {
      "name": "促销活动",
      "current_value": true,
      "previous_value": false,
      "type": "boolean",
      "weight": 2.0
    }
  ],
  "data_points": [
    {
      "metric_value": 6.8,
      "factors": {
        "网站访问量": 10000,
        "平均停留时间": 90,
        "广告投放": "中",
        "促销活动": false
      },
      "timestamp": "2023-07-01T00:00:00Z"
    },
    {
      "metric_value": 7.0,
      "factors": {
        "网站访问量": 11000,
        "平均停留时间": 92,
        "广告投放": "中",
        "促销活动": false
      },
      "timestamp": "2023-07-08T00:00:00Z"
    },
    {
      "metric_value": 7.2,
      "factors": {
        "网站访问量": 12000,
        "平均停留时间": 95,
        "广告投放": "中",
        "促销活动": false
      },
      "timestamp": "2023-07-15T00:00:00Z"
    }
  ],
  "attribution_method": "shapley_value",
  "confidence_level": 0.9
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
| `data.attributions` | array | 各因素的归因结果 |
| `data.attributions[].factor` | string | 因素名称 |
| `data.attributions[].contribution` | number | 贡献率（百分比） |
| `data.attributions[].impact` | number | 对指标的实际影响值 |
| `data.attributions[].significance` | number | 统计显著性 (p-value) |
| `data.attributions[].confidence_interval` | array | 95% 置信区间 [下限, 上限] |
| `data.model_accuracy` | number | 模型准确度 (0-1) |
| `data.unexplained_ratio` | number | 无法解释的变化比例 |
| `data.summary` | string | 归因分析总结 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "归因分析成功",
  "status_code": 200,
  "data": {
    "attributions": [
      {
        "factor": "促销活动",
        "contribution": 45.8,
        "impact": 0.59,
        "significance": 0.001,
        "confidence_interval": [0.42, 0.76]
      },
      {
        "factor": "网站访问量",
        "contribution": 30.2,
        "impact": 0.39,
        "significance": 0.008,
        "confidence_interval": [0.25, 0.53]
      },
      {
        "factor": "平均停留时间",
        "contribution": 15.5,
        "impact": 0.20,
        "significance": 0.032,
        "confidence_interval": [0.12, 0.28]
      },
      {
        "factor": "广告投放",
        "contribution": 5.1,
        "impact": 0.07,
        "significance": 0.124,
        "confidence_interval": [0.02, 0.12]
      }
    ],
    "model_accuracy": 0.87,
    "unexplained_ratio": 3.4,
    "summary": "促销活动是指标上升的主要贡献因素，占比45.8%。网站访问量和平均停留时间也有显著贡献。广告投放的影响较小且不具有统计显著性。"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

### 异步归因分析

**端点:** `/api/v1/attribution-async`

**方法:** `POST`

**描述:** 异步分析指标变化的归因因素。立即返回任务ID，可以通过任务ID查询分析结果。

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
  "message": "归因分析任务已创建",
  "status_code": 202,
  "data": {
    "task_id": "12345678-1234-5678-1234-567812345678",
    "status": "pending",
    "check_url": "/api/v1/tasks/12345678-1234-5678-1234-567812345678"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

## 归因方法说明

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| `last_touch` | 将全部影响归因于最后接触的因素 | 简单分析，直接转化场景 |
| `first_touch` | 将全部影响归因于首次接触的因素 | 品牌意识，初始互动分析 |
| `linear` | 平均分配影响给所有因素 | 简单多因素分析 |
| `time_decay` | 基于时间衰减的归因模型 | 考虑时间序列影响的场景 |
| `position_based` | 基于位置的归因模型 | 强调开始和结束因素的场景 |
| `shapley_value` | 基于合作博弈论的公平归因 | 复杂多因素交互分析 |
| `markov_chain` | 基于马尔可夫链的概率归因 | 用户路径分析，多步骤转化 |
| `auto` | 自动选择最适合的归因方法 | 一般用途，不确定最佳方法时 |

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 无权限访问 |
| 404 | 任务不存在 |
| 422 | 数据不足以进行归因分析 |
| 429 | 请求频率超过限制 |
| 500 | 服务器内部错误 |

## 使用示例

### Python

```python
import requests
import json

url = "https://api.data-insight.example.com/api/v1/attribution"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}
data = {
    "metric_name": "总转化率",
    "metric_value": 8.5,
    "previous_value": 7.2,
    "factors": [
        {
            "name": "网站访问量",
            "current_value": 15000,
            "previous_value": 12000
        },
        {
            "name": "促销活动",
            "current_value": True,
            "previous_value": False,
            "weight": 2.0
        }
    ],
    "attribution_method": "shapley_value"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    attributions = result["data"]["attributions"]
    for attribution in attributions:
        factor = attribution["factor"]
        contribution = attribution["contribution"]
        print(f"因素: {factor}, 贡献率: {contribution}%")
else:
    print(f"分析失败: {result['message']}")
```

### JavaScript

```javascript
const url = "https://api.data-insight.example.com/api/v1/attribution";
const headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
};
const data = {
    metric_name: "总转化率",
    metric_value: 8.5,
    previous_value: 7.2,
    factors: [
        {
            name: "网站访问量",
            current_value: 15000,
            previous_value: 12000
        },
        {
            name: "促销活动",
            current_value: true,
            previous_value: false,
            weight: 2.0
        }
    ],
    attribution_method: "shapley_value"
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        const attributions = result.data.attributions;
        attributions.forEach(attribution => {
            const factor = attribution.factor;
            const contribution = attribution.contribution;
            console.log(`因素: ${factor}, 贡献率: ${contribution}%`);
        });
    } else {
        console.error(`分析失败: ${result.message}`);
    }
})
.catch(error => {
    console.error("请求错误:", error);
});
``` 