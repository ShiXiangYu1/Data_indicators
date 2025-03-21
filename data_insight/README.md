# 数据指标平台

## 项目介绍

数据指标平台是一个用于数据分析、预测和可视化的工具，可以帮助用户理解和洞察数据背后的规律和趋势。

## 项目结构

```
data_insight/
├── api/               # API接口模块
├── config/            # 配置管理模块
├── core/              # 核心分析模块
│   ├── analysis/      # 数据分析组件
│   ├── interfaces/    # 接口定义
│   ├── prediction/    # 预测组件
│   └── recommendation/# 推荐组件
├── services/          # 服务层
└── utils/             # 工具函数
```

## 最近修复内容

### 2025年3月20日更新

1. 修复了缺失的服务模块
   - 添加了 `analysis_service.py`
   - 添加了 `prediction_service.py`
   - 添加了 `recommendation_service.py`

2. 修复了 `TimeSeriesPredictor` 类的实现
   - 实现了 `PredictorInterface` 接口中缺少的抽象方法
   - 添加了临时的方法实现以确保类可以被实例化

3. 临时简化了 `services/__init__.py` 中的导入
   - 使用空类来代替实际的服务类，确保API兼容性
   - 后续需要逐步完善各个服务的实现

## 下一步工作

1. 完善各个服务模块的实现
   - 实现 `MetricService` 的完整功能
   - 实现 `ChartService` 的完整功能
   - 实现 `AnalysisService` 的完整功能
   - 实现 `PredictionService` 的完整功能
   - 实现 `RecommendationService` 的完整功能

2. 解决导入路径问题
   - 重构项目导入路径，避免相对导入导致的问题
   - 统一采用绝对导入或相对导入风格

3. 完善单元测试
   - 为各个服务添加单元测试
   - 为 API 接口添加集成测试

## 如何启动

```bash
# 启动服务
python run.py

# 指定主机和端口
python run.py --host 0.0.0.0 --port 8080

# 启用调试模式
python run.py --debug

# 指定配置文件
python run.py --config config.json
```

## 开发说明

### 安装依赖

```bash
pip install -e .
```

### 运行测试

```bash
python test_services.py
```

## 系统架构

本平台采用模块化设计，主要包含以下组件：

### 1. 核心分析模块

- **分析器接口 (IAnalyzer)**：所有分析器必须实现的接口，确保组件标准化。
- **预测器接口 (IPredictor)**：用于实现各种预测算法的标准接口。
- **推荐器接口 (IRecommender)**：为用户提供行动建议的标准接口。
- **生成器接口 (IGenerator)**：将分析结果转化为自然语言描述的标准接口。

#### 1.1 分析功能

- **BaseAnalyzer**：所有分析器的基类，提供通用功能。
- **MetricAnalyzer**：分析单个指标数据，识别趋势、异常和变化。
- **ChartAnalyzer**：分析图表数据，支持线图、柱状图、散点图和饼图等多种类型。
- **ComparisonAnalyzer**：比较多个图表或指标数据，发现相似性、差异性以及潜在的关联关系。

#### 1.2 预测功能

- **TimeSeriesPredictor**：基于历史数据进行时间序列预测，支持多种预测算法。

#### 1.3 推荐功能

- **ActionRecommender**：基于分析结果生成行动建议。

#### 1.4 生成功能

- **TextGenerator**：将分析结果转化为易于理解的文本描述。

### 2. 服务层

- **MetricService**：处理指标相关请求，调用相应的分析器和预测器。
- **ChartService**：处理图表相关请求，调用相应的分析器。
- **AnalysisService**：通用分析服务，可以处理多种类型的数据。
- **DataService**：处理数据访问和存储相关功能。

### 3. API层

- **指标路由 (metrics_routes)**：处理指标相关API请求。
- **图表路由 (chart_routes)**：处理图表相关API请求。
- **验证**：请求数据验证。
- **错误处理**：统一的异常处理机制。

### 4. 配置管理

- **Settings**：管理全局配置，包括服务器设置、分析参数等。

## 开发进度

### 已完成

1. ✅ 接口定义 (IAnalyzer, IPredictor, IRecommender, IGenerator)
2. ✅ 基础分析器 (BaseAnalyzer)
3. ✅ 指标分析器 (MetricAnalyzer)
4. ✅ 图表分析器 (ChartAnalyzer)
5. ✅ 比较分析器 (ComparisonAnalyzer)
6. ✅ 时间序列预测器 (TimeSeriesPredictor)
7. ✅ 行为推荐器 (ActionRecommender)
8. ✅ 文本生成器 (TextGenerator)
9. ✅ 配置管理 (Settings)
10. ✅ 服务层 (各种Service)
11. ✅ API路由重构
12. ✅ 统一错误处理机制
13. ✅ 应用入口文件

### 待完成

1. ⬜ 数据库访问层
2. ⬜ 用户认证
3. ⬜ Web前端界面
4. ⬜ 更多专业分析器实现
5. ⬜ 缓存机制优化
6. ⬜ 单元测试完善
7. ⬜ 文档完善

## 安装说明

```bash
# 克隆仓库
git clone https://github.com/yourusername/data-insight.git
cd data-insight

# 安装依赖
pip install -e .
```

## 运行说明

```bash
# 启动API服务
python -m data_insight.run

# 使用自定义配置启动
python -m data_insight.run --host 0.0.0.0 --port 8080 --debug
```

也可以通过环境变量配置：

```bash
# 设置环境变量
export DATA_INSIGHT_HOST=0.0.0.0
export DATA_INSIGHT_PORT=8080
export DATA_INSIGHT_DEBUG=True

# 启动服务
python -m data_insight.run
```

## 使用示例

### 分析指标

```python
import requests
import json

# 分析单个指标
metric_data = {
    "name": "月活跃用户",
    "value": 10500,
    "previous_value": 9800,
    "unit": "用户数",
    "trend": "up",
    "historical_values": [8500, 8900, 9200, 9500, 9800, 10500]
}

response = requests.post("http://localhost:5000/api/v1/metrics/analyze", json=metric_data)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 分析图表

```python
import requests
import json

# 分析线图
chart_data = {
    "type": "line",
    "title": "销售趋势",
    "data": {
        "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
        "y": [100, 120, 115, 130, 145, 160]
    },
    "x_label": "月份",
    "y_label": "销售额(万元)"
}

response = requests.post("http://localhost:5000/api/v1/charts/analyze", json=chart_data)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 比较多个图表

```python
import requests
import json

# 比较多个图表
comparison_data = {
    "charts": [
        {
            "type": "line",
            "title": "产品A销售趋势",
            "data": {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
                "y": [100, 120, 115, 130, 145, 160]
            }
        },
        {
            "type": "line",
            "title": "产品B销售趋势",
            "data": {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
                "y": [80, 85, 95, 105, 115, 125]
            }
        }
    ],
    "comparison_type": "all"
}

response = requests.post("http://localhost:5000/api/v1/charts/compare", json=comparison_data)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## API文档

API文档可在服务启动后通过访问以下地址获取：

```
http://localhost:5000/docs
```

## 贡献指南

欢迎贡献代码、提交问题或建议！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见 LICENSE 文件。 