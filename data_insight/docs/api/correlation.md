# 相关性分析 API

## 概述

相关性分析 API 用于分析指标之间的相互关系和依赖程度，识别强相关、弱相关和无相关的指标对，并提供相关性的统计显著性和置信区间。API 支持多种相关性计算方法，适用于不同类型的数据分析需求。

## API 端点

### 相关性分析

**端点:** `/api/v1/correlation`

**方法:** `POST`

**描述:** 分析指标之间的相关性，计算相关系数和显著性。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `metrics` | array | 是 | 需要分析相关性的指标列表 | - | 数组长度: 2-50 |
| `metrics[].name` | string | 是 | 指标名称 | - | 长度: 1-100 |
| `metrics[].values` | array | 是 | 指标数据点数组 | - | 数组长度: 10-10000 |
| `metrics[].unit` | string | 否 | 指标单位 | "" | - |
| `time_points` | array | 否 | 数据点对应的时间点 | [] | 长度应与各指标的values数组长度相同 |
| `correlation_method` | string | 否 | 相关性计算方法 | "pearson" | 可选值: "pearson", "spearman", "kendall", "distance", "mutual_info", "chi_square" |
| `significance_level` | number | 否 | 显著性水平 | 0.05 | 取值范围: 0.001-0.1 |
| `include_time_lag` | boolean | 否 | 是否计算时间滞后相关性 | false | - |
| `max_lag` | integer | 否 | 最大时间滞后值 | 10 | 取值范围: 1-100 |
| `segment_by` | array | 否 | 分段分析的字段 | [] | - |
| `filter_threshold` | number | 否 | 相关系数过滤阈值 | 0 | 取值范围: 0-1 |
| `include_details` | boolean | 否 | 是否包含详细分析数据 | false | - |

**请求示例:**

```json
{
  "metrics": [
    {
      "name": "网站访问量",
      "values": [1200, 1250, 1400, 1500, 1480, 1550, 1600, 1650, 1700, 1750, 1850, 1900],
      "unit": "次"
    },
    {
      "name": "转化率",
      "values": [3.2, 3.3, 3.5, 3.8, 3.7, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5],
      "unit": "%"
    },
    {
      "name": "平均停留时间",
      "values": [65, 68, 72, 75, 74, 77, 79, 80, 82, 83, 85, 86],
      "unit": "秒"
    },
    {
      "name": "跳出率",
      "values": [42, 41, 39, 37, 38, 36, 35, 34, 33, 32, 31, 30],
      "unit": "%"
    }
  ],
  "time_points": [
    "2023-07-01", "2023-07-02", "2023-07-03", "2023-07-04", "2023-07-05", 
    "2023-07-06", "2023-07-07", "2023-07-08", "2023-07-09", "2023-07-10", 
    "2023-07-11", "2023-07-12"
  ],
  "correlation_method": "pearson",
  "significance_level": 0.05,
  "include_time_lag": true,
  "max_lag": 3,
  "filter_threshold": 0.3,
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
| `data.correlation_matrix` | array | 相关系数矩阵 |
| `data.significant_pairs` | array | 具有统计显著性的指标对 |
| `data.significant_pairs[].metrics` | array | 具有显著相关性的指标对名称 |
| `data.significant_pairs[].coefficient` | number | 相关系数 |
| `data.significant_pairs[].coefficient_type` | string | 相关系数类型 |
| `data.significant_pairs[].p_value` | number | p值（统计显著性） |
| `data.significant_pairs[].confidence_interval` | array | 置信区间 [下限, 上限] |
| `data.significant_pairs[].relationship_type` | string | 关系类型，如"正相关"、"负相关" |
| `data.significant_pairs[].strength` | string | 相关性强度，如"强"、"中等"、"弱" |
| `data.significant_pairs[].time_lag` | integer | 时间滞后值（如果有） |
| `data.time_lag_analysis` | object | 时间滞后分析结果（如果requested） |
| `data.segments` | object | 分段分析结果（如果requested） |
| `data.visualizations` | object | 可视化数据（如果requested） |
| `data.summary` | string | 相关性分析的文字总结 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "相关性分析成功",
  "status_code": 200,
  "data": {
    "correlation_matrix": [
      [1.00, 0.92, 0.89, -0.95],
      [0.92, 1.00, 0.78, -0.88],
      [0.89, 0.78, 1.00, -0.82],
      [-0.95, -0.88, -0.82, 1.00]
    ],
    "significant_pairs": [
      {
        "metrics": ["网站访问量", "转化率"],
        "coefficient": 0.92,
        "coefficient_type": "pearson",
        "p_value": 0.0001,
        "confidence_interval": [0.85, 0.96],
        "relationship_type": "正相关",
        "strength": "强",
        "time_lag": 0
      },
      {
        "metrics": ["网站访问量", "平均停留时间"],
        "coefficient": 0.89,
        "coefficient_type": "pearson",
        "p_value": 0.0003,
        "confidence_interval": [0.81, 0.94],
        "relationship_type": "正相关",
        "strength": "强",
        "time_lag": 0
      },
      {
        "metrics": ["网站访问量", "跳出率"],
        "coefficient": -0.95,
        "coefficient_type": "pearson",
        "p_value": 0.0000,
        "confidence_interval": [-0.98, -0.90],
        "relationship_type": "负相关",
        "strength": "强",
        "time_lag": 0
      },
      {
        "metrics": ["转化率", "平均停留时间"],
        "coefficient": 0.78,
        "coefficient_type": "pearson",
        "p_value": 0.0026,
        "confidence_interval": [0.65, 0.87],
        "relationship_type": "正相关",
        "strength": "强",
        "time_lag": 0
      },
      {
        "metrics": ["转化率", "跳出率"],
        "coefficient": -0.88,
        "coefficient_type": "pearson",
        "p_value": 0.0002,
        "confidence_interval": [-0.94, -0.78],
        "relationship_type": "负相关",
        "strength": "强",
        "time_lag": 0
      },
      {
        "metrics": ["平均停留时间", "跳出率"],
        "coefficient": -0.82,
        "coefficient_type": "pearson",
        "p_value": 0.0011,
        "confidence_interval": [-0.91, -0.68],
        "relationship_type": "负相关",
        "strength": "强",
        "time_lag": 0
      },
      {
        "metrics": ["网站访问量", "转化率"],
        "coefficient": 0.75,
        "coefficient_type": "pearson",
        "p_value": 0.0081,
        "confidence_interval": [0.61, 0.85],
        "relationship_type": "正相关",
        "strength": "强",
        "time_lag": 1
      }
    ],
    "time_lag_analysis": {
      "网站访问量_转化率": {
        "optimal_lag": 1,
        "lags": [0, 1, 2, 3],
        "coefficients": [0.92, 0.75, 0.56, 0.32]
      },
      "网站访问量_平均停留时间": {
        "optimal_lag": 0,
        "lags": [0, 1, 2, 3],
        "coefficients": [0.89, 0.61, 0.42, 0.23]
      }
    },
    "visualizations": {
      "heatmap_data": {
        "x_labels": ["网站访问量", "转化率", "平均停留时间", "跳出率"],
        "y_labels": ["网站访问量", "转化率", "平均停留时间", "跳出率"],
        "values": [
          [1.00, 0.92, 0.89, -0.95],
          [0.92, 1.00, 0.78, -0.88],
          [0.89, 0.78, 1.00, -0.82],
          [-0.95, -0.88, -0.82, 1.00]
        ]
      },
      "scatter_plots": [
        {
          "pair": ["网站访问量", "转化率"],
          "x_values": [1200, 1250, 1400, 1500, 1480, 1550, 1600, 1650, 1700, 1750, 1850, 1900],
          "y_values": [3.2, 3.3, 3.5, 3.8, 3.7, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5],
          "trend_line": {
            "slope": 0.0010,
            "intercept": 1.99
          }
        }
      ]
    },
    "summary": "网站访问量与转化率、平均停留时间表现出强烈的正相关关系，与跳出率表现出强烈的负相关关系。这表明随着访问量的增加，用户体验指标普遍向好发展。转化率与平均停留时间也呈现显著正相关，表明用户停留时间越长，转化的可能性越高。值得注意的是，网站访问量对转化率有一天的滞后影响，系数为0.75，这可能表明部分用户需要考虑后再做出转化决策。"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

### 异步相关性分析

**端点:** `/api/v1/correlation-async`

**方法:** `POST`

**描述:** 异步分析指标之间的相关性。立即返回任务ID，可以通过任务ID查询分析结果。

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
  "message": "相关性分析任务已创建",
  "status_code": 202,
  "data": {
    "task_id": "12345678-1234-5678-1234-567812345678",
    "status": "pending",
    "check_url": "/api/v1/tasks/12345678-1234-5678-1234-567812345678"
  },
  "timestamp": "2023-07-25T12:34:56.789Z"
}
```

## 相关性计算方法说明

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| `pearson` | 皮尔逊相关系数，测量线性相关性 | 连续变量的线性关系分析 |
| `spearman` | 斯皮尔曼秩相关系数，测量单调相关性 | 序数变量或不符合正态分布的数据 |
| `kendall` | 肯德尔秩相关系数，测量一致性 | 小样本数据或有许多相同值的数据 |
| `distance` | 基于距离的相关性测量 | 非线性关系分析 |
| `mutual_info` | 互信息，测量任意关系 | 复杂非线性关系，分类变量与连续变量的关系 |
| `chi_square` | 卡方检验，测量分类变量间关系 | 分类变量间的相关性分析 |

## 相关性强度参考

| 相关系数绝对值 | 强度分类 |
|--------------|---------|
| 0.0 - 0.19   | 极弱相关 |
| 0.2 - 0.39   | 弱相关   |
| 0.4 - 0.59   | 中等相关 |
| 0.6 - 0.79   | 强相关   |
| 0.8 - 1.0    | 极强相关 |

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 无权限访问 |
| 404 | 任务不存在 |
| 422 | 数据不足以进行相关性分析 |
| 429 | 请求频率超过限制 |
| 500 | 服务器内部错误 |

## 使用示例

### Python

```python
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 准备数据
url = "https://api.data-insight.example.com/api/v1/correlation"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}
# 生成相关的随机数据，用于演示
np.random.seed(42)
n = 100
website_visits = np.random.normal(1000, 200, n)
conversion_rate = 2 + 0.002 * website_visits + np.random.normal(0, 0.3, n)
bounce_rate = 50 - 0.02 * website_visits + np.random.normal(0, 2, n)

data = {
    "metrics": [
        {
            "name": "网站访问量",
            "values": website_visits.tolist(),
            "unit": "次"
        },
        {
            "name": "转化率",
            "values": conversion_rate.tolist(),
            "unit": "%"
        },
        {
            "name": "跳出率",
            "values": bounce_rate.tolist(),
            "unit": "%"
        }
    ],
    "correlation_method": "pearson",
    "include_details": True
}

# 发送请求
response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    # 提取相关系数矩阵
    corr_matrix = np.array(result["data"]["correlation_matrix"])
    labels = [metric["name"] for metric in data["metrics"]]
    
    # 使用Seaborn绘制热力图
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", 
                xticklabels=labels, yticklabels=labels, cmap="coolwarm")
    plt.title("指标相关性热力图")
    plt.tight_layout()
    plt.show()
    
    # 打印显著相关的指标对
    print("显著相关的指标对:")
    for pair in result["data"]["significant_pairs"]:
        print(f"{pair['metrics'][0]} 与 {pair['metrics'][1]}: {pair['coefficient']:.2f} ({pair['relationship_type']})")
    
    # 打印分析总结
    print("\n分析总结:")
    print(result["data"]["summary"])
else:
    print(f"分析失败: {result['message']}")
```

### JavaScript

```javascript
// 使用D3.js绘制相关性热力图
const url = "https://api.data-insight.example.com/api/v1/correlation";
const headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
};

// 准备示例数据
const data = {
    metrics: [
        {
            name: "网站访问量",
            values: [1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100]
        },
        {
            name: "转化率",
            values: [3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0]
        },
        {
            name: "跳出率",
            values: [45, 44, 43, 42, 41, 40, 39, 38, 37, 36]
        }
    ],
    correlation_method: "pearson"
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        const correlationMatrix = result.data.correlation_matrix;
        const labels = data.metrics.map(metric => metric.name);
        
        // 使用D3.js绘制热力图
        const margin = {top: 50, right: 50, bottom: 100, left: 100};
        const width = 500 - margin.left - margin.right;
        const height = 500 - margin.top - margin.bottom;
        
        const svg = d3.select("#heatmap")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);
        
        // 创建X和Y轴
        const x = d3.scaleBand()
            .range([0, width])
            .domain(labels)
            .padding(0.05);
        
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)");
        
        const y = d3.scaleBand()
            .range([height, 0])
            .domain(labels)
            .padding(0.05);
        
        svg.append("g")
            .call(d3.axisLeft(y));
        
        // 创建颜色比例尺
        const myColor = d3.scaleSequential()
            .interpolator(d3.interpolateRdBu)
            .domain([-1, 1]);
        
        // 将相关系数矩阵转换为适合D3的格式
        const data = [];
        for (let i = 0; i < labels.length; i++) {
            for (let j = 0; j < labels.length; j++) {
                data.push({
                    x: labels[i],
                    y: labels[j],
                    value: correlationMatrix[i][j]
                });
            }
        }
        
        // 绘制热力图单元格
        svg.selectAll()
            .data(data, d => `${d.x}:${d.y}`)
            .enter()
            .append("rect")
            .attr("x", d => x(d.x))
            .attr("y", d => y(d.y))
            .attr("width", x.bandwidth())
            .attr("height", y.bandwidth())
            .style("fill", d => myColor(d.value))
            .attr("stroke", "white")
            .attr("stroke-width", 1)
            .append("title")
            .text(d => `${d.x} 与 ${d.y}: ${d.value.toFixed(2)}`);
        
        // 添加相关系数文本
        svg.selectAll()
            .data(data, d => `${d.x}:${d.y}`)
            .enter()
            .append("text")
            .attr("x", d => x(d.x) + x.bandwidth() / 2)
            .attr("y", d => y(d.y) + y.bandwidth() / 2)
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle")
            .text(d => d.value.toFixed(2))
            .style("font-size", "12px")
            .style("fill", d => Math.abs(d.value) > 0.5 ? "white" : "black");
        
        // 显示分析总结
        document.getElementById("summary").innerText = result.data.summary;
    } else {
        console.error(`分析失败: ${result.message}`);
    }
})
.catch(error => {
    console.error("请求错误:", error);
});
``` 