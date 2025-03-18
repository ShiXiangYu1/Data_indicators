"""
智能建议生成器使用示例
===================

本示例展示如何使用SuggestionGenerator类生成智能建议。
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_insight.core.suggestion_generator import SuggestionGenerator


def load_sample_data(file_path):
    """加载示例数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_sales_analysis_data():
    """生成销售分析数据"""
    # 生成12个月的销售数据
    dates = pd.date_range(start='2023-01-01', periods=12, freq='M')
    sales = np.random.normal(1000, 100, 12)
    sales = np.maximum(sales, 0)  # 确保销售额为正
    
    # 添加趋势和季节性
    trend = np.linspace(0, 200, 12)
    seasonality = 100 * np.sin(np.linspace(0, 2*np.pi, 12))
    sales += trend + seasonality
    
    # 生成影响因素数据
    ad_spend = np.random.normal(200, 50, 12)
    ad_spend = np.maximum(ad_spend, 0)
    
    price = np.random.normal(100, 10, 12)
    price = np.maximum(price, 50)
    
    competitor_price = np.random.normal(90, 10, 12)
    competitor_price = np.maximum(competitor_price, 40)
    
    # 构建分析结果
    analysis_data = {
        "metric_analysis": {
            "基本信息": {
                "指标名称": "销售额",
                "时间范围": "2023年1月-12月"
            },
            "变化分析": {
                "变化类别": "显著上升" if sales[-1] > sales[0] else "显著下降",
                "变化率": (sales[-1] - sales[0]) / sales[0]
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0
            }
        },
        "chart_analysis": {
            "基本信息": {
                "图表标题": "销售额趋势分析"
            },
            "趋势分析": {
                "趋势类型": "上升" if sales[-1] > sales[0] else "下降",
                "趋势强度": abs((sales[-1] - sales[0]) / sales[0])
            },
            "异常点分析": []
        },
        "attribution_analysis": {
            "目标指标": "销售额",
            "因素贡献": [
                {
                    "因素名称": "广告支出",
                    "贡献度": 0.4,
                    "影响方向": "正向"
                },
                {
                    "因素名称": "价格调整",
                    "贡献度": 0.3,
                    "影响方向": "负向"
                },
                {
                    "因素名称": "竞争对手价格",
                    "贡献度": 0.3,
                    "影响方向": "负向"
                }
            ]
        },
        "root_cause_analysis": {
            "目标指标": "销售额",
            "根因列表": [
                {
                    "根因描述": "市场竞争加剧",
                    "根因类型": "外部因素",
                    "影响程度": 0.6
                },
                {
                    "根因描述": "产品竞争力不足",
                    "根因类型": "内部因素",
                    "影响程度": 0.4
                }
            ]
        },
        "prediction_analysis": {
            "基本信息": {
                "指标名称": "销售额"
            },
            "预测结果": {
                "预测值": list(sales[-5:])  # 使用最后5个月作为预测值
            },
            "异常预测": {
                "风险等级": "中"
            }
        }
    }
    
    return analysis_data


def generate_conversion_rate_analysis_data():
    """生成转化率分析数据"""
    # 生成12个月的转化率数据
    dates = pd.date_range(start='2023-01-01', periods=12, freq='M')
    conversion_rate = np.random.normal(0.05, 0.01, 12)
    conversion_rate = np.clip(conversion_rate, 0, 0.1)  # 确保转化率在合理范围内
    
    # 生成影响因素数据
    page_load_time = np.random.normal(2, 0.5, 12)
    page_load_time = np.maximum(page_load_time, 0.5)
    
    ad_quality = np.random.normal(0.7, 0.1, 12)
    ad_quality = np.clip(ad_quality, 0, 1)
    
    # 构建分析结果
    analysis_data = {
        "metric_analysis": {
            "基本信息": {
                "指标名称": "转化率",
                "时间范围": "2023年1月-12月"
            },
            "变化分析": {
                "变化类别": "显著上升" if conversion_rate[-1] > conversion_rate[0] else "显著下降",
                "变化率": (conversion_rate[-1] - conversion_rate[0]) / conversion_rate[0]
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0
            }
        },
        "chart_analysis": {
            "基本信息": {
                "图表标题": "转化率趋势分析"
            },
            "趋势分析": {
                "趋势类型": "上升" if conversion_rate[-1] > conversion_rate[0] else "下降",
                "趋势强度": abs((conversion_rate[-1] - conversion_rate[0]) / conversion_rate[0])
            },
            "异常点分析": []
        },
        "attribution_analysis": {
            "目标指标": "转化率",
            "因素贡献": [
                {
                    "因素名称": "页面加载时间",
                    "贡献度": 0.4,
                    "影响方向": "负向"
                },
                {
                    "因素名称": "广告质量",
                    "贡献度": 0.6,
                    "影响方向": "正向"
                }
            ]
        },
        "root_cause_analysis": {
            "目标指标": "转化率",
            "根因列表": [
                {
                    "根因描述": "网站性能问题",
                    "根因类型": "技术因素",
                    "影响程度": 0.7
                },
                {
                    "根因描述": "广告投放策略不当",
                    "根因类型": "运营因素",
                    "影响程度": 0.3
                }
            ]
        },
        "prediction_analysis": {
            "基本信息": {
                "指标名称": "转化率"
            },
            "预测结果": {
                "预测值": list(conversion_rate[-5:])  # 使用最后5个月作为预测值
            },
            "异常预测": {
                "风险等级": "低"
            }
        }
    }
    
    return analysis_data


def generate_cost_analysis_data():
    """生成成本分析数据"""
    # 生成12个月的成本数据
    dates = pd.date_range(start='2023-01-01', periods=12, freq='M')
    cost = np.random.normal(800, 100, 12)
    cost = np.maximum(cost, 0)  # 确保成本为正
    
    # 生成影响因素数据
    raw_material = np.random.normal(400, 50, 12)
    raw_material = np.maximum(raw_material, 0)
    
    labor = np.random.normal(300, 30, 12)
    labor = np.maximum(labor, 0)
    
    energy = np.random.normal(100, 20, 12)
    energy = np.maximum(energy, 0)
    
    # 构建分析结果
    analysis_data = {
        "metric_analysis": {
            "基本信息": {
                "指标名称": "总成本",
                "时间范围": "2023年1月-12月"
            },
            "变化分析": {
                "变化类别": "显著上升" if cost[-1] > cost[0] else "显著下降",
                "变化率": (cost[-1] - cost[0]) / cost[0]
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0
            }
        },
        "chart_analysis": {
            "基本信息": {
                "图表标题": "成本趋势分析"
            },
            "趋势分析": {
                "趋势类型": "上升" if cost[-1] > cost[0] else "下降",
                "趋势强度": abs((cost[-1] - cost[0]) / cost[0])
            },
            "异常点分析": []
        },
        "attribution_analysis": {
            "目标指标": "总成本",
            "因素贡献": [
                {
                    "因素名称": "原材料成本",
                    "贡献度": 0.5,
                    "影响方向": "正向"
                },
                {
                    "因素名称": "人工成本",
                    "贡献度": 0.3,
                    "影响方向": "正向"
                },
                {
                    "因素名称": "能源成本",
                    "贡献度": 0.2,
                    "影响方向": "正向"
                }
            ]
        },
        "root_cause_analysis": {
            "目标指标": "总成本",
            "根因列表": [
                {
                    "根因描述": "原材料价格上涨",
                    "根因类型": "外部因素",
                    "影响程度": 0.6
                },
                {
                    "根因描述": "生产效率低下",
                    "根因类型": "内部因素",
                    "影响程度": 0.4
                }
            ]
        },
        "prediction_analysis": {
            "基本信息": {
                "指标名称": "总成本"
            },
            "预测结果": {
                "预测值": list(cost[-5:])  # 使用最后5个月作为预测值
            },
            "异常预测": {
                "风险等级": "高"
            }
        }
    }
    
    return analysis_data


def analyze_sales_suggestions():
    """分析销售数据并生成建议"""
    # 生成销售分析数据
    analysis_data = generate_sales_analysis_data()
    
    # 创建建议生成器
    generator = SuggestionGenerator()
    
    # 生成建议
    result = generator.analyze(analysis_data)
    
    # 打印结果
    print("\n=== 销售分析建议 ===")
    print(f"建议数量: {result['建议数量']}")
    print(f"高优先级建议数: {result['高优先级建议数']}")
    print(f"总体效果: {result['总体效果']:.2f}")
    print(f"效果评估: {result['效果评估']}")
    
    print("\n建议列表:")
    for i, suggestion in enumerate(result['建议列表'], 1):
        print(f"\n{i}. {suggestion['建议内容']}")
        print(f"   优先级: {suggestion['优先级']}")
        print(f"   置信度: {suggestion['置信度']:.2f}")
        print(f"   预期效果: {suggestion['预期效果']:.2f}")
        print(f"   建议类型: {suggestion['建议类型']}")


def analyze_conversion_rate_suggestions():
    """分析转化率数据并生成建议"""
    # 生成转化率分析数据
    analysis_data = generate_conversion_rate_analysis_data()
    
    # 创建建议生成器
    generator = SuggestionGenerator()
    
    # 生成建议
    result = generator.analyze(analysis_data)
    
    # 打印结果
    print("\n=== 转化率分析建议 ===")
    print(f"建议数量: {result['建议数量']}")
    print(f"高优先级建议数: {result['高优先级建议数']}")
    print(f"总体效果: {result['总体效果']:.2f}")
    print(f"效果评估: {result['效果评估']}")
    
    print("\n建议列表:")
    for i, suggestion in enumerate(result['建议列表'], 1):
        print(f"\n{i}. {suggestion['建议内容']}")
        print(f"   优先级: {suggestion['优先级']}")
        print(f"   置信度: {suggestion['置信度']:.2f}")
        print(f"   预期效果: {suggestion['预期效果']:.2f}")
        print(f"   建议类型: {suggestion['建议类型']}")


def analyze_cost_suggestions():
    """分析成本数据并生成建议"""
    # 生成成本分析数据
    analysis_data = generate_cost_analysis_data()
    
    # 创建建议生成器
    generator = SuggestionGenerator()
    
    # 生成建议
    result = generator.analyze(analysis_data)
    
    # 打印结果
    print("\n=== 成本分析建议 ===")
    print(f"建议数量: {result['建议数量']}")
    print(f"高优先级建议数: {result['高优先级建议数']}")
    print(f"总体效果: {result['总体效果']:.2f}")
    print(f"效果评估: {result['效果评估']}")
    
    print("\n建议列表:")
    for i, suggestion in enumerate(result['建议列表'], 1):
        print(f"\n{i}. {suggestion['建议内容']}")
        print(f"   优先级: {suggestion['优先级']}")
        print(f"   置信度: {suggestion['置信度']:.2f}")
        print(f"   预期效果: {suggestion['预期效果']:.2f}")
        print(f"   建议类型: {suggestion['建议类型']}")


def main():
    """主函数"""
    # 分析销售数据
    analyze_sales_suggestions()
    
    # 分析转化率数据
    analyze_conversion_rate_suggestions()
    
    # 分析成本数据
    analyze_cost_suggestions()


if __name__ == "__main__":
    main() 