# 根因分析 API

## 概述

根因分析 API 用于深入挖掘指标变化的根本原因，通过多层次因果分析，找出导致指标异常或变化的深层次原因。根因分析不仅识别直接影响因素，还会追溯到更深层次的因果链，帮助用户理解问题的本质。

## API 端点

### 根因分析

**端点:** `/api/v1/root-cause`

**方法:** `POST`

**描述:** 分析指标变化的根本原因，构建因果关系网络，并识别关键影响路径。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `metric_name` | string | 是 | 需要分析的指标名称 | - | 长度: 1-100 |
| `metric_value` | number | 是 | 当前指标值 | - | - |
| `expected_value` | number | 否 | 预期指标值 | null | - |
| `threshold` | number | 否 | 异常判定阈值 | 0.1 | 取值范围: 0.01-0.5 |
| `time_period` | string | 否 | 时间周期 | "day" | 可选值: "minute", "hour", "day", "week", "month", "quarter", "year" |
| `timestamp` | string | 否 | 指标时间戳 | 当前时间 | ISO 8601 格式 |
| `dimension_filters` | object | 否 | 维度过滤器 | {} | 键值对格式 |
| `factors` | array | 是 | 可能影响指标的因素列表 | - | 数组长度: 1-50 |
| `factors[].name` | string | 是 | 因素名称 | - | 长度: 1-100 |
| `factors[].value` | any | 是 | 因素当前值 | - | - |
| `factors[].type` | string | 否 | 因素数据类型 | "numeric" | 可选值: "numeric", "categorical", "boolean", "event" |
| `factors[].sub_factors` | array | 否 | 影响此因素的子因素列表 | [] | 数组长度: 0-20 |
| `historical_data` | array | 否 | 历史数据点 | [] | 数组长度: 0-1000 |
| `max_depth` | integer | 否 | 最大分析深度 | 3 | 取值范围: 1-5 |
| `min_impact` | number | 否 | 最小影响阈值 | 0.05 | 取值范围: 0.01-0.2 |
| `analysis_method` | string | 否 | 分析方法 | "bayesian_network" | 可选值: "bayesian_network", "causal_inference", "correlation_analysis", "decision_tree", "neural_network" |
| `include_graph` | boolean | 否 | 是否包含因果图数据 | false | - |

**请求示例:**

```json
{
  "metric_name": "网站转化率",
  "metric_value": 2.3,
  "expected_value": 3.5,
  "threshold": 0.15,
  "time_period": "day",
  "timestamp": "2023-07-25T00:00:00Z",
  "dimension_filters": {
    "country": "中国",
    "device": "mobile"
  },
  "factors": [
    {
      "name": "页面加载时间",
      "value": 4.2,
      "type": "numeric",
      "sub_factors": [
        {
          "name": "服务器响应时间",
          "value": 1.8,
          "type": "numeric"
        },
        {
          "name": "资源加载时间",
          "value": 2.4,
          "type": "numeric"
        }
      ]
    },
    {
      "name": "用户会话数",
      "value": 15000,
      "type": "numeric",
      "sub_factors": [
        {
          "name": "广告活动点击次数",
          "value": 8500,
          "type": "numeric"
        },
        {
          "name": "自然搜索流量",
          "value": 4500,
          "type": "numeric"
        },
        {
          "name": "直接访问流量",
          "value": 2000,
          "type": "numeric"
        }
      ]
    },
    {
      "name": "结算页面错误",
      "value": true,
      "type": "boolean"
    },
    {
      "name": "促销活动",
      "value": "无促销",
      "type": "categorical",
      "sub_factors": [
        {
          "name": "上期促销力度",
          "value": "高",
          "type": "categorical"
        }
      ]
    }
  ],
  "max_depth": 4,
  "min_impact": 0.03,
  "analysis_method": "causal_inference",
  "include_graph": true
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
| `data.root_causes` | array | 识别出的根本原因列表，按影响程度排序 |
| `data.root_causes[].factor` | string | 因素名称 |
| `data.root_causes[].path` | array | 从根本原因到指标的因果路径 |
| `data.root_causes[].impact` | number | 对指标的总体影响程度 (0-1) |
| `data.root_causes[].confidence` | number | 分析结果的置信度 (0-1) |
| `data.root_causes[].evidence` | string | 支持该因果关系的证据描述 |
| `data.root_causes[].recommended_actions` | array | 推荐的改进措施 |
| `data.causal_graph` | object | 因果关系图数据（如果请求中 include_graph=true） |
| `data.impact_summary` | object | 各因素的直接和间接影响汇总 |
| `data.anomaly_score` | number | 指标异常程度评分 (0-1) |
| `data.analysis_summary` | string | 根因分析的文字总结 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "根因分析成功",
  "status_code": 200,
  "data": {
    "root_causes": [
      {
        "factor": "结算页面错误",
        "path": ["结算页面错误", "购物车完成率", "网站转化率"],
        "impact": 0.45,
        "confidence": 0.92,
        "evidence": "在过去的24小时内，结算页面出现了JavaScript错误，导致约60%的用户无法完成支付",
        "recommended_actions": [
          "修复结算页面的JavaScript错误",
          "优化结算流程的错误处理机制",
          "添加更明确的用户引导提示"
        ]
      },
      {
        "factor": "广告活动点击次数",
        "path": ["广告活动点击次数", "用户会话数", "潜在客户量", "网站转化率"],
        "impact": 0.28,
        "confidence": 0.85,
        "evidence": "与正常水平相比，当前广告活动的转化质量明显下降，流量增加但质量较低",
        "recommended_actions": [
          "优化广告系列的目标受众定位",
          "审查当前广告内容与落地页的一致性",
          "调整广告预算分配策略"
        ]
      },
      {
        "factor": "上期促销力度",
        "path": ["上期促销力度", "促销活动", "用户购买意愿", "网站转化率"],
        "impact": 0.18,
        "confidence": 0.78,
        "evidence": "上期高强度促销后，用户预期差异导致常规价格下的转化率降低",
        "recommended_actions": [
          "设计更平缓的促销节奏",
          "为高价值客户提供个性化优惠",
          "强调产品的非价格价值因素"
        ]
      }
    ],
    "causal_graph": {
      "nodes": [
        {"id": "网站转化率", "type": "metric", "anomaly": true},
        {"id": "购物车完成率", "type": "factor", "anomaly": true},
        {"id": "结算页面错误", "type": "root_cause", "anomaly": true},
        {"id": "用户会话数", "type": "factor", "anomaly": false},
        {"id": "广告活动点击次数", "type": "root_cause", "anomaly": true},
        {"id": "促销活动", "type": "factor", "anomaly": false},
        {"id": "上期促销力度", "type": "root_cause", "anomaly": false},
        {"id": "用户购买意愿", "type": "factor", "anomaly": true},
        {"id": "潜在客户量", "type": "factor", "anomaly": true}
      ],
      "edges": [
        {"source": "结算页面错误", "target": "购物车完成率", "weight": 0.8},
        {"source": "购物车完成率", "target": "网站转化率", "weight": 0.9},
        {"source": "广告活动点击次数", "target": "用户会话数", "weight": 0.7},
        {"source": "用户会话数", "target": "潜在客户量", "weight": 0.6},
        {"source": "潜在客户量", "target": "网站转化率", "weight": 0.5},
        {"source": "上期促销力度", "target": "促销活动", "weight": 0.4},
        {"source": "促销活动", "target": "用户购买意愿", "weight": 0.6},
        {"source": "用户购买意愿", "target": "网站转化率", "weight": 0.7}
      ]
    },
    "impact_summary": {
      "直接影响": {
        "购物车完成率": 0.42,
        "潜在客户量": 0.25,
        "用户购买意愿": 0.15
      },
      "间接影响": {
        "结算页面错误": 0.45,
        "广告活动点击次数": 0.28,
        "上期促销力度": 0.18
      }
    },
    "anomaly_score": 0.82,
    "analysis_summary": "网站转化率下降的主要根本原因是结算页面出现技术错误，导致大量用户无法完成购买流程。其次，当前广告活动带来的流量质量较低，以及上期高强度促销后的用户预期差异也对转化率造成了负面影响。建议优先修复结算页面错误，同时优化广告定位和促销策略。"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

### 异步根因分析

**端点:** `/api/v1/root-cause-async`

**方法:** `POST`

**描述:** 异步分析指标变化的根本原因。立即返回任务ID，可以通过任务ID查询分析结果。

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
  "message": "根因分析任务已创建",
  "status_code": 202,
  "data": {
    "task_id": "12345678-1234-5678-1234-567812345678",
    "status": "pending",
    "check_url": "/api/v1/tasks/12345678-1234-5678-1234-567812345678"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

## 分析方法说明

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| `bayesian_network` | 基于贝叶斯网络的因果推断 | 复杂系统的概率建模，适合有大量历史数据的场景 |
| `causal_inference` | 基于干预和反事实的因果推断 | 基于现有数据估计因果关系的强度和方向 |
| `correlation_analysis` | 基于相关性分析的简化因果推断 | 简单场景的快速分析，适合数据量有限的情况 |
| `decision_tree` | 基于决策树的根因分析 | 适合分类明确、规则性强的问题 |
| `neural_network` | 基于神经网络的复杂关系挖掘 | 适合非线性关系和高维数据的复杂场景 |

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 无权限访问 |
| 404 | 任务不存在 |
| 422 | 数据不足以进行根因分析 |
| 429 | 请求频率超过限制 |
| 500 | 服务器内部错误 |

## 使用示例

### Python

```python
import requests
import json

url = "https://api.data-insight.example.com/api/v1/root-cause"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}
data = {
    "metric_name": "网站转化率",
    "metric_value": 2.3,
    "expected_value": 3.5,
    "factors": [
        {
            "name": "页面加载时间",
            "value": 4.2,
            "sub_factors": [
                {
                    "name": "服务器响应时间",
                    "value": 1.8
                },
                {
                    "name": "资源加载时间",
                    "value": 2.4
                }
            ]
        },
        {
            "name": "结算页面错误",
            "value": True
        }
    ],
    "max_depth": 3
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    root_causes = result["data"]["root_causes"]
    for cause in root_causes:
        factor = cause["factor"]
        impact = cause["impact"]
        actions = cause["recommended_actions"]
        print(f"根本原因: {factor}, 影响程度: {impact}")
        print(f"推荐措施: {', '.join(actions)}")
else:
    print(f"分析失败: {result['message']}")
```

### JavaScript

```javascript
const url = "https://api.data-insight.example.com/api/v1/root-cause";
const headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
};
const data = {
    metric_name: "网站转化率",
    metric_value: 2.3,
    expected_value: 3.5,
    factors: [
        {
            name: "页面加载时间",
            value: 4.2,
            sub_factors: [
                {
                    name: "服务器响应时间",
                    value: 1.8
                },
                {
                    name: "资源加载时间",
                    value: 2.4
                }
            ]
        },
        {
            name: "结算页面错误",
            value: true
        }
    ],
    max_depth: 3
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        const rootCauses = result.data.root_causes;
        rootCauses.forEach(cause => {
            const factor = cause.factor;
            const impact = cause.impact;
            const actions = cause.recommended_actions;
            console.log(`根本原因: ${factor}, 影响程度: ${impact}`);
            console.log(`推荐措施: ${actions.join(', ')}`);
        });
    } else {
        console.error(`分析失败: ${result.message}`);
    }
})
.catch(error => {
    console.error("请求错误:", error);
});
``` 