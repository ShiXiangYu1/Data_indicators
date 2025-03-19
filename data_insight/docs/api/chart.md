# 图表分析 API

## 概述

图表分析 API 用于分析可视化图表中的数据模式、趋势和异常，提取图表中的关键信息并生成洞察。支持多种常见图表类型，包括线图、柱状图、面积图、散点图等，能够识别图表中的重要特征点、趋势变化和数据异常。

## API 端点

### 图表分析

**端点:** `/api/v1/chart/analyze`

**方法:** `POST`

**描述:** 分析图表数据，提取关键特征和生成数据洞察。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `chart_type` | string | 是 | 图表类型 | - | 可选值: "line", "bar", "area", "scatter", "pie" |
| `data` | object | 是 | 图表数据 | - | - |
| `data.series` | array | 是 | 数据系列数组 | - | 最小长度: 1, 最大长度: 10 |
| `data.series[].name` | string | 是 | 系列名称 | - | 长度: 1-100 |
| `data.series[].values` | array | 是 | 数据点值数组 | - | 最小长度: 2, 最大长度: 1000 |
| `data.categories` | array | 否 | 类别/时间轴标签 | - | 最大长度: 1000 |
| `data.title` | string | 否 | 图表标题 | - | 长度: 0-200 |
| `options` | object | 否 | 分析选项 | {} | - |
| `options.detect_anomalies` | boolean | 否 | 是否检测异常点 | true | - |
| `options.identify_trends` | boolean | 否 | 是否识别趋势 | true | - |
| `options.detect_patterns` | boolean | 否 | 是否检测模式 | true | - |
| `options.compare_series` | boolean | 否 | 是否比较多个系列 | true | - |
| `options.sensitivity` | number | 否 | 异常检测灵敏度 | 0.8 | 范围: 0.1-1.0 |
| `options.include_details` | boolean | 否 | 是否包含详细分析 | true | - |
| `time_format` | string | 否 | 时间格式(如果是时间序列) | - | 如: "YYYY-MM-DD" |
| `context` | object | 否 | 业务上下文信息 | {} | - |

#### 请求示例

```json
{
  "chart_type": "line",
  "data": {
    "series": [
      {
        "name": "销售额",
        "values": [120, 132, 101, 134, 90, 230, 210]
      }
    ],
    "categories": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    "title": "周销售额趋势"
  },
  "options": {
    "detect_anomalies": true,
    "identify_trends": true,
    "sensitivity": 0.8
  },
  "time_format": null,
  "context": {
    "business_unit": "零售部",
    "target_value": 150
  }
}
```

#### 响应参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 响应消息 |
| `status_code` | number | HTTP状态码 |
| `data` | object | 分析结果数据 |
| `data.chart_insights` | object | 图表洞察 |
| `data.chart_insights.summary` | string | 总体分析摘要 |
| `data.chart_insights.trends` | array | 识别出的趋势 |
| `data.chart_insights.anomalies` | array | 检测到的异常点 |
| `data.chart_insights.patterns` | array | 发现的数据模式 |
| `data.chart_insights.comparison` | object | 多系列比较结果(如适用) |
| `data.series_analysis` | array | 各数据系列的分析结果 |
| `data.metadata` | object | 分析元数据 |
| `timestamp` | string | 响应时间戳 |

#### 响应示例

```json
{
  "success": true,
  "message": "图表分析完成",
  "status_code": 200,
  "data": {
    "chart_insights": {
      "summary": "销售额整体呈上升趋势，周六达到最高值230，周五出现异常低谷90。",
      "trends": [
        {
          "type": "上升",
          "from_index": 4,
          "to_index": 5,
          "from_value": 90,
          "to_value": 230,
          "change_rate": 1.56,
          "description": "从周五到周六，销售额大幅上升155.6%"
        }
      ],
      "anomalies": [
        {
          "index": 4,
          "value": 90,
          "expected_range": [110, 150],
          "deviation": -0.25,
          "description": "周五销售额异常偏低，低于预期范围25%"
        }
      ],
      "patterns": [
        {
          "type": "周期性",
          "description": "工作日销售额相对平稳，周末(周六、周日)销售额明显上升",
          "confidence": 0.85
        }
      ]
    },
    "series_analysis": [
      {
        "name": "销售额",
        "min": 90,
        "max": 230,
        "average": 145.29,
        "median": 132,
        "std_deviation": 52.71,
        "growth_rate": 0.75,
        "volatility": 0.36
      }
    ],
    "metadata": {
      "analysis_duration_ms": 156,
      "model_version": "1.2.0",
      "data_points_count": 7
    }
  },
  "timestamp": "2023-04-10T14:23:45.678Z"
}
```

### 异步图表分析

**端点:** `/api/v1/chart/analyze-async`

**方法:** `POST`

**描述:** 异步分析图表数据，适用于大型复杂图表或批量分析任务。

请求参数与同步分析接口相同。

#### 响应参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 响应消息 |
| `status_code` | number | HTTP状态码 |
| `data` | object | 任务信息 |
| `data.task_id` | string | 异步任务ID |
| `data.status` | string | 任务状态 |
| `data.estimated_time` | number | 预计完成时间(秒) |
| `timestamp` | string | 响应时间戳 |

#### 获取异步任务结果

**端点:** `/api/v1/tasks/{task_id}`

**方法:** `GET`

**描述:** 获取异步任务的结果。

### 图表比较分析

**端点:** `/api/v1/chart/compare`

**方法:** `POST`

**描述:** 比较两个或多个图表数据，分析它们之间的差异和相似性。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `chart_type` | string | 是 | 图表类型 | - | 可选值: "line", "bar", "area", "scatter" |
| `charts` | array | 是 | 待比较的图表数组 | - | 最小长度: 2, 最大长度: 5 |
| `charts[].name` | string | 是 | 图表名称 | - | 长度: 1-100 |
| `charts[].data` | object | 是 | 图表数据(同analyze接口) | - | - |
| `comparison_options` | object | 否 | 比较选项 | {} | - |
| `comparison_options.metrics` | array | 否 | 比较指标列表 | ["shape", "trend", "range"] | - |
| `comparison_options.normalize` | boolean | 否 | 是否归一化数据 | true | - |
| `time_format` | string | 否 | 时间格式(如果是时间序列) | - | 如: "YYYY-MM-DD" |

## 错误码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | `InvalidChartType` | 无效的图表类型 |
| 400 | `InvalidSeriesData` | 无效的系列数据 |
| 400 | `InsufficientDataPoints` | 数据点数量不足 |
| 400 | `MismatchedCategories` | 类别与数据点数量不匹配 |
| 400 | `InvalidOptions` | 无效的分析选项 |
| 429 | `RateLimitExceeded` | 超出请求速率限制 |
| 500 | `AnalysisError` | 分析过程中发生错误 |

## 使用示例

### Python

```python
import requests
import json

url = "https://api.data-insight.example.com/api/v1/chart/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}

data = {
    "chart_type": "line",
    "data": {
        "series": [
            {
                "name": "用户增长",
                "values": [1020, 1050, 1100, 1120, 1250, 1380, 1400, 1450]
            }
        ],
        "categories": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月"],
        "title": "2023年月度用户增长"
    },
    "options": {
        "detect_anomalies": True,
        "identify_trends": True
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    insights = result["data"]["chart_insights"]
    print(f"分析摘要: {insights['summary']}")
    
    # 打印检测到的异常
    if insights["anomalies"]:
        print("\n检测到的异常:")
        for anomaly in insights["anomalies"]:
            print(f" - {anomaly['description']}")
    
    # 打印识别的趋势
    if insights["trends"]:
        print("\n识别的趋势:")
        for trend in insights["trends"]:
            print(f" - {trend['description']}")
else:
    print(f"分析失败: {result['message']}")
```

### JavaScript

```javascript
const analyzeChart = async () => {
  const url = 'https://api.data-insight.example.com/api/v1/chart/analyze';
  
  const requestData = {
    chart_type: 'bar',
    data: {
      series: [
        {
          name: '收入',
          values: [300, 350, 320, 410, 490, 530, 600]
        },
        {
          name: '支出',
          values: [250, 280, 260, 300, 310, 350, 380]
        }
      ],
      categories: ['Q1-2022', 'Q2-2022', 'Q3-2022', 'Q4-2022', 'Q1-2023', 'Q2-2023', 'Q3-2023'],
      title: '季度财务表现'
    },
    options: {
      detect_anomalies: true,
      identify_trends: true,
      compare_series: true
    }
  };
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Token': 'your_api_token'
      },
      body: JSON.stringify(requestData)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('分析摘要:', result.data.chart_insights.summary);
      
      // 处理系列比较结果
      if (result.data.chart_insights.comparison) {
        console.log('系列比较结果:', result.data.chart_insights.comparison);
      }
      
      // 获取各系列分析
      const seriesAnalysis = result.data.series_analysis;
      seriesAnalysis.forEach(series => {
        console.log(`${series.name} 分析:`, 
          `平均值: ${series.average}, 增长率: ${series.growth_rate}`);
      });
    } else {
      console.error('分析失败:', result.message);
    }
  } catch (error) {
    console.error('请求错误:', error);
  }
};

analyzeChart();
``` 