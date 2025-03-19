# 指标分析 API

## 概述

指标分析 API 用于分析单个指标的特性和变化情况，以及比较多个指标之间的差异和关系。API 支持指标健康度评分、同比环比分析、阈值判断和多维度分解等功能，帮助用户全面理解指标的状态和价值。

## API 端点

### 指标分析

**端点:** `/api/v1/analyze`

**方法:** `POST`

**描述:** 分析单个指标的特性、变化和健康度。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `name` | string | 是 | 指标名称 | - | 长度: 1-100 |
| `value` | number | 是 | 当前指标值 | - | - |
| `previous_value` | number | 是 | 上期指标值 | - | - |
| `unit` | string | 否 | 指标单位 | "" | - |
| `time_period` | string | 否 | 时间周期 | "day" | 可选值: "minute", "hour", "day", "week", "month", "quarter", "year" |
| `timestamp` | string | 否 | 指标时间戳 | 当前时间 | ISO 8601 格式 |
| `historical_values` | array | 否 | 历史指标值数组 | [] | 数组长度: 0-1000 |
| `historical_times` | array | 否 | 历史时间点数组 | [] | 长度应与historical_values相同 |
| `target_value` | number | 否 | 目标指标值 | null | - |
| `threshold` | object | 否 | 指标阈值设置 | {} | - |
| `threshold.warning` | number | 否 | 警告阈值 | null | - |
| `threshold.error` | number | 否 | 错误阈值 | null | - |
| `threshold.direction` | string | 否 | 阈值判断方向 | "below" | 可选值: "below", "above" |
| `dimensions` | object | 否 | 多维度数据 | {} | - |
| `evaluation_criteria` | array | 否 | 评估标准 | [] | - |
| `include_forecast` | boolean | 否 | 是否包含预测数据 | false | - |
| `include_decomposition` | boolean | 否 | 是否包含时间序列分解 | false | - |

**请求示例:**

```json
{
  "name": "网站转化率",
  "value": 3.8,
  "previous_value": 3.5,
  "unit": "%",
  "time_period": "month",
  "timestamp": "2023-07-31T23:59:59Z",
  "historical_values": [2.8, 2.9, 3.0, 3.2, 3.3, 3.5, 3.8],
  "historical_times": ["2023-01-31", "2023-02-28", "2023-03-31", "2023-04-30", "2023-05-31", "2023-06-30", "2023-07-31"],
  "target_value": 4.0,
  "threshold": {
    "warning": 2.5,
    "error": 2.0,
    "direction": "below"
  },
  "dimensions": {
    "by_device": {
      "desktop": 4.2,
      "mobile": 3.1,
      "tablet": 3.9
    },
    "by_country": {
      "US": 4.5,
      "UK": 3.9,
      "Germany": 3.7,
      "France": 3.3,
      "Japan": 2.8
    }
  },
  "evaluation_criteria": [
    {"name": "同比增长", "weight": 0.4},
    {"name": "环比增长", "weight": 0.3},
    {"name": "接近目标值", "weight": 0.3}
  ],
  "include_forecast": true,
  "include_decomposition": true
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
| `data.metric_info` | object | 指标基本信息 |
| `data.change_analysis` | object | 变化分析结果 |
| `data.change_analysis.absolute_change` | number | 绝对变化值 |
| `data.change_analysis.percentage_change` | number | 百分比变化 |
| `data.change_analysis.acceleration` | number | 变化加速度（相比上期变化） |
| `data.trend_analysis` | object | 趋势分析结果 |
| `data.trend_analysis.trend_type` | string | 趋势类型 |
| `data.trend_analysis.trend_strength` | number | 趋势强度 |
| `data.trend_analysis.seasonality` | object | 季节性信息（如有） |
| `data.comparative_analysis` | object | 比较分析结果 |
| `data.comparative_analysis.vs_target` | object | 与目标值的比较 |
| `data.comparative_analysis.vs_threshold` | object | 与阈值的比较 |
| `data.comparative_analysis.yoy_change` | object | 同比变化（如有历史数据） |
| `data.comparative_analysis.mom_change` | object | 环比变化 |
| `data.dimension_analysis` | object | 维度分析结果（如有） |
| `data.health_score` | object | 指标健康度评分 |
| `data.health_score.overall_score` | number | 总体健康度评分 (0-100) |
| `data.health_score.components` | array | 评分组成部分 |
| `data.forecast` | object | 预测结果（如请求） |
| `data.decomposition` | object | 时间序列分解（如请求） |
| `data.insights` | array | 关键洞察列表 |
| `data.recommendations` | array | 推荐操作列表 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "指标分析成功",
  "status_code": 200,
  "data": {
    "metric_info": {
      "name": "网站转化率",
      "value": 3.8,
      "previous_value": 3.5,
      "unit": "%",
      "time_period": "month",
      "timestamp": "2023-07-31T23:59:59Z"
    },
    "change_analysis": {
      "absolute_change": 0.3,
      "percentage_change": 8.57,
      "acceleration": 2.5,
      "change_description": "显著上升",
      "z_score": 1.8
    },
    "trend_analysis": {
      "trend_type": "increasing",
      "trend_strength": 0.92,
      "slope": 0.15,
      "r_squared": 0.94,
      "seasonality": {
        "detected": false,
        "period": null,
        "strength": null
      },
      "anomaly_detected": false
    },
    "comparative_analysis": {
      "vs_target": {
        "difference": -0.2,
        "percentage_difference": -5.0,
        "status": "approaching",
        "estimated_achievement_date": "2023-09-30"
      },
      "vs_threshold": {
        "warning": {
          "difference": 1.3,
          "status": "above"
        },
        "error": {
          "difference": 1.8,
          "status": "above"
        },
        "overall_status": "healthy"
      },
      "yoy_change": {
        "value": 0.8,
        "percentage": 26.67,
        "description": "强劲增长"
      },
      "mom_change": {
        "value": 0.3,
        "percentage": 8.57,
        "description": "稳健增长"
      }
    },
    "dimension_analysis": {
      "by_device": {
        "highest": {
          "key": "desktop",
          "value": 4.2
        },
        "lowest": {
          "key": "mobile",
          "value": 3.1
        },
        "variance": 0.31,
        "range": 1.1,
        "distribution": [
          {"key": "desktop", "value": 4.2, "percentage": 37.5},
          {"key": "tablet", "value": 3.9, "percentage": 34.8},
          {"key": "mobile", "value": 3.1, "percentage": 27.7}
        ]
      },
      "by_country": {
        "highest": {
          "key": "US",
          "value": 4.5
        },
        "lowest": {
          "key": "Japan",
          "value": 2.8
        },
        "variance": 0.45,
        "range": 1.7,
        "distribution": [
          {"key": "US", "value": 4.5, "percentage": 24.6},
          {"key": "UK", "value": 3.9, "percentage": 21.3},
          {"key": "Germany", "value": 3.7, "percentage": 20.2},
          {"key": "France", "value": 3.3, "percentage": 18.0},
          {"key": "Japan", "value": 2.8, "percentage": 15.3}
        ]
      }
    },
    "health_score": {
      "overall_score": 82,
      "components": [
        {"name": "同比增长", "score": 90, "weight": 0.4},
        {"name": "环比增长", "score": 75, "weight": 0.3},
        {"name": "接近目标值", "score": 80, "weight": 0.3}
      ],
      "interpretation": "健康",
      "historical_scores": [68, 70, 72, 75, 78, 80, 82]
    },
    "forecast": {
      "next_periods": [3.95, 4.1, 4.25],
      "confidence_intervals": [
        [3.8, 4.1],
        [3.9, 4.3],
        [4.0, 4.5]
      ],
      "trend_forecast": "continued_growth",
      "estimated_target_achievement": "2023-09-30"
    },
    "decomposition": {
      "trend": [2.75, 2.87, 3.00, 3.17, 3.33, 3.50, 3.80],
      "seasonal": [0.05, -0.01, 0.02, 0.03, -0.04, 0.01, 0.00],
      "residual": [0.00, 0.04, -0.02, 0.00, 0.01, -0.01, 0.00]
    },
    "insights": [
      "转化率持续稳定增长，6个月内增加了35.7%",
      "桌面端转化率显著高于移动端，可能存在移动体验优化空间",
      "当前增长速度下，预计将在2个月内达到目标值4.0%",
      "美国市场表现最佳，而日本市场表现相对较弱"
    ],
    "recommendations": [
      "优化移动端用户体验，缩小与桌面端的转化率差距",
      "分析日本市场低转化率原因，考虑本地化策略调整",
      "保持当前增长策略，重点关注能够加速达成目标的举措",
      "考虑设置更高的长期目标值，以保持增长动力"
    ]
  },
  "timestamp": "2023-08-01T12:34:56.789Z"
}
```

### 异步指标分析

**端点:** `/api/v1/analyze-async`

**方法:** `POST`

**描述:** 异步分析指标。立即返回任务ID，可以通过任务ID查询分析结果。

#### 请求参数

与同步分析端点相同。

#### 响应参数

与其他异步接口相同，返回任务ID和状态信息。

### 指标比较

**端点:** `/api/v1/compare`

**方法:** `POST`

**描述:** 比较多个指标之间的关系和差异。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `metrics` | array | 是 | 要比较的指标数组 | - | 数组长度: 2-10 |
| `metrics[].name` | string | 是 | 指标名称 | - | 长度: 1-100 |
| `metrics[].value` | number | 是 | 当前指标值 | - | - |
| `metrics[].previous_value` | number | 是 | 上期指标值 | - | - |
| `metrics[].unit` | string | 否 | 指标单位 | "" | - |
| `metrics[].weight` | number | 否 | 指标权重 | 1.0 | 取值范围: 0.1-10.0 |
| `comparison_type` | string | 否 | 比较类型 | "comprehensive" | 可选值: "comprehensive", "value", "change", "growth", "volatility", "impact" |
| `normalization` | boolean | 否 | 是否归一化比较 | true | - |
| `time_period` | string | 否 | 比较的时间周期 | "current" | 可选值: "current", "mom", "yoy", "custom" |
| `custom_period` | object | 否 | 自定义比较周期 | {} | 仅当time_period="custom"时有效 |
| `include_correlation` | boolean | 否 | 是否包含相关性分析 | false | - |
| `include_historical_comparison` | boolean | 否 | 是否包含历史比较 | false | - |
| `historical_values` | object | 否 | 各指标的历史值 | {} | 仅当include_historical_comparison=true时有效 |

**请求示例:**

```json
{
  "metrics": [
    {
      "name": "网站转化率",
      "value": 3.8,
      "previous_value": 3.5,
      "unit": "%",
      "weight": 1.5
    },
    {
      "name": "平均订单金额",
      "value": 85.2,
      "previous_value": 80.5,
      "unit": "美元",
      "weight": 1.2
    },
    {
      "name": "客户获取成本",
      "value": 22.5,
      "previous_value": 25.0,
      "unit": "美元",
      "weight": 1.0
    },
    {
      "name": "用户活跃度",
      "value": 42,
      "previous_value": 38,
      "unit": "%",
      "weight": 0.8
    }
  ],
  "comparison_type": "comprehensive",
  "normalization": true,
  "time_period": "mom",
  "include_correlation": true,
  "include_historical_comparison": true,
  "historical_values": {
    "网站转化率": [2.8, 3.0, 3.2, 3.4, 3.5, 3.8],
    "平均订单金额": [70.5, 73.2, 75.8, 78.4, 80.5, 85.2],
    "客户获取成本": [28.0, 27.2, 26.5, 25.8, 25.0, 22.5],
    "用户活跃度": [30, 32, 34, 36, 38, 42]
  }
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
| `data.comparison_results` | array | 比较结果数组 |
| `data.comparison_results[].metric` | string | 指标名称 |
| `data.comparison_results[].rank` | integer | 指标排名 |
| `data.comparison_results[].score` | number | 比较得分 (0-100) |
| `data.comparison_results[].change` | object | 变化情况 |
| `data.comparison_results[].performance` | string | 表现评估 |
| `data.comparison_summary` | object | 比较结果摘要 |
| `data.comparison_summary.best_performing` | object | 表现最佳的指标 |
| `data.comparison_summary.worst_performing` | object | 表现最差的指标 |
| `data.comparison_summary.highest_improvement` | object | 改善最多的指标 |
| `data.comparison_summary.highest_deterioration` | object | 恶化最严重的指标 |
| `data.correlation_analysis` | object | 相关性分析结果（如请求） |
| `data.historical_comparison` | object | 历史比较结果（如请求） |
| `data.visualization_data` | object | 可视化数据 |
| `data.insights` | array | 关键洞察列表 |
| `data.recommendations` | array | 推荐操作列表 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "指标比较成功",
  "status_code": 200,
  "data": {
    "comparison_results": [
      {
        "metric": "客户获取成本",
        "rank": 1,
        "score": 92,
        "change": {
          "absolute": -2.5,
          "percentage": -10.0,
          "direction": "decrease",
          "is_positive": true
        },
        "performance": "excellent"
      },
      {
        "metric": "用户活跃度",
        "rank": 2,
        "score": 85,
        "change": {
          "absolute": 4.0,
          "percentage": 10.5,
          "direction": "increase",
          "is_positive": true
        },
        "performance": "excellent"
      },
      {
        "metric": "网站转化率",
        "rank": 3,
        "score": 78,
        "change": {
          "absolute": 0.3,
          "percentage": 8.6,
          "direction": "increase",
          "is_positive": true
        },
        "performance": "good"
      },
      {
        "metric": "平均订单金额",
        "rank": 4,
        "score": 75,
        "change": {
          "absolute": 4.7,
          "percentage": 5.8,
          "direction": "increase",
          "is_positive": true
        },
        "performance": "good"
      }
    ],
    "comparison_summary": {
      "best_performing": {
        "metric": "客户获取成本",
        "score": 92,
        "reason": "显著下降10%，表明营销效率提高"
      },
      "worst_performing": {
        "metric": "平均订单金额",
        "score": 75,
        "reason": "虽有增长，但相对其他指标增幅较小"
      },
      "highest_improvement": {
        "metric": "客户获取成本",
        "change_percentage": -10.0,
        "compared_to_previous": "加速改善（前期为-3.1%）"
      },
      "highest_deterioration": null,
      "overall_health": "优秀",
      "weighted_average_score": 83.5
    },
    "correlation_analysis": {
      "matrix": [
        [1.00, 0.85, -0.92, 0.78],
        [0.85, 1.00, -0.76, 0.64],
        [-0.92, -0.76, 1.00, -0.70],
        [0.78, 0.64, -0.70, 1.00]
      ],
      "significant_pairs": [
        {
          "metrics": ["网站转化率", "客户获取成本"],
          "coefficient": -0.92,
          "relationship": "强负相关",
          "insight": "转化率提高时，客户获取成本显著降低"
        },
        {
          "metrics": ["网站转化率", "平均订单金额"],
          "coefficient": 0.85,
          "relationship": "强正相关",
          "insight": "转化率与订单金额同步增长，表明高质量流量增加"
        }
      ]
    },
    "historical_comparison": {
      "trends": {
        "网站转化率": {
          "overall_change": 35.7,
          "trend_type": "consistently_increasing",
          "acceleration": "stable"
        },
        "平均订单金额": {
          "overall_change": 20.9,
          "trend_type": "consistently_increasing",
          "acceleration": "increasing"
        },
        "客户获取成本": {
          "overall_change": -19.6,
          "trend_type": "consistently_decreasing",
          "acceleration": "increasing"
        },
        "用户活跃度": {
          "overall_change": 40.0,
          "trend_type": "consistently_increasing",
          "acceleration": "increasing"
        }
      },
      "relative_performance": {
        "best_consistent_performer": "用户活跃度",
        "most_improved": "用户活跃度",
        "most_volatile": "平均订单金额"
      }
    },
    "visualization_data": {
      "radar_chart": {
        "categories": ["网站转化率", "平均订单金额", "客户获取成本", "用户活跃度"],
        "current_period": [0.86, 0.75, 0.92, 0.85],
        "previous_period": [0.79, 0.71, 0.82, 0.77]
      },
      "trend_chart": {
        "categories": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "series": [
          {
            "name": "网站转化率 (归一化)",
            "data": [0.5, 0.57, 0.64, 0.71, 0.79, 0.86]
          },
          {
            "name": "平均订单金额 (归一化)",
            "data": [0.45, 0.52, 0.58, 0.65, 0.71, 0.75]
          },
          {
            "name": "客户获取成本 (归一化)",
            "data": [0.55, 0.62, 0.69, 0.75, 0.82, 0.92]
          },
          {
            "name": "用户活跃度 (归一化)",
            "data": [0.5, 0.56, 0.62, 0.69, 0.77, 0.85]
          }
        ]
      }
    },
    "insights": [
      "所有关键指标均呈现积极变化，整体业务健康度处于优秀水平",
      "客户获取成本持续下降，同时转化率上升，表明营销效率显著提高",
      "转化率与平均订单金额的强相关性表明用户质量提升",
      "用户活跃度增长最为稳定且加速度最高，预示良好的用户粘性"
    ],
    "recommendations": [
      "进一步优化营销渠道组合，继续降低客户获取成本",
      "针对平均订单金额设计提升策略，如交叉销售和向上销售",
      "分析用户活跃度提升因素，将成功经验应用到其他领域",
      "建立综合指标仪表板，持续监控这些关键指标的相互关系"
    ]
  },
  "timestamp": "2023-08-01T12:34:56.789Z"
}
```

### 异步指标比较

**端点:** `/api/v1/compare-async`

**方法:** `POST`

**描述:** 异步比较多个指标。立即返回任务ID，可以通过任务ID查询分析结果。

#### 请求参数

与同步指标比较端点相同。

#### 响应参数

与其他异步接口相同，返回任务ID和状态信息。

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 无权限访问 |
| 404 | 任务不存在 |
| 422 | 数据不足以进行指标分析 |
| 429 | 请求频率超过限制 |
| 500 | 服务器内部错误 |

## 使用示例

### Python

```python
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 准备数据
url = "https://api.data-insight.example.com/api/v1/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}
data = {
    "name": "网站转化率",
    "value": 3.8,
    "previous_value": 3.5,
    "unit": "%",
    "time_period": "month",
    "historical_values": [2.8, 3.0, 3.2, 3.5, 3.8],
    "historical_times": ["2023-03-31", "2023-04-30", "2023-05-31", "2023-06-30", "2023-07-31"],
    "target_value": 4.0,
    "threshold": {
        "warning": 2.5,
        "error": 2.0,
        "direction": "below"
    }
}

# 发送请求
response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    # 提取分析结果
    metric_info = result["data"]["metric_info"]
    change_analysis = result["data"]["change_analysis"]
    trend_analysis = result["data"]["trend_analysis"]
    health_score = result["data"]["health_score"]
    insights = result["data"]["insights"]
    
    # 打印基本信息
    print(f"指标: {metric_info['name']} ({metric_info['unit']})")
    print(f"当前值: {metric_info['value']}")
    print(f"变化: {change_analysis['absolute_change']} ({change_analysis['percentage_change']}%)")
    print(f"健康度评分: {health_score['overall_score']}/100 ({health_score['interpretation']})")
    
    # 绘制历史趋势图
    hist_values = data["historical_values"]
    hist_times = data["historical_times"]
    
    plt.figure(figsize=(10, 6))
    plt.plot(hist_times, hist_values, 'b-o', linewidth=2)
    
    # 添加目标线和阈值线
    plt.axhline(y=data["target_value"], color='g', linestyle='--', label=f"目标值 ({data['target_value']}%)")
    plt.axhline(y=data["threshold"]["warning"], color='y', linestyle='--', label=f"警告阈值 ({data['threshold']['warning']}%)")
    plt.axhline(y=data["threshold"]["error"], color='r', linestyle='--', label=f"错误阈值 ({data['threshold']['error']}%)")
    
    # 添加标签和图例
    plt.xlabel('时间')
    plt.ylabel(f"{metric_info['name']} ({metric_info['unit']})")
    plt.title(f"{metric_info['name']}趋势分析")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    # 健康度评分组件
    if "components" in health_score:
        components = health_score["components"]
        labels = [comp["name"] for comp in components]
        scores = [comp["score"] for comp in components]
        weights = [comp["weight"] for comp in components]
        
        plt.figure(figsize=(8, 6))
        bars = plt.bar(labels, scores, color=['#3498db', '#2ecc71', '#f39c12'])
        
        # 添加分数标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # 添加标签和图例
        plt.xlabel('评分组件')
        plt.ylabel('分数')
        plt.title('健康度评分组成')
        plt.ylim(0, 100)
        plt.tight_layout()
    
    # 打印关键洞察
    print("\n关键洞察:")
    for insight in insights:
        print(f"- {insight}")
    
    # 显示图表
    plt.show()
else:
    print(f"分析失败: {result['message']}")
```

### JavaScript

```javascript
// 使用Chart.js绘制指标比较雷达图
const url = "https://api.data-insight.example.com/api/v1/compare";
const headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
};

// 准备示例数据
const data = {
    metrics: [
        {
            name: "网站转化率",
            value: 3.8,
            previous_value: 3.5,
            unit: "%",
            weight: 1.5
        },
        {
            name: "平均订单金额",
            value: 85.2,
            previous_value: 80.5,
            unit: "美元",
            weight: 1.2
        },
        {
            name: "客户获取成本",
            value: 22.5,
            previous_value: 25.0,
            unit: "美元",
            weight: 1.0
        },
        {
            name: "用户活跃度",
            value: 42,
            previous_value: 38,
            unit: "%",
            weight: 0.8
        }
    ],
    comparison_type: "comprehensive",
    normalization: true,
    include_correlation: true
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        // 提取比较结果数据
        const comparisonResults = result.data.comparison_results;
        const radarData = result.data.visualization_data.radar_chart;
        
        // 使用Chart.js绘制雷达图
        const ctx = document.getElementById('radarChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: radarData.categories,
                datasets: [
                    {
                        label: '当前周期',
                        data: radarData.current_period,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: 'rgb(54, 162, 235)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(54, 162, 235)'
                    },
                    {
                        label: '上一周期',
                        data: radarData.previous_period,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgb(255, 99, 132)',
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(255, 99, 132)'
                    }
                ]
            },
            options: {
                elements: {
                    line: {
                        tension: 0,
                        borderWidth: 3
                    }
                },
                scale: {
                    ticks: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
        
        // 创建结果表格
        const tableBody = document.getElementById('resultsTable').getElementsByTagName('tbody')[0];
        comparisonResults.forEach(result => {
            const row = tableBody.insertRow();
            
            const metricCell = row.insertCell(0);
            metricCell.textContent = result.metric;
            
            const rankCell = row.insertCell(1);
            rankCell.textContent = result.rank;
            
            const scoreCell = row.insertCell(2);
            scoreCell.textContent = result.score;
            
            const changeCell = row.insertCell(3);
            const changeValue = result.change.percentage.toFixed(2);
            const direction = result.change.direction === 'increase' ? '↑' : '↓';
            const color = result.change.is_positive ? 'green' : 'red';
            changeCell.innerHTML = `<span style="color:${color}">${changeValue}% ${direction}</span>`;
            
            const performanceCell = row.insertCell(4);
            performanceCell.textContent = result.performance;
        });
        
        // 显示洞察
        const insightsDiv = document.getElementById('insights');
        result.data.insights.forEach(insight => {
            const p = document.createElement('p');
            p.textContent = insight;
            insightsDiv.appendChild(p);
        });
        
        // 显示推荐
        const recommendationsDiv = document.getElementById('recommendations');
        result.data.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.textContent = recommendation;
            recommendationsDiv.appendChild(li);
        });
    } else {
        console.error(`比较失败: ${result.message}`);
    }
})
.catch(error => {
    console.error("请求错误:", error);
});
```