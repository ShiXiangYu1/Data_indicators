#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表比较API示例客户端
===================

展示如何使用图表比较API来分析多个图表之间的关系。
"""

import requests
import json
from datetime import datetime


def main():
    """主函数，演示图表比较API的使用"""
    # API基础URL
    base_url = "http://localhost:5000/api/v1"
    
    # 准备两个销售趋势线图数据
    line_chart1 = {
        "type": "line",
        "title": "产品A销售趋势",
        "data": {
            "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
            "y": [100, 120, 115, 130, 145, 160]
        },
        "x_label": "月份",
        "y_label": "销售额(万元)"
    }
    
    line_chart2 = {
        "type": "line",
        "title": "产品B销售趋势",
        "data": {
            "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
            "y": [80, 85, 95, 105, 115, 125]
        },
        "x_label": "月份",
        "y_label": "销售额(万元)"
    }
    
    # 准备相关但有负相关的线图数据
    line_chart3 = {
        "type": "line",
        "title": "产品C销售趋势",
        "data": {
            "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
            "y": [150, 140, 130, 120, 110, 100]
        },
        "x_label": "月份",
        "y_label": "销售额(万元)"
    }
    
    # 准备饼图数据
    pie_chart = {
        "type": "pie",
        "title": "销售份额分布",
        "data": {
            "labels": ["产品A", "产品B", "产品C", "产品D"],
            "values": [35, 25, 20, 20]
        }
    }
    
    # 准备柱状图数据
    bar_chart = {
        "type": "bar",
        "title": "各部门销售业绩",
        "data": {
            "x": ["部门1", "部门2", "部门3", "部门4"],
            "y": [120, 80, 100, 95]
        },
        "x_label": "部门",
        "y_label": "销售额(万元)"
    }
    
    # 检查API服务是否可用
    try:
        response = requests.get(f"{base_url}/charts/comparison-types")
        comparison_types = response.json()
        print(f"可用的比较类型: {comparison_types}")
    except Exception as e:
        print(f"无法连接到API服务: {str(e)}")
        print("请确保API服务已启动并且可访问。")
        return
    
    # 示例1: 比较两个相似的线图
    print("\n=== 示例1: 比较两个相似的线图 ===")
    comparison_data = {
        "charts": [line_chart1, line_chart2],
        "comparison_type": "all",
        "context": {"note": "比较产品A和B的销售趋势"}
    }
    
    try:
        response = requests.post(
            f"{base_url}/charts/compare",
            json=comparison_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 打印结果摘要
            print("比较结果摘要:")
            print(f"- 数据类型: {result.get('data_type')}")
            print(f"- 比较类型: {result.get('comparison_type')}")
            print(f"- 图表数量: {result.get('count')}")
            
            # 提取相关性分析结果
            correlations = result.get("comparison", {}).get("correlation_analysis", [])
            if correlations and len(correlations) > 0:
                correlation_data = correlations[0].get("correlations", [])
                if correlation_data and len(correlation_data) > 0:
                    corr = correlation_data[0]
                    print(f"- 相关性: {corr.get('pearson_correlation', 0):.4f} ({corr.get('direction')})")
                    print(f"- 相关性强度: {corr.get('strength')}")
                    print(f"- 显著性: {'是' if corr.get('is_significant', False) else '否'}")
            
            # 保存完整结果到文件
            filename = f"comparison_similar_lines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"完整结果已保存到文件: {filename}")
        else:
            print(f"API请求失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"请求发生错误: {str(e)}")
    
    # 示例2: 比较相关和负相关的线图
    print("\n=== 示例2: 比较相关和负相关的线图 ===")
    comparison_data = {
        "charts": [line_chart1, line_chart3],
        "comparison_type": "correlation",
        "context": {"note": "比较产品A和C的销售趋势（可能存在负相关）"}
    }
    
    try:
        response = requests.post(
            f"{base_url}/charts/compare",
            json=comparison_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 打印相关性结果
            correlations = result.get("comparison", {}).get("correlation_analysis", [])
            if correlations and len(correlations) > 0:
                correlation_data = correlations[0].get("correlations", [])
                if correlation_data and len(correlation_data) > 0:
                    corr = correlation_data[0]
                    print(f"产品A和C的相关性分析:")
                    print(f"- 皮尔逊相关系数: {corr.get('pearson_correlation', 0):.4f}")
                    print(f"- 相关性方向: {corr.get('direction')}")
                    print(f"- 相关性强度: {corr.get('strength')}")
                    print(f"- p值: {corr.get('p_value', 0):.4f}")
                    print(f"- 斯皮尔曼相关系数: {corr.get('spearman_correlation', 0):.4f}")
            
            # 保存完整结果到文件
            filename = f"comparison_neg_correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"完整结果已保存到文件: {filename}")
        else:
            print(f"API请求失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"请求发生错误: {str(e)}")
    
    # 示例3: 比较不同类型的图表
    print("\n=== 示例3: 比较不同类型的图表 ===")
    comparison_data = {
        "charts": [line_chart1, bar_chart],
        "comparison_type": "feature",
        "context": {"note": "比较不同类型图表的特征"}
    }
    
    try:
        response = requests.post(
            f"{base_url}/charts/compare",
            json=comparison_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 打印特征比较结果
            feature_comparison = result.get("comparison", {}).get("feature_comparison", [])
            if feature_comparison:
                print("不同类型图表的特征比较:")
                for feature in feature_comparison:
                    if isinstance(feature, dict) and "type" in feature:
                        print(f"- 特征: {feature.get('type')}")
            
            # 保存完整结果到文件
            filename = f"comparison_diff_chart_types_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"完整结果已保存到文件: {filename}")
        else:
            print(f"API请求失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"请求发生错误: {str(e)}")


if __name__ == "__main__":
    main()
    print("\n所有示例执行完毕。") 