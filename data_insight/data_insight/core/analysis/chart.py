"""
图表分析器
========

针对不同类型的图表数据进行专业分析，包括趋势分析、分布分析、异常检测等。
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import statistics
import math
import numpy as np
from scipy import stats
from datetime import datetime

from data_insight.core.analysis.base import BaseAnalyzer


class ChartAnalyzer(BaseAnalyzer):
    """
    图表分析器
    
    针对不同类型的图表数据（线图、柱状图、散点图、饼图等）进行专业分析，
    包括趋势分析、分布分析、异常点检测、相关性分析等。
    """
    
    def __init__(self):
        """初始化图表分析器"""
        super().__init__(name="ChartAnalyzer", version="1.0.0")
        self.logger = logging.getLogger("data_insight.analysis.chart")
        self.supported_chart_types = ["line", "bar", "scatter", "pie"]
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析图表数据
        
        参数:
            data (Dict[str, Any]): 图表数据
            
        返回:
            Dict[str, Any]: 分析结果
            
        异常:
            ValueError: 如果图表类型不受支持或数据格式不正确
        """
        # 验证输入数据
        self.validate_input(data, ["type", "data", "title"])
        
        chart_type = data.get("type")
        chart_data = data.get("data")
        chart_title = data.get("title", "未命名图表")
        
        # 验证图表类型
        if chart_type not in self.supported_chart_types:
            raise ValueError(f"不支持的图表类型: {chart_type}, 支持的类型有: {', '.join(self.supported_chart_types)}")
        
        self.logger.info(f"开始分析 {chart_type} 图表: {chart_title}")
        
        # 根据图表类型选择不同的分析方法
        analysis_result = {}
        
        if chart_type == "line":
            analysis_result = self._analyze_line_chart(chart_data, data)
        elif chart_type == "bar":
            analysis_result = self._analyze_bar_chart(chart_data, data)
        elif chart_type == "scatter":
            analysis_result = self._analyze_scatter_chart(chart_data, data)
        elif chart_type == "pie":
            analysis_result = self._analyze_pie_chart(chart_data, data)
        
        # 添加基本信息
        analysis_result.update({
            "chart_type": chart_type,
            "title": chart_title,
            "分析时间": self._get_timestamp(),
        })
        
        self.logger.info(f"{chart_type} 图表分析完成: {chart_title}")
        
        return self._format_results(analysis_result)
    
    def supports_async(self) -> bool:
        """
        检查分析器是否支持异步处理
        
        返回:
            bool: 当前不支持异步处理
        """
        return False
    
    def get_supported_chart_types(self) -> List[str]:
        """
        获取支持的图表类型
        
        返回:
            List[str]: 支持的图表类型列表
        """
        return self.supported_chart_types.copy()
    
    def _analyze_line_chart(self, chart_data: Dict[str, Any], full_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析线图数据
        
        参数:
            chart_data (Dict[str, Any]): 图表数据
            full_data (Dict[str, Any]): 完整图表数据
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证线图数据
        if "x" not in chart_data or "y" not in chart_data:
            raise ValueError("线图数据必须包含x和y字段")
        
        x_data = chart_data.get("x", [])
        y_data = chart_data.get("y", [])
        
        if len(x_data) != len(y_data):
            raise ValueError("x和y数据长度必须相同")
        
        if len(y_data) < 2:
            raise ValueError("线图数据至少需要2个点")
        
        # 获取x轴和y轴标签
        x_label = full_data.get("x_label", "X轴")
        y_label = full_data.get("y_label", "Y轴")
        
        # 将y值转换为数值列表
        y_values = self._convert_to_numeric(y_data)
        
        # 分析结果
        result = {
            "基本信息": {
                "图表类型": "线图",
                "数据点数": len(y_values),
                "x轴标签": x_label,
                "y轴标签": y_label,
                "x轴范围": [x_data[0], x_data[-1]] if x_data else [],
                "y轴范围": [min(y_values), max(y_values)] if y_values else []
            },
            "统计信息": self._calculate_statistics(y_values),
            "趋势分析": self._analyze_trend(y_values, x_data),
            "异常点": self._detect_anomalies(y_values, x_data)
        }
        
        return result
    
    def _analyze_bar_chart(self, chart_data: Dict[str, Any], full_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析柱状图数据
        
        参数:
            chart_data (Dict[str, Any]): 图表数据
            full_data (Dict[str, Any]): 完整图表数据
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证柱状图数据
        if "x" not in chart_data or "y" not in chart_data:
            raise ValueError("柱状图数据必须包含x和y字段")
        
        x_data = chart_data.get("x", [])
        y_data = chart_data.get("y", [])
        
        if len(x_data) != len(y_data):
            raise ValueError("x和y数据长度必须相同")
        
        # 获取x轴和y轴标签
        x_label = full_data.get("x_label", "X轴")
        y_label = full_data.get("y_label", "Y轴")
        
        # 将y值转换为数值列表
        y_values = self._convert_to_numeric(y_data)
        
        # 分析分布
        distribution_analysis = self._analyze_distribution(y_values, x_data)
        
        # 分析结果
        result = {
            "基本信息": {
                "图表类型": "柱状图",
                "类别数量": len(x_data),
                "x轴标签": x_label,
                "y轴标签": y_label
            },
            "统计信息": self._calculate_statistics(y_values),
            "分布分析": distribution_analysis,
            "异常类别": self._detect_anomalies(y_values, x_data, is_bar_chart=True)
        }
        
        return result
    
    def _analyze_scatter_chart(self, chart_data: Dict[str, Any], full_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析散点图数据
        
        参数:
            chart_data (Dict[str, Any]): 图表数据
            full_data (Dict[str, Any]): 完整图表数据
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证散点图数据
        if "x" not in chart_data or "y" not in chart_data:
            raise ValueError("散点图数据必须包含x和y字段")
        
        x_data = chart_data.get("x", [])
        y_data = chart_data.get("y", [])
        
        if len(x_data) != len(y_data):
            raise ValueError("x和y数据长度必须相同")
        
        # 获取x轴和y轴标签
        x_label = full_data.get("x_label", "X轴")
        y_label = full_data.get("y_label", "Y轴")
        
        # 将x和y值转换为数值列表
        x_values = self._convert_to_numeric(x_data)
        y_values = self._convert_to_numeric(y_data)
        
        # 计算相关性
        correlation_result = self._analyze_correlation(x_values, y_values)
        
        # 执行聚类分析
        clusters_result = self._analyze_clusters(x_values, y_values) if len(x_values) >= 5 else {"聚类数": 0}
        
        # 分析结果
        result = {
            "基本信息": {
                "图表类型": "散点图",
                "数据点数": len(x_values),
                "x轴标签": x_label,
                "y轴标签": y_label,
                "x轴范围": [min(x_values), max(x_values)] if x_values else [],
                "y轴范围": [min(y_values), max(y_values)] if y_values else []
            },
            "x轴统计信息": self._calculate_statistics(x_values),
            "y轴统计信息": self._calculate_statistics(y_values),
            "相关性分析": correlation_result,
            "聚类分析": clusters_result,
            "异常点": self._detect_outliers(x_values, y_values)
        }
        
        return result
    
    def _analyze_pie_chart(self, chart_data: Dict[str, Any], full_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析饼图数据
        
        参数:
            chart_data (Dict[str, Any]): 图表数据
            full_data (Dict[str, Any]): 完整图表数据
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证饼图数据
        if "labels" not in chart_data or "values" not in chart_data:
            raise ValueError("饼图数据必须包含labels和values字段")
        
        labels = chart_data.get("labels", [])
        values = chart_data.get("values", [])
        
        if len(labels) != len(values):
            raise ValueError("labels和values数据长度必须相同")
        
        # 将values转换为数值列表
        values_numeric = self._convert_to_numeric(values)
        
        # 计算总和和比例
        total = sum(values_numeric)
        if total == 0:
            raise ValueError("饼图数据值总和不能为0")
        
        proportions = [value / total for value in values_numeric]
        
        # 找出最大切片和最小切片
        max_idx = proportions.index(max(proportions))
        min_idx = proportions.index(min(proportions))
        
        # 计算分布均匀性（用变异系数的倒数表示，越接近1表示越均匀）
        cv = statistics.stdev(proportions) / statistics.mean(proportions) if len(proportions) > 1 else 0
        uniformity = 1 / (1 + cv) if cv > 0 else 1
        
        # 准备各切片数据
        slices_data = []
        for i, (label, value, proportion) in enumerate(zip(labels, values_numeric, proportions)):
            slices_data.append({
                "标签": label,
                "值": value,
                "比例": proportion,
                "百分比": f"{proportion*100:.2f}%"
            })
        
        # 提取主要类别（比例超过10%的类别）
        main_categories = [slice_data["标签"] for slice_data in slices_data if slice_data["比例"] >= 0.1]
        
        # 分析结果
        result = {
            "基本信息": {
                "图表类型": "饼图",
                "类别数量": len(labels)
            },
            "分布分析": {
                "最大切片": {
                    "名称": labels[max_idx],
                    "值": values_numeric[max_idx],
                    "比例": proportions[max_idx],
                    "百分比": f"{proportions[max_idx]*100:.2f}%"
                },
                "最小切片": {
                    "名称": labels[min_idx],
                    "值": values_numeric[min_idx],
                    "比例": proportions[min_idx],
                    "百分比": f"{proportions[min_idx]*100:.2f}%"
                },
                "分布均匀性": uniformity,
                "主要类别": main_categories,
                "其他类别数量": len(labels) - len(main_categories)
            },
            "切片详情": slices_data
        }
        
        # 分析比例集中度
        if proportions[max_idx] > 0.5:
            result["分布分析"]["比例集中度"] = "高度集中"
            result["分布分析"]["主导类别"] = labels[max_idx]
        elif proportions[max_idx] > 0.3:
            result["分布分析"]["比例集中度"] = "中度集中"
        else:
            result["分布分析"]["比例集中度"] = "分散"
        
        return result
    
    def _convert_to_numeric(self, data: List[Any]) -> List[float]:
        """
        将数据转换为数值列表
        
        参数:
            data (List[Any]): 任意数据列表
            
        返回:
            List[float]: 数值列表
        """
        result = []
        for item in data:
            try:
                result.append(float(item))
            except (ValueError, TypeError):
                self.logger.warning(f"无法将 {item} 转换为数值，使用0代替")
                result.append(0.0)
        return result
    
    def _calculate_statistics(self, values: List[float]) -> Dict[str, Any]:
        """
        计算基本统计信息
        
        参数:
            values (List[float]): 数值列表
            
        返回:
            Dict[str, Any]: 统计信息
        """
        if not values:
            return {"数据点数": 0}
        
        result = {
            "最小值": min(values),
            "最大值": max(values),
            "平均值": statistics.mean(values),
            "中位数": statistics.median(values),
            "总和": sum(values),
            "数据点数": len(values)
        }
        
        # 如果数据点数大于1，计算标准差和四分位值
        if len(values) > 1:
            result["标准差"] = statistics.stdev(values)
            result["变异系数"] = result["标准差"] / result["平均值"] if result["平均值"] != 0 else float('inf')
            
            # 计算四分位值
            sorted_values = sorted(values)
            q1_idx = int(len(values) * 0.25)
            q3_idx = int(len(values) * 0.75)
            result["第一四分位值"] = sorted_values[q1_idx]
            result["第三四分位值"] = sorted_values[q3_idx]
            result["四分位距"] = result["第三四分位值"] - result["第一四分位值"]
        
        return result
    
    def _analyze_trend(self, values: List[float], labels: List[Any] = None) -> Dict[str, Any]:
        """
        分析数据趋势
        
        参数:
            values (List[float]): 数值列表
            labels (List[Any], optional): 对应的标签列表
            
        返回:
            Dict[str, Any]: 趋势分析结果
        """
        if len(values) < 3:
            return {"趋势类型": "数据点不足，无法分析趋势"}
        
        # 计算简单线性回归
        x = list(range(len(values)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # 确定趋势类型
        trend_type = "上升" if slope > 0 else "下降" if slope < 0 else "稳定"
        trend_strength = abs(r_value)
        
        # 评估趋势强度
        if trend_strength > 0.8:
            trend_strength_desc = "强"
        elif trend_strength > 0.5:
            trend_strength_desc = "中等"
        elif trend_strength > 0.3:
            trend_strength_desc = "弱"
        else:
            trend_strength_desc = "无明显趋势"
            
        # 检测是否有季节性模式
        has_seasonality = False
        seasonality_period = 0
        if len(values) >= 8:  # 至少需要8个点来检测季节性
            has_seasonality, seasonality_period = self._detect_seasonality(values)
        
        # 分析最近趋势（使用后半部分数据）
        half_point = len(values) // 2
        if half_point >= 3:  # 确保有足够的数据点
            recent_values = values[half_point:]
            recent_x = list(range(half_point, len(values)))
            recent_slope, _, _, _, _ = stats.linregress(recent_x, recent_values)
            
            # 比较整体趋势和最近趋势
            recent_trend = "加速" if slope > 0 and recent_slope > slope else "减速" if slope > 0 and recent_slope < slope else "反转" if slope * recent_slope < 0 else "持续"
        else:
            recent_trend = "数据点不足，无法分析最近趋势"
        
        result = {
            "主要趋势": trend_type,
            "趋势强度": trend_strength,
            "趋势强度描述": trend_strength_desc,
            "趋势显著性": p_value < 0.05,
            "相关系数": r_value,
            "显著性p值": p_value,
            "斜率": slope,
            "截距": intercept,
            "最近趋势": recent_trend,
            "季节性": has_seasonality
        }
        
        if has_seasonality:
            result["季节周期"] = seasonality_period
        
        # 计算趋势变化点
        if len(values) >= 5:
            change_points = self._detect_trend_change_points(values)
            if change_points:
                result["趋势变化点"] = []
                for idx in change_points:
                    point_info = {
                        "位置": idx,
                        "值": values[idx]
                    }
                    if labels and idx < len(labels):
                        point_info["标签"] = labels[idx]
                    result["趋势变化点"].append(point_info)
        
        return result
    
    def _detect_seasonality(self, values: List[float]) -> Tuple[bool, int]:
        """
        检测时间序列的季节性
        
        参数:
            values (List[float]): 数值列表
            
        返回:
            Tuple[bool, int]: (是否存在季节性, 季节周期)
        """
        # 这里使用简化的方法来检测季节性
        # 对于更复杂的季节性检测，可以使用FFT或自相关函数
        
        # 尝试不同的可能周期（从2到len(values)/2）
        max_period = min(len(values) // 2, 12)  # 最多检测到12个周期
        best_period = 0
        best_correlation = 0
        
        for period in range(2, max_period + 1):
            # 计算当前周期的自相关
            shifted_values = values[period:] + [0] * period
            shifted_values = shifted_values[:len(values)]
            
            # 计算相关系数
            correlation = abs(np.corrcoef(values, shifted_values)[0, 1])
            
            if correlation > best_correlation and correlation > 0.5:  # 只考虑强相关
                best_correlation = correlation
                best_period = period
        
        # 如果找到了较强的周期性相关，则认为存在季节性
        return best_correlation > 0.5, best_period
    
    def _detect_trend_change_points(self, values: List[float]) -> List[int]:
        """
        检测趋势变化点
        
        参数:
            values (List[float]): 数值列表
            
        返回:
            List[int]: 变化点索引列表
        """
        if len(values) < 5:
            return []
        
        # 计算一阶差分
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # 计算差分的变化点（符号变化）
        change_points = []
        for i in range(1, len(diffs)):
            if diffs[i] * diffs[i-1] < 0:  # 符号变化
                change_points.append(i)
        
        # 只保留显著的变化点（变化幅度大的）
        significant_points = []
        if change_points:
            # 计算平均变化幅度
            avg_change = sum(abs(diffs)) / len(diffs)
            
            for point in change_points:
                if point < len(diffs) and abs(diffs[point]) > avg_change * 1.5:
                    significant_points.append(point)
        
        return significant_points
    
    def _detect_anomalies(self, values: List[float], labels: List[Any] = None, is_bar_chart: bool = False) -> List[Dict[str, Any]]:
        """
        检测异常点
        
        参数:
            values (List[float]): 数值列表
            labels (List[Any], optional): 对应的标签列表
            is_bar_chart (bool, optional): 是否是柱状图数据
            
        返回:
            List[Dict[str, Any]]: 异常点列表
        """
        if len(values) < 3:
            return []
        
        anomalies = []
        
        # 计算统计量
        mean_value = statistics.mean(values)
        if len(values) > 1:
            std_dev = statistics.stdev(values)
            
            # 使用Z分数法检测异常点
            for i, value in enumerate(values):
                z_score = (value - mean_value) / std_dev if std_dev > 0 else 0
                
                # Z分数绝对值大于2.5视为异常
                if abs(z_score) > 2.5:
                    anomaly = {
                        "位置": i,
                        "值": value,
                        "Z分数": z_score,
                        "异常程度": "高" if abs(z_score) > 3.5 else "中" if abs(z_score) > 3 else "低"
                    }
                    
                    if labels and i < len(labels):
                        anomaly["标签"] = labels[i]
                    
                    anomalies.append(anomaly)
        
        # 对于柱状图，也检测比例异常
        if is_bar_chart and len(values) > 0:
            total = sum(values)
            if total > 0:
                # 计算每个值占总和的比例
                proportions = [value / total for value in values]
                
                # 计算比例的平均值和标准差
                mean_prop = 1.0 / len(values)  # 期望的均匀分布
                
                # 检查比例异常（超过期望的3倍或小于期望的1/3）
                for i, prop in enumerate(proportions):
                    if prop > mean_prop * 3 or prop < mean_prop / 3:
                        # 如果这个位置已经被检测为异常，则更新信息而不是添加新条目
                        existing = next((a for a in anomalies if a["位置"] == i), None)
                        
                        if existing:
                            existing["比例异常"] = True
                            existing["比例"] = prop
                            existing["期望比例"] = mean_prop
                        else:
                            anomaly = {
                                "位置": i,
                                "值": values[i],
                                "比例异常": True,
                                "比例": prop,
                                "期望比例": mean_prop
                            }
                            
                            if labels and i < len(labels):
                                anomaly["标签"] = labels[i]
                            
                            anomalies.append(anomaly)
        
        return anomalies
    
    def _analyze_distribution(self, values: List[float], categories: List[str] = None) -> Dict[str, Any]:
        """
        分析数据分布
        
        参数:
            values (List[float]): 数值列表
            categories (List[str], optional): 类别列表
            
        返回:
            Dict[str, Any]: 分布分析结果
        """
        if len(values) < 2:
            return {"分布类型": "数据点不足，无法分析分布"}
        
        # 计算分布统计量
        skewness = stats.skew(values)
        kurtosis = stats.kurtosis(values)
        
        # 确定分布类型
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            distribution_type = "近似正态分布"
        elif skewness > 0.5:
            distribution_type = "右偏分布"
        elif skewness < -0.5:
            distribution_type = "左偏分布"
        else:
            distribution_type = "无法确定分布类型"
        
        # 找出最大值和最小值的位置
        max_idx = values.index(max(values))
        min_idx = values.index(min(values))
        
        # 计算熵（分布的均匀程度）
        total = sum(values)
        entropy = 0
        if total > 0:
            proportions = [v / total for v in values]
            for p in proportions:
                if p > 0:
                    entropy -= p * math.log2(p)
            
            # 归一化熵值，使其范围在[0,1]
            max_entropy = math.log2(len(values))
            entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        result = {
            "分布类型": distribution_type,
            "偏度": skewness,
            "峰度": kurtosis,
            "熵值": entropy,
            "最大值位置": max_idx,
            "最小值位置": min_idx
        }
        
        # 如果提供了类别信息，添加到结果中
        if categories:
            if max_idx < len(categories):
                result["最大值类别"] = categories[max_idx]
            if min_idx < len(categories):
                result["最小值类别"] = categories[min_idx]
            
            # 提取主要类别（值大于平均值的类别）
            mean_value = statistics.mean(values)
            main_categories = [categories[i] for i in range(len(values)) if values[i] > mean_value and i < len(categories)]
            
            result["主要类别"] = main_categories
            result["类别总数"] = len(categories)
        
        return result
    
    def _analyze_correlation(self, x_values: List[float], y_values: List[float]) -> Dict[str, Any]:
        """
        分析两组数据的相关性
        
        参数:
            x_values (List[float]): X轴数值列表
            y_values (List[float]): Y轴数值列表
            
        返回:
            Dict[str, Any]: 相关性分析结果
        """
        if len(x_values) < 3 or len(y_values) < 3:
            return {"相关性类型": "数据点不足，无法分析相关性"}
        
        # 计算皮尔逊相关系数
        correlation, p_value = stats.pearsonr(x_values, y_values)
        
        # 确定相关性类型
        if abs(correlation) < 0.2:
            correlation_type = "无明显相关"
        elif correlation > 0:
            correlation_type = "正相关"
        else:
            correlation_type = "负相关"
        
        # 评估相关性强度
        if abs(correlation) > 0.8:
            strength = "强"
        elif abs(correlation) > 0.5:
            strength = "中等"
        elif abs(correlation) > 0.2:
            strength = "弱"
        else:
            strength = "无"
        
        return {
            "相关性系数": correlation,
            "相关性类型": correlation_type,
            "相关性强度": abs(correlation),
            "强度描述": strength,
            "显著性p值": p_value,
            "显著性": p_value < 0.05
        }
    
    def _analyze_clusters(self, x_values: List[float], y_values: List[float]) -> Dict[str, Any]:
        """
        分析数据点的聚类情况
        
        参数:
            x_values (List[float]): X轴数值列表
            y_values (List[float]): Y轴数值列表
            
        返回:
            Dict[str, Any]: 聚类分析结果
        """
        if len(x_values) < 5 or len(y_values) < 5:
            return {"聚类数": 0, "聚类结果": "数据点不足，无法进行聚类分析"}
        
        try:
            # 使用简化的方法来检测聚类
            # 实际应用中可以使用K-means或DBSCAN等算法
            
            # 将数据组合为点坐标
            points = np.array(list(zip(x_values, y_values)))
            
            # 估计簇数
            # 这里使用间距统计的简化方法
            distances = []
            for i in range(len(points)):
                for j in range(i+1, len(points)):
                    distances.append(np.linalg.norm(points[i] - points[j]))
            
            # 计算距离的平均值和标准差
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            
            # 如果距离变异大，可能存在簇
            cv_distance = std_distance / avg_distance if avg_distance > 0 else 0
            
            # 基于变异系数估计簇数
            if cv_distance > 0.5:
                estimated_clusters = max(2, int(cv_distance * 3))
                if estimated_clusters > len(points) // 5:  # 限制最大簇数
                    estimated_clusters = len(points) // 5
                
                # 确保簇数至少为1
                estimated_clusters = max(1, estimated_clusters)
            else:
                estimated_clusters = 1
            
            return {
                "聚类数": estimated_clusters,
                "聚类特征": "明显" if cv_distance > 0.7 else "轻微" if cv_distance > 0.3 else "不明显",
                "距离变异系数": cv_distance
            }
            
        except Exception as e:
            self.logger.warning(f"聚类分析失败: {str(e)}")
            return {"聚类数": 0, "聚类结果": f"聚类分析失败: {str(e)}"}
    
    def _detect_outliers(self, x_values: List[float], y_values: List[float]) -> List[Dict[str, Any]]:
        """
        检测散点图中的离群点
        
        参数:
            x_values (List[float]): X轴数值列表
            y_values (List[float]): Y轴数值列表
            
        返回:
            List[Dict[str, Any]]: 离群点列表
        """
        if len(x_values) < 5 or len(y_values) < 5:
            return []
        
        outliers = []
        
        try:
            # 将数据组合为点坐标
            points = np.array(list(zip(x_values, y_values)))
            
            # 计算每个点到其他点的平均距离
            avg_distances = []
            for i, point in enumerate(points):
                distances = [np.linalg.norm(point - other_point) for j, other_point in enumerate(points) if i != j]
                avg_distances.append(np.mean(distances))
            
            # 计算平均距离的平均值和标准差
            mean_distance = np.mean(avg_distances)
            std_distance = np.std(avg_distances)
            
            # 检测离群点（平均距离超过2个标准差）
            for i, (x, y, dist) in enumerate(zip(x_values, y_values, avg_distances)):
                if dist > mean_distance + 2 * std_distance:
                    z_score = (dist - mean_distance) / std_distance if std_distance > 0 else 0
                    outliers.append({
                        "位置": i,
                        "x值": x,
                        "y值": y,
                        "Z分数": z_score,
                        "异常程度": "高" if z_score > 3 else "中等" if z_score > 2.5 else "低"
                    })
                    
        except Exception as e:
            self.logger.warning(f"离群点检测失败: {str(e)}")
        
        return outliers 