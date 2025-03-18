"""
图表分析器
========

分析图表数据，生成趋势、异常点、对比等分析结果。
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.utils.data_utils import (
    calculate_trend,
    detect_anomaly
)


class ChartAnalyzer(BaseAnalyzer):
    """
    图表分析器
    
    分析图表数据，包括趋势分析、异常点检测、关键特征提取等。
    支持线图、柱状图等常见图表类型。
    """
    
    def __init__(self):
        """
        初始化图表分析器
        """
        super().__init__()
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析图表数据
        
        参数:
            data (Dict[str, Any]): 图表数据，应包含以下字段:
                - chart_type: 图表类型，如"line"、"bar"等
                - title: 图表标题
                - data: 图表数据，包含x_axis和y_axis
                  - x_axis: X轴数据，包含label和values
                  - y_axis: Y轴数据，包含label和series(系列数据)
                
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证必要字段
        required_fields = ["chart_type", "title", "data"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        chart_type = data["chart_type"]
        title = data["title"]
        chart_data = data["data"]
        
        # 根据图表类型调用相应的分析方法
        if chart_type == "line":
            return self.analyze_line_chart(title, chart_data)
        elif chart_type == "bar":
            return self.analyze_bar_chart(title, chart_data)
        else:
            return {
                "错误": f"不支持的图表类型: {chart_type}",
                "支持的类型": ["line", "bar"]
            }
    
    def analyze_line_chart(self, title: str, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析线图数据
        
        参数:
            title (str): 图表标题
            chart_data (Dict[str, Any]): 图表数据
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证线图数据格式
        if "x_axis" not in chart_data or "y_axis" not in chart_data:
            raise ValueError("线图数据缺少x_axis或y_axis字段")
        
        x_axis = chart_data["x_axis"]
        y_axis = chart_data["y_axis"]
        
        if "values" not in x_axis or "series" not in y_axis:
            raise ValueError("线图数据格式不正确，缺少values或series字段")
        
        x_values = x_axis.get("values", [])
        x_label = x_axis.get("label", "")
        y_label = y_axis.get("label", "")
        series_list = y_axis.get("series", [])
        
        # 创建基本信息
        result = {
            "基本信息": {
                "图表类型": "线图",
                "图表标题": title,
                "X轴标签": x_label,
                "Y轴标签": y_label,
                "X轴数据点数": len(x_values),
                "系列数": len(series_list)
            },
            "系列分析": []
        }
        
        # 分析每个系列
        all_trends = []
        for series in series_list:
            series_name = series.get("name", "未命名系列")
            series_values = series.get("values", [])
            
            if not series_values or len(series_values) < 2:
                continue
            
            # 趋势分析
            trend_type, trend_strength = calculate_trend(series_values)
            
            # 异常点检测
            anomalies = self._detect_anomalies_in_series(series_values)
            
            # 计算基本统计信息
            max_value = max(series_values)
            max_index = series_values.index(max_value)
            min_value = min(series_values)
            min_index = series_values.index(min_value)
            avg_value = sum(series_values) / len(series_values)
            
            # 计算变化率
            last_value = series_values[-1]
            first_value = series_values[0]
            total_change_rate = (last_value - first_value) / first_value if first_value != 0 else None
            
            # 保存系列分析结果
            series_analysis = {
                "系列名称": series_name,
                "趋势分析": {
                    "趋势类型": trend_type,
                    "趋势强度": trend_strength
                },
                "统计信息": {
                    "最大值": max_value,
                    "最大值位置": x_values[max_index] if max_index < len(x_values) else max_index,
                    "最小值": min_value,
                    "最小值位置": x_values[min_index] if min_index < len(x_values) else min_index,
                    "平均值": avg_value,
                    "总体变化率": total_change_rate
                },
                "异常点": anomalies
            }
            
            result["系列分析"].append(series_analysis)
            all_trends.append(trend_type)
        
        # 添加整体趋势分析
        result["整体分析"] = {
            "整体趋势": self._determine_overall_trend(all_trends)
        }
        
        return result
    
    def analyze_bar_chart(self, title: str, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析柱状图数据
        
        参数:
            title (str): 图表标题
            chart_data (Dict[str, Any]): 图表数据
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 柱状图分析与线图类似，但更关注分类对比而非趋势
        # 基本验证
        if "x_axis" not in chart_data or "y_axis" not in chart_data:
            raise ValueError("柱状图数据缺少x_axis或y_axis字段")
        
        x_axis = chart_data["x_axis"]
        y_axis = chart_data["y_axis"]
        
        if "values" not in x_axis or "series" not in y_axis:
            raise ValueError("柱状图数据格式不正确，缺少values或series字段")
        
        x_values = x_axis.get("values", [])
        x_label = x_axis.get("label", "")
        y_label = y_axis.get("label", "")
        series_list = y_axis.get("series", [])
        
        # 创建基本信息
        result = {
            "基本信息": {
                "图表类型": "柱状图",
                "图表标题": title,
                "X轴标签": x_label,
                "Y轴标签": y_label,
                "X轴类别数": len(x_values),
                "系列数": len(series_list)
            },
            "系列分析": [],
            "类别对比": []
        }
        
        # 分析每个系列
        for series in series_list:
            series_name = series.get("name", "未命名系列")
            series_values = series.get("values", [])
            
            if not series_values:
                continue
            
            # 计算基本统计信息
            max_value = max(series_values)
            max_index = series_values.index(max_value)
            min_value = min(series_values)
            min_index = series_values.index(min_value)
            avg_value = sum(series_values) / len(series_values)
            
            # 计算分布情况
            values_above_avg = len([v for v in series_values if v > avg_value])
            values_below_avg = len([v for v in series_values if v < avg_value])
            
            # 保存系列分析结果
            series_analysis = {
                "系列名称": series_name,
                "统计信息": {
                    "最大值": max_value,
                    "最大值类别": x_values[max_index] if max_index < len(x_values) else max_index,
                    "最小值": min_value,
                    "最小值类别": x_values[min_index] if min_index < len(x_values) else min_index,
                    "平均值": avg_value,
                    "高于平均值的类别数": values_above_avg,
                    "低于平均值的类别数": values_below_avg
                },
                "分布特征": self._determine_distribution_feature(series_values)
            }
            
            result["系列分析"].append(series_analysis)
        
        # 如果只有一个系列，分析各类别的对比情况
        if len(series_list) == 1 and len(x_values) > 1 and len(series_list[0].get("values", [])) == len(x_values):
            series_values = series_list[0].get("values", [])
            category_comparisons = self._analyze_categories(x_values, series_values)
            result["类别对比"] = category_comparisons
        
        return result
    
    def _detect_anomalies_in_series(self, values: List[float]) -> List[Dict[str, Any]]:
        """
        检测系列数据中的异常点
        
        参数:
            values (List[float]): 数据值列表
            
        返回:
            List[Dict[str, Any]]: 异常点列表，每个点包含索引和值
        """
        anomalies = []
        for i, value in enumerate(values):
            # 使用相邻点不包含当前点的列表进行异常检测
            neighboring_values = values[:i] + values[i+1:] if i > 0 and i < len(values) - 1 else values[max(0, i-5):i] + values[i+1:i+6]
            
            if not neighboring_values:
                continue
            
            is_anomaly, anomaly_degree = detect_anomaly(value, neighboring_values)
            if is_anomaly:
                anomalies.append({
                    "索引": i,
                    "值": value,
                    "异常程度": anomaly_degree,
                    "是否高于正常范围": value > np.mean(neighboring_values) if neighboring_values else None
                })
        
        return anomalies
    
    def _determine_overall_trend(self, trends: List[str]) -> str:
        """
        根据所有系列的趋势确定整体趋势
        
        参数:
            trends (List[str]): 所有系列的趋势类型列表
            
        返回:
            str: 整体趋势描述
        """
        if not trends:
            return "无法确定"
        
        # 对趋势进行分类和计数
        upward_trends = ["强烈上升", "上升", "轻微上升"]
        downward_trends = ["强烈下降", "下降", "轻微下降"]
        stable_trends = ["平稳"]
        
        upward_count = sum(1 for t in trends if t in upward_trends)
        downward_count = sum(1 for t in trends if t in downward_trends)
        stable_count = sum(1 for t in trends if t in stable_trends)
        
        # 确定主导趋势
        total = len(trends)
        if upward_count > total / 2:
            return "总体上升"
        elif downward_count > total / 2:
            return "总体下降"
        elif stable_count > total / 2:
            return "总体平稳"
        elif upward_count > downward_count and upward_count > stable_count:
            return "总体趋向上升但不明显"
        elif downward_count > upward_count and downward_count > stable_count:
            return "总体趋向下降但不明显"
        else:
            return "各系列趋势不一致"
    
    def _determine_distribution_feature(self, values: List[float]) -> str:
        """
        确定数据分布特征
        
        参数:
            values (List[float]): 数据值列表
            
        返回:
            str: 分布特征描述
        """
        if not values or len(values) < 2:
            return "数据点不足"
        
        # 计算基本统计量
        mean_value = np.mean(values)
        median_value = np.median(values)
        max_value = max(values)
        min_value = min(values)
        
        # 判断是否有明显的偏斜
        skewness = (mean_value - median_value) / mean_value if mean_value != 0 else 0
        
        # 判断数据的分散程度
        range_value = max_value - min_value
        average_deviation = np.mean([abs(v - mean_value) for v in values])
        relative_deviation = average_deviation / mean_value if mean_value != 0 else 0
        
        # 根据特征确定分布描述
        if abs(skewness) < 0.1:
            if relative_deviation < 0.2:
                return "数据分布均匀且集中"
            else:
                return "数据分布均匀但分散"
        elif skewness > 0:
            if relative_deviation < 0.2:
                return "数据正偏斜且集中"
            else:
                return "数据正偏斜且分散"
        else:
            if relative_deviation < 0.2:
                return "数据负偏斜且集中"
            else:
                return "数据负偏斜且分散"
    
    def _analyze_categories(self, categories: List[str], values: List[float]) -> List[Dict[str, Any]]:
        """
        分析类别之间的对比关系
        
        参数:
            categories (List[str]): 类别名称列表
            values (List[float]): 对应的数据值列表
            
        返回:
            List[Dict[str, Any]]: 类别对比分析结果
        """
        if len(categories) != len(values) or len(categories) < 2:
            return []
        
        mean_value = np.mean(values)
        max_value = max(values)
        min_value = min(values)
        max_index = values.index(max_value)
        min_index = values.index(min_value)
        
        # 计算类别之间的关系
        category_relations = []
        
        # 最大值与平均值的比较
        max_vs_avg = {
            "对比类型": "最大值与平均值",
            "主体类别": categories[max_index],
            "主体值": max_value,
            "对比值": mean_value,
            "差异比例": (max_value - mean_value) / mean_value if mean_value != 0 else None,
            "分析结果": f"{categories[max_index]}显著高于平均水平" if max_value > 1.5 * mean_value else 
                      f"{categories[max_index]}高于平均水平" if max_value > 1.1 * mean_value else
                      f"{categories[max_index]}接近平均水平"
        }
        category_relations.append(max_vs_avg)
        
        # 最小值与平均值的比较
        min_vs_avg = {
            "对比类型": "最小值与平均值",
            "主体类别": categories[min_index],
            "主体值": min_value,
            "对比值": mean_value,
            "差异比例": (min_value - mean_value) / mean_value if mean_value != 0 else None,
            "分析结果": f"{categories[min_index]}显著低于平均水平" if min_value < 0.5 * mean_value else 
                      f"{categories[min_index]}低于平均水平" if min_value < 0.9 * mean_value else
                      f"{categories[min_index]}接近平均水平"
        }
        category_relations.append(min_vs_avg)
        
        # 最大值与最小值的比较
        max_vs_min = {
            "对比类型": "最大值与最小值",
            "主体类别": categories[max_index],
            "对比类别": categories[min_index],
            "主体值": max_value,
            "对比值": min_value,
            "差异比例": (max_value - min_value) / min_value if min_value != 0 else None,
            "分析结果": f"{categories[max_index]}显著高于{categories[min_index]}" if max_value > 3 * min_value else 
                      f"{categories[max_index]}明显高于{categories[min_index]}" if max_value > 1.5 * min_value else
                      f"{categories[max_index]}略高于{categories[min_index]}"
        }
        category_relations.append(max_vs_min)
        
        return category_relations 