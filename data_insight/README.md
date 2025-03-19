# 数据指标分析系统

数据指标分析API，提供趋势分析、原因分析、归因分析、相关性分析、预测分析和指标分析等功能。

## 项目概述

本项目是一个数据分析平台，提供API服务和Web界面，支持多种数据分析功能，包括但不限于：

- **趋势分析**：识别时间序列数据中的趋势模式，包括上升、下降、周期性和季节性趋势
- **归因分析**：分析影响指标变化的因素并量化每个因素的贡献率
- **根因分析**：深入挖掘指标变化背后的根本原因，构建因果关系网络
- **相关性分析**：分析指标间的关系和依赖性，识别强相关、弱相关和无相关的指标对
- **预测分析**：基于历史数据预测未来趋势，支持时间序列预测和异常检测
- **指标分析**：全面分析单个指标的特征和变化，并比较多个指标之间的差异和关系
- **图表分析**：自动生成适合数据特征的可视化图表，支持多种图表类型和自定义选项
- **智能建议**：基于分析结果自动生成行动建议，帮助用户从数据洞察转化为实际行动
- **结果导出**：支持将分析结果导出为多种格式，包括CSV、Excel、JSON和PDF

该项目采用Python FastAPI框架构建，提供RESTful API接口和用户友好的Web界面，支持JSON格式的数据交换，为数据分析提供全方位解决方案。

## 系统架构

系统采用模块化设计，主要包括以下组件：

### 核心组件
- **核心分析引擎**：提供各种数据分析算法实现
  - 趋势分析器
  - 归因分析器
  - 根因分析器
  - 相关性分析器
  - 预测分析器
  - 指标分析器
  - 图表分析器
  - 智能建议生成器

### API层
- **RESTful API**：提供HTTP接口，处理客户端请求
  - 请求验证
  - 访问控制
  - 速率限制
  - API文档

### 服务层
- **任务管理**：处理异步分析任务
- **缓存管理**：优化系统性能，减少重复计算
- **数据预处理**：数据清洗、转换和标准化

### 性能与监控
- **性能优化**：内存优化、并行处理、数据分块处理
- **系统监控**：提供Prometheus格式的指标导出

### 部署
- **Docker支持**：容器化部署
- **Kubernetes配置**：云原生部署支持
  - 基础配置
  - 环境覆盖（生产、测试、开发）
  - 水平扩展

## 环境要求

- Python 3.9+
- Redis (可选，用于缓存)
- Docker (可选，用于容器化部署)
- Kubernetes (可选，用于云原生部署)

## 安装方法

### 本地开发环境

1. 克隆项目仓库
```bash
git clone https://github.com/yourusername/data-insight.git
cd data-insight
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
uvicorn data_insight.app:app --reload
```

### Docker部署

1. 构建Docker镜像
```bash
docker build -t data-insight:latest .
```

2. 运行容器
```bash
docker run -p 8000:8000 data-insight:latest
```

### Kubernetes部署

详见[部署文档](./docs/deployment.md)

## 使用示例

### 趋势分析示例

```python
import requests
import json

# API请求示例
url = "http://localhost:8000/api/v1/trend/analyze"
payload = {
    "metric_name": "用户增长率",
    "values": [1.2, 1.5, 1.7, 2.0, 2.3, 2.7, 3.1, 3.5, 3.8, 4.2],
    "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", 
                  "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10"],
    "trend_method": "linear"
}
headers = {
    "Content-Type": "application/json",
    "X-API-Token": "your_api_token"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)
result = response.json()
print(json.dumps(result, indent=2))
```

## 相关文档

- [用户手册](./docs/user_manual.md) - 系统功能和使用方法详解
- [API文档](./docs/api/index.md) - API接口详细说明
- [开发文档](./docs/development.md) - 开发指南和贡献方法
- [部署文档](./docs/deployment.md) - 部署指南和环境配置

## 贡献指南

欢迎对项目提出建议或贡献代码。请遵循以下步骤：

1. Fork仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 联系方式

项目负责人 - [your-email@example.com](mailto:your-email@example.com)

项目链接: [https://github.com/yourusername/data-insight](https://github.com/yourusername/data-insight) 