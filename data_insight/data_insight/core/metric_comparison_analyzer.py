"""
指标对比分析器
==========

分析多个指标之间的关系，生成对比分析、相关性分析和指标群组分析结果。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Tuple, Optional, Any
from scipy import stats

from data_insight.core.base_analyzer import BaseAnalyzer


class MetricComparisonAnalyzer(BaseAnalyzer):
    """
    指标对比分析器
    
    分析多个指标之间的关系，包括对比分析、相关性分析和指标群组分析。
    """
    
    def __init__(self):
        """
        初始化指标对比分析器
        """
        super().__init__()
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
        分析多个指标的对比关系
        
        参数:
            data (Dict[str, Any]): 指标数据，应包含以下字段:
                - metrics: 指标列表，每个指标应包含name、values等信息
                - time_periods: 时间周期列表(可选)
                - dimensions: 维度信息(可选)
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证必要字段
        required_fields = ["metrics"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        metrics = data["metrics"]
        time_periods = data.get("time_periods", [])
        dimensions = data.get("dimensions", {})
        
        # 验证指标数量
        if len(metrics) < 2:
            raise ValueError("指标对比分析需要至少两个指标")
        
        # 整合基本信息
        result = {
            "基本信息": {
                "指标数量": len(metrics),
                "指标名称列表": [metric["name"] for metric in metrics],
                "时间周期数": len(time_periods),
                "维度数量": len(dimensions)
            },
            "对比分析": [],
            "相关性分析": [],
            "群组分析": {}
        }
        
        # 执行各类分析
        result["对比分析"] = self._analyze_metric_comparisons(metrics)
        result["相关性分析"] = self._analyze_correlations(metrics, time_periods)
        result["群组分析"] = self._analyze_metric_groups(metrics)
        
        return result
    
    def _analyze_metric_comparisons(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析指标之间的对比关系
        
        参数:
            metrics (List[Dict[str, Any]]): 指标列表
            
        返回:
            List[Dict[str, Any]]: 对比分析结果
        """
        comparisons = []
        
        # 提取当前值进行对比
        for i in range(len(metrics)):
            for j in range(i+1, len(metrics)):
                metric1 = metrics[i]
                metric2 = metrics[j]
                
                # 确保两个指标都有当前值
                if "value" not in metric1 or "value" not in metric2:
                    continue
                
                # 计算差异
                value1 = metric1["value"]
                value2 = metric2["value"]
                absolute_diff = abs(value1 - value2)
                
                # 计算相对差异（如果可能）
                relative_diff = None
                if value2 != 0:
                    relative_diff = (value1 - value2) / value2
                
                # 创建对比结果
                comparison = {
                    "指标1": {
                        "名称": metric1["name"],
                        "当前值": value1,
                        "单位": metric1.get("unit", "")
                    },
                    "指标2": {
                        "名称": metric2["name"],
                        "当前值": value2,
                        "单位": metric2.get("unit", "")
                    },
                    "绝对差异": absolute_diff,
                    "相对差异": relative_diff,
                    "差异方向": "高于" if value1 > value2 else "低于" if value1 < value2 else "相等",
                    "差异大小": self._classify_difference(relative_diff) if relative_diff is not None else "无法比较"
                }
                
                # 添加描述性文本
                if relative_diff is not None:
                    if relative_diff > 0:
                        comparison["描述"] = f"{metric1['name']}比{metric2['name']}高{abs(relative_diff)*100:.1f}%"
                    elif relative_diff < 0:
                        comparison["描述"] = f"{metric1['name']}比{metric2['name']}低{abs(relative_diff)*100:.1f}%"
                    else:
                        comparison["描述"] = f"{metric1['name']}与{metric2['name']}相等"
                
                comparisons.append(comparison)
        
        return comparisons
    
    def _analyze_correlations(self, metrics: List[Dict[str, Any]], time_periods: List[str]) -> List[Dict[str, Any]]:
        """
        分析指标之间的相关性
        
        参数:
            metrics (List[Dict[str, Any]]): 指标列表
            time_periods (List[str]): 时间周期列表
            
        返回:
            List[Dict[str, Any]]: 相关性分析结果
        """
        correlations = []
        
        # 检查是否每个指标都有历史值，如果没有则无法进行相关性分析
        for metric in metrics:
            if "historical_values" not in metric or len(metric["historical_values"]) < 2:
                return correlations  # 返回空列表，表示无法进行相关性分析
        
        # 分析指标对之间的相关性
        for i in range(len(metrics)):
            for j in range(i+1, len(metrics)):
                metric1 = metrics[i]
                metric2 = metrics[j]
                
                # 获取历史值
                values1 = metric1.get("historical_values", [])
                values2 = metric2.get("historical_values", [])
                
                # 确保两个序列长度一致
                min_length = min(len(values1), len(values2))
                if min_length < 2:
                    continue  # 样本太少，跳过
                
                values1 = values1[-min_length:]
                values2 = values2[-min_length:]
                
                # 计算相关系数
                corr_coefficient, p_value = stats.pearsonr(values1, values2)
                
                # 判断相关性显著性
                is_significant = p_value < 0.05
                
                # 创建相关性结果
                correlation = {
                    "指标1": metric1["name"],
                    "指标2": metric2["name"],
                    "相关系数": corr_coefficient,
                    "P值": p_value,
                    "显著性": is_significant,
                    "相关性类型": "正相关" if corr_coefficient > 0 else "负相关" if corr_coefficient < 0 else "无相关",
                    "相关性强度": self._describe_correlation_strength(abs(corr_coefficient)),
                    "样本数量": min_length
                }
                
                # 添加描述性文本
                direction = "正相关" if corr_coefficient > 0 else "负相关" if corr_coefficient < 0 else "不相关"
                strength = self._describe_correlation_strength(abs(corr_coefficient))
                significance = "，且具有统计显著性" if is_significant else "，但不具有统计显著性"
                
                correlation["描述"] = f"{metric1['name']}与{metric2['name']}呈{direction}({strength}){significance}"
                
                correlations.append(correlation)
        
        return correlations
    
    def _analyze_metric_groups(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        将指标分组进行群组分析
        
        参数:
            metrics (List[Dict[str, Any]]): 指标列表
            
        返回:
            Dict[str, Any]: 群组分析结果
        """
        # 初始化结果
        groups = {
            "增长指标": [],
            "下降指标": [],
            "稳定指标": [],
            "异常指标": []
        }
        
        # 根据变化趋势和异常情况分组
        for metric in metrics:
            # 检查是否有变化分析
            if "previous_value" in metric and "value" in metric:
                change_rate = (metric["value"] - metric["previous_value"]) / metric["previous_value"] if metric["previous_value"] != 0 else None
                
                if change_rate is not None:
                    if change_rate > 0.05:  # 增长超过5%
                        groups["增长指标"].append({
                            "指标名称": metric["name"],
                            "变化率": change_rate,
                            "变化值": metric["value"] - metric["previous_value"]
                        })
                    elif change_rate < -0.05:  # 下降超过5%
                        groups["下降指标"].append({
                            "指标名称": metric["name"],
                            "变化率": change_rate,
                            "变化值": metric["value"] - metric["previous_value"]
                        })
                    else:  # 基本稳定
                        groups["稳定指标"].append({
                            "指标名称": metric["name"],
                            "变化率": change_rate,
                            "变化值": metric["value"] - metric["previous_value"]
                        })
            
            # 检查是否为异常
            is_anomaly = metric.get("is_anomaly", False)
            if is_anomaly:
                groups["异常指标"].append({
                    "指标名称": metric["name"],
                    "异常程度": metric.get("anomaly_degree", 0.0),
                    "当前值": metric.get("value")
                })
        
        # 按变化率或异常程度排序
        groups["增长指标"] = sorted(groups["增长指标"], key=lambda x: x["变化率"], reverse=True)
        groups["下降指标"] = sorted(groups["下降指标"], key=lambda x: x["变化率"])
        groups["异常指标"] = sorted(groups["异常指标"], key=lambda x: x["异常程度"], reverse=True)
        
        return groups
    
    def _classify_difference(self, relative_diff: Optional[float]) -> str:
        """
        根据相对差异值分类差异大小
        
        参数:
            relative_diff (Optional[float]): 相对差异值
            
        返回:
            str: 差异大小分类
        """
        if relative_diff is None:
            return "无法比较"
        
        abs_diff = abs(relative_diff)
        
        if abs_diff < 0.05:
            return "微小差异"
        elif abs_diff < 0.2:
            return "小幅差异"
        elif abs_diff < 0.5:
            return "中等差异"
        elif abs_diff < 1.0:
            return "大幅差异"
        else:
            return "巨大差异"
    
    def _describe_correlation_strength(self, correlation_abs: float) -> str:
        """
        描述相关性强度
        
        参数:
            correlation_abs (float): 相关系数的绝对值
            
        返回:
            str: 相关性强度描述
        """
        for (lower, upper), description in self.correlation_strength.items():
            if lower <= correlation_abs < upper:
                return description
        
        return "强相关"  # 默认为强相关（当correlation_abs >= 1.0时） 