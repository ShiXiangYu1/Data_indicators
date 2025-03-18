# 数据指标解读系统

本项目是数据指标平台的一个模块，专注于自动化数据解读和洞察生成，帮助用户快速理解数据图表和指标卡中的关键信息。

## 功能特点

- **指标数据分析**：自动分析指标的变化、趋势和异常情况
- **智能解读生成**：生成专业、通俗易懂的数据解读文本
- **多维异常检测**：检测并解释数据中的异常波动
- **趋势识别分析**：识别数据的发展趋势并提供解读
- **指标对比分析**：分析多个指标之间的关系，进行相关性和群组分析
- **智能原因分析**：分析指标变化背后的可能原因，支持多维度归因
- **中文语境优化**：针对中文用户习惯优化解读表述

## 项目结构

```
data_insight/
├── README.md               # 项目说明文档
├── requirements.txt        # 项目依赖
├── setup.py                # 安装脚本
├── data_insight/           # 核心代码目录
│   ├── __init__.py         
│   ├── core/               # 核心功能模块
│   │   ├── __init__.py
│   │   ├── base_analyzer.py        # 基础分析器
│   │   ├── metric_analyzer.py      # 指标卡分析器
│   │   ├── chart_analyzer.py       # 图表分析器
│   │   ├── metric_comparison_analyzer.py  # 指标对比分析器
│   │   ├── reason_analyzer.py      # 智能原因分析器
│   │   └── text_generator.py       # 文本生成器
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── data_utils.py         # 数据处理工具
│   │   └── text_utils.py         # 文本处理工具
│   ├── models/             # 模型定义
│   │   ├── __init__.py
│   │   └── insight_model.py      # 洞察模型
│   └── templates/          # 文本模板
│       ├── __init__.py
│       └── templates.py           # 解读文本模板
├── data/                   # 示例数据
│   └── sample_data.json    # 示例数据文件
├── tests/                  # 测试目录
│   ├── __init__.py
│   ├── test_data_utils.py        # 数据工具测试
│   ├── test_text_utils.py        # 文本工具测试
│   ├── test_metric_analyzer.py   # 指标分析器测试
│   ├── test_chart_analyzer.py    # 图表分析器测试
│   ├── test_metric_comparison_analyzer.py  # 指标对比分析器测试
│   ├── test_reason_analyzer.py   # 原因分析器测试
│   └── test_text_generator.py    # 文本生成器测试
└── examples/               # 使用示例
    ├── simple_metric_analysis.py # 简单指标分析示例
    ├── using_model_classes.py    # 使用模型类示例
    ├── using_chart_analyzer.py   # 图表分析示例
    ├── using_metric_comparison.py # 指标对比分析示例
    └── using_reason_analyzer.py  # 原因分析示例
```

## 安装方法

1. 克隆项目到本地
2. 安装依赖：`pip install -r requirements.txt`
3. 安装开发模式：`pip install -e .`

## 使用示例

### 单个指标解读

```python
from data_insight.core.metric_analyzer import MetricAnalyzer
from data_insight.core.text_generator import TextGenerator

# 创建指标数据
metric_data = {
    "name": "月度销售额",
    "value": 1250000,
    "previous_value": 1000000,
    "unit": "元",
    "time_period": "2023年7月",
    "previous_time_period": "2023年6月",
    "historical_values": [920000, 980000, 950000, 1010000, 1000000]
}

# 分析指标
analyzer = MetricAnalyzer()
analysis_result = analyzer.analyze(metric_data)

# 生成解读文本
generator = TextGenerator()
insight_text = generator.generate_text(analysis_result)

print(insight_text)
```

### 指标对比分析

```python
from data_insight.core.metric_comparison_analyzer import MetricComparisonAnalyzer
from data_insight.core.text_generator import TextGenerator

# 准备多个指标数据
metrics_data = {
    "metrics": [
        {
            "name": "销售额",
            "value": 1250000,
            "previous_value": 1000000,
            "unit": "元",
            "historical_values": [920000, 980000, 950000, 1010000, 1000000]
        },
        {
            "name": "利润",
            "value": 300000,
            "previous_value": 250000,
            "unit": "元",
            "historical_values": [220000, 235000, 228000, 245000, 250000]
        },
        {
            "name": "客户投诉",
            "value": 85,
            "previous_value": 120,
            "unit": "件",
            "historical_values": [150, 140, 130, 125, 120],
            "is_positive_better": False
        }
    ],
    "time_periods": ["2023年3月", "2023年4月", "2023年5月", "2023年6月", "2023年7月"]
}

# 分析指标对比关系
analyzer = MetricComparisonAnalyzer()
analysis_result = analyzer.analyze(metrics_data)

# 生成解读文本
generator = TextGenerator()
insight_text = generator.generate_text(analysis_result)

print(insight_text)
```

### 智能原因分析

```python
from data_insight.core.metric_analyzer import MetricAnalyzer
from data_insight.core.reason_analyzer import ReasonAnalyzer

# 准备指标数据
metric_data = {
    "name": "销售额",
    "value": 1250000,
    "previous_value": 1000000,
    "unit": "元",
    "time_period": "2023年7月",
    "previous_time_period": "2023年6月",
    "historical_values": [920000, 980000, 950000, 1010000, 1000000]
}

# 进行基础分析
metric_analyzer = MetricAnalyzer()
analysis_result = metric_analyzer.analyze(metric_data)

# 添加历史数据和相关指标
analysis_result["历史数据"] = {
    "values": [920000, 980000, 950000, 1010000, 1000000, 1250000],
    "time_periods": ["2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月", "2023年7月"]
}
analysis_result["相关指标"] = [
    {
        "name": "营销费用",
        "value": 300000,
        "previous_value": 250000,
        "unit": "元",
        "correlation": 0.85
    },
    {
        "name": "客户数量",
        "value": 5200,
        "previous_value": 4800,
        "unit": "人",
        "correlation": 0.78
    }
]

# 进行原因分析
reason_analyzer = ReasonAnalyzer(use_llm=False)  # 默认为True，使用LLM增强分析
reason_result = reason_analyzer.analyze(analysis_result)

# 输出分析结果
for i, reason in enumerate(reason_result["原因分析"]["可能原因"]):
    print(f"{i+1}. {reason}")
print(f"置信度: {reason_result['原因分析']['置信度']}")
print(f"分析方法: {reason_result['原因分析']['分析方法']}")
```

## 数据格式说明

### 指标数据格式

```json
{
  "name": "指标名称",
  "value": 当前值(数值),
  "previous_value": 上一期值(数值),
  "unit": "单位(可选)",
  "time_period": "当前时间段(可选)",
  "previous_time_period": "上一时间段(可选)",
  "historical_values": [历史值数组(可选)],
  "is_positive_better": true/false(可选，指标增长是否为好)
}
```

### 指标对比数据格式

```json
{
  "metrics": [
    {
      "name": "指标1名称",
      "value": 当前值1,
      "previous_value": 上一期值1,
      "unit": "单位1",
      "historical_values": [指标1历史值]
    },
    {
      "name": "指标2名称",
      "value": 当前值2,
      "previous_value": 上一期值2,
      "unit": "单位2",
      "historical_values": [指标2历史值]
    }
  ],
  "time_periods": ["时间段1", "时间段2", ...],
  "dimensions": {
    "维度1": "值1",
    "维度2": "值2"
  }
}
```

### 原因分析输入格式

原因分析器接收指标分析结果作为输入，可以额外添加以下内容增强分析:

```json
{
  "基本信息": { /* 指标基本信息 */ },
  "变化分析": { /* 变化分析结果 */ },
  "异常分析": { /* 异常分析结果 */ },
  "历史数据": {
    "values": [历史值数组],
    "time_periods": ["时间段1", "时间段2", ...]
  },
  "相关指标": [
    {
      "name": "相关指标1",
      "value": 当前值,
      "previous_value": 上一期值,
      "unit": "单位",
      "correlation": 相关系数  // 可选，范围-1到1
    }
  ]
}
```

## 开发规范

- **遵循PEP8规范**：代码格式严格按照PEP8标准
- **详细的中文注释**：所有函数和类都有完整的中文文档
- **完善的单元测试**：每个功能模块都有对应的单元测试
- **类型注解**：使用类型提示增强代码可读性和IDE支持

## 当前开发状态

- [x] 基础指标卡分析功能
- [x] 指标变化分析功能
- [x] 异常检测功能
- [x] 趋势分析功能
- [x] 文本生成功能
- [x] 图表分析功能
- [x] 多维度指标对比功能
- [x] 智能原因分析功能
- [ ] 行动建议生成功能 