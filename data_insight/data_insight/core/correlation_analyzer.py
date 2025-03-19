#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
相关性分析器
===========

用于分析指标间的相关性，支持各种相关性计算方法。
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats
import logging

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.models.insight_model import CorrelationResult, CorrelationItem
from data_insight.utils.data_processor import validate_data, normalize_data


class CorrelationAnalyzer(BaseAnalyzer):
    """
    相关性分析器
    
    用于分析指标之间的相关性，支持各种相关性计算方法，如皮尔逊相关系数、斯皮尔曼等级相关和肯德尔秩相关等。
    还支持时间延迟相关性分析，可以检测指标变化的滞后效应。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化相关性分析器
        
        参数:
            config (Dict[str, Any], optional): 分析器配置
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    def analyze(self,
               primary_metric: Dict[str, Any],
               secondary_metrics: List[Dict[str, Any]],
               time_periods: Optional[List[str]] = None,
               correlation_method: str = 'pearson',
               lag: int = 0,
               significance_level: float = 0.05) -> CorrelationResult:
        """
        分析指标之间的相关性
        
        参数:
            primary_metric (Dict[str, Any]): 主要指标，包含名称和值列表
            secondary_metrics (List[Dict[str, Any]]): 次要指标列表，每个包含名称和值列表
            time_periods (List[str], optional): 时间周期列表，与值列表长度相同
            correlation_method (str): 相关性计算方法，可选 'pearson', 'spearman', 'kendall'
            lag (int): 时间延迟，用于检测滞后效应
            significance_level (float): 显著性水平，默认为0.05
            
        返回:
            CorrelationResult: 相关性分析结果
        
        示例:
            >>> analyzer = CorrelationAnalyzer()
            >>> result = analyzer.analyze(
            ...     primary_metric={"name": "销售额", "values": [100, 120, 140, 130, 150]},
            ...     secondary_metrics=[
            ...         {"name": "广告投入", "values": [50, 60, 65, 70, 75]},
            ...         {"name": "网站访问量", "values": [1000, 1200, 1400, 1300, 1500]}
            ...     ],
            ...     time_periods=["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
            ...     correlation_method="pearson"
            ... )
        """
        self.logger.info(f"开始相关性分析，主指标: {primary_metric['name']}, 方法: {correlation_method}")
        
        # 验证输入数据
        self._validate_inputs(primary_metric, secondary_metrics, time_periods)
        
        # 获取主指标数据
        primary_values = primary_metric['values']
        primary_name = primary_metric['name']
        
        # 初始化结果列表
        correlations = []
        
        # 计算每个次要指标与主要指标的相关性
        for secondary_metric in secondary_metrics:
            secondary_name = secondary_metric['name']
            secondary_values = secondary_metric['values']
            
            # 处理时间延迟
            if lag != 0:
                primary_values_lagged, secondary_values_lagged = self._apply_lag(
                    primary_values, secondary_values, lag
                )
            else:
                primary_values_lagged, secondary_values_lagged = primary_values, secondary_values
            
            # 计算相关性
            correlation, p_value = self._compute_correlation(
                primary_values_lagged, 
                secondary_values_lagged, 
                correlation_method
            )
            
            # 判断是否显著
            is_significant = p_value < significance_level
            
            # 创建相关性项
            correlation_item = CorrelationItem(
                primary_metric=primary_name,
                secondary_metric=secondary_name,
                correlation=round(float(correlation), 3),
                p_value=round(float(p_value), 4),
                is_significant=is_significant,
                lag=lag
            )
            
            correlations.append(correlation_item)
        
        # 生成摘要文本
        summary = self._generate_summary(correlations, primary_name)
        
        # 创建结果对象
        result = CorrelationResult(
            correlations=correlations,
            summary=summary
        )
        
        self.logger.info(f"相关性分析完成，发现 {len(correlations)} 个相关性")
        return result
    
    def _validate_inputs(self, 
                        primary_metric: Dict[str, Any], 
                        secondary_metrics: List[Dict[str, Any]],
                        time_periods: Optional[List[str]]) -> None:
        """
        验证输入数据
        
        参数:
            primary_metric (Dict[str, Any]): 主要指标
            secondary_metrics (List[Dict[str, Any]]): 次要指标列表
            time_periods (List[str], optional): 时间周期列表
            
        异常:
            ValueError: 当输入数据无效时
        """
        # 检查主要指标
        if 'name' not in primary_metric or 'values' not in primary_metric:
            raise ValueError("主要指标必须包含'name'和'values'字段")
        
        if not isinstance(primary_metric['values'], list):
            raise ValueError("主要指标的'values'必须是列表")
        
        if len(primary_metric['values']) < 3:
            raise ValueError("计算相关性至少需要3个数据点")
        
        # 检查次要指标
        for idx, metric in enumerate(secondary_metrics):
            if 'name' not in metric or 'values' not in metric:
                raise ValueError(f"次要指标 #{idx+1} 必须包含'name'和'values'字段")
            
            if not isinstance(metric['values'], list):
                raise ValueError(f"次要指标 '{metric['name']}' 的'values'必须是列表")
            
            if len(metric['values']) != len(primary_metric['values']):
                raise ValueError(f"次要指标 '{metric['name']}' 的数据点数量与主要指标不一致")
        
        # 检查时间周期
        if time_periods is not None:
            if len(time_periods) != len(primary_metric['values']):
                raise ValueError("时间周期数量与数据点数量不一致")
    
    def _apply_lag(self, 
                  primary_values: List[float], 
                  secondary_values: List[float], 
                  lag: int) -> Tuple[List[float], List[float]]:
        """
        应用时间延迟
        
        参数:
            primary_values (List[float]): 主要指标值列表
            secondary_values (List[float]): 次要指标值列表
            lag (int): 时间延迟
            
        返回:
            Tuple[List[float], List[float]]: 处理后的主要指标和次要指标值列表
        """
        if lag > 0:
            # 正延迟：secondary_values的变化滞后于primary_values
            return primary_values[:-lag], secondary_values[lag:]
        elif lag < 0:
            # 负延迟：primary_values的变化滞后于secondary_values
            return primary_values[-lag:], secondary_values[:lag]
        else:
            # 无延迟
            return primary_values, secondary_values
    
    def _compute_correlation(self, 
                           x: List[float], 
                           y: List[float], 
                           method: str) -> Tuple[float, float]:
        """
        计算相关性
        
        参数:
            x (List[float]): 第一个指标值列表
            y (List[float]): 第二个指标值列表
            method (str): 相关性计算方法
            
        返回:
            Tuple[float, float]: 相关系数和p值
            
        异常:
            ValueError: 当方法无效时
        """
        # 转换为numpy数组
        x_array = np.array(x, dtype=float)
        y_array = np.array(y, dtype=float)
        
        # 根据方法计算相关性
        if method == 'pearson':
            return stats.pearsonr(x_array, y_array)
        elif method == 'spearman':
            return stats.spearmanr(x_array, y_array)
        elif method == 'kendall':
            return stats.kendalltau(x_array, y_array)
        else:
            raise ValueError(f"不支持的相关性计算方法: {method}")
    
    def _generate_summary(self, 
                         correlations: List[CorrelationItem], 
                         primary_name: str) -> str:
        """
        生成摘要文本
        
        参数:
            correlations (List[CorrelationItem]): 相关性项列表
            primary_name (str): 主要指标名称
            
        返回:
            str: 摘要文本
        """
        # 筛选显著的相关性
        significant_correlations = [c for c in correlations if c.is_significant]
        
        if not significant_correlations:
            return f"{primary_name}与所分析的指标之间未发现显著相关性"
        
        # 按相关性绝对值排序
        sorted_correlations = sorted(
            significant_correlations, 
            key=lambda x: abs(x.correlation), 
            reverse=True
        )
        
        # 取最强的相关性
        strongest = sorted_correlations[0]
        
        # 生成相关性描述
        if strongest.correlation > 0.7:
            strength = "强正相关"
        elif strongest.correlation > 0.3:
            strength = "中等正相关"
        elif strongest.correlation > 0:
            strength = "弱正相关"
        elif strongest.correlation > -0.3:
            strength = "弱负相关"
        elif strongest.correlation > -0.7:
            strength = "中等负相关"
        else:
            strength = "强负相关"
        
        # 生成滞后描述
        lag_desc = ""
        if strongest.lag > 0:
            lag_desc = f"，滞后{strongest.lag}个时间单位"
        elif strongest.lag < 0:
            lag_desc = f"，提前{abs(strongest.lag)}个时间单位"
        
        # 生成摘要
        summary = f"{primary_name}与{strongest.secondary_metric}存在显著的{strength}{lag_desc}"
        
        # 如果有多个显著相关性，添加额外信息
        if len(significant_correlations) > 1:
            other_metrics = [c.secondary_metric for c in sorted_correlations[1:3]]
            summary += f"，此外还与{', '.join(other_metrics)}等指标存在显著相关性"
        
        return summary
    
    def get_lagged_correlations(self,
                              primary_metric: Dict[str, Any],
                              secondary_metrics: List[Dict[str, Any]],
                              max_lag: int = 3,
                              correlation_method: str = 'pearson',
                              significance_level: float = 0.05) -> Dict[str, List[CorrelationItem]]:
        """
        获取不同滞后值的相关性
        
        参数:
            primary_metric (Dict[str, Any]): 主要指标
            secondary_metrics (List[Dict[str, Any]]): 次要指标列表
            max_lag (int): 最大滞后值
            correlation_method (str): 相关性计算方法
            significance_level (float): 显著性水平
            
        返回:
            Dict[str, List[CorrelationItem]]: 每个次要指标的不同滞后值相关性
        """
        results = {}
        
        for secondary_metric in secondary_metrics:
            secondary_name = secondary_metric['name']
            correlations = []
            
            # 计算不同滞后值的相关性
            for lag in range(-max_lag, max_lag + 1):
                # 分析当前滞后值
                result = self.analyze(
                    primary_metric=primary_metric,
                    secondary_metrics=[secondary_metric],
                    correlation_method=correlation_method,
                    lag=lag,
                    significance_level=significance_level
                )
                
                if result.correlations:
                    correlations.append(result.correlations[0])
            
            # 存储结果
            results[secondary_name] = correlations
        
        return results
    
    def find_optimal_lag(self,
                       primary_metric: Dict[str, Any],
                       secondary_metric: Dict[str, Any],
                       max_lag: int = 3,
                       correlation_method: str = 'pearson',
                       significance_level: float = 0.05) -> Tuple[int, float]:
        """
        找到最优滞后值
        
        参数:
            primary_metric (Dict[str, Any]): 主要指标
            secondary_metric (Dict[str, Any]): 次要指标
            max_lag (int): 最大滞后值
            correlation_method (str): 相关性计算方法
            significance_level (float): 显著性水平
            
        返回:
            Tuple[int, float]: 最优滞后值和对应的相关系数
        """
        best_lag = 0
        best_corr = 0
        
        # 计算不同滞后值的相关性
        lagged_results = self.get_lagged_correlations(
            primary_metric=primary_metric,
            secondary_metrics=[secondary_metric],
            max_lag=max_lag,
            correlation_method=correlation_method,
            significance_level=significance_level
        )
        
        if secondary_metric['name'] in lagged_results:
            correlations = lagged_results[secondary_metric['name']]
            
            # 筛选显著的相关性
            significant_correlations = [c for c in correlations if c.is_significant]
            
            if significant_correlations:
                # 找到相关性绝对值最大的滞后值
                best_item = max(significant_correlations, key=lambda x: abs(x.correlation))
                best_lag = best_item.lag
                best_corr = best_item.correlation
        
        return best_lag, best_corr 