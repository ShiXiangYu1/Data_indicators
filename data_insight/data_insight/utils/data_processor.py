#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据处理模块
==========

提供数据处理、验证和归一化等功能。
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Optional, Tuple


def validate_data(data: Union[pd.DataFrame, np.ndarray, List], 
                 min_samples: int = 5, 
                 check_nan: bool = True,
                 check_variance: bool = True) -> Tuple[bool, str]:
    """
    验证数据是否有效
    
    参数:
        data: 输入数据，可以是DataFrame, ndarray或List
        min_samples: 最小样本数要求
        check_nan: 是否检查NaN值
        check_variance: 是否检查方差
    
    返回:
        (is_valid, message): 是否有效及原因
    """
    # 转换为numpy数组进行处理
    if isinstance(data, pd.DataFrame):
        data_array = data.values
    elif isinstance(data, list):
        data_array = np.array(data)
    else:
        data_array = data
    
    # 检查样本数量
    if len(data_array) < min_samples:
        return False, f"样本数量不足，至少需要{min_samples}个样本"
    
    # 检查NaN值
    if check_nan and np.isnan(data_array).any():
        return False, "数据中包含NaN值"
    
    # 检查方差
    if check_variance:
        # 对二维数据，检查每列方差
        if data_array.ndim > 1:
            variances = np.var(data_array, axis=0)
            if np.any(variances < 1e-10):
                return False, "数据方差过小，存在常量列"
        else:
            # 一维数据
            if np.var(data_array) < 1e-10:
                return False, "数据方差过小，几乎为常量"
    
    return True, "数据有效"


def normalize_data(data: Union[pd.DataFrame, np.ndarray, List], 
                  method: str = 'minmax',
                  feature_range: Tuple[float, float] = (0, 1)) -> np.ndarray:
    """
    归一化数据
    
    参数:
        data: 输入数据，可以是DataFrame, ndarray或List
        method: 归一化方法，'minmax', 'zscore', 'robust'
        feature_range: minmax归一化的范围
    
    返回:
        归一化后的数据
    """
    # 转换为numpy数组进行处理
    if isinstance(data, pd.DataFrame):
        data_array = data.values
    elif isinstance(data, list):
        data_array = np.array(data)
    else:
        data_array = data
    
    # 处理一维数据
    if data_array.ndim == 1:
        data_array = data_array.reshape(-1, 1)
    
    if method == 'minmax':
        # Min-Max归一化
        min_vals = np.min(data_array, axis=0)
        max_vals = np.max(data_array, axis=0)
        range_vals = max_vals - min_vals
        # 防止除零
        range_vals[range_vals == 0] = 1
        
        normalized_data = (data_array - min_vals) / range_vals
        # 调整到指定范围
        if feature_range != (0, 1):
            normalized_data = normalized_data * (feature_range[1] - feature_range[0]) + feature_range[0]
    
    elif method == 'zscore':
        # Z-score标准化
        mean_vals = np.mean(data_array, axis=0)
        std_vals = np.std(data_array, axis=0)
        # 防止除零
        std_vals[std_vals == 0] = 1
        
        normalized_data = (data_array - mean_vals) / std_vals
    
    elif method == 'robust':
        # 稳健归一化，使用中位数和四分位距
        median_vals = np.median(data_array, axis=0)
        q1 = np.percentile(data_array, 25, axis=0)
        q3 = np.percentile(data_array, 75, axis=0)
        iqr = q3 - q1
        # 防止除零
        iqr[iqr == 0] = 1
        
        normalized_data = (data_array - median_vals) / iqr
    
    else:
        raise ValueError(f"不支持的归一化方法: {method}")
    
    return normalized_data 


def detect_frequency(timestamps: Union[pd.Series, List, np.ndarray],
                    min_periods: int = 3) -> str:
    """
    检测时间序列数据的频率
    
    参数:
        timestamps: 时间戳列表，可以是pandas.Series, list或numpy数组
        min_periods: 最小样本数，用于确定频率
    
    返回:
        str: 推断的频率字符串，如'D'（天）, 'H'（小时）, 'T'或'min'（分钟）, 'S'（秒）
             无法确定时返回None
    """
    # 确保数据是pandas.Series类型
    if not isinstance(timestamps, pd.Series):
        if isinstance(timestamps, list) or isinstance(timestamps, np.ndarray):
            timestamps = pd.Series(timestamps)
        else:
            raise ValueError("timestamps必须是pandas.Series, list或numpy数组")
    
    # 确保为日期时间类型
    if not pd.api.types.is_datetime64_any_dtype(timestamps):
        try:
            timestamps = pd.to_datetime(timestamps)
        except:
            raise ValueError("无法将timestamps转换为日期时间类型")
    
    # 确保时间戳是排序的
    if not timestamps.equals(timestamps.sort_values()):
        timestamps = timestamps.sort_values().reset_index(drop=True)
    
    # 如果样本数太少，无法确定
    if len(timestamps) < min_periods:
        return None
    
    # 计算时间差
    time_diffs = timestamps.diff().dropna()
    
    # 如果没有时间差值，无法确定
    if len(time_diffs) == 0:
        return None
    
    # 计算众数时间差，用于确定最常见的时间间隔
    mode_td = time_diffs.mode().iloc[0]
    
    # 将时间差转换为秒
    seconds = mode_td.total_seconds()
    
    # 确定频率
    if seconds == 0:
        return None
    elif seconds < 1:
        return 'ms'  # 毫秒
    elif seconds == 1:
        return 'S'   # 秒
    elif seconds == 60:
        return 'T'   # 分钟
    elif seconds == 3600:
        return 'H'   # 小时
    elif seconds == 86400:
        return 'D'   # 天
    elif 86400*6.5 <= seconds <= 86400*7.5:
        return 'W'   # 周
    elif 86400*28 <= seconds <= 86400*31:
        return 'M'   # 月
    elif 86400*365 <= seconds <= 86400*366:
        return 'Y'   # 年
    else:
        # 其他情况，尝试用pandas推断
        try:
            freq = pd.infer_freq(timestamps)
            return freq
        except:
            # 如果pandas无法推断，则基于秒数返回近似值
            if seconds < 60:
                return f'{int(seconds)}S'  # 秒
            elif seconds < 3600:
                return f'{int(seconds/60)}T'  # 分钟
            elif seconds < 86400:
                return f'{int(seconds/3600)}H'  # 小时
            else:
                return f'{int(seconds/86400)}D'  # 天 