#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表分析器测试
===========

测试chart_analyzer模块中的ChartAnalyzer类。
"""

import pytest
import numpy as np
from data_insight.core.chart_analyzer import ChartAnalyzer


class TestChartAnalyzer:
    """测试图表分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.analyzer = ChartAnalyzer()
    
    def test_analyze_unsupported_chart_type(self):
        """测试不支持的图表类型"""
        # 准备测试数据
        chart_data = {
            "chart_type": "pie",  # 不支持的类型
            "title": "测试图表",
            "data": {}
        }
        
        # 运行分析
        result = self.analyzer.analyze(chart_data)
        
        # 验证结果包含错误信息
        assert "错误" in result
        assert "不支持的图表类型" in result["错误"]
        assert "pie" in result["错误"]
        assert "支持的类型" in result
        assert "line" in result["支持的类型"]
        assert "bar" in result["支持的类型"]
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备测试数据 - 缺少data字段
        chart_data = {
            "chart_type": "line",
            "title": "测试图表"
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(chart_data)
        
        # 验证异常消息包含缺少的字段
        assert "data" in str(excinfo.value)
    
    def test_analyze_line_chart_basic(self):
        """测试基本线图分析功能"""
        # 准备测试数据
        chart_data = {
            "chart_type": "line",
            "title": "月度销售额趋势",
            "data": {
                "x_axis": {
                    "label": "月份",
                    "values": ["2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月"]
                },
                "y_axis": {
                    "label": "销售额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [10000, 12000, 11500, 13500, 15000]
                        }
                    ]
                }
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(chart_data)
        
        # 验证基本信息
        assert "基本信息" in result
        assert result["基本信息"]["图表类型"] == "线图"
        assert result["基本信息"]["图表标题"] == "月度销售额趋势"
        assert result["基本信息"]["X轴标签"] == "月份"
        assert result["基本信息"]["Y轴标签"] == "销售额(元)"
        assert result["基本信息"]["X轴数据点数"] == 5
        assert result["基本信息"]["系列数"] == 1
        
        # 验证系列分析
        assert "系列分析" in result
        assert len(result["系列分析"]) == 1
        
        series_analysis = result["系列分析"][0]
        assert series_analysis["系列名称"] == "销售额"
        assert "趋势分析" in series_analysis
        assert "统计信息" in series_analysis
        
        # 验证统计信息
        stats = series_analysis["统计信息"]
        assert stats["最大值"] == 15000
        assert stats["最大值位置"] == "2023年6月"
        assert stats["最小值"] == 10000
        assert stats["最小值位置"] == "2023年2月"
        assert stats["平均值"] == 12400
        assert stats["总体变化率"] == 0.5  # (15000 - 10000) / 10000 = 0.5
        
        # 验证整体分析
        assert "整体分析" in result
        assert "整体趋势" in result["整体分析"]
    
    def test_analyze_line_chart_with_multiple_series(self):
        """测试多系列线图分析功能"""
        # 准备测试数据
        chart_data = {
            "chart_type": "line",
            "title": "销售与成本趋势对比",
            "data": {
                "x_axis": {
                    "label": "月份",
                    "values": ["2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月"]
                },
                "y_axis": {
                    "label": "金额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [10000, 12000, 11500, 13500, 15000]
                        },
                        {
                            "name": "成本",
                            "values": [8000, 8500, 8200, 9000, 9500]
                        }
                    ]
                }
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(chart_data)
        
        # 验证基本信息
        assert result["基本信息"]["系列数"] == 2
        
        # 验证系列分析
        assert len(result["系列分析"]) == 2
        
        # 验证销售额系列
        sales_series = next((s for s in result["系列分析"] if s["系列名称"] == "销售额"), None)
        assert sales_series is not None
        assert sales_series["统计信息"]["最大值"] == 15000
        assert sales_series["统计信息"]["最小值"] == 10000
        
        # 验证成本系列
        cost_series = next((s for s in result["系列分析"] if s["系列名称"] == "成本"), None)
        assert cost_series is not None
        assert cost_series["统计信息"]["最大值"] == 9500
        assert cost_series["统计信息"]["最小值"] == 8000
    
    def test_analyze_line_chart_with_anomalies(self):
        """测试包含异常点的线图分析功能"""
        # 准备测试数据 - 包含一个明显的异常值
        chart_data = {
            "chart_type": "line",
            "title": "月度销售额趋势",
            "data": {
                "x_axis": {
                    "label": "月份",
                    "values": ["2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月"]
                },
                "y_axis": {
                    "label": "销售额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [10000, 11000, 30000, 12000, 13000]  # 30000是异常值
                        }
                    ]
                }
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(chart_data)
        
        # 验证异常点检测
        series_analysis = result["系列分析"][0]
        assert "异常点" in series_analysis
        anomalies = series_analysis["异常点"]
        
        # 至少应该检测到一个异常点
        assert len(anomalies) >= 1
        
        # 验证异常点索引是否为2（对应值30000）
        anomaly_indices = [a["索引"] for a in anomalies]
        assert 2 in anomaly_indices
        
        # 验证该异常点的值是否为30000
        anomaly = next((a for a in anomalies if a["索引"] == 2), None)
        assert anomaly is not None
        assert anomaly["值"] == 30000
        assert anomaly["是否高于正常范围"] == True
    
    def test_analyze_bar_chart(self):
        """测试柱状图分析功能"""
        # 准备测试数据
        chart_data = {
            "chart_type": "bar",
            "title": "各地区销售额对比",
            "data": {
                "x_axis": {
                    "label": "地区",
                    "values": ["华东", "华南", "华北", "西南", "西北"]
                },
                "y_axis": {
                    "label": "销售额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [25000, 18000, 22000, 12000, 8000]
                        }
                    ]
                }
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(chart_data)
        
        # 验证基本信息
        assert "基本信息" in result
        assert result["基本信息"]["图表类型"] == "柱状图"
        assert result["基本信息"]["X轴类别数"] == 5
        assert result["基本信息"]["系列数"] == 1
        
        # 验证系列分析
        assert "系列分析" in result
        series_analysis = result["系列分析"][0]
        
        # 验证统计信息
        stats = series_analysis["统计信息"]
        assert stats["最大值"] == 25000
        assert stats["最大值类别"] == "华东"
        assert stats["最小值"] == 8000
        assert stats["最小值类别"] == "西北"
        
        # 验证分布特征
        assert "分布特征" in series_analysis
        
        # 验证类别对比
        assert "类别对比" in result
        category_comparisons = result["类别对比"]
        assert len(category_comparisons) == 3  # 最大值vs平均值、最小值vs平均值、最大值vs最小值
        
        # 验证最大值与最小值的对比
        max_vs_min = next((c for c in category_comparisons if c["对比类型"] == "最大值与最小值"), None)
        assert max_vs_min is not None
        assert max_vs_min["主体类别"] == "华东"
        assert max_vs_min["对比类别"] == "西北"
        assert max_vs_min["主体值"] == 25000
        assert max_vs_min["对比值"] == 8000
        assert "华东" in max_vs_min["分析结果"]
        assert "西北" in max_vs_min["分析结果"]
    
    def test_analyze_bar_chart_with_multiple_series(self):
        """测试多系列柱状图分析功能"""
        # 准备测试数据
        chart_data = {
            "chart_type": "bar",
            "title": "各地区销售额与利润对比",
            "data": {
                "x_axis": {
                    "label": "地区",
                    "values": ["华东", "华南", "华北", "西南", "西北"]
                },
                "y_axis": {
                    "label": "金额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [25000, 18000, 22000, 12000, 8000]
                        },
                        {
                            "name": "利润",
                            "values": [7500, 5400, 6600, 3000, 1600]
                        }
                    ]
                }
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(chart_data)
        
        # 验证基本信息
        assert result["基本信息"]["系列数"] == 2
        
        # 验证系列分析
        assert len(result["系列分析"]) == 2
        
        # 验证销售额系列
        sales_series = next((s for s in result["系列分析"] if s["系列名称"] == "销售额"), None)
        assert sales_series is not None
        assert sales_series["统计信息"]["最大值"] == 25000
        
        # 验证利润系列
        profit_series = next((s for s in result["系列分析"] if s["系列名称"] == "利润"), None)
        assert profit_series is not None
        assert profit_series["统计信息"]["最大值"] == 7500
        
        # 验证不应该有类别对比（因为有多个系列）
        assert result["类别对比"] == []
    
    def test_detect_anomalies_in_series(self):
        """测试系列中的异常值检测功能"""
        # 准备测试数据
        values = [100, 105, 102, 108, 200, 110, 115]  # 200是异常值
        
        # 检测异常点
        anomalies = self.analyzer._detect_anomalies_in_series(values)
        
        # 验证结果
        assert len(anomalies) >= 1
        
        # 验证异常点索引是否为4（对应值200）
        anomaly_indices = [a["索引"] for a in anomalies]
        assert 4 in anomaly_indices
        
        # 验证该异常点的值是否为200
        anomaly = next((a for a in anomalies if a["索引"] == 4), None)
        assert anomaly is not None
        assert anomaly["值"] == 200
        assert anomaly["是否高于正常范围"] == True
    
    def test_determine_overall_trend(self):
        """测试整体趋势确定功能"""
        # 测试上升趋势
        trends1 = ["上升", "强烈上升", "轻微上升", "平稳"]
        result1 = self.analyzer._determine_overall_trend(trends1)
        assert result1 == "总体上升"
        
        # 测试下降趋势
        trends2 = ["下降", "强烈下降", "平稳"]
        result2 = self.analyzer._determine_overall_trend(trends2)
        assert result2 == "总体趋向下降但不明显"
        
        # 测试平稳趋势
        trends3 = ["平稳", "平稳", "轻微上升"]
        result3 = self.analyzer._determine_overall_trend(trends3)
        assert result3 == "总体平稳"
        
        # 测试趋势不一致
        trends4 = ["上升", "下降", "平稳"]
        result4 = self.analyzer._determine_overall_trend(trends4)
        assert result4 == "各系列趋势不一致"
        
        # 测试空趋势列表
        trends5 = []
        result5 = self.analyzer._determine_overall_trend(trends5)
        assert result5 == "无法确定"
    
    def test_determine_distribution_feature(self):
        """测试分布特征确定功能"""
        # 测试均匀且集中的分布
        values1 = [100, 102, 101, 103, 102, 101]
        result1 = self.analyzer._determine_distribution_feature(values1)
        assert "均匀" in result1
        assert "集中" in result1
        
        # 测试均匀但分散的分布
        values2 = [80, 100, 90, 120, 110, 70]
        result2 = self.analyzer._determine_distribution_feature(values2)
        assert "均匀" in result2
        assert "分散" in result2
        
        # 测试正偏斜的分布
        values3 = [100, 105, 108, 120, 150, 200]
        result3 = self.analyzer._determine_distribution_feature(values3)
        assert "正偏斜" in result3
        
        # 测试负偏斜的分布
        values4 = [200, 150, 120, 108, 105, 100]
        result4 = self.analyzer._determine_distribution_feature(values4)
        assert "负偏斜" in result4
        
        # 测试数据点不足
        values5 = [100]
        result5 = self.analyzer._determine_distribution_feature(values5)
        assert result5 == "数据点不足"
    
    def test_analyze_categories(self):
        """测试类别对比分析功能"""
        # 准备测试数据
        categories = ["华东", "华南", "华北", "西南", "西北"]
        values = [25000, 18000, 22000, 12000, 8000]
        
        # 分析类别对比
        results = self.analyzer._analyze_categories(categories, values)
        
        # 验证结果
        assert len(results) == 3  # 最大值vs平均值、最小值vs平均值、最大值vs最小值
        
        # 验证最大值与平均值的对比
        max_vs_avg = next((r for r in results if r["对比类型"] == "最大值与平均值"), None)
        assert max_vs_avg is not None
        assert max_vs_avg["主体类别"] == "华东"
        assert max_vs_avg["主体值"] == 25000
        assert abs(max_vs_avg["对比值"] - np.mean(values)) < 0.001
        
        # 验证最小值与平均值的对比
        min_vs_avg = next((r for r in results if r["对比类型"] == "最小值与平均值"), None)
        assert min_vs_avg is not None
        assert min_vs_avg["主体类别"] == "西北"
        assert min_vs_avg["主体值"] == 8000
        
        # 验证最大值与最小值的对比
        max_vs_min = next((r for r in results if r["对比类型"] == "最大值与最小值"), None)
        assert max_vs_min is not None
        assert max_vs_min["主体类别"] == "华东"
        assert max_vs_min["对比类别"] == "西北"
        assert max_vs_min["主体值"] == 25000
        assert max_vs_min["对比值"] == 8000
        assert "华东" in max_vs_min["分析结果"]
        assert "西北" in max_vs_min["分析结果"]
        
        # 测试数据不足的情况
        categories2 = ["华东"]
        values2 = [25000]
        results2 = self.analyzer._analyze_categories(categories2, values2)
        assert results2 == []
        
        # 测试类别和值数量不匹配的情况
        categories3 = ["华东", "华南", "华北"]
        values3 = [25000, 18000]
        results3 = self.analyzer._analyze_categories(categories3, values3)
        assert results3 == [] 