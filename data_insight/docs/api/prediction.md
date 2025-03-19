# 预测分析 API

## 概述

预测分析 API 用于根据历史数据预测指标的未来趋势，支持时间序列预测、异常检测和预警。API 提供多种预测算法和参数配置，可以根据不同的数据特性和业务需求选择合适的预测模型。

## API 端点

### 预测分析

**端点:** `/api/v1/forecast`

**方法:** `POST`

**描述:** 基于历史数据预测未来指标值，支持季节性分解和置信区间。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `values` | array | 是 | 历史数据点数组 | - | 数组长度: 最少10个点 |
| `target_periods` | integer | 否 | 预测未来的期数 | 5 | 取值范围: 1-100 |
| `seasonality` | integer | 否 | 季节性周期长度 | null | 取值范围: 0-365，0表示无季节性 |
| `auto_seasonality` | boolean | 否 | 是否自动检测季节性 | true | - |
| `time_points` | array | 否 | 历史数据对应的时间点 | [] | 长度应与values数组长度相同 |
| `time_frequency` | string | 否 | 时间频率 | "auto" | 可选值: "auto", "minute", "hour", "day", "week", "month", "quarter", "year" |
| `model` | string | 否 | 预测模型 | "auto" | 可选值: "auto", "arima", "prophet", "exponential_smoothing", "lstm", "gru" |
| `confidence_level` | number | 否 | 置信水平 | 0.95 | 取值范围: 0.5-0.99 |
| `include_history` | boolean | 否 | 是否在结果中包含历史数据 | false | - |
| `include_decomposition` | boolean | 否 | 是否包含时间序列分解结果 | false | - |
| `include_diagnostics` | boolean | 否 | 是否包含模型诊断信息 | false | - |

**请求示例:**

```json
{
  "values": [105, 112, 118, 125, 131, 135, 142, 150, 157, 162, 170, 175, 180, 185, 188, 195, 202, 210, 215, 218, 222, 228, 232, 235],
  "target_periods": 8,
  "seasonality": 12,
  "model": "prophet",
  "confidence_level": 0.9,
  "time_points": ["2022-01-01", "2022-02-01", "2022-03-01", "2022-04-01", "2022-05-01", "2022-06-01", "2022-07-01", "2022-08-01", "2022-09-01", "2022-10-01", "2022-11-01", "2022-12-01", "2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01", "2023-11-01", "2023-12-01"],
  "time_frequency": "month",
  "include_decomposition": true,
  "include_diagnostics": true
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
| `data.forecast` | array | 预测结果数组 |
| `data.forecast[].value` | number | 预测点值 |
| `data.forecast[].lower_bound` | number | 预测下限（置信区间） |
| `data.forecast[].upper_bound` | number | 预测上限（置信区间） |
| `data.forecast[].time_point` | string | 预测点对应的时间（如有） |
| `data.forecast_summary` | object | 预测结果统计摘要 |
| `data.model_info` | object | 使用的模型信息 |
| `data.decomposition` | object | 时间序列分解结果（如有） |
| `data.diagnostics` | object | 模型诊断信息（如有） |
| `data.forecast_accuracy` | object | 预测准确度指标 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "预测分析成功",
  "status_code": 200,
  "data": {
    "forecast": [
      {
        "value": 240.3,
        "lower_bound": 235.8,
        "upper_bound": 244.7,
        "time_point": "2024-01-01"
      },
      {
        "value": 245.1,
        "lower_bound": 239.5,
        "upper_bound": 250.7,
        "time_point": "2024-02-01"
      },
      {
        "value": 249.8,
        "lower_bound": 243.0,
        "upper_bound": 256.6,
        "time_point": "2024-03-01"
      },
      {
        "value": 254.5,
        "lower_bound": 246.5,
        "upper_bound": 262.5,
        "time_point": "2024-04-01"
      },
      {
        "value": 259.2,
        "lower_bound": 249.9,
        "upper_bound": 268.5,
        "time_point": "2024-05-01"
      },
      {
        "value": 263.9,
        "lower_bound": 253.2,
        "upper_bound": 274.6,
        "time_point": "2024-06-01"
      },
      {
        "value": 268.7,
        "lower_bound": 256.4,
        "upper_bound": 281.0,
        "time_point": "2024-07-01"
      },
      {
        "value": 273.4,
        "lower_bound": 259.5,
        "upper_bound": 287.3,
        "time_point": "2024-08-01"
      }
    ],
    "forecast_summary": {
      "min": 240.3,
      "max": 273.4,
      "mean": 256.9,
      "median": 257.0,
      "trend_type": "increasing",
      "growth_rate": 1.9
    },
    "model_info": {
      "name": "prophet",
      "parameters": {
        "seasonality_mode": "multiplicative",
        "changepoint_prior_scale": 0.05,
        "seasonality_prior_scale": 10
      },
      "detected_seasonality": 12
    },
    "decomposition": {
      "trend": [105.2, 112.5, 118.3, 125.2, 131.6, 135.4, 142.1, 150.3, 157.2, 162.5, 170.3, 175.2, 180.4, 185.3, 188.2, 195.4, 202.5, 210.1, 215.2, 218.3, 222.4, 228.1, 232.2, 235.5],
      "seasonal": [0.98, 0.95, 1.03, 1.01, 0.99, 1.04, 1.02, 0.98, 1.01, 0.97, 0.99, 1.02, 0.98, 0.95, 1.03, 1.01, 0.99, 1.04, 1.02, 0.98, 1.01, 0.97, 0.99, 1.02],
      "residual": [0.01, 0.02, -0.01, -0.01, 0.00, -0.02, -0.01, 0.01, -0.01, 0.02, 0.01, -0.01, 0.01, 0.01, -0.01, -0.00, 0.00, -0.02, -0.01, 0.01, -0.01, 0.02, 0.01, -0.01]
    },
    "diagnostics": {
      "mape": 1.2,
      "rmse": 2.3,
      "mae": 1.8,
      "r_squared": 0.992,
      "aic": 156.8,
      "bic": 172.3,
      "residual_tests": {
        "ljung_box_test": {
          "statistic": 15.2,
          "p_value": 0.38,
          "result": "white_noise"
        },
        "jarque_bera_test": {
          "statistic": 1.8,
          "p_value": 0.41,
          "result": "normal"
        }
      }
    },
    "forecast_accuracy": {
      "cross_validation": {
        "mape": 2.1,
        "rmse": 4.2,
        "mae": 3.5
      },
      "confidence": 0.88
    }
  },
  "timestamp": "2023-12-05T12:34:56.789Z"
}
```

### 异步预测分析

**端点:** `/api/v1/forecast-async`

**方法:** `POST`

**描述:** 异步执行预测分析。立即返回任务ID，可以通过任务ID查询分析结果。

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
  "message": "预测分析任务已创建",
  "status_code": 202,
  "data": {
    "task_id": "12345678-1234-5678-1234-567812345678",
    "status": "pending",
    "check_url": "/api/v1/tasks/12345678-1234-5678-1234-567812345678"
  },
  "timestamp": "2023-12-05T12:34:56.789Z"
}
```

### 异常检测分析

**端点:** `/api/v1/anomaly`

**方法:** `POST`

**描述:** 在时间序列数据中检测异常点或异常模式。

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| `values` | array | 是 | 时间序列数据点数组 | - | 数组长度: 最少10个点 |
| `threshold` | number | 否 | 异常检测阈值（标准差倍数） | 3.0 | 取值范围: 1.0-10.0 |
| `lookback_periods` | integer | 否 | 用于计算基线的回溯期数 | 5 | 取值范围: 3-100 |
| `time_points` | array | 否 | 数据点对应的时间点 | [] | 长度应与values数组长度相同 |
| `method` | string | 否 | 异常检测方法 | "z_score" | 可选值: "z_score", "iqr", "isolation_forest", "prophet", "seasonal_decompose", "lstm" |
| `seasonality` | integer | 否 | 季节性周期长度 | null | 取值范围: 0-365，0表示无季节性 |
| `sensitivity` | number | 否 | 检测灵敏度 | 0.05 | 取值范围: 0.01-0.5 |
| `include_forecast` | boolean | 否 | 是否在结果中包含预测 | false | - |
| `target_periods` | integer | 否 | 预测未来的期数（如需） | 5 | 取值范围: 1-100 |

**请求示例:**

```json
{
  "values": [105, 110, 108, 112, 115, 140, 118, 120, 125, 122, 128, 130, 135, 132, 138, 140, 142, 145, 150, 190, 155, 158, 160, 165],
  "threshold": 2.5,
  "lookback_periods": 5,
  "time_points": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10", "2023-01-11", "2023-01-12", "2023-01-13", "2023-01-14", "2023-01-15", "2023-01-16", "2023-01-17", "2023-01-18", "2023-01-19", "2023-01-20", "2023-01-21", "2023-01-22", "2023-01-23", "2023-01-24"],
  "method": "seasonal_decompose",
  "seasonality": 7,
  "include_forecast": true,
  "target_periods": 7
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
| `data.anomalies` | array | 检测到的异常点数组 |
| `data.anomalies[].index` | integer | 异常点在原始数据中的索引 |
| `data.anomalies[].value` | number | 异常点的值 |
| `data.anomalies[].expected_value` | number | 异常点的预期值 |
| `data.anomalies[].deviation` | number | 异常点的偏差量 |
| `data.anomalies[].deviation_percentage` | number | 异常点的偏差百分比 |
| `data.anomalies[].score` | number | 异常分数 (0-1) |
| `data.anomalies[].time_point` | string | 异常点对应的时间（如有） |
| `data.anomalies[].type` | string | 异常类型，如"spike"、"dip"、"level_shift"等 |
| `data.baseline` | array | 基线数据 |
| `data.upper_bound` | array | 上限阈值 |
| `data.lower_bound` | array | 下限阈值 |
| `data.forecast` | object | 预测结果（如有） |
| `data.summary` | object | 异常检测摘要 |
| `timestamp` | string | 响应时间戳 |

**响应示例:**

```json
{
  "success": true,
  "message": "异常检测成功",
  "status_code": 200,
  "data": {
    "anomalies": [
      {
        "index": 5,
        "value": 140,
        "expected_value": 114.2,
        "deviation": 25.8,
        "deviation_percentage": 22.6,
        "score": 0.92,
        "time_point": "2023-01-06",
        "type": "spike"
      },
      {
        "index": 19,
        "value": 190,
        "expected_value": 147.5,
        "deviation": 42.5,
        "deviation_percentage": 28.8,
        "score": 0.98,
        "time_point": "2023-01-20",
        "type": "spike"
      }
    ],
    "baseline": [null, null, null, null, null, 114.2, 116.8, 119.3, 121.7, 124.0, 126.3, 128.5, 130.8, 133.0, 135.2, 137.5, 139.7, 142.0, 144.3, 147.5, 149.9, 152.3, 154.7, 157.1],
    "upper_bound": [null, null, null, null, null, 128.9, 131.7, 134.4, 137.1, 139.7, 142.3, 144.8, 147.3, 149.8, 152.3, 154.7, 157.1, 159.5, 162.0, 164.8, 167.5, 170.2, 172.9, 175.6],
    "lower_bound": [null, null, null, null, null, 99.6, 102.0, 104.2, 106.4, 108.4, 110.4, 112.3, 114.3, 116.2, 118.2, 120.2, 122.3, 124.4, 126.6, 130.2, 132.3, 134.4, 136.5, 138.6],
    "forecast": {
      "values": [161.5, 164.1, 166.7, 169.3, 171.9, 174.6, 177.2],
      "upper_bound": [179.4, 183.4, 187.4, 191.5, 195.7, 199.9, 204.2],
      "lower_bound": [143.6, 144.8, 145.9, 147.1, 148.2, 149.3, 150.3],
      "time_points": ["2023-01-25", "2023-01-26", "2023-01-27", "2023-01-28", "2023-01-29", "2023-01-30", "2023-01-31"]
    },
    "summary": {
      "total_anomalies": 2,
      "anomaly_percentage": 8.3,
      "anomaly_types": {
        "spike": 2,
        "dip": 0,
        "level_shift": 0,
        "trend_change": 0
      },
      "largest_anomaly": {
        "value": 190,
        "time_point": "2023-01-20",
        "deviation_percentage": 28.8
      },
      "model_info": {
        "method": "seasonal_decompose",
        "seasonality": 7,
        "parameters": {
          "threshold": 2.5,
          "lookback_periods": 5
        }
      }
    }
  },
  "timestamp": "2023-12-05T12:34:56.789Z"
}
```

### 异步异常检测分析

**端点:** `/api/v1/anomaly-async`

**方法:** `POST`

**描述:** 异步执行异常检测分析。立即返回任务ID，可以通过任务ID查询分析结果。

#### 请求参数

与同步分析端点相同。

#### 响应参数

与其他异步接口相同，返回任务ID和状态信息。

## 预测模型说明

| 模型 | 描述 | 适用场景 |
|------|------|----------|
| `arima` | 自回归积分移动平均模型 | 线性、平稳、无强季节性的时间序列 |
| `prophet` | Facebook Prophet时间序列预测框架 | 具有强季节性和长期趋势的数据，可处理异常值和缺失值 |
| `exponential_smoothing` | 指数平滑模型 | 短期预测，可以处理趋势和季节性 |
| `lstm` | 长短期记忆神经网络 | 复杂非线性关系，长序列依赖的数据 |
| `gru` | 门控循环单元神经网络 | 类似LSTM但更轻量，适合资源受限场景 |
| `auto` | 自动选择最优模型 | 不确定最适合的模型时 |

## 异常检测方法说明

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| `z_score` | 基于Z分数（标准分数）的异常检测 | 数据近似正态分布时 |
| `iqr` | 基于四分位距的异常检测 | 非正态分布或有离群值的数据 |
| `isolation_forest` | 隔离森林算法 | 高维数据，无需假设数据分布 |
| `prophet` | 基于Prophet预测的异常检测 | 有明显季节性和趋势的数据 |
| `seasonal_decompose` | 基于季节性分解的异常检测 | 有明显季节性的数据 |
| `lstm` | 基于LSTM的异常检测 | 复杂时间序列，可捕捉长时间的依赖关系 |

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 无权限访问 |
| 404 | 任务不存在 |
| 422 | 数据不足以进行预测分析 |
| 429 | 请求频率超过限制 |
| 500 | 服务器内部错误 |

## 使用示例

### Python

```python
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# 准备数据 - 生成带趋势和季节性的时间序列
np.random.seed(42)
n = 24
trend = np.linspace(100, 200, n)
seasonality = 15 * np.sin(2 * np.pi * np.arange(n) / 12)
noise = np.random.normal(0, 5, n)
values = trend + seasonality + noise

# 生成日期序列
start_date = datetime(2022, 1, 1)
dates = [(start_date + timedelta(days=30*i)).strftime("%Y-%m-%d") for i in range(n)]

# 构建请求体
url = "https://api.data-insight.example.com/api/v1/forecast"
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}
data = {
    "values": values.tolist(),
    "target_periods": 6,
    "seasonality": 12,
    "time_points": dates,
    "time_frequency": "month",
    "confidence_level": 0.9,
    "include_decomposition": True
}

# 发送请求
response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

if result["success"]:
    # 提取历史数据和预测结果
    historical_values = values
    forecast_values = [point["value"] for point in result["data"]["forecast"]]
    lower_bound = [point["lower_bound"] for point in result["data"]["forecast"]]
    upper_bound = [point["upper_bound"] for point in result["data"]["forecast"]]
    
    # 生成预测期的日期
    forecast_dates = []
    last_date = datetime.strptime(dates[-1], "%Y-%m-%d")
    for i in range(len(forecast_values)):
        next_date = last_date + timedelta(days=30*(i+1))
        forecast_dates.append(next_date.strftime("%Y-%m-%d"))
    
    # 绘制结果
    plt.figure(figsize=(12, 6))
    
    # 绘制历史数据
    plt.plot(range(len(historical_values)), historical_values, 'b-', label='历史数据')
    
    # 绘制预测值
    start_idx = len(historical_values) - 1
    x_forecast = range(start_idx, start_idx + len(forecast_values) + 1)
    y_forecast = [historical_values[-1]] + forecast_values
    plt.plot(x_forecast, y_forecast, 'r-', label='预测值')
    
    # 绘制置信区间
    x_conf = range(start_idx + 1, start_idx + len(forecast_values) + 1)
    plt.fill_between(x_conf, lower_bound, upper_bound, color='red', alpha=0.2, label='90%置信区间')
    
    # 添加标签和图例
    date_labels = dates + forecast_dates
    plt.xticks(range(0, len(historical_values) + len(forecast_values), 3), 
               [date_labels[i] for i in range(0, len(date_labels), 3)], rotation=45)
    plt.xlabel('日期')
    plt.ylabel('值')
    plt.title('时间序列预测')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # 如果有季节性分解，绘制分解结果
    if "decomposition" in result["data"]:
        decomp = result["data"]["decomposition"]
        trend = decomp["trend"]
        seasonal = decomp["seasonal"]
        residual = decomp["residual"]
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        
        # 绘制趋势
        axes[0].plot(trend, 'g-')
        axes[0].set_ylabel('趋势')
        axes[0].grid(True)
        
        # 绘制季节性
        axes[1].plot(seasonal, 'm-')
        axes[1].set_ylabel('季节性')
        axes[1].grid(True)
        
        # 绘制残差
        axes[2].plot(residual, 'k-')
        axes[2].set_ylabel('残差')
        axes[2].grid(True)
        
        fig.suptitle('时间序列分解')
        plt.tight_layout()
    
    plt.show()
    
    # 打印预测结果摘要
    print("预测结果摘要:")
    summary = result["data"]["forecast_summary"]
    print(f"最小值: {summary['min']}")
    print(f"最大值: {summary['max']}")
    print(f"均值: {summary['mean']}")
    print(f"趋势类型: {summary['trend_type']}")
    print(f"增长率: {summary['growth_rate']}%")
    
    # 打印预测值
    print("\n预测值:")
    for i, f in enumerate(result["data"]["forecast"]):
        print(f"时间: {forecast_dates[i]}, 预测值: {f['value']:.2f}, 区间: [{f['lower_bound']:.2f}, {f['upper_bound']:.2f}]")
else:
    print(f"预测失败: {result['message']}")
```

### JavaScript

```javascript
// 使用Chart.js绘制预测图表
const url = "https://api.data-insight.example.com/api/v1/forecast";
const headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
};

// 生成示例数据 - 带趋势和季节性的时间序列
function generateData() {
    const n = 24;
    const values = [];
    const dates = [];
    const baseDate = new Date(2022, 0, 1);
    
    for (let i = 0; i < n; i++) {
        // 趋势 + 季节性 + 噪声
        const trend = 100 + (100 / n) * i;
        const seasonality = 15 * Math.sin(2 * Math.PI * i / 12);
        const noise = Math.random() * 10 - 5;
        values.push(trend + seasonality + noise);
        
        // 日期
        const currentDate = new Date(baseDate);
        currentDate.setMonth(baseDate.getMonth() + i);
        dates.push(currentDate.toISOString().split('T')[0]);
    }
    
    return { values, dates };
}

const data = generateData();

// 构建请求体
const requestData = {
    values: data.values,
    target_periods: 6,
    seasonality: 12,
    time_points: data.dates,
    time_frequency: "month",
    confidence_level: 0.9,
    include_decomposition: true
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(requestData)
})
.then(response => response.json())
.then(result => {
    if (result.success) {
        // 提取历史数据和预测结果
        const historicalValues = data.values;
        const forecastValues = result.data.forecast.map(point => point.value);
        const lowerBound = result.data.forecast.map(point => point.lower_bound);
        const upperBound = result.data.forecast.map(point => point.upper_bound);
        
        // 生成预测期的日期
        const forecastDates = [];
        const lastDate = new Date(data.dates[data.dates.length - 1]);
        for (let i = 0; i < forecastValues.length; i++) {
            const nextDate = new Date(lastDate);
            nextDate.setMonth(lastDate.getMonth() + i + 1);
            forecastDates.push(nextDate.toISOString().split('T')[0]);
        }
        
        // 使用Chart.js绘制结果
        const ctx = document.getElementById('forecastChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [...data.dates, ...forecastDates],
                datasets: [
                    {
                        label: '历史数据',
                        data: [...historicalValues, null, null, null, null, null, null],
                        borderColor: 'blue',
                        fill: false
                    },
                    {
                        label: '预测值',
                        data: [...Array(historicalValues.length).fill(null), historicalValues[historicalValues.length - 1], ...forecastValues],
                        borderColor: 'red',
                        fill: false
                    },
                    {
                        label: '置信区间',
                        data: [...Array(historicalValues.length).fill(null), null, ...upperBound],
                        borderColor: 'rgba(255, 0, 0, 0.2)',
                        backgroundColor: 'rgba(255, 0, 0, 0.1)',
                        fill: '+1',
                        pointRadius: 0
                    },
                    {
                        label: '置信区间',
                        data: [...Array(historicalValues.length).fill(null), null, ...lowerBound],
                        borderColor: 'rgba(255, 0, 0, 0.2)',
                        backgroundColor: 'rgba(255, 0, 0, 0.1)',
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: '时间序列预测'
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: '日期'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: '值'
                        }
                    }]
                }
            }
        });
        
        // 显示预测结果摘要
        const summary = result.data.forecast_summary;
        document.getElementById('forecastSummary').innerHTML = `
            <h3>预测结果摘要</h3>
            <p>最小值: ${summary.min.toFixed(2)}</p>
            <p>最大值: ${summary.max.toFixed(2)}</p>
            <p>均值: ${summary.mean.toFixed(2)}</p>
            <p>趋势类型: ${summary.trend_type}</p>
            <p>增长率: ${summary.growth_rate.toFixed(2)}%</p>
            
            <h3>详细预测值</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>预测值</th>
                        <th>下限</th>
                        <th>上限</th>
                    </tr>
                </thead>
                <tbody>
                    ${result.data.forecast.map((f, i) => `
                        <tr>
                            <td>${forecastDates[i]}</td>
                            <td>${f.value.toFixed(2)}</td>
                            <td>${f.lower_bound.toFixed(2)}</td>
                            <td>${f.upper_bound.toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else {
        console.error(`预测失败: ${result.message}`);
    }
})
.catch(error => {
    console.error("请求错误:", error);
});