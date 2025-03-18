# 数据指标解读系统

本项目是数据指标平台的一个模块，专注于自动化数据解读和洞察生成，帮助用户快速理解数据图表和指标卡中的关键信息。

## 功能特点

- **指标数据分析**：自动分析指标的变化、趋势和异常情况
- **智能解读生成**：生成专业、通俗易懂的数据解读文本
- **多维异常检测**：检测并解释数据中的异常波动，支持季节性数据和多维度关联分析
- **趋势识别分析**：识别数据的发展趋势并提供解读
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
│   │   ├── base_analyzer.py      # 基础分析器
│   │   ├── metric_analyzer.py    # 指标卡分析器
│   │   ├── chart_analyzer.py     # 图表分析器
│   │   └── text_generator.py     # 文本生成器
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
│   ├── test_text_generator.py    # 文本生成器测试
│   └── test_enhanced_anomaly_detection.py # 增强异常检测算法测试
└── examples/               # 使用示例
    ├── simple_metric_analysis.py  # 简单指标分析示例
    ├── using_model_classes.py     # 使用模型类示例
    ├── using_chart_analyzer.py    # 图表分析示例
    └── using_enhanced_anomaly_detection.py # 增强异常检测示例
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

### 使用MetricInsight模型

```python
from data_insight.models.insight_model import MetricInsight
from datetime import datetime

# 创建指标洞察对象
insight = MetricInsight(
    metric_id="sales_202307",
    metric_name="月度销售额",
    current_value=1250000,
    previous_value=1000000,
    unit="元",
    time_period="2023年7月",
    previous_time_period="2023年6月",
    change_value=250000,
    change_rate=0.25,
    change_class="大幅增长",
    is_anomaly=True,
    anomaly_degree=1.8,
    trend_type="上升",
    trend_strength=0.92,
    insight_text="2023年7月月度销售额为125万元，相比2023年6月增加了25万元，增长25%。该指标呈现大幅增长，这是一个积极的信号。",
    created_at=datetime.now().isoformat()
)

# 转换为JSON格式
json_data = insight.to_json()
print(json_data)
```

### 使用增强的异常检测算法

```python
from data_insight.utils.data_utils import detect_anomaly_enhanced, detect_multi_dimensional_anomaly

# 基本异常检测 - 考虑季节性
historical_values = [100, 120, 95, 110, 105, 125, 90, 115, 110]  # 历史数据
current_value = 150  # 当前值

# 使用增强的异常检测算法
result = detect_anomaly_enhanced(
    value=current_value,
    historical_values=historical_values,
    seasonality=7,  # 指定季节周期为7（如每周数据）
    threshold=1.5   # 异常阈值
)

print(f"是否异常: {'是' if result['is_anomaly'] else '否'}")
print(f"异常程度: {result['anomaly_degree']:.2f}")
print(f"检测方法: {result['method']}")
print(f"异常原因: {result['reason']}")

# 多维异常检测
main_value = 150
main_history = [100, 120, 95, 110, 105, 125, 90, 115, 110]

# 相关维度数据
context_values = {
    "用户活跃度": 1500,
    "系统负载": 75,
    "营销支出": 5000
}

context_history = {
    "用户活跃度": [1000, 1100, 950, 1050, 1000, 1200, 900, 1100, 1050],
    "系统负载": [60, 65, 70, 60, 55, 65, 70, 60, 65],
    "营销支出": [3000, 3500, 3000, 4000, 3500, 3000, 3500, 4000, 4500]
}

# 执行多维异常检测
multi_result = detect_multi_dimensional_anomaly(
    main_value=main_value,
    main_history=main_history,
    context_values=context_values,
    context_history=context_history
)

print(f"\n多维异常检测结果:")
print(f"是否异常: {'是' if multi_result['is_anomaly'] else '否'}")
print(f"异常分数: {multi_result['anomaly_score']:.2f}")

# 显示影响因素
if multi_result['influencing_factors']:
    print("主要影响因素:")
    for factor in multi_result['influencing_factors']:
        print(f"  - {factor['dimension']}: 影响度 {factor['impact']:.2f}")
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

## 增强异常检测功能

系统提供了增强版的异常检测算法，具有以下特点：

1. **季节性数据支持**：自动检测或手动指定数据的季节性周期，排除正常的季节性波动
2. **多维度异常分析**：考虑多个相关维度的数据，综合判断异常情况
3. **上下文相关性分析**：分析目标指标与各维度的相关性，识别可能的影响因素
4. **异常原因解释**：自动生成可能的异常原因解释
5. **可视化异常展示**：支持异常数据的可视化展示

这些功能帮助用户更准确地识别真正的异常，而不是正常的季节性波动或与其他维度相关的变化。

## 开发规范

- **遵循PEP8规范**：代码格式严格按照PEP8标准
- **详细的中文注释**：所有函数和类都有完整的中文文档
- **完善的单元测试**：每个功能模块都有对应的单元测试
- **类型注解**：使用类型提示增强代码可读性和IDE支持

## 当前开发状态

- [x] 基础指标卡分析功能
- [x] 指标变化分析功能
- [x] 基础异常检测功能
- [x] 增强型异常检测算法
  - [x] 季节性数据支持
  - [x] 多维度异常检测
  - [x] 相关性分析
- [x] 趋势分析功能
- [x] 文本生成功能
- [x] 图表分析功能
- [ ] 多维度指标对比功能
- [ ] 高级归因分析 