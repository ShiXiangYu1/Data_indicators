"""
文本生成器
========

根据分析结果生成自然语言解读文本。
"""

import random
from typing import Dict, Any, List, Optional, Union

from data_insight.utils.text_utils import (
    format_number,
    format_percentage,
    get_change_description,
    get_anomaly_description
)
from data_insight.templates.templates import (
    generate_metric_insight_template,
    METRIC_CHANGE_TEMPLATES,
    ANOMALY_TEMPLATES_LIST,
    TREND_TEMPLATES,
    REASON_TEMPLATES_LIST,
    ACTION_TEMPLATES_LIST,
    ALL_TEMPLATES
)


class TextGenerator:
    """
    文本生成器
    
    根据分析结果生成自然语言的解读文本。
    """
    
    def __init__(self, templates: Optional[Dict[str, Any]] = None):
        """
        初始化文本生成器
        
        参数:
            templates (Optional[Dict[str, Any]]): 自定义模板字典，如果不提供则使用默认模板
        """
        self.templates = templates if templates is not None else ALL_TEMPLATES
    
    def generate_text(self, analysis_result: Dict[str, Any]) -> str:
        """
        生成解读文本
        
        参数:
            analysis_result (Dict[str, Any]): 分析结果，包含基本信息、变化分析等
            
        返回:
            str: 生成的解读文本
        """
        # 检查分析结果类型，调用相应的生成方法
        if "基本信息" in analysis_result and "变化分析" in analysis_result:
            return self.generate_metric_insight(analysis_result)
        elif "基本信息" in analysis_result and "指标数量" in analysis_result["基本信息"]:
            return self.generate_metric_comparison_insight(analysis_result)
        else:
            return "无法识别的分析结果类型"
    
    def generate_metric_insight(self, metric_analysis: Dict[str, Any]) -> str:
        """
        生成指标卡解读文本
        
        参数:
            metric_analysis (Dict[str, Any]): 指标分析结果
            
        返回:
            str: 生成的指标解读文本
        """
        # 提取基本信息
        basic_info = metric_analysis["基本信息"]
        metric_name = basic_info["指标名称"]
        current_value = basic_info["当前值"]
        previous_value = basic_info["上一期值"]
        unit = basic_info["单位"]
        time_period = basic_info["当前周期"]
        previous_time_period = basic_info["上一周期"]
        is_positive_better = basic_info["正向增长是否为好"]
        
        # 提取变化分析
        change_analysis = metric_analysis["变化分析"]
        change_value = change_analysis["变化量"]
        change_rate = change_analysis["变化率"]
        change_class = change_analysis["变化类别"]
        change_direction = change_analysis["变化方向"]
        
        # 确定是否有异常分析和趋势分析
        has_anomaly = "异常分析" in metric_analysis and metric_analysis["异常分析"]["是否异常"]
        has_trend = "趋势分析" in metric_analysis
        
        # 格式化数值
        current_value_formatted = format_number(current_value, unit)
        previous_value_formatted = format_number(previous_value, unit)
        change_value_formatted = format_number(abs(change_value), unit)
        change_rate_text = format_percentage(change_rate) + ("增长" if change_rate > 0 else "下降" if change_rate < 0 else "")
        
        # 获取变化描述
        change_description = get_change_description(change_class, metric_name, is_positive_better)
        
        # 准备模板填充数据
        template_data = {
            "metric_name": metric_name,
            "current_value": current_value_formatted,
            "previous_value": previous_value_formatted,
            "change_value": change_value_formatted,
            "change_rate_text": change_rate_text,
            "change_direction": change_direction,
            "time_period": time_period,
            "previous_time_period": previous_time_period,
            "unit": unit,
            "change_description": change_description
        }
        
        # 添加异常分析（如果有）
        if has_anomaly:
            anomaly_info = metric_analysis["异常分析"]
            anomaly_degree = anomaly_info["异常程度"]
            is_higher_anomaly = anomaly_info["是否高于正常范围"]
            
            anomaly_description = get_anomaly_description(
                True, anomaly_degree, metric_name, is_higher_anomaly
            )
            template_data["anomaly_description"] = anomaly_description
        
        # 添加趋势分析（如果有）
        if has_trend:
            trend_info = metric_analysis["趋势分析"]
            trend_type = trend_info["趋势类型"]
            template_data["trend_type"] = trend_type
        
        # 生成文本模板
        template = generate_metric_insight_template(
            has_anomaly=has_anomaly,
            has_trend=has_trend,
            has_reason=False,  # 暂不支持原因分析
            has_action=False   # 暂不支持行动建议
        )
        
        # 填充模板
        try:
            insight_text = template.format(**template_data)
            return insight_text
        except KeyError as e:
            return f"生成文本时出错: 缺少必要的模板参数 {e}"
    
    def generate_metric_comparison_insight(self, comparison_analysis: Dict[str, Any]) -> str:
        """
        生成指标对比解读文本
        
        参数:
            comparison_analysis (Dict[str, Any]): 指标对比分析结果
            
        返回:
            str: 生成的指标对比解读文本
        """
        # 检查必要的分析结果是否存在
        if "对比分析" not in comparison_analysis or not comparison_analysis["对比分析"]:
            return "没有足够的数据进行指标对比分析"
        
        insights = []
        
        # 生成基本信息概述
        basic_info = comparison_analysis["基本信息"]
        insights.append(f"本次分析包含{basic_info['指标数量']}个指标: {', '.join(basic_info['指标名称列表'])}。")
        
        # 生成指标对比洞察
        if comparison_analysis["对比分析"]:
            # 找出最显著的对比（差异最大的）
            most_significant_comparison = max(
                comparison_analysis["对比分析"], 
                key=lambda x: abs(x["相对差异"]) if x["相对差异"] is not None else 0
            )
            
            # 生成对比洞察
            try:
                comparison_insight = self.generate(
                    "metric_comparison", 
                    {"comparison": most_significant_comparison}
                )
                insights.append(comparison_insight)
            except ValueError as e:
                pass
        
        # 生成相关性分析洞察
        if comparison_analysis["相关性分析"]:
            # 找出最显著的相关性（相关系数绝对值最大且统计显著的）
            significant_correlations = [c for c in comparison_analysis["相关性分析"] if c["显著性"]]
            if significant_correlations:
                most_significant_correlation = max(
                    significant_correlations,
                    key=lambda x: abs(x["相关系数"])
                )
                
                # 生成相关性洞察
                try:
                    correlation_insight = self.generate(
                        "metric_correlation", 
                        {"correlation": most_significant_correlation}
                    )
                    insights.append(correlation_insight)
                except ValueError as e:
                    pass
        
        # 生成指标群组分析洞察
        if comparison_analysis["群组分析"]:
            groups = comparison_analysis["群组分析"]
            group_stats = {
                "增长指标数量": len(groups.get("增长指标", [])),
                "下降指标数量": len(groups.get("下降指标", [])),
                "稳定指标数量": len(groups.get("稳定指标", [])),
                "异常指标数量": len(groups.get("异常指标", []))
            }
            
            # 生成群组概述
            try:
                group_insight = self.generate(
                    "metric_group", 
                    {"group_stats": group_stats}
                )
                insights.append(group_insight)
            except ValueError as e:
                pass
            
            # 生成增长最快指标信息
            if groups.get("增长指标"):
                top_grower = groups["增长指标"][0]  # 已按变化率排序，第一个是增长最快的
                top_grower["变化率百分比"] = f"{top_grower['变化率']*100:.1f}%"
                
                try:
                    grower_insight = self.generate(
                        "top_growers", 
                        {"top_grower": top_grower}
                    )
                    insights.append(grower_insight)
                except ValueError as e:
                    pass
            
            # 生成下降最快指标信息
            if groups.get("下降指标"):
                top_decliner = groups["下降指标"][0]  # 已按变化率排序，第一个是下降最快的
                top_decliner["变化率百分比"] = f"{abs(top_decliner['变化率'])*100:.1f}%"
                
                try:
                    decliner_insight = self.generate(
                        "top_decliners", 
                        {"top_decliner": top_decliner}
                    )
                    insights.append(decliner_insight)
                except ValueError as e:
                    pass
            
            # 生成异常指标信息
            if groups.get("异常指标"):
                anomaly_count = len(groups["异常指标"])
                if anomaly_count > 0:
                    top_anomaly = groups["异常指标"][0]  # 已按异常程度排序
                    
                    try:
                        anomaly_insight = self.generate(
                            "anomaly_group", 
                            {
                                "anomaly_count": anomaly_count,
                                "top_anomaly": top_anomaly
                            }
                        )
                        insights.append(anomaly_insight)
                    except ValueError as e:
                        pass
        
        # 合并所有洞察
        return "\n\n".join(insights)
    
    def generate(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        根据指定模板名称生成文本
        
        参数:
            template_name (str): 模板名称，对应templates中的键
            data (Dict[str, Any]): 用于填充模板的数据
            
        返回:
            str: 生成的文本
            
        异常:
            ValueError: 如果指定的模板名称不存在
        """
        if template_name not in self.templates:
            raise ValueError(f"模板名称 '{template_name}' 不存在")
        
        # 获取模板
        templates = self.templates[template_name]
        
        # 如果模板是字符串列表，随机选择一个
        if isinstance(templates, list):
            template = random.choice(templates)
        else:
            template = templates
        
        # 尝试使用数据填充模板
        try:
            result = template.format(**data)
            return result
        except KeyError as e:
            # 如果缺少必要的数据字段，给出更友好的错误提示
            missing_key = str(e).strip("'")
            raise ValueError(f"模板 '{template_name}' 需要数据字段 '{missing_key}'，但未提供")
        except Exception as e:
            # 其他错误
            raise ValueError(f"填充模板时出错: {str(e)}") 