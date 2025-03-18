#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表分析器使用示例
=============

演示如何使用图表分析器对不同类型的图表进行分析和解读。
"""

import json
from pprint import pprint
from data_insight.core.chart_analyzer import ChartAnalyzer
from data_insight.core.text_generator import TextGenerator
from data_insight.templates.templates import CHART_TEMPLATES


def analyze_line_chart():
    """
    分析线图示例
    """
    print("\n" + "=" * 50)
    print("线图分析示例")
    print("=" * 50)
    
    # 创建分析器实例
    analyzer = ChartAnalyzer()
    
    # 准备线图数据
    line_chart_data = {
        "chart_type": "line",
        "title": "北京地区2023年季度销售额走势",
        "data": {
            "x_axis": {
                "label": "季度",
                "values": ["2023Q1", "2023Q2", "2023Q3", "2023Q4"]
            },
            "y_axis": {
                "label": "销售额(万元)",
                "series": [
                    {
                        "name": "电子产品",
                        "values": [120, 135, 125, 160]
                    },
                    {
                        "name": "家居用品",
                        "values": [85, 90, 88, 105]
                    }
                ]
            }
        }
    }
    
    # 分析线图
    result = analyzer.analyze(line_chart_data)
    
    # 打印分析结果的主要部分
    print("\n基本信息:")
    pprint(result["基本信息"])
    
    print("\n系列分析:")
    for series in result["系列分析"]:
        print(f"\n系列: {series['系列名称']}")
        print(f"  趋势类型: {series['趋势分析']['趋势类型']}")
        print(f"  趋势强度: {series['趋势分析']['趋势强度']}")
        print(f"  最大值: {series['统计信息']['最大值']} (位置: {series['统计信息']['最大值位置']})")
        print(f"  最小值: {series['统计信息']['最小值']} (位置: {series['统计信息']['最小值位置']})")
        print(f"  平均值: {series['统计信息']['平均值']}")
        print(f"  总体变化率: {series['统计信息']['总体变化率']}")
        
        if series["异常点"]:
            print("\n  异常点:")
            for anomaly in series["异常点"]:
                anomaly_direction = "高于" if anomaly["是否高于正常范围"] else "低于"
                print(f"    位置: {anomaly['索引']}, 值: {anomaly['值']}, 方向: {anomaly_direction}正常范围")
    
    print("\n整体趋势分析:")
    print(f"  {result['整体分析']['整体趋势']}")
    
    # 使用文本生成器生成解读
    generate_line_chart_insight(result, line_chart_data)


def analyze_bar_chart():
    """
    分析柱状图示例
    """
    print("\n" + "=" * 50)
    print("柱状图分析示例")
    print("=" * 50)
    
    # 创建分析器实例
    analyzer = ChartAnalyzer()
    
    # 准备柱状图数据
    bar_chart_data = {
        "chart_type": "bar",
        "title": "2023年各区域销售业绩对比",
        "data": {
            "x_axis": {
                "label": "区域",
                "values": ["华东", "华南", "华北", "西南", "东北"]
            },
            "y_axis": {
                "label": "销售额(万元)",
                "series": [
                    {
                        "name": "销售额",
                        "values": [245, 187, 205, 132, 98]
                    }
                ]
            }
        }
    }
    
    # 分析柱状图
    result = analyzer.analyze(bar_chart_data)
    
    # 打印分析结果
    print("\n基本信息:")
    pprint(result["基本信息"])
    
    print("\n系列分析:")
    for series in result["系列分析"]:
        print(f"\n系列: {series['系列名称']}")
        print(f"  最大值: {series['统计信息']['最大值']} (类别: {series['统计信息']['最大值类别']})")
        print(f"  最小值: {series['统计信息']['最小值']} (类别: {series['统计信息']['最小值类别']})")
        print(f"  平均值: {series['统计信息']['平均值']}")
        print(f"  高于平均值的类别数: {series['统计信息']['高于平均值的类别数']}")
        print(f"  低于平均值的类别数: {series['统计信息']['低于平均值的类别数']}")
        print(f"  分布特征: {series['分布特征']}")
    
    print("\n类别对比:")
    for comparison in result["类别对比"]:
        print(f"\n  对比类型: {comparison['对比类型']}")
        if "对比类别" in comparison:
            print(f"  {comparison['主体类别']} vs {comparison['对比类别']}")
        else:
            print(f"  {comparison['主体类别']} vs 平均值")
        print(f"  主体值: {comparison['主体值']}")
        print(f"  对比值: {comparison['对比值']}")
        print(f"  差异比例: {comparison['差异比例']}")
        print(f"  分析结果: {comparison['分析结果']}")
    
    # 使用文本生成器生成解读
    generate_bar_chart_insight(result, bar_chart_data)


def generate_line_chart_insight(analysis_result, chart_data):
    """
    生成线图数据解读
    
    参数:
        analysis_result (Dict): 分析结果
        chart_data (Dict): 原始图表数据
    """
    print("\n" + "-" * 50)
    print("生成线图解读文本:")
    print("-" * 50)
    
    # 创建文本生成器
    text_generator = TextGenerator(templates=CHART_TEMPLATES)
    
    # 准备整体趋势模板数据
    template_data = {
        "chart_title": chart_data["title"],
        "x_axis_label": chart_data["data"]["x_axis"]["label"],
        "y_axis_label": chart_data["data"]["y_axis"]["label"],
        "analysis": analysis_result
    }
    
    # 生成整体趋势解读
    overall_insight = text_generator.generate("chart_overall_trend", template_data)
    print("\n整体趋势解读:")
    print(overall_insight)
    
    # 为每个系列生成详细解读
    for i, series_analysis in enumerate(analysis_result["系列分析"]):
        # 构建临时分析结果结构，使其与模板匹配
        temp_analysis = {
            "系列分析": [
                {
                    "系列名称": series_analysis["系列名称"],
                    "趋势分析": series_analysis["趋势分析"]
                }
            ]
        }

        # 准备系列趋势模板数据
        series_template_data = {
            "analysis": temp_analysis
        }
        
        # 生成系列趋势解读
        series_trend_insight = text_generator.generate("chart_series_trend", series_template_data)
        print(f"\n{series_analysis['系列名称']}系列趋势解读:")
        print(series_trend_insight)
        
        # 如果有异常点，生成异常点解读
        if series_analysis["异常点"]:
            # 构建临时异常点分析结构
            temp_anomaly_analysis = {
                "系列分析": [
                    {
                        "系列名称": series_analysis["系列名称"],
                        "异常点数量": len(series_analysis["异常点"]),
                        "异常点": [
                            {
                                "索引": anomaly["索引"],
                                "值": anomaly["值"],
                                "描述": "异常偏高" if anomaly.get("是否高于正常范围", False) else "异常偏低",
                                "位置": chart_data["data"]["x_axis"]["values"][anomaly["索引"]] if anomaly["索引"] < len(chart_data["data"]["x_axis"]["values"]) else f"索引 {anomaly['索引']}"
                            }
                            for anomaly in series_analysis["异常点"]
                        ]
                    }
                ]
            }
            
            # 准备异常点模板数据
            anomaly_template_data = {
                "analysis": temp_anomaly_analysis
            }
            
            # 生成异常点解读
            anomaly_insight = text_generator.generate("chart_anomaly", anomaly_template_data)
            print(f"\n{series_analysis['系列名称']}系列异常点解读:")
            print(anomaly_insight)


def generate_bar_chart_insight(analysis_result, chart_data):
    """
    生成柱状图数据解读
    
    参数:
        analysis_result (Dict): 分析结果
        chart_data (Dict): 原始图表数据
    """
    print("\n" + "-" * 50)
    print("生成柱状图解读文本:")
    print("-" * 50)
    
    # 创建文本生成器
    text_generator = TextGenerator(templates=CHART_TEMPLATES)
    
    # 准备模板数据 - 分布特征
    if len(analysis_result["系列分析"]) > 0:
        # 构建临时结构，使其与模板匹配
        temp_analysis = {
            "系列分析": [analysis_result["系列分析"][0]],
            "基本信息": analysis_result["基本信息"]
        }
        
        distribution_template_data = {
            "x_axis_label": chart_data["data"]["x_axis"]["label"],
            "y_axis_label": chart_data["data"]["y_axis"]["label"],
            "analysis": temp_analysis
        }
        
        # 生成分布特征解读
        distribution_insight = text_generator.generate("chart_distribution", distribution_template_data)
        print("\n分布特征解读:")
        print(distribution_insight)
    
    # 生成类别对比解读
    if analysis_result["类别对比"]:
        # 找到类型为"最大值与最小值"的对比
        max_vs_min = next((c for c in analysis_result["类别对比"] if c["对比类型"] == "最大值与最小值"), None)
        
        if max_vs_min:
            # 构建临时结构，使其与模板匹配
            temp_comparison_analysis = {
                "类别对比": [
                    {
                        "主体类别": max_vs_min["主体类别"],
                        "对比类别": max_vs_min["对比类别"],
                        "差异比例": max_vs_min["差异比例"]
                    }
                ]
            }
            
            comparison_template_data = {
                "x_axis_label": chart_data["data"]["x_axis"]["label"],
                "y_axis_label": chart_data["data"]["y_axis"]["label"],
                "analysis": temp_comparison_analysis
            }
            
            # 生成类别对比解读
            comparison_insight = text_generator.generate("chart_category_comparison", comparison_template_data)
            print("\n类别对比解读:")
            print(comparison_insight)


def analyze_multi_series_bar_chart():
    """
    分析多系列柱状图示例
    """
    print("\n" + "=" * 50)
    print("多系列柱状图分析示例")
    print("=" * 50)
    
    # 创建分析器实例
    analyzer = ChartAnalyzer()
    
    # 准备多系列柱状图数据
    bar_chart_data = {
        "chart_type": "bar",
        "title": "2023年各区域销售额与利润对比",
        "data": {
            "x_axis": {
                "label": "区域",
                "values": ["华东", "华南", "华北", "西南", "东北"]
            },
            "y_axis": {
                "label": "金额(万元)",
                "series": [
                    {
                        "name": "销售额",
                        "values": [245, 187, 205, 132, 98]
                    },
                    {
                        "name": "利润",
                        "values": [73.5, 52.4, 61.5, 39.6, 27.4]
                    }
                ]
            }
        }
    }
    
    # 分析多系列柱状图
    result = analyzer.analyze(bar_chart_data)
    
    # 打印分析结果
    print("\n基本信息:")
    pprint(result["基本信息"])
    
    print("\n系列分析:")
    for series in result["系列分析"]:
        print(f"\n系列: {series['系列名称']}")
        print(f"  最大值: {series['统计信息']['最大值']} (类别: {series['统计信息']['最大值类别']})")
        print(f"  最小值: {series['统计信息']['最小值']} (类别: {series['统计信息']['最小值类别']})")
        print(f"  平均值: {series['统计信息']['平均值']}")
        print(f"  分布特征: {series['分布特征']}")
    
    # 计算并打印各区域的利润率
    print("\n附加分析 - 利润率比较:")
    sales_values = next((s["统计信息"] for s in result["系列分析"] if s["系列名称"] == "销售额"), None)
    profit_values = next((s["统计信息"] for s in result["系列分析"] if s["系列名称"] == "利润"), None)
    
    if sales_values and profit_values:
        sales_max_region = sales_values["最大值类别"]
        profit_max_region = profit_values["最大值类别"]
        
        if sales_max_region == profit_max_region:
            print(f"  销售额最高和利润最高的区域一致: {sales_max_region}")
        else:
            print(f"  销售额最高的区域: {sales_max_region}")
            print(f"  利润最高的区域: {profit_max_region}")
        
        # 提取原始数据计算利润率
        sales = bar_chart_data["data"]["y_axis"]["series"][0]["values"]
        profits = bar_chart_data["data"]["y_axis"]["series"][1]["values"]
        regions = bar_chart_data["data"]["x_axis"]["values"]
        
        profit_rates = []
        for i, region in enumerate(regions):
            profit_rate = (profits[i] / sales[i]) * 100 if sales[i] > 0 else 0
            profit_rates.append(profit_rate)
            print(f"  {region}区域利润率: {profit_rate:.1f}%")
        
        max_rate_index = profit_rates.index(max(profit_rates))
        min_rate_index = profit_rates.index(min(profit_rates))
        
        print(f"\n  利润率最高的区域: {regions[max_rate_index]} ({profit_rates[max_rate_index]:.1f}%)")
        print(f"  利润率最低的区域: {regions[min_rate_index]} ({profit_rates[min_rate_index]:.1f}%)")
        
        # 计算利润率与销售额的关系
        high_sales_regions = [i for i, sales_val in enumerate(sales) if sales_val > sum(sales)/len(sales)]
        high_profit_rate_regions = [i for i, rate in enumerate(profit_rates) if rate > sum(profit_rates)/len(profit_rates)]
        
        common_regions = set(high_sales_regions).intersection(set(high_profit_rate_regions))
        if common_regions:
            print("\n  高销售额且高利润率的区域:")
            for idx in common_regions:
                print(f"    {regions[idx]}: 销售额 {sales[idx]}万元, 利润率 {profit_rates[idx]:.1f}%")
        
        # 利润率与销售额的相关性分析
        correlation = "正相关" if len(common_regions) > len(regions)/2 else "弱相关或负相关"
        print(f"\n  销售额与利润率的关系: {correlation}")


def main():
    """主函数"""
    print("图表分析器使用示例")
    
    # 分析线图
    analyze_line_chart()
    
    # 分析柱状图
    analyze_bar_chart()
    
    # 分析多系列柱状图
    analyze_multi_series_bar_chart()


if __name__ == "__main__":
    main() 