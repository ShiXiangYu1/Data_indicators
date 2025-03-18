#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单指标分析示例

演示如何使用data_insight包分析单个指标卡数据并生成解读文本。
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.core.metric_analyzer import MetricAnalyzer
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


def analyze_single_metric(metric_data):
    """
    分析单个指标数据
    
    参数:
        metric_data (dict): 指标数据
        
    返回:
        tuple: (分析结果, 解读文本)
    """
    # 创建分析器和生成器
    analyzer = MetricAnalyzer()
    generator = TextGenerator()
    
    # 分析指标
    analysis_result = analyzer.analyze(metric_data)
    
    # 生成解读文本
    insight_text = generator.generate_text(analysis_result)
    
    return analysis_result, insight_text


def main():
    """主函数"""
    # 构建示例数据文件路径
    current_dir = Path(__file__).parent
    sample_data_path = current_dir.parent / 'data' / 'sample_data.json'
    
    # 加载示例数据
    print(f"加载示例数据: {sample_data_path}")
    sample_data = load_sample_data(sample_data_path)
    
    # 分析每个指标
    print("\n=== 指标解读示例 ===\n")
    
    for i, metric_data in enumerate(sample_data['metrics']):
        print(f"\n--- {i+1}. {metric_data['name']} ---")
        print(f"当前值: {metric_data['value']} {metric_data['unit']}")
        print(f"上期值: {metric_data['previous_value']} {metric_data['unit']}")
        
        # 分析指标并生成解读文本
        analysis_result, insight_text = analyze_single_metric(metric_data)
        
        # 打印解读文本
        print("\n解读文本:")
        print(insight_text)
        
        # 打印分析结果的一部分
        print("\n变化分析:")
        for key, value in analysis_result["变化分析"].items():
            print(f"{key}: {value}")
        
        if "异常分析" in analysis_result and analysis_result["异常分析"]["是否异常"]:
            print("\n异常分析:")
            for key, value in analysis_result["异常分析"].items():
                print(f"{key}: {value}")
        
        if "趋势分析" in analysis_result:
            print("\n趋势分析:")
            for key, value in analysis_result["趋势分析"].items():
                print(f"{key}: {value}")
        
        print("\n" + "-" * 50)


if __name__ == "__main__":
    main() 