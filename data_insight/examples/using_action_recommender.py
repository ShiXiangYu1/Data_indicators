#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
行动建议生成器使用示例

演示如何使用ActionRecommender为各种指标分析结果生成行动建议。
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.core.metric_analyzer import MetricAnalyzer
from data_insight.core.reason_analyzer import ReasonAnalyzer
from data_insight.core.action_recommender import ActionRecommender
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


def recommend_actions_for_sales():
    """
    为销售额指标生成行动建议
    """
    print("\n=== 销售额增长的行动建议 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "月度销售额",
            "当前值": 1250000,
            "上一期值": 1000000,
            "单位": "元",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月",
            "正向增长是否为好": True
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
        "原因分析": {
            "可能原因": [
                "营销活动效果显著，带来更多客户流量和订单量",
                "新产品线的推出吸引了新客户群体",
                "竞争对手产品供应短缺，导致客户流向本公司"
            ],
            "置信度": "高",
            "分析方法": "规则匹配"
        },
        "相关指标": [
            {
                "name": "营销费用",
                "value": 300000,
                "previous_value": 250000,
                "unit": "元",
                "correlation": 0.85
            },
            {
                "name": "客户数量",
                "value": 10000,
                "previous_value": 8000,
                "unit": "个",
                "correlation": 0.78
            }
        ]
    }
    
    # 创建行动建议生成器
    recommender = ActionRecommender(use_llm=False)  # 示例中不使用LLM
    
    # 生成行动建议
    result = recommender.analyze(data)
    
    # 打印行动建议
    print(f"针对指标: {result['行动建议']['针对指标']}")
    print(f"建议数量: {result['行动建议']['建议数量']}")
    print(f"基于原因分析: {'是' if result['行动建议']['基于原因分析'] else '否'}")
    
    print("\n行动建议:")
    for i, (action, priority) in enumerate(zip(result['行动建议']['建议列表'], result['行动建议']['优先级']), 1):
        print(f"{i}. [{priority}] {action}")

    # 使用文本生成器生成综合洞察
    generator = TextGenerator()
    insight_text = generator.generate("action_recommendation", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": data["原因分析"]["可能原因"] if "原因分析" in data else [],
        "建议列表": result['行动建议']['建议列表'][:3]  # 取前三条最重要的建议
    })
    
    print("\n综合洞察:")
    print(insight_text)


def recommend_actions_for_cost():
    """
    为成本类指标生成行动建议
    """
    print("\n=== 运营成本上升的行动建议 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "运营成本",
            "当前值": 800000,
            "上一期值": 700000,
            "单位": "元",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月",
            "正向增长是否为好": False
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
        "原因分析": {
            "可能原因": [
                "原材料价格上涨导致采购成本增加",
                "新增产能投入带来了短期成本增加",
                "人力成本随团队扩张而上升"
            ],
            "置信度": "中高",
            "分析方法": "规则匹配"
        }
    }
    
    # 创建行动建议生成器
    recommender = ActionRecommender(use_llm=False)
    
    # 生成行动建议
    result = recommender.analyze(data)
    
    # 打印行动建议
    print(f"针对指标: {result['行动建议']['针对指标']}")
    print(f"建议数量: {result['行动建议']['建议数量']}")
    print(f"基于原因分析: {'是' if result['行动建议']['基于原因分析'] else '否'}")
    
    print("\n行动建议:")
    for i, (action, priority) in enumerate(zip(result['行动建议']['建议列表'], result['行动建议']['优先级']), 1):
        print(f"{i}. [{priority}] {action}")
    
    # 使用文本生成器生成综合洞察
    generator = TextGenerator()
    insight_text = generator.generate("action_recommendation", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": data["原因分析"]["可能原因"] if "原因分析" in data else [],
        "建议列表": result['行动建议']['建议列表'][:3]
    })
    
    print("\n综合洞察:")
    print(insight_text)


def recommend_actions_for_anomaly():
    """
    为异常指标生成行动建议
    """
    print("\n=== 客户投诉率异常上升的行动建议 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "客户投诉率",
            "当前值": 0.0256,
            "上一期值": 0.0198,
            "单位": "",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月",
            "正向增长是否为好": False
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
        "原因分析": {
            "可能原因": [
                "新版产品存在质量问题，导致用户体验下降",
                "客服响应速度变慢，无法及时解决客户问题",
                "配送延误问题增多，引起客户不满"
            ],
            "置信度": "高",
            "分析方法": "规则匹配 + 异常分析"
        }
    }
    
    # 创建行动建议生成器
    recommender = ActionRecommender(use_llm=False)
    
    # 生成行动建议
    result = recommender.analyze(data)
    
    # 打印行动建议
    print(f"针对指标: {result['行动建议']['针对指标']}")
    print(f"建议数量: {result['行动建议']['建议数量']}")
    print(f"基于原因分析: {'是' if result['行动建议']['基于原因分析'] else '否'}")
    
    print("\n行动建议:")
    for i, (action, priority) in enumerate(zip(result['行动建议']['建议列表'], result['行动建议']['优先级']), 1):
        print(f"{i}. [{priority}] {action}")
    
    # 使用文本生成器生成综合洞察
    generator = TextGenerator()
    insight_text = generator.generate("action_recommendation", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": data["原因分析"]["可能原因"] if "原因分析" in data else [],
        "建议列表": result['行动建议']['建议列表'][:3]
    })
    
    print("\n综合洞察:")
    print(insight_text)


def recommend_actions_for_positive_trend():
    """
    为正向趋势指标生成行动建议
    """
    print("\n=== 用户活跃度持续上升的行动建议 ===\n")
    
    # 准备测试数据
    data = {
        "基本信息": {
            "指标名称": "日活跃用户数",
            "当前值": 58500,
            "上一期值": 52000,
            "单位": "人",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月",
            "正向增长是否为好": True
        },
        "变化分析": {
            "变化量": 6500,
            "变化率": 0.125,
            "变化类别": "增长",
            "变化方向": "增加"
        },
        "异常分析": {
            "是否异常": False,
            "异常程度": 0.0,
            "是否高于正常范围": None
        },
        "趋势分析": {
            "趋势类型": "持续上升",
            "趋势强度": 0.92
        },
        "原因分析": {
            "可能原因": [
                "产品功能迭代优化，提升了用户体验",
                "社交分享功能带来的病毒式传播效应",
                "用户留存措施效果显著，老用户活跃度提升"
            ],
            "置信度": "高",
            "分析方法": "规则匹配 + 趋势分析"
        }
    }
    
    # 创建行动建议生成器
    recommender = ActionRecommender(use_llm=False)
    
    # 生成行动建议
    result = recommender.analyze(data)
    
    # 打印行动建议
    print(f"针对指标: {result['行动建议']['针对指标']}")
    print(f"建议数量: {result['行动建议']['建议数量']}")
    print(f"基于原因分析: {'是' if result['行动建议']['基于原因分析'] else '否'}")
    
    print("\n行动建议:")
    for i, (action, priority) in enumerate(zip(result['行动建议']['建议列表'], result['行动建议']['优先级']), 1):
        print(f"{i}. [{priority}] {action}")
    
    # 使用文本生成器生成综合洞察
    generator = TextGenerator()
    insight_text = generator.generate("action_recommendation", {
        "指标名称": data["基本信息"]["指标名称"],
        "当前值": data["基本信息"]["当前值"],
        "单位": data["基本信息"]["单位"],
        "变化率": data["变化分析"]["变化率"],
        "变化方向": data["变化分析"]["变化方向"],
        "原因列表": data["原因分析"]["可能原因"] if "原因分析" in data else [],
        "建议列表": result['行动建议']['建议列表'][:3]
    })
    
    print("\n综合洞察:")
    print(insight_text)


def complete_analysis_example():
    """
    完整的分析流程示例：指标分析→原因分析→行动建议
    """
    print("\n=== 完整分析流程示例 ===\n")
    
    # 准备原始指标数据
    metric_data = {
        "name": "转化率",
        "value": 0.0658,
        "previous_value": 0.0512,
        "unit": "",
        "time_period": "2023年7月",
        "previous_time_period": "2023年6月",
        "historical_values": [0.0485, 0.0492, 0.0501, 0.0508, 0.0512]
    }
    
    print("原始指标数据:")
    print(f"指标名称: {metric_data['name']}")
    print(f"当前值: {metric_data['value']}")
    print(f"上一期值: {metric_data['previous_value']}")
    print(f"历史数据: {metric_data['historical_values']}")
    
    # 第一步：指标分析
    print("\n步骤1: 指标分析")
    metric_analyzer = MetricAnalyzer()
    analysis_result = metric_analyzer.analyze(metric_data)
    
    # 打印指标分析结果
    print(f"变化量: {analysis_result['变化分析']['变化量']}")
    print(f"变化率: {analysis_result['变化分析']['变化率']:.2%}")
    print(f"变化类别: {analysis_result['变化分析']['变化类别']}")
    print(f"是否异常: {analysis_result['异常分析']['是否异常']}")
    
    # 添加相关指标(用于原因分析)
    analysis_result["相关指标"] = [
        {
            "name": "广告投放量",
            "value": 250000,
            "previous_value": 200000,
            "unit": "元",
            "correlation": 0.82
        },
        {
            "name": "网站访问量",
            "value": 180000,
            "previous_value": 150000,
            "unit": "次",
            "correlation": 0.75
        },
        {
            "name": "页面加载速度",
            "value": 1.8,
            "previous_value": 2.5,
            "unit": "秒",
            "correlation": -0.65
        }
    ]
    
    # 第二步：原因分析
    print("\n步骤2: 原因分析")
    reason_analyzer = ReasonAnalyzer(use_llm=False)
    reason_result = reason_analyzer.analyze(analysis_result)
    
    # 打印原因分析结果
    print("可能原因:")
    for i, reason in enumerate(reason_result["原因分析"]["可能原因"], 1):
        print(f"{i}. {reason}")
    print(f"置信度: {reason_result['原因分析']['置信度']}")
    
    # 合并结果(用于行动建议)
    combined_result = analysis_result.copy()
    combined_result["原因分析"] = reason_result["原因分析"]
    
    # 第三步：生成行动建议
    print("\n步骤3: 生成行动建议")
    action_recommender = ActionRecommender(use_llm=False)
    action_result = action_recommender.analyze(combined_result)
    
    # 打印行动建议
    print("行动建议:")
    for i, (action, priority) in enumerate(zip(action_result['行动建议']['建议列表'], action_result['行动建议']['优先级']), 1):
        print(f"{i}. [{priority}] {action}")
    
    # 生成综合洞察文本
    generator = TextGenerator()
    
    # 生成变化分析文本
    change_text = generator.generate("metric_analysis", {
        "指标名称": analysis_result["基本信息"]["指标名称"],
        "当前值": analysis_result["基本信息"]["当前值"],
        "上一期值": analysis_result["基本信息"]["上一期值"],
        "单位": analysis_result["基本信息"]["单位"],
        "变化量": analysis_result["变化分析"]["变化量"],
        "变化率": analysis_result["变化分析"]["变化率"],
        "变化类别": analysis_result["变化分析"]["变化类别"],
        "是否异常": analysis_result["异常分析"]["是否异常"]
    })
    
    # 生成原因分析文本
    reason_text = generator.generate("reason_analysis", {
        "指标名称": analysis_result["基本信息"]["指标名称"],
        "当前值": analysis_result["基本信息"]["当前值"],
        "单位": analysis_result["基本信息"]["单位"],
        "变化率": analysis_result["变化分析"]["变化率"],
        "变化方向": analysis_result["变化分析"]["变化方向"],
        "原因列表": reason_result["原因分析"]["可能原因"],
        "置信度": reason_result["原因分析"]["置信度"]
    })
    
    # 生成行动建议文本
    action_text = generator.generate("action_recommendation", {
        "指标名称": analysis_result["基本信息"]["指标名称"],
        "当前值": analysis_result["基本信息"]["当前值"],
        "单位": analysis_result["基本信息"]["单位"],
        "变化率": analysis_result["变化分析"]["变化率"],
        "变化方向": analysis_result["变化分析"]["变化方向"],
        "原因列表": reason_result["原因分析"]["可能原因"],
        "建议列表": action_result["行动建议"]["建议列表"][:3]
    })
    
    # 输出完整的洞察报告
    print("\n完整洞察报告:")
    print("=" * 50)
    print(f"【{analysis_result['基本信息']['指标名称']}指标分析报告】")
    print("\n【变化分析】")
    print(change_text)
    print("\n【原因分析】")
    print(reason_text)
    print("\n【行动建议】")
    print(action_text)
    print("=" * 50)


def main():
    """主函数"""
    print("===== 行动建议生成器示例 =====")
    print("演示如何使用ActionRecommender为不同场景生成行动建议")
    
    # 为不同场景生成行动建议
    recommend_actions_for_sales()
    recommend_actions_for_cost()
    recommend_actions_for_anomaly()
    recommend_actions_for_positive_trend()
    
    # 完整的分析流程示例
    complete_analysis_example()
    
    print("\n===== 示例结束 =====")


if __name__ == "__main__":
    main() 