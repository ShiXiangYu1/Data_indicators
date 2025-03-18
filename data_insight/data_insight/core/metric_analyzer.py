"""
指标卡分析器
==========

分析单个指标卡数据，生成指标变化、异常检测等分析结果。
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.utils.data_utils import (
    calculate_change_rate,
    calculate_change,
    classify_change,
    detect_anomaly,
    calculate_trend
)


class MetricAnalyzer(BaseAnalyzer):
    """
    指标卡分析器
    
    分析单个指标卡数据，包括变化率、变化量、异常检测等。
    """
    
    def __init__(self):
        """
        初始化指标卡分析器
        """
        super().__init__()
        # 指标值为正数时增长是否为好的趋势的默认配置
        self.positive_growth_is_good = {
            # 收入类指标
            "收入": True,
            "销售额": True,
            "营业额": True,
            "收益": True,
            "利润": True,
            "收益率": True,
            "利润率": True,
            "增长率": True,
            "用户数": True,
            "活跃用户": True,
            "转化率": True,
            "新增用户": True,
            
            # 成本类指标
            "成本": False,
            "费用": False,
            "支出": False,
            "耗时": False,
            "流失率": False,
            "跳出率": False,
            "投诉率": False,
            "错误率": False,
            "故障率": False,
            "失败率": False
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标卡数据
        
        参数:
            data (Dict[str, Any]): 指标卡数据，应包含以下字段:
                - name: 指标名称
                - value: 当前值
                - previous_value: 上一期值
                - unit: 单位(可选)
                - time_period: 当前时间周期(可选)
                - previous_time_period: 上一时间周期(可选)
                - historical_values: 历史值列表(可选)
                - is_positive_better: 正向变化是否为好(可选)
            
        返回:
            Dict[str, Any]: 分析结果
        """
        # 验证必要字段
        required_fields = ["name", "value", "previous_value"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        metric_name = data["name"]
        current_value = data["value"]
        previous_value = data["previous_value"]
        unit = data.get("unit", "")
        time_period = data.get("time_period", "当前")
        previous_time_period = data.get("previous_time_period", "上一期")
        historical_values = data.get("historical_values", [])
        
        # 判断指标正向增长是否为好
        is_positive_better = data.get("is_positive_better", None)
        if is_positive_better is None:
            # 根据指标名称判断
            for key, value in self.positive_growth_is_good.items():
                if key in metric_name:
                    is_positive_better = value
                    break
            # 如果无法判断，默认为正向增长是好的
            if is_positive_better is None:
                is_positive_better = True
        
        # 计算基本指标
        change_value = calculate_change(current_value, previous_value)
        change_rate = calculate_change_rate(current_value, previous_value)
        change_class = classify_change(change_rate)
        
        # 异常检测
        is_anomaly, anomaly_degree = detect_anomaly(current_value, historical_values)
        is_higher_anomaly = current_value > np.mean(historical_values) if historical_values else None
        
        # 趋势分析
        if historical_values and len(historical_values) >= 2:
            trend_type, trend_strength = calculate_trend(historical_values + [current_value])
        else:
            trend_type, trend_strength = None, 0.0
        
        # 整合结果
        result = {
            "基本信息": {
                "指标名称": metric_name,
                "当前值": current_value,
                "上一期值": previous_value,
                "单位": unit,
                "当前周期": time_period,
                "上一周期": previous_time_period,
                "正向增长是否为好": is_positive_better
            },
            "变化分析": {
                "变化量": change_value,
                "变化率": change_rate,
                "变化类别": change_class,
                "变化方向": "增加" if change_value > 0 else "减少" if change_value < 0 else "保持不变"
            },
            "异常分析": {
                "是否异常": is_anomaly,
                "异常程度": anomaly_degree,
                "是否高于正常范围": is_higher_anomaly
            }
        }
        
        # 添加趋势分析(如果有)
        if trend_type:
            result["趋势分析"] = {
                "趋势类型": trend_type,
                "趋势强度": trend_strength
            }
        
        return result 