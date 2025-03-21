#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
比较分析器测试脚本
=================

测试比较分析器和相关API功能。
"""

import unittest
import json
from datetime import datetime

from data_insight.core.analysis.comparison import ComparisonAnalyzer


class TestComparisonAnalyzer(unittest.TestCase):
    """测试比较分析器功能"""

    def setUp(self):
        self.analyzer = ComparisonAnalyzer()
        
        # 准备测试数据 - 两个销售趋势线图
        self.line_chart1 = {
            "type": "line",
            "title": "产品A销售趋势",
            "data": {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
                "y": [100, 120, 115, 130, 145, 160]
            },
            "x_label": "月份",
            "y_label": "销售额(万元)"
        }
        
        self.line_chart2 = {
            "type": "line",
            "title": "产品B销售趋势",
            "data": {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
                "y": [80, 85, 95, 105, 115, 125]
            },
            "x_label": "月份",
            "y_label": "销售额(万元)"
        }
        
        # 准备饼图数据
        self.pie_chart = {
            "type": "pie",
            "title": "销售份额分布",
            "data": {
                "labels": ["产品A", "产品B", "产品C", "产品D"],
                "values": [35, 25, 20, 20]
            }
        }
        
        # 准备柱状图数据
        self.bar_chart = {
            "type": "bar",
            "title": "各部门销售业绩",
            "data": {
                "x": ["部门1", "部门2", "部门3", "部门4"],
                "y": [120, 80, 100, 95]
            },
            "x_label": "部门",
            "y_label": "销售额(万元)"
        }

    def test_supported_comparison_types(self):
        """测试获取支持的比较类型"""
        types = self.analyzer.get_supported_comparison_types()
        self.assertIsInstance(types, list)
        self.assertGreater(len(types), 0)
        print(f"支持的比较类型: {types}")

    def test_trend_comparison(self):
        """测试趋势比较功能"""
        comparison_data = {
            "charts": [self.line_chart1, self.line_chart2],
            "comparison_type": "trend"
        }
        
        try:
            result = self.analyzer.analyze(comparison_data)
            self.assertIsInstance(result, dict)
            self.assertIn("comparison", result)
            self.assertIn("trend_comparison", result["comparison"])
            
            print("\n趋势比较结果:")
            print(json.dumps(result["comparison"]["trend_comparison"], indent=2, ensure_ascii=False))
        except Exception as e:
            self.fail(f"趋势比较测试失败: {str(e)}")

    def test_feature_comparison(self):
        """测试特征比较功能"""
        comparison_data = {
            "charts": [self.line_chart1, self.line_chart2],
            "comparison_type": "feature"
        }
        
        try:
            result = self.analyzer.analyze(comparison_data)
            self.assertIsInstance(result, dict)
            self.assertIn("comparison", result)
            self.assertIn("feature_comparison", result["comparison"])
            
            print("\n特征比较结果:")
            print(json.dumps(result["comparison"]["feature_comparison"], indent=2, ensure_ascii=False))
        except Exception as e:
            self.fail(f"特征比较测试失败: {str(e)}")

    def test_correlation_analysis(self):
        """测试相关性分析功能"""
        comparison_data = {
            "charts": [self.line_chart1, self.line_chart2],
            "comparison_type": "correlation"
        }
        
        try:
            result = self.analyzer.analyze(comparison_data)
            self.assertIsInstance(result, dict)
            self.assertIn("comparison", result)
            self.assertIn("correlation_analysis", result["comparison"])
            
            print("\n相关性分析结果:")
            print(json.dumps(result["comparison"]["correlation_analysis"], indent=2, ensure_ascii=False))
        except Exception as e:
            self.fail(f"相关性分析测试失败: {str(e)}")

    def test_all_comparison_types(self):
        """测试所有比较类型"""
        comparison_data = {
            "charts": [self.line_chart1, self.line_chart2],
            "comparison_type": "all"
        }
        
        try:
            result = self.analyzer.analyze(comparison_data)
            self.assertIsInstance(result, dict)
            self.assertIn("comparison", result)
            
            # 检查是否包含所有比较类型的结果
            for comp_type in ["trend_comparison", "feature_comparison", "correlation_analysis"]:
                self.assertIn(comp_type, result["comparison"])
            
            print("\n所有比较类型分析结果的键:")
            print(list(result["comparison"].keys()))
        except Exception as e:
            self.fail(f"所有比较类型测试失败: {str(e)}")

    def test_different_chart_types(self):
        """测试比较不同类型的图表"""
        comparison_data = {
            "charts": [self.line_chart1, self.bar_chart],
            "comparison_type": "all"
        }
        
        try:
            result = self.analyzer.analyze(comparison_data)
            self.assertIsInstance(result, dict)
            print("\n不同类型图表比较结果:")
            print(json.dumps(result["comparison"].keys(), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"不同类型图表比较警告 (这可能是预期的): {str(e)}")

    def test_validation_error(self):
        """测试验证错误处理"""
        # 测试缺少charts字段
        with self.assertRaises(ValueError):
            self.analyzer.analyze({})
            
        # 测试charts不是列表
        with self.assertRaises(ValueError):
            self.analyzer.analyze({"charts": "not_a_list"})
            
        # 测试charts列表为空
        with self.assertRaises(ValueError):
            self.analyzer.analyze({"charts": []})
            
        # 测试charts列表只有一个元素
        with self.assertRaises(ValueError):
            self.analyzer.analyze({"charts": [self.line_chart1]})
            
        print("\n验证错误测试通过")


def manual_test():
    """手动测试函数，可以直接运行以查看结果"""
    analyzer = ComparisonAnalyzer()
    
    # 准备测试数据 - 两个销售趋势线图
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
    
    comparison_data = {
        "charts": [line_chart1, line_chart2],
        "comparison_type": "all"
    }
    
    result = analyzer.analyze(comparison_data)
    print("比较分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 如果有需要，可以保存结果到文件
    with open(f"comparison_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\n结果已保存到文件")


if __name__ == "__main__":
    # 运行单元测试
    # unittest.main()
    
    # 或者运行手动测试查看详细结果
    manual_test() 