"""
文本处理工具函数
==============

提供用于文本生成和处理的工具函数。
"""

from typing import Dict, List, Any, Optional
import random


def format_number(
    value: float, unit: str = "", precision: int = 2, use_wan: bool = True
) -> str:
    """
    格式化数字显示
    
    参数:
        value (float): 要格式化的数值
        unit (str, optional): 单位，如"元"、"个"等，默认为空字符串
        precision (int, optional): 小数点后保留的位数，默认为2
        use_wan (bool, optional): 是否使用"万"、"亿"来简化数字，默认为True
        
    返回:
        str: 格式化后的数字字符串
    """
    if abs(value) < 1e-10:  # 接近于0
        return f"0{unit}"
    
    # 处理负数
    negative = value < 0
    abs_value = abs(value)
    
    # 根据数值大小选择合适的表示方式
    if use_wan:
        if abs_value >= 1e8:  # 亿
            formatted = round(abs_value / 1e8, precision)
            suffix = "亿"
        elif abs_value >= 1e4:  # 万
            formatted = round(abs_value / 1e4, precision)
            suffix = "万"
        else:
            formatted = round(abs_value, precision)
            suffix = ""
    else:
        if abs_value >= 1e9:  # 十亿
            formatted = round(abs_value / 1e9, precision)
            suffix = "B"
        elif abs_value >= 1e6:  # 百万
            formatted = round(abs_value / 1e6, precision)
            suffix = "M"
        elif abs_value >= 1e3:  # 千
            formatted = round(abs_value / 1e3, precision)
            suffix = "K"
        else:
            formatted = round(abs_value, precision)
            suffix = ""
    
    # 去除小数点后多余的0
    formatted_str = str(formatted)
    if "." in formatted_str:
        formatted_str = formatted_str.rstrip("0").rstrip(".")
    
    # 添加负号(如果需要)和单位
    result = f"{'-' if negative else ''}{formatted_str}{suffix}{unit}"
    return result


def format_percentage(value: Optional[float], precision: int = 2) -> str:
    """
    格式化百分比显示
    
    参数:
        value (Optional[float]): 要格式化的比率值，如0.1565表示15.65%
                               None表示无法计算百分比
        precision (int, optional): 小数点后保留的位数，默认为2
        
    返回:
        str: 格式化后的百分比字符串
    """
    if value is None:
        return "N/A"
    
    # 转换为百分比并四舍五入
    percentage = round(value * 100, precision)
    
    # 去除小数点后多余的0
    formatted = str(percentage)
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    
    return f"{formatted}%"


def get_change_description(
    change_class: str, metrics_name: str, is_positive_better: bool = True
) -> str:
    """
    获取变化描述文本
    
    参数:
        change_class (str): 变化分类，如"大幅增长"、"下降"等
        metrics_name (str): 指标名称
        is_positive_better (bool, optional): 正向变化是否为好的趋势，默认为True
        
    返回:
        str: 描述变化的文本
    """
    # 定义不同变化类型的描述模板
    descriptions = {
        "大幅增长": [
            f"{metrics_name}大幅增长",
            f"{metrics_name}显著提升",
            f"{metrics_name}大幅提高",
            f"{metrics_name}大幅上升"
        ],
        "增长": [
            f"{metrics_name}有所增长",
            f"{metrics_name}明显提升",
            f"{metrics_name}稳步增加",
            f"{metrics_name}保持增长"
        ],
        "轻微增长": [
            f"{metrics_name}略有增长",
            f"{metrics_name}小幅提升",
            f"{metrics_name}微幅增加",
            f"{metrics_name}有小幅上涨"
        ],
        "基本持平": [
            f"{metrics_name}基本持平",
            f"{metrics_name}保持稳定",
            f"{metrics_name}变化不大",
            f"{metrics_name}相对稳定"
        ],
        "轻微下降": [
            f"{metrics_name}略有下降",
            f"{metrics_name}小幅下滑",
            f"{metrics_name}微幅降低",
            f"{metrics_name}有小幅下跌"
        ],
        "下降": [
            f"{metrics_name}明显下降",
            f"{metrics_name}显著下滑",
            f"{metrics_name}明显降低",
            f"{metrics_name}持续下跌"
        ],
        "大幅下降": [
            f"{metrics_name}大幅下降",
            f"{metrics_name}显著下跌",
            f"{metrics_name}大幅降低",
            f"{metrics_name}大幅下滑"
        ],
        "未知": [
            f"{metrics_name}变化无法确定",
            f"{metrics_name}变化情况不明",
            f"{metrics_name}数据不足以判断变化",
            f"{metrics_name}变化趋势不确定"
        ]
    }
    
    # 随机选择一个描述
    if change_class in descriptions:
        description = random.choice(descriptions[change_class])
    else:
        description = f"{metrics_name}{change_class}"
    
    # 添加好坏评价
    if change_class != "基本持平" and change_class != "未知":
        # 判断变化是好是坏
        is_increase = change_class in ["大幅增长", "增长", "轻微增长"]
        is_good = (is_increase and is_positive_better) or (not is_increase and not is_positive_better)
        
        if is_good:
            evaluation = random.choice([
                "，这是一个积极的信号",
                "，表现良好",
                "，是一个正面趋势",
                "，发展态势良好"
            ])
        else:
            evaluation = random.choice([
                "，需要关注",
                "，是一个需要警惕的信号",
                "，表现不佳",
                "，是一个负面趋势"
            ])
        
        description += evaluation
    
    return description


def get_anomaly_description(
    is_anomaly: bool, 
    anomaly_degree: float, 
    metrics_name: str, 
    is_higher_anomaly: bool
) -> str:
    """
    获取异常情况描述文本
    
    参数:
        is_anomaly (bool): 是否为异常值
        anomaly_degree (float): 异常程度
        metrics_name (str): 指标名称
        is_higher_anomaly (bool): 异常值是否为高于正常范围
        
    返回:
        str: 描述异常情况的文本
    """
    if not is_anomaly:
        return ""
    
    # 根据异常程度选择描述
    if anomaly_degree > 3.0:
        degree_desc = "极度"
    elif anomaly_degree > 2.0:
        degree_desc = "非常"
    elif anomaly_degree > 1.0:
        degree_desc = "明显"
    else:
        degree_desc = "略微"
    
    # 根据异常方向选择描述
    direction_desc = "高于" if is_higher_anomaly else "低于"
    
    # 随机选择一个描述模板
    templates = [
        f"{metrics_name}的表现{degree_desc}{direction_desc}历史正常水平，属于异常情况",
        f"注意到{metrics_name}{degree_desc}{direction_desc}一般水平，可能需要特别关注",
        f"{metrics_name}出现{degree_desc}异常，{direction_desc}历史平均水平",
        f"本期{metrics_name}值{degree_desc}{direction_desc}预期范围，建议分析原因"
    ]
    
    return random.choice(templates) 