# 数据指标解读系统

本项目是数据指标平台的一个模块，专注于自动化数据解读和洞察生成，帮助用户快速理解数据图表和指标卡中的关键信息。

## 功能特点

- **指标数据分析**：自动分析指标的变化、趋势和异常情况
- **智能解读生成**：生成专业、通俗易懂的数据解读文本
- **多维异常检测**：检测并解释数据中的异常波动
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
│   └── test_text_generator.py    # 文本生成器测试
└── examples/               # 使用示例
    └── simple_metric_analysis.py # 简单指标分析示例
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
- [ ] 图表分析功能
- [ ] 多维度指标对比功能
- [ ] 高级归因分析 

# 数据洞察分析系统

## 项目简介
数据洞察分析系统是一个强大的数据分析工具，能够自动分析数据指标的变化趋势、异常情况和可能原因，并生成易于理解的洞察报告。

## 主要功能

### 1. 指标分析
- 基础指标计算（变化量、变化率等）
- 趋势分析（上升、下降、波动等）
- 异常检测（基于统计方法）
- 多维度指标对比

### 2. 图表分析
- 自动生成数据可视化图表
- 支持多种图表类型（折线图、柱状图、散点图等）
- 智能图表解读
- 异常点标注

### 3. 智能原因分析
- 基于规则的原因分析
- 多维度指标关联分析
- 异常值原因分析
- 季节性变化原因分析
- 置信度评估
- 自然语言解读生成

### 4. 文本生成
- 自动生成数据洞察报告
- 多语言支持
- 可定制的报告模板
- 智能摘要生成

## 项目结构
```
data_insight/
├── core/                    # 核心功能模块
│   ├── metric_analyzer.py   # 指标分析器
│   ├── chart_analyzer.py    # 图表分析器
│   ├── reason_analyzer.py   # 原因分析器
│   └── text_generator.py    # 文本生成器
├── examples/                # 示例代码
│   ├── using_metric_analyzer.py
│   ├── using_chart_analyzer.py
│   └── using_reason_analyzer.py
└── tests/                   # 单元测试
    ├── test_metric_analyzer.py
    ├── test_chart_analyzer.py
    └── test_reason_analyzer.py
```

## 开发进度

### 已完成功能
1. 指标分析器
   - [x] 基础指标计算
   - [x] 趋势分析
   - [x] 异常检测
   - [x] 多维度指标对比

2. 图表分析器
   - [x] 基础图表生成
   - [x] 智能图表解读
   - [x] 异常点标注
   - [x] 多图表类型支持

3. 智能原因分析
   - [x] 基于规则的原因分析
   - [x] 多维度指标关联分析
   - [x] 异常值原因分析
   - [x] 季节性变化原因分析
   - [x] 置信度评估
   - [x] 自然语言解读生成

4. 文本生成器
   - [x] 基础文本生成
   - [x] 多语言支持
   - [x] 报告模板

### 待开发功能
1. 高级分析功能
   - [ ] 预测分析
   - [ ] 归因分析
   - [ ] 根因分析
   - [ ] 智能建议生成

2. API接口
   - [ ] RESTful API
   - [ ] WebSocket实时分析
   - [ ] 批量处理接口
   - [ ] 异步任务处理

3. 系统优化
   - [ ] 性能优化
   - [ ] 内存优化
   - [ ] 并发处理
   - [ ] 缓存机制

## 使用示例

### 1. 指标分析
```python
from data_insight.core.metric_analyzer import MetricAnalyzer

analyzer = MetricAnalyzer()
result = analyzer.analyze({
    "name": "销售额",
    "value": 1000000,
    "previous_value": 800000,
    "unit": "元"
})
```

### 2. 图表分析
```python
from data_insight.core.chart_analyzer import ChartAnalyzer

analyzer = ChartAnalyzer()
result = analyzer.analyze({
    "type": "line",
    "data": [...],
    "time_periods": [...]
})
```

### 3. 原因分析
```python
from data_insight.core.reason_analyzer import ReasonAnalyzer

analyzer = ReasonAnalyzer()
result = analyzer.analyze({
    "基本信息": {...},
    "变化分析": {...},
    "相关指标": [...]
})
```

### 4. 文本生成
```python
from data_insight.core.text_generator import TextGenerator

generator = TextGenerator()
text = generator.generate("metric_analysis", {
    "指标名称": "销售额",
    "当前值": 1000000,
    "变化率": 0.25
})
```

## 开发规范

### 代码规范
1. 遵循PEP 8规范
2. 使用类型注解
3. 编写详细的文档字符串
4. 保持代码简洁清晰

### 测试规范
1. 编写单元测试
2. 测试覆盖率要求
3. 边界条件测试
4. 异常情况处理

### 文档规范
1. 及时更新文档
2. 编写使用示例
3. 记录API变更
4. 维护更新日志

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 许可证
MIT License 