#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用指标对比分析器示例

演示如何使用data_insight包分析多个指标之间的关系，生成对比、相关性和群组分析洞察。
"""

import json
import sys
from pathlib import Path
import random
import numpy as np
import matplotlib.pyplot as plt

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.core.metric_comparison_analyzer import MetricComparisonAnalyzer
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


def generate_correlated_metrics(base_values, correlation_factor=0.8, noise_level=0.2):
    """
    生成具有指定相关性的指标值
    
    参数:
        base_values (list): 基础指标值
        correlation_factor (float): 目标相关系数
        noise_level (float): 噪音水平
        
    返回:
        list: 生成的指标值
    """
    # 生成随机噪音
    noise = np.random.normal(0, noise_level, len(base_values))
    
    # 生成相关序列
    correlated_values = []
    for i, value in enumerate(base_values):
        # 使用相关因子和噪音生成新值
        new_value = correlation_factor * value + (1 - correlation_factor) * noise[i]
        correlated_values.append(max(0, new_value))  # 确保值非负
    
    return correlated_values


def create_sample_data():
    """
    创建示例数据
    
    返回:
        dict: 创建的示例数据
    """
    # 创建时间周期
    time_periods = [f"2023年{i}月" for i in range(1, 13)]
    
    # 创建基础销售额指标值（随机增长趋势）
    base_sales = [100]
    for _ in range(11):
        prev = base_sales[-1]
        change = random.uniform(-0.1, 0.15) # -10% 到 +15% 的随机变化
        new_value = prev * (1 + change)
        base_sales.append(new_value)
    
    # 创建几个相关指标
    # 利润（与销售额高度正相关）
    profit_rates = [0.15 + random.uniform(-0.02, 0.03) for _ in range(12)]  # 利润率在 13-18% 之间浮动
    profit = [sales * rate for sales, rate in zip(base_sales, profit_rates)]
    
    # 营销支出（与销售额中度正相关，但领先一个月）
    marketing_expenses = [0] + generate_correlated_metrics(base_sales[:-1], 0.6, 0.3)
    marketing_expenses = [expense * 0.12 for expense in marketing_expenses]  # 营销支出约为销售额的12%
    
    # 客户投诉（与销售额弱负相关）
    complaints = generate_correlated_metrics([-s for s in base_sales], 0.3, 0.8)
    complaints = [abs(c) * 0.02 for c in complaints]  # 投诉数约为销售额的2%
    
    # 客户满意度（与投诉强负相关）
    satisfaction = [90 - c * 5 for c in complaints]  # 基础满意度90，减去投诉的影响
    
    # 创建指标数据
    metrics = [
        {
            "name": "销售额",
            "value": base_sales[-1],
            "previous_value": base_sales[-2],
            "unit": "万元",
            "time_period": time_periods[-1],
            "previous_time_period": time_periods[-2],
            "historical_values": base_sales[:-1],
            "is_positive_better": True
        },
        {
            "name": "利润",
            "value": profit[-1],
            "previous_value": profit[-2],
            "unit": "万元",
            "time_period": time_periods[-1],
            "previous_time_period": time_periods[-2],
            "historical_values": profit[:-1],
            "is_positive_better": True
        },
        {
            "name": "营销支出",
            "value": marketing_expenses[-1],
            "previous_value": marketing_expenses[-2],
            "unit": "万元",
            "time_period": time_periods[-1],
            "previous_time_period": time_periods[-2],
            "historical_values": marketing_expenses[:-1],
            "is_positive_better": False
        },
        {
            "name": "客户投诉",
            "value": complaints[-1],
            "previous_value": complaints[-2],
            "unit": "件",
            "time_period": time_periods[-1],
            "previous_time_period": time_periods[-2],
            "historical_values": complaints[:-1],
            "is_positive_better": False
        },
        {
            "name": "客户满意度",
            "value": satisfaction[-1],
            "previous_value": satisfaction[-2],
            "unit": "%",
            "time_period": time_periods[-1],
            "previous_time_period": time_periods[-2],
            "historical_values": satisfaction[:-1],
            "is_positive_better": True
        }
    ]
    
    # 添加异常值
    metrics[3]["value"] *= 1.5  # 客户投诉突然增加50%
    metrics[3]["is_anomaly"] = True
    metrics[3]["anomaly_degree"] = 2.1
    
    # 创建完整数据对象
    sample_data = {
        "metrics": metrics,
        "time_periods": time_periods,
        "dimensions": {
            "地区": "华东",
            "产品线": "电子产品",
            "客户类型": "企业客户"
        }
    }
    
    return sample_data


def visualize_metrics(metrics, time_periods):
    """
    可视化指标数据
    
    参数:
        metrics (list): 指标列表
        time_periods (list): 时间周期列表
    """
    plt.figure(figsize=(12, 8))
    
    for metric in metrics:
        name = metric["name"]
        values = metric["historical_values"] + [metric["value"]]
        plt.plot(time_periods, values, marker='o', label=f"{name} ({metric['unit']})")
    
    plt.title("多指标趋势对比")
    plt.xlabel("时间")
    plt.ylabel("指标值")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存图表
    plt.savefig("metric_comparison.png")
    print("指标对比图表已保存为 metric_comparison.png")


def print_analysis_result(result):
    """
    打印分析结果
    
    参数:
        result (dict): 分析结果
    """
    print("\n==== 指标对比分析结果 ====\n")
    
    # 打印基本信息
    basic_info = result["基本信息"]
    print(f"指标数量: {basic_info['指标数量']}")
    print(f"指标列表: {', '.join(basic_info['指标名称列表'])}")
    print(f"时间周期数: {basic_info['时间周期数']}")
    print(f"维度数量: {basic_info['维度数量']}")
    
    # 打印对比分析
    print("\n--- 对比分析 ---")
    for i, comparison in enumerate(result["对比分析"], 1):
        print(f"\n对比 {i}:")
        print(f"  {comparison['指标1']['名称']} vs {comparison['指标2']['名称']}")
        print(f"  值: {comparison['指标1']['当前值']}{comparison['指标1']['单位']} vs {comparison['指标2']['当前值']}{comparison['指标2']['单位']}")
        if comparison['相对差异'] is not None:
            print(f"  相对差异: {comparison['相对差异'] * 100:.2f}%")
        print(f"  差异大小: {comparison['差异大小']}")
        if "描述" in comparison:
            print(f"  描述: {comparison['描述']}")
    
    # 打印相关性分析
    if result["相关性分析"]:
        print("\n--- 相关性分析 ---")
        for i, correlation in enumerate(result["相关性分析"], 1):
            print(f"\n相关性 {i}:")
            print(f"  {correlation['指标1']} vs {correlation['指标2']}")
            print(f"  相关系数: {correlation['相关系数']:.4f}")
            print(f"  P值: {correlation['P值']:.4f}")
            print(f"  显著性: {'是' if correlation['显著性'] else '否'}")
            print(f"  相关性类型: {correlation['相关性类型']}")
            print(f"  相关性强度: {correlation['相关性强度']}")
            print(f"  样本数量: {correlation['样本数量']}")
            if "描述" in correlation:
                print(f"  描述: {correlation['描述']}")
    
    # 打印群组分析
    print("\n--- 群组分析 ---")
    groups = result["群组分析"]
    
    # 打印增长指标
    if groups["增长指标"]:
        print("\n增长指标:")
        for item in groups["增长指标"]:
            print(f"  {item['指标名称']}: 变化率 {item['变化率'] * 100:.2f}%")
    
    # 打印下降指标
    if groups["下降指标"]:
        print("\n下降指标:")
        for item in groups["下降指标"]:
            print(f"  {item['指标名称']}: 变化率 {item['变化率'] * 100:.2f}%")
    
    # 打印稳定指标
    if groups["稳定指标"]:
        print("\n稳定指标:")
        for item in groups["稳定指标"]:
            print(f"  {item['指标名称']}: 变化率 {item['变化率'] * 100:.2f}%")
    
    # 打印异常指标
    if groups["异常指标"]:
        print("\n异常指标:")
        for item in groups["异常指标"]:
            print(f"  {item['指标名称']}: 异常程度 {item['异常程度']:.2f}")


def main():
    """主函数"""
    print("=== 指标对比分析示例 ===\n")
    
    # 创建示例数据
    print("创建示例数据...")
    sample_data = create_sample_data()
    
    # 打印数据概要
    print(f"生成了 {len(sample_data['metrics'])} 个指标，时间周期为 {sample_data['time_periods'][0]} 至 {sample_data['time_periods'][-1]}")
    print("指标列表:")
    for metric in sample_data["metrics"]:
        print(f"  - {metric['name']}: 当前值 {metric['value']:.2f}{metric['unit']}")
    
    # 可视化指标数据
    visualize_metrics(sample_data["metrics"], sample_data["time_periods"])
    
    # 创建分析器和生成器
    analyzer = MetricComparisonAnalyzer()
    generator = TextGenerator()
    
    # 分析指标
    print("\n执行指标对比分析...")
    analysis_result = analyzer.analyze(sample_data)
    
    # 打印分析结果
    print_analysis_result(analysis_result)
    
    # 生成解读文本
    print("\n=== 自动生成的解读文本 ===\n")
    insight_text = generator.generate_text(analysis_result)
    print(insight_text)


if __name__ == "__main__":
    main() 