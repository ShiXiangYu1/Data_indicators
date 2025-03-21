"""
图表对比分析器
==========

分析多个图表之间的对比关系，生成趋势、异常点、相关性等分析结果。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Tuple, Optional, Any
from scipy import stats

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.core.chart_analyzer import ChartAnalyzer
from data_insight.utils.data_utils import calculate_trend, detect_anomaly


class ChartComparisonAnalyzer(BaseAnalyzer):
    """
    图表对比分析器
    
    分析多个图表之间的对比关系，包括趋势对比、异常点对比、特征对比等。
    支持线图、柱状图等常见图表类型。
    """
    
    def __init__(self):
        """
        初始化图表对比分析器
        """
        super().__init__()
        self.chart_analyzer = ChartAnalyzer()
        # 相关性强度描述映射
        self.correlation_strength = {
            (0.0, 0.2): "几乎不相关",
            (0.2, 0.4): "弱相关",
            (0.4, 0.6): "中等相关",
            (0.6, 0.8): "较强相关",
            (0.8, 1.0): "强相关"
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析多个图表的对比关系
        
        参数:
            data (Dict[str, Any]): 图表数据，应包含以下字段:
                - charts: 图表列表，每个图表应包含type、title、data等信息
                - time_periods: 时间周期列表(可选)
                - group_by: 分组方式(可选)，如"category"、"dimension"、"time"
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证必要字段
        required_fields = ["charts"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        charts = data["charts"]
        time_periods = data.get("time_periods", [])
        group_by = data.get("group_by", "category")
        
        # 验证图表数量
        if len(charts) < 2:
            raise ValueError("图表对比分析需要至少两个图表")
        
        # 整合基本信息
        result = {
            "基本信息": {
                "图表数量": len(charts),
                "图表标题列表": [chart.get("title", "未命名图表") for chart in charts],
                "图表类型列表": [chart.get("type", "未知类型") for chart in charts],
                "时间周期数": len(time_periods),
                "分组方式": group_by
            },
            "各图表分析": [],
            "对比分析": {
                "趋势对比": [],
                "特征对比": [],
                "异常点对比": []
            },
            "相关性分析": []
        }
        
        # 分析每个图表
        for chart in charts:
            # 使用ChartAnalyzer分析单个图表
            chart_analysis = self.chart_analyzer.analyze(chart)
            result["各图表分析"].append(chart_analysis)
        
        # 执行对比分析
        result["对比分析"]["趋势对比"] = self._analyze_trend_comparison(charts, result["各图表分析"])
        result["对比分析"]["特征对比"] = self._analyze_feature_comparison(charts, result["各图表分析"])
        result["对比分析"]["异常点对比"] = self._analyze_anomaly_comparison(charts, result["各图表分析"])
        
        # 执行相关性分析
        result["相关性分析"] = self._analyze_correlations(charts)
        
        return result
    
    def _analyze_trend_comparison(self, charts: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表的趋势对比
        
        参数:
            charts (List[Dict[str, Any]]): 图表列表
            analyses (List[Dict[str, Any]]): 各图表分析结果
            
        返回:
            List[Dict[str, Any]]: 趋势对比分析结果
        """
        trend_comparisons = []
        
        # 提取每个图表的趋势信息
        for i in range(len(charts)):
            for j in range(i+1, len(charts)):
                chart1 = charts[i]
                chart2 = charts[j]
                analysis1 = analyses[i]
                analysis2 = analyses[j]
                
                # 获取图表标题
                title1 = chart1.get("title", "未命名图表")
                title2 = chart2.get("title", "未命名图表")
                
                # 确保有系列分析结果
                if "系列分析" not in analysis1 or "系列分析" not in analysis2:
                    continue
                
                # 获取各图表趋势
                trend1 = ""
                trend2 = ""
                
                if analysis1["系列分析"] and "趋势分析" in analysis1["系列分析"][0]:
                    trend1 = analysis1["系列分析"][0]["趋势分析"].get("趋势类型", "未知")
                
                if analysis2["系列分析"] and "趋势分析" in analysis2["系列分析"][0]:
                    trend2 = analysis2["系列分析"][0]["趋势分析"].get("趋势类型", "未知")
                
                # 比较趋势
                trend_consistency = "一致" if trend1 == trend2 else "不一致"
                
                # 创建趋势对比结果
                comparison = {
                    "图表1": {
                        "标题": title1,
                        "趋势": trend1
                    },
                    "图表2": {
                        "标题": title2,
                        "趋势": trend2
                    },
                    "趋势一致性": trend_consistency,
                    "描述": f"{title1}和{title2}的趋势{trend_consistency}，分别是{trend1}和{trend2}"
                }
                
                trend_comparisons.append(comparison)
        
        return trend_comparisons
    
    def _analyze_feature_comparison(self, charts: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表的特征对比，如最大值、最小值、平均值等
        
        参数:
            charts (List[Dict[str, Any]]): 图表列表
            analyses (List[Dict[str, Any]]): 各图表分析结果
            
        返回:
            List[Dict[str, Any]]: 特征对比分析结果
        """
        feature_comparisons = []
        
        # 提取每个图表的特征信息
        for i in range(len(charts)):
            for j in range(i+1, len(charts)):
                chart1 = charts[i]
                chart2 = charts[j]
                analysis1 = analyses[i]
                analysis2 = analyses[j]
                
                # 获取图表标题
                title1 = chart1.get("title", "未命名图表")
                title2 = chart2.get("title", "未命名图表")
                
                # 确保有系列分析结果
                if "系列分析" not in analysis1 or "系列分析" not in analysis2:
                    continue
                
                # 确保有统计信息
                if (not analysis1["系列分析"] or "统计信息" not in analysis1["系列分析"][0] or 
                    not analysis2["系列分析"] or "统计信息" not in analysis2["系列分析"][0]):
                    continue
                
                # 获取各图表统计信息
                stats1 = analysis1["系列分析"][0]["统计信息"]
                stats2 = analysis2["系列分析"][0]["统计信息"]
                
                # 比较最大值
                max1 = stats1.get("最大值", 0)
                max2 = stats2.get("最大值", 0)
                max_diff = max1 - max2
                max_relative_diff = max_diff / max2 if max2 != 0 else None
                
                # 比较平均值
                avg1 = stats1.get("平均值", 0)
                avg2 = stats2.get("平均值", 0)
                avg_diff = avg1 - avg2
                avg_relative_diff = avg_diff / avg2 if avg2 != 0 else None
                
                # 创建特征对比结果
                comparison = {
                    "图表1": {
                        "标题": title1,
                        "最大值": max1,
                        "平均值": avg1
                    },
                    "图表2": {
                        "标题": title2,
                        "最大值": max2,
                        "平均值": avg2
                    },
                    "最大值差异": {
                        "绝对差异": max_diff,
                        "相对差异": max_relative_diff,
                        "描述": f"{title1}的最大值比{title2}高{abs(max_relative_diff)*100:.1f}%" if max_relative_diff and max_relative_diff > 0 else 
                               f"{title1}的最大值比{title2}低{abs(max_relative_diff)*100:.1f}%" if max_relative_diff and max_relative_diff < 0 else
                               f"{title1}和{title2}的最大值相等"
                    },
                    "平均值差异": {
                        "绝对差异": avg_diff,
                        "相对差异": avg_relative_diff,
                        "描述": f"{title1}的平均值比{title2}高{abs(avg_relative_diff)*100:.1f}%" if avg_relative_diff and avg_relative_diff > 0 else 
                               f"{title1}的平均值比{title2}低{abs(avg_relative_diff)*100:.1f}%" if avg_relative_diff and avg_relative_diff < 0 else
                               f"{title1}和{title2}的平均值相等"
                    }
                }
                
                feature_comparisons.append(comparison)
        
        return feature_comparisons
    
    def _analyze_anomaly_comparison(self, charts: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表的异常点对比
        
        参数:
            charts (List[Dict[str, Any]]): 图表列表
            analyses (List[Dict[str, Any]]): 各图表分析结果
            
        返回:
            List[Dict[str, Any]]: 异常点对比分析结果
        """
        anomaly_comparisons = []
        
        # 提取每个图表的异常点信息
        for i in range(len(charts)):
            for j in range(i+1, len(charts)):
                chart1 = charts[i]
                chart2 = charts[j]
                analysis1 = analyses[i]
                analysis2 = analyses[j]
                
                # 获取图表标题
                title1 = chart1.get("title", "未命名图表")
                title2 = chart2.get("title", "未命名图表")
                
                # 确保有系列分析结果
                if "系列分析" not in analysis1 or "系列分析" not in analysis2:
                    continue
                
                # 确保有异常点信息
                if (not analysis1["系列分析"] or "异常点" not in analysis1["系列分析"][0] or 
                    not analysis2["系列分析"] or "异常点" not in analysis2["系列分析"][0]):
                    continue
                
                # 获取各图表异常点
                anomalies1 = analysis1["系列分析"][0]["异常点"]
                anomalies2 = analysis2["系列分析"][0]["异常点"]
                
                # 计算异常点数量
                anomaly_count1 = len(anomalies1)
                anomaly_count2 = len(anomalies2)
                
                # 创建异常点对比结果
                comparison = {
                    "图表1": {
                        "标题": title1,
                        "异常点数量": anomaly_count1
                    },
                    "图表2": {
                        "标题": title2,
                        "异常点数量": anomaly_count2
                    },
                    "异常点差异": {
                        "差异数量": anomaly_count1 - anomaly_count2,
                        "描述": f"{title1}的异常点数量比{title2}多{anomaly_count1 - anomaly_count2}个" if anomaly_count1 > anomaly_count2 else
                               f"{title1}的异常点数量比{title2}少{anomaly_count2 - anomaly_count1}个" if anomaly_count1 < anomaly_count2 else
                               f"{title1}和{title2}的异常点数量相等"
                    }
                }
                
                anomaly_comparisons.append(comparison)
        
        return anomaly_comparisons
    
    def _analyze_correlations(self, charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表数据的相关性
        
        参数:
            charts (List[Dict[str, Any]]): 图表列表
            
        返回:
            List[Dict[str, Any]]: 相关性分析结果
        """
        correlations = []
        
        # 提取每个图表的数据系列
        for i in range(len(charts)):
            for j in range(i+1, len(charts)):
                chart1 = charts[i]
                chart2 = charts[j]
                
                # 获取图表标题
                title1 = chart1.get("title", "未命名图表")
                title2 = chart2.get("title", "未命名图表")
                
                # 获取图表数据
                data1 = self._extract_chart_data(chart1)
                data2 = self._extract_chart_data(chart2)
                
                # 确保数据长度相同
                if len(data1) != len(data2) or len(data1) < 2:
                    continue
                
                # 计算皮尔逊相关系数
                correlation, p_value = stats.pearsonr(data1, data2)
                correlation_abs = abs(correlation)
                
                # 获取相关性强度描述
                strength = self._describe_correlation_strength(correlation_abs)
                
                # 创建相关性分析结果
                result = {
                    "图表1": {
                        "标题": title1
                    },
                    "图表2": {
                        "标题": title2
                    },
                    "相关性系数": correlation,
                    "相关性绝对值": correlation_abs,
                    "相关性强度": strength,
                    "相关性方向": "正相关" if correlation > 0 else "负相关" if correlation < 0 else "无相关",
                    "p值": p_value,
                    "统计显著性": p_value < 0.05,
                    "描述": f"{title1}和{title2}存在{strength}的{('正相关' if correlation > 0 else '负相关')}关系" if correlation != 0 else
                            f"{title1}和{title2}之间不存在线性相关关系"
                }
                
                correlations.append(result)
        
        return correlations
    
    def _extract_chart_data(self, chart: Dict[str, Any]) -> List[float]:
        """
        从图表数据中提取数值序列
        
        参数:
            chart (Dict[str, Any]): 图表数据
            
        返回:
            List[float]: 数值序列
        """
        chart_type = chart.get("type", "")
        data = chart.get("data", {})
        
        if chart_type == "line" or chart_type == "bar":
            y_axis = data.get("y_axis", {})
            series = y_axis.get("series", [])
            
            if series and "values" in series[0]:
                return series[0]["values"]
        
        # 直接寻找数据中的y值
        if "y" in data and isinstance(data["y"], list):
            return data["y"]
        
        return []
    
    def _describe_correlation_strength(self, correlation_abs: float) -> str:
        """
        描述相关性强度
        
        参数:
            correlation_abs (float): 相关系数绝对值
            
        返回:
            str: 相关性强度描述
        """
        for (lower, upper), description in self.correlation_strength.items():
            if lower <= correlation_abs < upper or (upper == 1.0 and correlation_abs == 1.0):
                return description
        return "未知强度" 