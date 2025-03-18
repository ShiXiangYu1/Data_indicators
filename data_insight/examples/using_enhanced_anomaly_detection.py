#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强异常检测算法使用示例
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple
import json

from data_insight.utils.data_utils import (
    detect_anomaly_enhanced,
    detect_seasonal_pattern,
    detect_multi_dimensional_anomaly
)


def generate_sample_data() -> Tuple[List[float], Dict[str, List[float]]]:
    """
    生成示例数据集，包含主指标和多个相关维度
    
    返回:
        Tuple[List[float], Dict[str, List[float]]]: (主指标历史数据, 相关维度历史数据字典)
    """
    # 设置随机种子以确保可重现性
    np.random.seed(42)
    
    # 创建时间序列 (模拟90天数据)
    days = 90
    time_points = np.arange(days)
    
    # 生成基础趋势 (略微上升)
    base_trend = time_points * 0.05
    
    # 添加周期性（周期为7天，模拟周周期）
    weekly_cycle = 3 * np.sin(2 * np.pi * time_points / 7)
    
    # 添加随机噪声
    noise = np.random.normal(0, 1, days)
    
    # 主指标 = 基础趋势 + 周期 + 噪声
    main_metric = base_trend + weekly_cycle + noise
    
    # 添加几个特殊点（异常值）
    main_metric[30] += 10  # 第31天有个明显异常（大幅上升）
    main_metric[60] -= 8   # 第61天有个明显异常（大幅下降）
    
    # 生成相关维度
    dimensions = {}
    
    # 1. 正相关维度 (与主指标呈正相关)
    dimensions["用户活跃度"] = main_metric * 2 + np.random.normal(0, 1, days)
    
    # 2. 负相关维度 (与主指标呈负相关)
    dimensions["系统延迟"] = 100 - main_metric * 1.5 + np.random.normal(0, 2, days)
    
    # 3. 季节性相关维度 (与主指标有类似的季节性，但峰值有偏移)
    dimensions["广告展示量"] = weekly_cycle + np.sin(2 * np.pi * (time_points+2) / 7) * 5 + np.random.normal(0, 1, days)
    
    # 4. 无相关维度 (与主指标基本无关)
    dimensions["服务器负载"] = np.random.normal(50, 10, days)
    
    return main_metric.tolist(), {k: v.tolist() for k, v in dimensions.items()}


def print_detection_result(result: Dict[str, Any], metric_name: str = "主指标"):
    """
    打印异常检测结果
    
    参数:
        result: 异常检测结果字典
        metric_name: 指标名称
    """
    print(f"\n{'='*50}")
    print(f"指标 '{metric_name}' 异常检测结果:")
    print(f"{'='*50}")
    
    # 打印基本结果
    print(f"是否异常: {'是' if result['is_anomaly'] else '否'}")
    if "method" in result:
        print(f"检测方法: {result['method']}")
    if "reason" in result:
        print(f"异常原因: {result['reason']}")
    print(f"异常程度: {result.get('anomaly_degree', result.get('anomaly_score', 0)):.2f}")
    
    # 打印季节性影响（如果有）
    if "seasonality_impact" in result and result["seasonality_impact"] > 0:
        print(f"季节性影响: {result['seasonality_impact']:.2f}")
        if "detected_seasonality" in result:
            print(f"检测到的季节性周期: {result['detected_seasonality']}")
    
    # 打印上下文影响（如果有）
    if "context_impact" in result and result["context_impact"]:
        print("\n上下文维度影响:")
        for dim, impact in result["context_impact"].items():
            print(f"  - {dim}: {impact:.2f}")
    
    # 打印多维异常结果（如果有）
    if "influencing_factors" in result and result["influencing_factors"]:
        print("\n主要影响因素:")
        for factor in result["influencing_factors"]:
            print(f"  - {factor['dimension']}: 影响度 {factor['impact']:.2f}, "
                  f"{'异常' if factor['is_anomaly'] else '正常'}, "
                  f"异常程度 {factor['anomaly_degree']:.2f}")
    
    print(f"{'='*50}\n")


def visualize_data_with_anomalies(
    data: List[float], 
    anomaly_points: List[int],
    title: str = "数据与异常检测"
):
    """
    可视化数据和检测到的异常点
    
    参数:
        data: 数据列表
        anomaly_points: 异常点的索引列表
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    
    # 绘制原始数据
    plt.plot(data, label='原始数据', color='blue')
    
    # 标记异常点
    if anomaly_points:
        anomaly_values = [data[i] for i in anomaly_points]
        plt.scatter(anomaly_points, anomaly_values, color='red', s=100, label='异常点')
    
    plt.title(title)
    plt.xlabel('时间点')
    plt.ylabel('数值')
    plt.legend()
    plt.grid(True)
    
    # 保存图像
    plt.savefig(f"{title.replace(' ', '_')}.png")
    print(f"已保存图表: {title.replace(' ', '_')}.png")


def main():
    """主函数"""
    print("增强异常检测示例")
    print("-" * 50)
    
    # 1. 生成示例数据
    main_data, dimensions = generate_sample_data()
    print(f"已生成 {len(main_data)} 个数据点的主指标和 {len(dimensions)} 个维度")
    
    # 2. 检测季节性模式
    season_length, season_strength = detect_seasonal_pattern(main_data, max_period=30)
    print(f"\n季节性检测结果:")
    print(f"季节长度: {season_length if season_length else '未检测到'}")
    print(f"季节强度: {season_strength:.2f}")
    
    # 3. 单点基础异常检测示例
    normal_idx = 20  # 正常点
    anomaly_high_idx = 30  # 异常点（高）
    anomaly_low_idx = 60  # 异常点（低）
    
    # 检测正常点
    normal_result = detect_anomaly_enhanced(
        main_data[normal_idx],
        main_data[:normal_idx],
        seasonality=season_length
    )
    print_detection_result(normal_result, f"正常点 (索引 {normal_idx})")
    
    # 检测异常点（高值）
    high_anomaly_result = detect_anomaly_enhanced(
        main_data[anomaly_high_idx],
        main_data[:anomaly_high_idx],
        seasonality=season_length
    )
    print_detection_result(high_anomaly_result, f"高值异常点 (索引 {anomaly_high_idx})")
    
    # 检测异常点（低值）
    low_anomaly_result = detect_anomaly_enhanced(
        main_data[anomaly_low_idx],
        main_data[:anomaly_low_idx],
        seasonality=season_length
    )
    print_detection_result(low_anomaly_result, f"低值异常点 (索引 {anomaly_low_idx})")
    
    # 4. 多维异常检测示例
    # 准备最近一个时间点的数据进行多维分析
    current_idx = 70
    current_main = main_data[current_idx]
    historical_main = main_data[:current_idx]
    
    # 当前维度值
    current_dimensions = {dim: values[current_idx] for dim, values in dimensions.items()}
    # 历史维度值
    historical_dimensions = {dim: values[:current_idx] for dim, values in dimensions.items()}
    
    # 执行多维异常检测
    multi_dim_result = detect_multi_dimensional_anomaly(
        current_main,
        historical_main,
        current_dimensions,
        historical_dimensions
    )
    
    print_detection_result(multi_dim_result, f"多维分析 (索引 {current_idx})")
    
    # 5. 可视化异常点
    # 收集所有检测到的异常点
    anomaly_indices = []
    for i in range(10, len(main_data)):
        # 每隔10个点进行一次异常检测
        if i % 10 == 0:
            result = detect_anomaly_enhanced(
                main_data[i],
                main_data[:i],
                seasonality=season_length
            )
            if result["is_anomaly"]:
                anomaly_indices.append(i)
    
    # 可视化主指标数据和检测到的异常点
    visualize_data_with_anomalies(
        main_data, 
        anomaly_indices,
        "主指标异常检测结果"
    )
    
    print("\n示例完成! 增强型异常检测算法展示了如何处理季节性数据和多维异常检测。")


if __name__ == "__main__":
    main() 