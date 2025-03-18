"""
数据处理工具函数
==============

提供用于数据分析和处理的工具函数。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Tuple, Optional, Any


def calculate_change_rate(
    current_value: float, previous_value: float
) -> Optional[float]:
    """
    计算变化率
    
    参数:
        current_value (float): 当前值
        previous_value (float): 上一期值
        
    返回:
        Optional[float]: 变化率，如果previous_value为0则返回None
    """
    if previous_value == 0:
        return None
    return (current_value - previous_value) / previous_value


def calculate_change(current_value: float, previous_value: float) -> float:
    """
    计算变化量
    
    参数:
        current_value (float): 当前值
        previous_value (float): 上一期值
        
    返回:
        float: 变化量
    """
    return current_value - previous_value


def classify_change(change_rate: Optional[float]) -> str:
    """
    根据变化率分类变化程度
    
    参数:
        change_rate (Optional[float]): 变化率
        
    返回:
        str: 变化程度分类，可能的值包括: '大幅增长', '增长', '轻微增长', '基本持平', 
            '轻微下降', '下降', '大幅下降', '未知'
    """
    if change_rate is None:
        return "未知"
    
    if change_rate > 0.5:
        return "大幅增长"
    elif change_rate > 0.1:
        return "增长"
    elif change_rate > 0.02:
        return "轻微增长"
    elif change_rate >= -0.02:
        return "基本持平"
    elif change_rate >= -0.1:
        return "轻微下降"
    elif change_rate >= -0.5:
        return "下降"
    else:
        return "大幅下降"


def detect_anomaly(
    value: float, historical_values: List[float], threshold: float = 1.5
) -> Tuple[bool, float]:
    """
    检测数值是否异常
    
    使用IQR(四分位距)方法检测异常值
    
    参数:
        value (float): 要检测的值
        historical_values (List[float]): 历史值列表
        threshold (float, optional): 判断异常的阈值倍数，默认为1.5
        
    返回:
        Tuple[bool, float]: (是否异常, 异常程度)
    """
    if not historical_values:
        return False, 0.0
    
    # 添加当前值到历史值中一起计算
    all_values = historical_values + [value]
    
    # 计算四分位数
    q1, q3 = np.percentile(all_values, [25, 75])
    iqr = q3 - q1
    
    # 计算上下边界
    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr
    
    # 判断是否异常
    is_anomaly = value < lower_bound or value > upper_bound
    
    # 计算异常程度 (与边界的标准化距离)
    if is_anomaly:
        if value < lower_bound:
            anomaly_degree = (lower_bound - value) / iqr
        else:
            anomaly_degree = (value - upper_bound) / iqr
    else:
        anomaly_degree = 0.0
    
    return is_anomaly, anomaly_degree


def detect_anomaly_enhanced(
    value: float, 
    historical_values: List[float], 
    seasonality: Optional[int] = None,
    threshold: float = 1.5,
    context_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    增强版异常检测函数，支持季节性数据和多维上下文
    
    参数:
        value (float): 要检测的值
        historical_values (List[float]): 历史值列表
        seasonality (Optional[int]): 季节性周期长度（如每周7天，每年12个月等），如不提供则自动尝试检测
        threshold (float): 判断异常的阈值倍数，默认为1.5
        context_data (Optional[Dict[str, Any]]): 上下文数据，可以包含多维度的辅助信息，如相关指标、外部因素等
        
    返回:
        Dict[str, Any]: 包含多种异常检测结果的字典，包括：
            - is_anomaly (bool): 是否为异常值
            - anomaly_degree (float): 异常程度
            - method (str): 使用的检测方法
            - reason (str): 异常原因分析
            - seasonality_impact (float): 季节性影响程度
            - context_impact (Dict[str, float]): 各维度上下文的影响程度
    """
    result = {
        "is_anomaly": False,
        "anomaly_degree": 0.0,
        "method": "未知",
        "reason": "",
        "seasonality_impact": 0.0,
        "context_impact": {}
    }
    
    if not historical_values or len(historical_values) < 4:  # 至少需要4个点进行基本分析
        result["method"] = "基础IQR(数据不足)"
        return result
    
    # 1. 先使用基础IQR方法进行检测
    is_anomaly, anomaly_degree = detect_anomaly(value, historical_values, threshold)
    result["is_anomaly"] = is_anomaly
    result["anomaly_degree"] = anomaly_degree
    result["method"] = "基础IQR"
    
    if not is_anomaly:
        return result
    
    # 2. 如果有异常，尝试考虑季节性
    if seasonality is None and len(historical_values) >= 24:  # 自动检测季节性需要足够的数据点
        try:
            # 使用自相关函数尝试检测周期性
            from statsmodels.tsa.stattools import acf
            acf_values = acf(historical_values, nlags=len(historical_values)//2)
            # 寻找自相关函数的峰值（除了位置0之外）
            potential_seasons = np.argsort(acf_values[1:])[-3:] + 1  # 取前3个可能的周期
            
            # 选择自相关性最强的作为季节性
            seasonality = potential_seasons[-1]
            if acf_values[seasonality] < 0.3:  # 自相关性不够强
                seasonality = None
                
            result["detected_seasonality"] = seasonality
        except:
            # 如果统计分析失败，则不使用季节性
            seasonality = None
    
    # 3. 应用季节性调整（如果有）
    if seasonality and len(historical_values) >= seasonality * 2:
        # 找出同季节的历史值
        season_position = len(historical_values) % seasonality
        seasonal_values = [historical_values[i] for i in range(len(historical_values)) if i % seasonality == season_position]
        
        if len(seasonal_values) >= 3:  # 至少需要3个同周期数据点才能分析
            # 使用同周期数据进行IQR检测
            seasonal_mean = np.mean(seasonal_values)
            seasonal_std = np.std(seasonal_values) if len(seasonal_values) > 1 else 0
            
            if seasonal_std > 0:
                # 计算z分数 (标准分数)
                z_score = abs(value - seasonal_mean) / seasonal_std
                is_seasonal_anomaly = z_score > threshold * 1.5  # 稍微放宽阈值
                seasonal_anomaly_degree = max(0, z_score - threshold * 1.5)
                
                result["seasonal_z_score"] = z_score
                
                if not is_seasonal_anomaly and result["is_anomaly"]:
                    # 如果在季节性背景下不是异常，可能是正常的季节性波动
                    result["is_anomaly"] = False
                    result["reason"] = "考虑季节性因素后，该值在正常范围内"
                    result["seasonality_impact"] = 1.0 - (seasonal_anomaly_degree / max(anomaly_degree, 0.1))
                    result["method"] = "季节性调整IQR"
                    result["anomaly_degree"] = 0
                elif is_seasonal_anomaly:
                    # 在季节性背景下仍是异常
                    result["reason"] = "即使考虑季节性因素，该值仍然异常"
                    result["method"] = "季节性确认IQR"
                    # 保留较大的异常度
                    result["anomaly_degree"] = max(anomaly_degree, seasonal_anomaly_degree)
    
    # 4. 考虑多维上下文（如果提供）
    if context_data and isinstance(context_data, dict):
        context_corr = {}
        anomaly_explained = False
        
        # 检查每个上下文维度是否可以解释异常
        for key, data in context_data.items():
            if isinstance(data, (list, np.ndarray)) and len(data) == len(historical_values) + 1:
                # 计算上下文序列与主序列的相关性
                try:
                    current_context = data[-1]
                    hist_context = data[:-1]
                    
                    # 仅当有足够样本时才计算相关性
                    if len(historical_values) > 5:
                        # 计算皮尔逊相关系数
                        corr = np.corrcoef(historical_values, hist_context)[0, 1]
                        context_corr[key] = corr
                        
                        # 如果相关性强，检查当前上下文是否异常
                        if abs(corr) > 0.7:  # 强相关
                            ctx_is_anomaly, ctx_degree = detect_anomaly(current_context, hist_context, threshold)
                            
                            if ctx_is_anomaly and (
                                (corr > 0 and np.sign(current_context - np.mean(hist_context)) == np.sign(value - np.mean(historical_values))) or
                                (corr < 0 and np.sign(current_context - np.mean(hist_context)) != np.sign(value - np.mean(historical_values)))
                            ):
                                # 如果上下文维度异常且与主指标变化方向一致（正相关）或相反（负相关）
                                result["context_impact"][key] = abs(corr) * ctx_degree
                                
                                if abs(corr) > 0.85 and ctx_degree > anomaly_degree * 0.7:
                                    # 如果上下文异常程度足够高，且相关性非常强，可以作为解释
                                    anomaly_explained = True
                                    result["reason"] += f"可能与{key}的异常变化有关; "
                
                except:
                    # 如果计算出错，跳过这个上下文维度
                    pass
        
        if anomaly_explained:
            result["method"] += "+多维解释"
    
    # 格式化原因描述和剪裁异常程度
    if not result["reason"]:
        if result["is_anomaly"]:
            if value > np.mean(historical_values):
                result["reason"] = "高于历史正常范围"
            else:
                result["reason"] = "低于历史正常范围"
    
    # 确保异常程度被限制在合理范围
    result["anomaly_degree"] = min(5.0, result["anomaly_degree"])
    
    return result


def detect_seasonal_pattern(
    values: List[float], 
    max_period: int = 52
) -> Tuple[Optional[int], float]:
    """
    检测时间序列中的季节性模式
    
    参数:
        values (List[float]): 时间序列数据
        max_period (int): 检测的最大可能周期
        
    返回:
        Tuple[Optional[int], float]: (季节性周期长度, 季节强度)
            季节性周期为None表示未检测到明显的季节性
    """
    if len(values) < max_period * 2:
        # 数据不足以进行季节性分析
        return None, 0.0
    
    try:
        # 使用自相关函数进行季节性检测
        from statsmodels.tsa.stattools import acf
        
        # 计算自相关系数，最大滞后期限为max_period
        acf_values = acf(values, nlags=min(len(values)//2, max_period))
        
        # 除了滞后0外，找到自相关最高的滞后期
        periods = np.argsort(acf_values[1:])[-3:] + 1
        
        # 选择自相关性最强的作为季节性周期
        strongest_period = periods[-1]
        season_strength = acf_values[strongest_period]
        
        # 季节性强度阈值
        if season_strength > 0.3:
            return strongest_period, season_strength
        else:
            return None, season_strength
            
    except Exception as e:
        # 如果统计分析失败，则不使用季节性
        return None, 0.0


def detect_multi_dimensional_anomaly(
    main_value: float,
    main_history: List[float],
    context_values: Dict[str, float],
    context_history: Dict[str, List[float]],
    threshold: float = 1.5
) -> Dict[str, Any]:
    """
    多维异常检测，综合考虑主指标和多个相关维度
    
    参数:
        main_value (float): 主指标当前值
        main_history (List[float]): 主指标历史值
        context_values (Dict[str, float]): 上下文维度当前值字典
        context_history (Dict[str, List[float]]): 上下文维度历史值字典
        threshold (float): 判断异常的阈值倍数
        
    返回:
        Dict[str, Any]: 异常检测结果，包含:
            - is_anomaly (bool): 是否异常
            - main_anomaly (Dict): 主指标异常检测详情
            - context_anomalies (Dict): 各个上下文维度的异常检测详情
            - anomaly_score (float): 综合异常分数
            - influencing_factors (List): 影响异常的主要因素
    """
    result = {
        "is_anomaly": False,
        "main_anomaly": None,
        "context_anomalies": {},
        "anomaly_score": 0.0,
        "influencing_factors": []
    }
    
    # 主指标异常检测
    main_anomaly = detect_anomaly_enhanced(
        main_value, 
        main_history, 
        threshold=threshold
    )
    result["main_anomaly"] = main_anomaly
    
    # 收集用于多维分析的上下文数据
    context_data = {}
    for key, hist in context_history.items():
        if key in context_values:
            # 确保历史数据和当前值可以组合成完整的序列
            context_data[key] = hist + [context_values[key]]
    
    # 使用增强的异常检测算法(带上下文)
    enhanced_result = detect_anomaly_enhanced(
        main_value,
        main_history,
        threshold=threshold,
        context_data=context_data
    )
    
    # 检测各维度是否异常
    context_anomalies = {}
    influencing_dimensions = []
    total_context_impact = 0.0
    
    for dim, current in context_values.items():
        if dim in context_history:
            history = context_history[dim]
            dim_anomaly = detect_anomaly_enhanced(
                current,
                history,
                threshold=threshold
            )
            context_anomalies[dim] = dim_anomaly
            
            # 检查对主异常的影响
            if dim in enhanced_result.get("context_impact", {}):
                impact = enhanced_result["context_impact"][dim]
                if impact > 0.3:  # 影响较大
                    influencing_dimensions.append({
                        "dimension": dim,
                        "impact": impact,
                        "is_anomaly": dim_anomaly["is_anomaly"],
                        "anomaly_degree": dim_anomaly["anomaly_degree"]
                    })
                    total_context_impact += impact
    
    result["context_anomalies"] = context_anomalies
    
    # 确定最终异常状态
    # 如果主指标异常，则整体判定为异常
    if main_anomaly["is_anomaly"]:
        result["is_anomaly"] = True
        result["anomaly_score"] = main_anomaly["anomaly_degree"]
        
        # 考虑上下文解释后可能降低异常分数
        if total_context_impact > 0:
            # 最多降低50%的异常分数
            reduction_factor = min(0.5, total_context_impact * 0.1)
            result["anomaly_score"] *= (1 - reduction_factor)
            
        # 排序影响因素
        influencing_dimensions.sort(key=lambda x: x["impact"], reverse=True)
        result["influencing_factors"] = influencing_dimensions
        
    elif len([dim for dim, res in context_anomalies.items() if res["is_anomaly"]]) >= 3:
        # 如果至少3个上下文维度同时异常，也可能是整体异常的信号
        result["is_anomaly"] = True
        result["anomaly_score"] = 0.5  # 设置一个较低的异常分数
        result["influencing_factors"] = [
            {
                "dimension": dim,
                "impact": 0.5,
                "is_anomaly": res["is_anomaly"],
                "anomaly_degree": res["anomaly_degree"]
            }
            for dim, res in context_anomalies.items()
            if res["is_anomaly"]
        ]
    
    return result


def calculate_trend(values: List[float]) -> Tuple[str, float]:
    """
    计算数据趋势
    
    使用简单线性回归计算趋势斜率，并根据斜率判断趋势类型
    
    参数:
        values (List[float]): 数据值列表
        
    返回:
        Tuple[str, float]: (趋势类型, 趋势强度)，趋势类型可能的值包括:
            '强烈上升', '上升', '轻微上升', '平稳', '轻微下降', '下降', '强烈下降'
    """
    if len(values) < 2:
        return "数据不足", 0.0
    
    # 使用简单线性回归计算斜率
    x = np.arange(len(values))
    y = np.array(values)
    
    slope, _ = np.polyfit(x, y, 1)
    
    # 计算平均值作为基准来标准化斜率
    mean_value = np.mean(values)
    if mean_value == 0:
        normalized_slope = slope
    else:
        normalized_slope = slope / abs(mean_value)
    
    # 根据标准化斜率判断趋势
    if normalized_slope > 0.1:
        trend_type = "强烈上升"
    elif normalized_slope > 0.05:
        trend_type = "上升"
    elif normalized_slope > 0.01:
        trend_type = "轻微上升"
    elif normalized_slope >= -0.01:
        trend_type = "平稳"
    elif normalized_slope >= -0.05:
        trend_type = "轻微下降"
    elif normalized_slope >= -0.1:
        trend_type = "下降"
    else:
        trend_type = "强烈下降"
    
    # 计算趋势强度 (标准化斜率的绝对值)
    trend_strength = abs(normalized_slope)
    
    return trend_type, trend_strength 