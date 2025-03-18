#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用模型类示例

演示如何使用data_insight包中的模型类进行数据分析和处理。
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import uuid

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.models.insight_model import MetricInsight
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


def create_metric_insight_from_analysis(metric_data, analysis_result, insight_text):
    """
    从分析结果创建MetricInsight对象
    
    参数:
        metric_data (dict): 原始指标数据
        analysis_result (dict): 分析结果
        insight_text (str): 生成的洞察文本
        
    返回:
        MetricInsight: 创建的洞察对象
    """
    # 从分析结果中提取信息
    basic_info = analysis_result["基本信息"]
    change_analysis = analysis_result["变化分析"]
    anomaly_analysis = analysis_result["异常分析"]
    
    # 提取趋势信息(如果有)
    trend_type = None
    trend_strength = 0.0
    if "趋势分析" in analysis_result:
        trend_analysis = analysis_result["趋势分析"]
        trend_type = trend_analysis["趋势类型"]
        trend_strength = trend_analysis["趋势强度"]
    
    # 创建MetricInsight对象
    insight = MetricInsight(
        metric_id=f"{basic_info['指标名称']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
        metric_name=basic_info["指标名称"],
        current_value=basic_info["当前值"],
        previous_value=basic_info["上一期值"],
        unit=basic_info["单位"],
        time_period=basic_info["当前周期"],
        previous_time_period=basic_info["上一周期"],
        change_value=change_analysis["变化量"],
        change_rate=change_analysis["变化率"],
        change_class=change_analysis["变化类别"],
        is_anomaly=anomaly_analysis["是否异常"],
        anomaly_degree=anomaly_analysis["异常程度"],
        trend_type=trend_type,
        trend_strength=trend_strength,
        insight_text=insight_text,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        analysis_version="0.1.0"
    )
    
    return insight


def main():
    """主函数"""
    # 构建示例数据文件路径
    current_dir = Path(__file__).parent
    sample_data_path = current_dir.parent / 'data' / 'sample_data.json'
    
    # 加载示例数据
    print(f"加载示例数据: {sample_data_path}")
    sample_data = load_sample_data(sample_data_path)
    
    # 创建分析器和生成器
    analyzer = MetricAnalyzer()
    generator = TextGenerator()
    
    # 分析第一个指标并创建MetricInsight对象
    metric_data = sample_data['metrics'][0]
    analysis_result = analyzer.analyze(metric_data)
    insight_text = generator.generate_text(analysis_result)
    
    # 从分析结果创建MetricInsight对象
    metric_insight = create_metric_insight_from_analysis(
        metric_data, analysis_result, insight_text
    )
    
    # 打印MetricInsight对象信息
    print("\n=== MetricInsight对象详情 ===\n")
    print(f"指标ID: {metric_insight.metric_id}")
    print(f"指标名称: {metric_insight.metric_name}")
    print(f"当前值: {metric_insight.current_value} {metric_insight.unit}")
    print(f"上一期值: {metric_insight.previous_value} {metric_insight.unit}")
    print(f"变化量: {metric_insight.change_value} {metric_insight.unit}")
    print(f"变化率: {metric_insight.change_rate if metric_insight.change_rate is not None else 'N/A'}")
    print(f"变化类别: {metric_insight.change_class}")
    print(f"是否异常: {metric_insight.is_anomaly}")
    if metric_insight.is_anomaly:
        print(f"异常程度: {metric_insight.anomaly_degree}")
    if metric_insight.trend_type:
        print(f"趋势类型: {metric_insight.trend_type}")
        print(f"趋势强度: {metric_insight.trend_strength}")
    
    # 打印解读文本
    print("\n解读文本:")
    print(metric_insight.insight_text)
    
    # 将MetricInsight对象转换为JSON
    json_data = metric_insight.to_json()
    print("\nJSON格式数据:")
    print(json_data)
    
    # 从JSON创建新的MetricInsight对象
    print("\n从JSON重新创建MetricInsight对象...")
    new_insight = MetricInsight.from_json(json_data)
    
    # 验证新对象与原对象属性是否一致
    print(f"验证新对象是否与原对象一致: {new_insight.metric_name == metric_insight.metric_name}")
    print(f"验证新对象解读文本是否一致: {new_insight.insight_text == metric_insight.insight_text}")


if __name__ == "__main__":
    main() 