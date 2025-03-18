#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
原因分析器使用示例

演示如何使用ReasonAnalyzer进行指标变化的原因分析。
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.core.reason_analyzer import ReasonAnalyzer
from data_insight.core.text_generator import TextGenerator


def load_sample_data(file_path):
    """
    加载示例数据
    
    参数:
        file_path (str): 数据文件路径
        
    返回:
        dict: 加载的数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_sales_reason():
    """
    分析销售额变化原因
    """
    print("\n=== 销售额变化原因分析 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "销售额",
            "当前值": 1250000,
            "上一期值": 1000000,
            "单位": "元",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月"
        },
        "变化分析": {
            "变化量": 250000,
            "变化率": 0.25,
            "变化类别": "大幅增长",
            "变化方向": "增加"
        },
        "异常分析": {
            "是否异常": False,
            "异常程度": 0.0,
            "是否高于正常范围": None
        },
        "相关指标": [
            {
                "name": "营销费用",
                "value": 300000,
                "previous_value": 250000,
                "unit": "元"
            },
            {
                "name": "客户数量",
                "value": 10000,
                "previous_value": 8000,
                "unit": "个"
            },
            {
                "name": "客单价",
                "value": 125,
                "previous_value": 125,
                "unit": "元"
            }
        ],
        "历史数据": {
            "values": [920000, 980000, 950000, 1010000, 1000000, 1250000],
            "time_periods": ["2023年2月", "2023年3月", "2023年4月", 
                           "2023年5月", "2023年6月", "2023年7月"]
        }
    }
    
    # 创建分析器和生成器
    analyzer = ReasonAnalyzer(use_llm=False)  # 示例中不使用LLM
    generator = TextGenerator()
    
    # 分析原因
    result = analyzer.analyze(data)
    
    # 打印分析结果
    print("原因分析结果:")
    print(f"置信度: {result['原因分析']['置信度']}")
    print("\n可能原因:")
    for i, reason in enumerate(result['原因分析']['可能原因'], 1):
        print(f"{i}. {reason}")
    
    # 生成解读文本
    insight_text = generator.generate("reason_analysis", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": result['原因分析']['可能原因'],
        "置信度": result['原因分析']['置信度']
    })
    
    print("\n解读文本:")
    print(insight_text)


def analyze_cost_reason():
    """
    分析成本变化原因
    """
    print("\n=== 成本变化原因分析 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "运营成本",
            "当前值": 800000,
            "上一期值": 700000,
            "单位": "元",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月"
        },
        "变化分析": {
            "变化量": 100000,
            "变化率": 0.1429,
            "变化类别": "增长",
            "变化方向": "增加"
        },
        "异常分析": {
            "是否异常": False,
            "异常程度": 0.0,
            "是否高于正常范围": None
        },
        "相关指标": [
            {
                "name": "人工成本",
                "value": 400000,
                "previous_value": 350000,
                "unit": "元"
            },
            {
                "name": "原材料成本",
                "value": 300000,
                "previous_value": 250000,
                "unit": "元"
            },
            {
                "name": "其他费用",
                "value": 100000,
                "previous_value": 100000,
                "unit": "元"
            }
        ],
        "历史数据": {
            "values": [650000, 670000, 680000, 690000, 700000, 800000],
            "time_periods": ["2023年2月", "2023年3月", "2023年4月", 
                           "2023年5月", "2023年6月", "2023年7月"]
        }
    }
    
    # 创建分析器和生成器
    analyzer = ReasonAnalyzer(use_llm=False)
    generator = TextGenerator()
    
    # 分析原因
    result = analyzer.analyze(data)
    
    # 打印分析结果
    print("原因分析结果:")
    print(f"置信度: {result['原因分析']['置信度']}")
    print("\n可能原因:")
    for i, reason in enumerate(result['原因分析']['可能原因'], 1):
        print(f"{i}. {reason}")
    
    # 生成解读文本
    insight_text = generator.generate("reason_analysis", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": result['原因分析']['可能原因'],
        "置信度": result['原因分析']['置信度']
    })
    
    print("\n解读文本:")
    print(insight_text)


def analyze_anomaly_reason():
    """
    分析异常值原因
    """
    print("\n=== 异常值原因分析 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "客户投诉率",
            "当前值": 0.0256,
            "上一期值": 0.0198,
            "单位": "",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月"
        },
        "变化分析": {
            "变化量": 0.0058,
            "变化率": 0.2929,
            "变化类别": "大幅增长",
            "变化方向": "增加"
        },
        "异常分析": {
            "是否异常": True,
            "异常程度": 2.5,
            "是否高于正常范围": True
        },
        "相关指标": [
            {
                "name": "产品质量合格率",
                "value": 0.985,
                "previous_value": 0.992,
                "unit": ""
            },
            {
                "name": "物流准时率",
                "value": 0.95,
                "previous_value": 0.98,
                "unit": ""
            },
            {
                "name": "客服响应时间",
                "value": 120,
                "previous_value": 90,
                "unit": "秒"
            }
        ],
        "历史数据": {
            "values": [0.0185, 0.0174, 0.0182, 0.0191, 0.0198, 0.0256],
            "time_periods": ["2023年2月", "2023年3月", "2023年4月", 
                           "2023年5月", "2023年6月", "2023年7月"]
        }
    }
    
    # 创建分析器和生成器
    analyzer = ReasonAnalyzer(use_llm=False)
    generator = TextGenerator()
    
    # 分析原因
    result = analyzer.analyze(data)
    
    # 打印分析结果
    print("原因分析结果:")
    print(f"置信度: {result['原因分析']['置信度']}")
    print("\n可能原因:")
    for i, reason in enumerate(result['原因分析']['可能原因'], 1):
        print(f"{i}. {reason}")
    
    # 生成解读文本
    insight_text = generator.generate("reason_analysis", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": result['原因分析']['可能原因'],
        "置信度": result['原因分析']['置信度']
    })
    
    print("\n解读文本:")
    print(insight_text)


def analyze_seasonal_reason():
    """
    分析季节性变化原因
    """
    print("\n=== 季节性变化原因分析 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "空调销量",
            "当前值": 5000,
            "上一期值": 3000,
            "单位": "台",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月"
        },
        "变化分析": {
            "变化量": 2000,
            "变化率": 0.6667,
            "变化类别": "大幅增长",
            "变化方向": "增加"
        },
        "异常分析": {
            "是否异常": False,
            "异常程度": 0.0,
            "是否高于正常范围": None
        },
        "相关指标": [
            {
                "name": "平均气温",
                "value": 35,
                "previous_value": 28,
                "unit": "℃"
            },
            {
                "name": "促销力度",
                "value": 0.8,
                "previous_value": 0.6,
                "unit": ""
            },
            {
                "name": "库存水平",
                "value": 8000,
                "previous_value": 6000,
                "unit": "台"
            }
        ],
        "历史数据": {
            "values": [1000, 1500, 2000, 2500, 3000, 5000],
            "time_periods": ["2023年2月", "2023年3月", "2023年4月", 
                           "2023年5月", "2023年6月", "2023年7月"]
        }
    }
    
    # 创建分析器和生成器
    analyzer = ReasonAnalyzer(use_llm=False)
    generator = TextGenerator()
    
    # 分析原因
    result = analyzer.analyze(data)
    
    # 打印分析结果
    print("原因分析结果:")
    print(f"置信度: {result['原因分析']['置信度']}")
    print("\n可能原因:")
    for i, reason in enumerate(result['原因分析']['可能原因'], 1):
        print(f"{i}. {reason}")
    
    # 生成解读文本
    insight_text = generator.generate("reason_analysis", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": result['原因分析']['可能原因'],
        "置信度": result['原因分析']['置信度']
    })
    
    print("\n解读文本:")
    print(insight_text)


def main():
    """主函数"""
    # 分析各种场景
    analyze_sales_reason()
    analyze_cost_reason()
    analyze_anomaly_reason()
    analyze_seasonal_reason()


if __name__ == "__main__":
    main() 