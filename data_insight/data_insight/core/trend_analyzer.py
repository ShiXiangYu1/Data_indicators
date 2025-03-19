#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
趋势分析器
=========

用于分析时间序列数据的趋势特征，包括趋势方向、强度、持续性和拐点检测等。
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.nonparametric.smoothers_lowess import lowess

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.models.insight_model import TrendResult, TrendItem, TrendPattern, TrendInflection
from data_insight.utils.data_processor import validate_data, normalize_data, detect_frequency


class TrendAnalyzer(BaseAnalyzer):
    """
    趋势分析器
    
    用于分析时间序列数据的趋势特征，包括趋势方向、强度、持续性和拐点检测等。
    支持多种趋势分析方法，包括简单线性趋势、指数平滑、LOWESS平滑和季节性分解等。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化趋势分析器
        
        参数:
            config (Dict[str, Any], optional): 分析器配置
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # 设置默认趋势检测阈值
        self.config = {
            'slope_threshold': 0.01,  # 斜率被视为趋势的阈值
            'r2_threshold': 0.6,      # R²被视为显著趋势的阈值
            'window_size': 5,          # 移动窗口大小
            'lowess_frac': 0.3,        # LOWESS平滑参数
            'inflection_sensitivity': 0.2,  # 拐点检测敏感度
            **({} if config is None else config)
        }
    
    def analyze(self,
               metric_name: str,
               values: List[float],
               timestamps: List[str],
               trend_method: str = 'auto',
               seasonality: bool = True,
               detect_inflections: bool = True) -> TrendResult:
        """
        分析时间序列数据的趋势
        
        参数:
            metric_name (str): 指标名称
            values (List[float]): 指标值列表
            timestamps (List[str]): 时间戳列表，格式为ISO日期字符串
            trend_method (str): 趋势分析方法，可选'linear'、'exponential'、'lowess'或'auto'
            seasonality (bool): 是否分析季节性
            detect_inflections (bool): 是否检测拐点
            
        返回:
            TrendResult: 趋势分析结果
        
        示例:
            >>> analyzer = TrendAnalyzer()
            >>> result = analyzer.analyze(
            ...     metric_name="日活跃用户",
            ...     values=[1000, 1050, 1100, 1150, 1250, 1200, 1300],
            ...     timestamps=["2023-01-01", "2023-02-01", "2023-03-01", 
            ...                 "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01"],
            ...     trend_method="auto",
            ...     seasonality=True,
            ...     detect_inflections=True
            ... )
        """
        self.logger.info(f"开始趋势分析，指标: {metric_name}, 方法: {trend_method}")
        
        # 验证输入数据
        self._validate_inputs(values, timestamps)
        
        # 将时间戳转换为日期对象
        dates = [pd.to_datetime(ts) for ts in timestamps]
        
        # 创建时间序列数据
        ts_data = pd.Series(values, index=dates)
        
        # 检测数据频率
        freq = detect_frequency(dates)
        
        # 自动选择趋势方法
        if trend_method == 'auto':
            trend_method = self._auto_select_trend_method(values, len(values))
        
        # 分析总体趋势
        trend_slope, trend_direction, trend_significance, trend_r2 = self._analyze_overall_trend(values, dates)
        
        # 使用选择的方法分析趋势
        if trend_method == 'linear':
            trend_values, trend_pattern = self._analyze_linear_trend(values, dates)
        elif trend_method == 'exponential':
            trend_values, trend_pattern = self._analyze_exponential_trend(ts_data, freq)
        elif trend_method == 'lowess':
            trend_values, trend_pattern = self._analyze_lowess_trend(values, dates)
        else:
            raise ValueError(f"不支持的趋势分析方法: {trend_method}")
        
        # 季节性分析
        seasonality_strength = None
        seasonality_pattern = None
        if seasonality and len(values) >= 4:  # 至少需要4个点来分析季节性
            seasonality_strength, seasonality_pattern = self._analyze_seasonality(ts_data, freq)
        
        # 拐点检测
        inflections = []
        if detect_inflections and len(values) >= 5:  # 至少需要5个点来检测拐点
            inflections = self._detect_inflections(values, dates, trend_values)
        
        # 创建趋势项
        trend_item = TrendItem(
            metric_name=metric_name,
            direction=trend_direction,
            slope=round(float(trend_slope), 4),
            significance=round(float(trend_significance), 4),
            r_squared=round(float(trend_r2), 4),
            pattern=trend_pattern,
            method=trend_method,
            has_seasonality=seasonality_strength > 0.1 if seasonality_strength is not None else False,
            seasonality_strength=round(float(seasonality_strength), 4) if seasonality_strength is not None else None,
            seasonality_pattern=seasonality_pattern
        )
        
        # 生成摘要文本
        summary = self._generate_summary(trend_item, inflections)
        
        # 创建结果对象
        result = TrendResult(
            trend=trend_item,
            inflections=inflections,
            summary=summary
        )
        
        self.logger.info(f"趋势分析完成，方向: {trend_direction}, 显著性: {trend_significance:.4f}")
        return result
    
    def _validate_inputs(self, values: List[float], timestamps: List[str]) -> None:
        """
        验证输入数据
        
        参数:
            values (List[float]): 指标值列表
            timestamps (List[str]): 时间戳列表
            
        异常:
            ValueError: 当输入数据无效时
        """
        if len(values) != len(timestamps):
            raise ValueError("指标值列表和时间戳列表长度必须相同")
        
        if len(values) < 3:
            raise ValueError("趋势分析至少需要3个数据点")
        
        # 验证时间戳格式
        try:
            for ts in timestamps:
                pd.to_datetime(ts)
        except:
            raise ValueError("时间戳格式无效，请使用ISO日期格式")
        
        # 验证时间戳排序
        dates = [pd.to_datetime(ts) for ts in timestamps]
        if not all(dates[i] <= dates[i+1] for i in range(len(dates)-1)):
            raise ValueError("时间戳必须按时间顺序排列")
    
    def _auto_select_trend_method(self, values: List[float], n_points: int) -> str:
        """
        自动选择趋势分析方法
        
        参数:
            values (List[float]): 指标值列表
            n_points (int): 数据点数量
            
        返回:
            str: 选择的趋势分析方法
        """
        # 检测是否有负值
        has_negative = any(v < 0 for v in values)
        
        # 检测变化率
        changes = [values[i+1] / values[i] if values[i] != 0 else 1 for i in range(len(values)-1)]
        avg_change_rate = np.mean([abs(c - 1) for c in changes])
        
        # 对于长序列或变化率较大的情况，使用LOWESS更适合
        if n_points > 12 or avg_change_rate > 0.2:
            return 'lowess'
        # 对于包含负值的情况，使用线性趋势
        elif has_negative:
            return 'linear'
        # 默认使用指数平滑
        else:
            return 'exponential'
    
    def _analyze_overall_trend(self, 
                             values: List[float], 
                             dates: List[datetime]) -> Tuple[float, str, float, float]:
        """
        分析整体趋势
        
        参数:
            values (List[float]): 指标值列表
            dates (List[datetime]): 日期列表
            
        返回:
            Tuple[float, str, float, float]: 斜率、方向、显著性、R²
        """
        # 将日期转换为数值（距离第一个日期的天数）
        x = np.array([(d - dates[0]).total_seconds() / (24*3600) for d in dates])
        y = np.array(values)
        
        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # 计算R²
        r_squared = r_value ** 2
        
        # 判断趋势方向
        if p_value > 0.05 or abs(slope) < self.config['slope_threshold']:
            direction = "平稳"
        elif slope > 0:
            direction = "上升"
        else:
            direction = "下降"
        
        # 计算趋势显著性
        if p_value <= 0.05 and r_squared >= self.config['r2_threshold']:
            significance = r_squared
        else:
            significance = 0.0
        
        return slope, direction, significance, r_squared
    
    def _analyze_linear_trend(self, 
                            values: List[float], 
                            dates: List[datetime]) -> Tuple[List[float], TrendPattern]:
        """
        线性趋势分析
        
        参数:
            values (List[float]): 指标值列表
            dates (List[datetime]): 日期列表
            
        返回:
            Tuple[List[float], TrendPattern]: 趋势值列表和趋势模式
        """
        # 将日期转换为数值
        x = np.array([(d - dates[0]).total_seconds() / (24*3600) for d in dates])
        y = np.array(values)
        
        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # 计算趋势线值
        trend_values = [slope * xi + intercept for xi in x]
        
        # 判断趋势模式
        if p_value > 0.05 or abs(slope) < self.config['slope_threshold']:
            pattern = TrendPattern.STABLE
        elif slope > 0:
            pattern = TrendPattern.LINEAR_INCREASE
        else:
            pattern = TrendPattern.LINEAR_DECREASE
        
        return trend_values, pattern
    
    def _analyze_exponential_trend(self, 
                                  ts_data: pd.Series, 
                                  freq: str) -> Tuple[List[float], TrendPattern]:
        """
        指数平滑趋势分析
        
        参数:
            ts_data (pd.Series): 时间序列数据
            freq (str): 数据频率
            
        返回:
            Tuple[List[float], TrendPattern]: 趋势值列表和趋势模式
        """
        # 确保没有负值
        if any(ts_data.values < 0):
            # 将所有值平移到正数范围
            min_val = min(ts_data.values)
            if min_val < 0:
                ts_data = ts_data - min_val + 1
        
        # 应用指数平滑
        try:
            model = ExponentialSmoothing(ts_data, 
                                         trend='add', 
                                         seasonal=None,
                                         freq=freq)
            fit = model.fit()
            trend_values = fit.fittedvalues.tolist()
            
            # 计算第一个和最后一个趋势值的比例
            trend_ratio = trend_values[-1] / trend_values[0] if trend_values[0] != 0 else 1
            
            # 判断趋势模式
            if abs(trend_ratio - 1) < 0.05:
                pattern = TrendPattern.STABLE
            elif trend_ratio > 1.2:
                pattern = TrendPattern.EXPONENTIAL_INCREASE
            elif trend_ratio > 1:
                pattern = TrendPattern.LINEAR_INCREASE
            elif trend_ratio < 0.8:
                pattern = TrendPattern.EXPONENTIAL_DECREASE
            else:
                pattern = TrendPattern.LINEAR_DECREASE
            
        except:
            # 如果指数平滑失败，回退到线性趋势
            x = np.arange(len(ts_data))
            y = ts_data.values
            slope, intercept, _, _, _ = stats.linregress(x, y)
            trend_values = [slope * xi + intercept for xi in x]
            
            if abs(slope) < self.config['slope_threshold']:
                pattern = TrendPattern.STABLE
            elif slope > 0:
                pattern = TrendPattern.LINEAR_INCREASE
            else:
                pattern = TrendPattern.LINEAR_DECREASE
        
        return trend_values, pattern
    
    def _analyze_lowess_trend(self, 
                             values: List[float], 
                             dates: List[datetime]) -> Tuple[List[float], TrendPattern]:
        """
        LOWESS平滑趋势分析
        
        参数:
            values (List[float]): 指标值列表
            dates (List[datetime]): 日期列表
            
        返回:
            Tuple[List[float], TrendPattern]: 趋势值列表和趋势模式
        """
        # 将日期转换为数值
        x = np.array([(d - dates[0]).total_seconds() / (24*3600) for d in dates])
        y = np.array(values)
        
        # 应用LOWESS平滑
        smoothed = lowess(y, x, frac=self.config['lowess_frac'])
        trend_values = smoothed[:, 1].tolist()
        
        # 计算趋势的变化率
        changes = [trend_values[i+1] - trend_values[i] for i in range(len(trend_values)-1)]
        
        # 统计正变化和负变化的比例
        pos_changes = sum(1 for c in changes if c > 0)
        neg_changes = sum(1 for c in changes if c < 0)
        total_changes = len(changes)
        
        # 判断趋势模式
        first_third = trend_values[:len(trend_values)//3]
        last_third = trend_values[-len(trend_values)//3:]
        mid_val = trend_values[len(trend_values)//2]
        
        # 计算第一段和最后一段的平均值
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        # 计算趋势变化率
        trend_change_rate = (last_avg / first_avg - 1) if first_avg != 0 else 0
        
        # 基于变化率和方向判断模式
        if abs(trend_change_rate) < 0.05:
            pattern = TrendPattern.STABLE
        elif trend_change_rate > 0.2 and all(trend_values[i] <= trend_values[i+1] for i in range(len(trend_values)-1)):
            pattern = TrendPattern.EXPONENTIAL_INCREASE
        elif trend_change_rate > 0:
            if pos_changes > 0.8 * total_changes:
                pattern = TrendPattern.LINEAR_INCREASE
            else:
                pattern = TrendPattern.FLUCTUATING_INCREASE
        elif trend_change_rate < -0.2 and all(trend_values[i] >= trend_values[i+1] for i in range(len(trend_values)-1)):
            pattern = TrendPattern.EXPONENTIAL_DECREASE
        elif trend_change_rate < 0:
            if neg_changes > 0.8 * total_changes:
                pattern = TrendPattern.LINEAR_DECREASE
            else:
                pattern = TrendPattern.FLUCTUATING_DECREASE
        elif mid_val > first_avg and mid_val > last_avg:
            pattern = TrendPattern.PARABOLIC
        elif mid_val < first_avg and mid_val < last_avg:
            pattern = TrendPattern.VALLEY
        else:
            pattern = TrendPattern.FLUCTUATING
        
        return trend_values, pattern
    
    def _analyze_seasonality(self, 
                           ts_data: pd.Series, 
                           freq: str) -> Tuple[float, Optional[str]]:
        """
        季节性分析
        
        参数:
            ts_data (pd.Series): 时间序列数据
            freq (str): 数据频率
            
        返回:
            Tuple[float, Optional[str]]: 季节性强度和模式
        """
        try:
            # 如果数据点不足，返回无季节性
            if len(ts_data) < 4:
                return 0.0, None
            
            # 设置季节性周期
            if freq in ['D', 'B']:  # 日数据
                period = 7  # 周季节性
            elif freq in ['W', 'W-SUN', 'W-MON']:  # 周数据
                period = 4  # 月季节性
            elif freq in ['M', 'MS']:  # 月数据
                period = 12  # 年季节性
            elif freq in ['Q', 'QS']:  # 季度数据
                period = 4  # 年季节性
            else:
                period = min(len(ts_data) // 2, 12)  # 默认使用适当的周期
            
            # 如果数据点不足季节性周期的2倍，无法进行季节性分解
            if len(ts_data) < period * 2:
                return 0.0, None
            
            # 季节性分解
            decomposition = seasonal_decompose(ts_data, model='additive', period=period)
            
            # 计算季节性强度
            seasonal_values = decomposition.seasonal
            seasonal_variance = np.var(seasonal_values)
            total_variance = np.var(ts_data)
            
            seasonality_strength = seasonal_variance / total_variance if total_variance != 0 else 0
            
            # 判断季节性模式
            if seasonality_strength < 0.1:
                seasonality_pattern = None
            else:
                # 检测季节性模式特征
                if freq in ['M', 'MS'] and period == 12:
                    # 月数据，检查年度季节性
                    seasonality_pattern = self._detect_yearly_pattern(seasonal_values)
                elif freq in ['D', 'B'] and period == 7:
                    # 日数据，检查周季节性
                    seasonality_pattern = self._detect_weekly_pattern(seasonal_values)
                else:
                    seasonality_pattern = "周期性波动"
            
            return seasonality_strength, seasonality_pattern
            
        except:
            # 季节性分析失败
            return 0.0, None
    
    def _detect_yearly_pattern(self, seasonal_values: pd.Series) -> str:
        """
        检测年度季节性模式
        
        参数:
            seasonal_values (pd.Series): 季节性成分值
            
        返回:
            str: 季节性模式描述
        """
        # 获取月份索引
        months = np.arange(1, 13)
        
        # 获取一个完整周期的季节性值
        one_cycle = seasonal_values.iloc[:12].values
        
        # 找到季节性峰值的月份
        peak_month = months[np.argmax(one_cycle)]
        
        # 找到季节性谷值的月份
        trough_month = months[np.argmin(one_cycle)]
        
        # 常见季节性模式
        if peak_month in [12, 1, 2]:
            return "冬季高峰"
        elif peak_month in [3, 4, 5]:
            return "春季高峰"
        elif peak_month in [6, 7, 8]:
            return "夏季高峰"
        elif peak_month in [9, 10, 11]:
            return "秋季高峰"
        else:
            return f"{peak_month}月高峰, {trough_month}月低谷"
    
    def _detect_weekly_pattern(self, seasonal_values: pd.Series) -> str:
        """
        检测周季节性模式
        
        参数:
            seasonal_values (pd.Series): 季节性成分值
            
        返回:
            str: 季节性模式描述
        """
        # 获取星期几索引 (0 = 星期一, 6 = 星期日)
        weekdays = np.arange(7)
        
        # 获取一个完整周期的季节性值
        one_cycle = seasonal_values.iloc[:7].values
        
        # 找到季节性峰值的星期几
        peak_day = weekdays[np.argmax(one_cycle)]
        
        # 找到季节性谷值的星期几
        trough_day = weekdays[np.argmin(one_cycle)]
        
        # 将索引转换为星期几名称
        day_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        peak_day_name = day_names[peak_day]
        trough_day_name = day_names[trough_day]
        
        # 常见周季节性模式
        if peak_day in [5, 6]:  # 周末
            return "周末高峰"
        elif peak_day in [0, 1, 2, 3, 4]:  # 工作日
            return "工作日高峰"
        else:
            return f"{peak_day_name}高峰, {trough_day_name}低谷"
    
    def _detect_inflections(self, 
                          values: List[float], 
                          dates: List[datetime], 
                          trend_values: List[float]) -> List[TrendInflection]:
        """
        检测趋势拐点
        
        参数:
            values (List[float]): 指标值列表
            dates (List[datetime]): 日期列表
            trend_values (List[float]): 趋势值列表
            
        返回:
            List[TrendInflection]: 拐点列表
        """
        # 如果数据点太少，无法检测拐点
        if len(values) < 5:
            return []
        
        # 计算趋势的一阶导数（变化率）
        derivatives = [trend_values[i+1] - trend_values[i] for i in range(len(trend_values)-1)]
        
        # 计算二阶导数（变化率的变化率）
        second_derivatives = [derivatives[i+1] - derivatives[i] for i in range(len(derivatives)-1)]
        
        # 设置拐点检测阈值
        threshold = self.config['inflection_sensitivity'] * np.std(second_derivatives)
        
        # 检测符号变化的点
        inflection_points = []
        for i in range(1, len(second_derivatives)-1):
            # 检查是否为局部极值点
            if abs(second_derivatives[i]) > threshold:
                if (second_derivatives[i-1] < 0 and second_derivatives[i] > 0) or \
                   (second_derivatives[i-1] > 0 and second_derivatives[i] < 0):
                    # 这是一个拐点，i+1是原始列表中的索引（考虑到求导导致的索引偏移）
                    index = i + 1
                    
                    # 判断拐点类型
                    if second_derivatives[i-1] < 0 and second_derivatives[i] > 0:
                        inflection_type = "低点"
                    else:
                        inflection_type = "高点"
                    
                    # 计算拐点强度（归一化的二阶导数绝对值）
                    strength = abs(second_derivatives[i]) / (np.max(np.abs(second_derivatives)) or 1)
                    
                    # 创建拐点对象
                    inflection = TrendInflection(
                        date=dates[index].strftime("%Y-%m-%d"),
                        index=index,
                        value=values[index],
                        type=inflection_type,
                        strength=round(float(strength), 4)
                    )
                    
                    inflection_points.append(inflection)
        
        # 按时间排序
        inflection_points.sort(key=lambda x: x.index)
        
        return inflection_points
    
    def _generate_summary(self, 
                        trend: TrendItem, 
                        inflections: List[TrendInflection]) -> str:
        """
        生成趋势摘要文本
        
        参数:
            trend (TrendItem): 趋势项
            inflections (List[TrendInflection]): 拐点列表
            
        返回:
            str: 摘要文本
        """
        # 生成基本趋势描述
        if trend.direction == "平稳":
            summary = f"{trend.metric_name}整体呈现平稳趋势"
        elif trend.direction == "上升":
            if trend.pattern in [TrendPattern.LINEAR_INCREASE, TrendPattern.EXPONENTIAL_INCREASE]:
                pattern_desc = "持续" if trend.pattern == TrendPattern.LINEAR_INCREASE else "加速"
                summary = f"{trend.metric_name}整体呈现{pattern_desc}上升趋势"
            else:
                summary = f"{trend.metric_name}整体呈波动上升趋势"
        else:  # 下降
            if trend.pattern in [TrendPattern.LINEAR_DECREASE, TrendPattern.EXPONENTIAL_DECREASE]:
                pattern_desc = "持续" if trend.pattern == TrendPattern.LINEAR_DECREASE else "加速"
                summary = f"{trend.metric_name}整体呈现{pattern_desc}下降趋势"
            else:
                summary = f"{trend.metric_name}整体呈波动下降趋势"
        
        # 如果趋势显著，添加显著性描述
        if trend.significance > 0.8:
            summary += "，趋势非常显著"
        elif trend.significance > 0.6:
            summary += "，趋势显著"
        
        # 添加季节性描述
        if trend.has_seasonality and trend.seasonality_pattern:
            summary += f"，存在{trend.seasonality_pattern}的季节性波动"
        
        # 添加拐点描述
        if inflections:
            # 按强度排序
            sorted_inflections = sorted(inflections, key=lambda x: x.strength, reverse=True)
            
            # 取最重要的拐点
            main_inflection = sorted_inflections[0]
            
            # 添加拐点描述
            summary += f"，在{main_inflection.date}出现显著{main_inflection.type}"
            
            if len(inflections) > 1:
                summary += f"，总共检测到{len(inflections)}个拐点"
        
        return summary 