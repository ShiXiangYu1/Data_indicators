"""
指标分析器
========

分析单个指标数据，识别趋势、异常和变化情况。
"""

from typing import Dict, Any, List, Optional, Union
import logging
import statistics
import math
from datetime import datetime

from data_insight.core.analysis.base import BaseAnalyzer


class MetricAnalyzer(BaseAnalyzer):
    """
    指标分析器
    
    分析单个指标的各种特征，包括变化率、趋势、异常值等。
    """
    
    def __init__(self):
        """初始化指标分析器"""
        super().__init__(name="MetricAnalyzer", version="1.0.0")
        self.logger = logging.getLogger("data_insight.analysis.metric")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标数据
        
        参数:
            data (Dict[str, Any]): 需要分析的数据，应包含以下字段:
                - metric: 指标数据，包括name、value、previous_value等
                - context: 上下文信息(可选)
                
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证输入数据
        required_fields = ["metric"]
        self.validate_input(data, required_fields)
        
        # 提取指标数据和上下文
        metric = data["metric"]
        context = data.get("context", {})
        
        # 验证指标数据必须包含name和value
        if "name" not in metric or "value" not in metric:
            raise ValueError("指标数据必须包含name和value字段")
        
        # 获取当前值和指标名称
        current_value = metric["value"]
        metric_name = metric["name"]
        
        self.logger.info(f"开始分析指标: {metric_name}")
        
        # 分析结果
        result = {
            "基本信息": {
                "指标名称": metric_name,
                "当前值": current_value,
                "单位": metric.get("unit", ""),
                "时间周期": metric.get("time_period", "未知")
            },
            "变化分析": self._analyze_change(metric),
            "趋势分析": self._analyze_trend(metric),
            "异常检测": self._analyze_anomalies(metric),
            "统计信息": self._calculate_statistics(metric)
        }
        
        # 格式化结果
        formatted_result = self._format_results(result)
        
        self.logger.info(f"指标分析完成: {metric_name}")
        
        return formatted_result
    
    def _analyze_change(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标变化情况
        
        参数:
            metric (Dict[str, Any]): 指标数据
            
        返回:
            Dict[str, Any]: 变化分析结果
        """
        result = {}
        
        # 当前值
        current_value = metric["value"]
        
        # 分析环比变化
        if "previous_value" in metric and metric["previous_value"] is not None:
            previous_value = metric["previous_value"]
            
            # 计算变化量和变化率
            change = current_value - previous_value
            if previous_value != 0:
                change_rate = (change / previous_value) * 100
            else:
                change_rate = float('inf') if change > 0 else float('-inf') if change < 0 else 0
            
            # 添加到结果
            result["环比变化量"] = change
            result["环比变化率"] = change_rate
            result["变化方向"] = "上升" if change > 0 else "下降" if change < 0 else "持平"
            result["前期值"] = previous_value
            result["前期时间周期"] = metric.get("previous_time_period", "未知")
        
        # 如果有目标值，分析目标达成情况
        if "target_value" in metric and metric["target_value"] is not None:
            target_value = metric["target_value"]
            
            # 计算目标差距和达成率
            target_gap = current_value - target_value
            if target_value != 0:
                achievement_rate = (current_value / target_value) * 100
            else:
                achievement_rate = float('inf') if current_value > 0 else float('-inf') if current_value < 0 else 0
            
            # 添加到结果
            result["目标值"] = target_value
            result["目标差距"] = target_gap
            result["目标达成率"] = achievement_rate
            result["是否达标"] = target_gap >= 0
        
        return result
    
    def _analyze_trend(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标趋势
        
        参数:
            metric (Dict[str, Any]): 指标数据
            
        返回:
            Dict[str, Any]: 趋势分析结果
        """
        result = {}
        
        # 只有当有历史值时才能分析趋势
        if "historical_values" in metric and isinstance(metric["historical_values"], list) and len(metric["historical_values"]) >= 3:
            historical_values = metric["historical_values"]
            
            # 计算简单线性回归
            n = len(historical_values)
            x_values = list(range(1, n + 1))
            y_values = historical_values
            
            # 计算斜率和截距
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # 拟合值和R方
                y_fit = [slope * x + intercept for x in x_values]
                ss_total = sum((y - y_mean) ** 2 for y in y_values)
                ss_residual = sum((y - yf) ** 2 for y, yf in zip(y_values, y_fit))
                
                if ss_total != 0:
                    r_squared = 1 - (ss_residual / ss_total)
                else:
                    r_squared = 0
                
                # 判断趋势类型
                if abs(slope) < 0.01 * (max(y_values) - min(y_values)) / n:
                    trend_type = "稳定"
                elif slope > 0:
                    trend_type = "上升"
                else:
                    trend_type = "下降"
                
                # 计算最近的变化
                recent_values = historical_values[-3:] if len(historical_values) >= 3 else historical_values
                recent_diffs = [recent_values[i] - recent_values[i - 1] for i in range(1, len(recent_values))]
                recent_trend = "加速" if all(d > 0 for d in recent_diffs) and len(recent_diffs) >= 2 and recent_diffs[-1] > recent_diffs[0] else \
                             "减速" if all(d > 0 for d in recent_diffs) and len(recent_diffs) >= 2 and recent_diffs[-1] < recent_diffs[0] else \
                             "波动" if any(d > 0 for d in recent_diffs) and any(d < 0 for d in recent_diffs) else \
                             "稳定"
                
                # 添加到结果
                result["趋势类型"] = trend_type
                result["斜率"] = slope
                result["拟合优度"] = r_squared
                result["最近趋势"] = recent_trend
            else:
                result["趋势类型"] = "无法确定"
        else:
            result["趋势类型"] = "数据不足"
        
        return result
    
    def _analyze_anomalies(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测指标异常
        
        参数:
            metric (Dict[str, Any]): 指标数据
            
        返回:
            Dict[str, Any]: 异常检测结果
        """
        result = {}
        
        # 只有当有历史值时才能检测异常
        if "historical_values" in metric and isinstance(metric["historical_values"], list) and len(metric["historical_values"]) >= 5:
            historical_values = metric["historical_values"]
            current_value = metric["value"]
            
            # 计算均值和标准差
            mean = statistics.mean(historical_values)
            if len(historical_values) > 1:
                std_dev = statistics.stdev(historical_values)
            else:
                std_dev = 0
            
            # 如果标准差为0，设置一个小的值以避免除以零
            if std_dev == 0:
                std_dev = 0.0001 * mean if mean != 0 else 0.0001
            
            # 计算Z分数
            z_score = (current_value - mean) / std_dev if std_dev != 0 else 0
            
            # 判断是否为异常
            is_anomaly = abs(z_score) > 2
            
            # 添加到结果
            result["是否异常"] = is_anomaly
            result["Z分数"] = z_score
            result["异常程度"] = "严重" if abs(z_score) > 3 else "中等" if abs(z_score) > 2 else "轻微" if abs(z_score) > 1 else "正常"
            result["相对偏离度"] = (current_value - mean) / mean if mean != 0 else 0
        else:
            result["是否异常"] = "数据不足"
        
        return result
    
    def _calculate_statistics(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算统计信息
        
        参数:
            metric (Dict[str, Any]): 指标数据
            
        返回:
            Dict[str, Any]: 统计信息
        """
        result = {}
        
        # 如果有历史值，计算统计信息
        if "historical_values" in metric and isinstance(metric["historical_values"], list) and len(metric["historical_values"]) > 0:
            historical_values = metric["historical_values"]
            
            # 基本统计量
            result["最小值"] = min(historical_values)
            result["最大值"] = max(historical_values)
            result["平均值"] = statistics.mean(historical_values)
            
            # 如果有足够的数据点，计算中位数和标准差
            if len(historical_values) > 1:
                result["中位数"] = statistics.median(historical_values)
                result["标准差"] = statistics.stdev(historical_values)
                result["变异系数"] = result["标准差"] / result["平均值"] if result["平均值"] != 0 else 0
            
            # 计算环比增长率
            if len(historical_values) >= 2:
                growth_rates = [(historical_values[i] - historical_values[i - 1]) / historical_values[i - 1] * 100 
                              if historical_values[i - 1] != 0 else float('inf') 
                              for i in range(1, len(historical_values))]
                
                if growth_rates:
                    result["平均环比增长率"] = statistics.mean(growth_rates)
        
        return result
    
    def supports_async(self) -> bool:
        """
        是否支持异步处理
        
        返回:
            bool: 总是返回False，指标分析器不支持异步处理
        """
        return False 