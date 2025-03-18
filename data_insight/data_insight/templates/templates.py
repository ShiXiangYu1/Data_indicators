"""
文本生成模板
=========

定义用于生成数据解读文本的各类模板。
"""

from typing import Dict, List, Any, Optional

# 指标变化解读模板
METRIC_CHANGE_TEMPLATES = [
    # 基本模板
    "{time_period}的{metric_name}为{current_value}{unit}，相比{previous_time_period}的{previous_value}{unit}{change_direction}了{change_value}{unit}，{change_rate_text}。{change_description}",
    
    # 先说变化比例，再说具体数值
    "{time_period}的{metric_name}{change_rate_text}。从{previous_value}{unit}增加到{current_value}{unit}，{change_direction}了{change_value}{unit}。{change_description}",
    
    # 简洁版
    "{metric_name}从{previous_value}{unit}{change_direction}至{current_value}{unit}，{change_rate_text}。{change_description}",
    
    # 强调现状
    "{time_period}{metric_name}达到{current_value}{unit}，与{previous_time_period}相比{change_direction}了{change_value}{unit}，{change_rate_text}。{change_description}"
]

# 异常情况解读模板（列表）
ANOMALY_TEMPLATES_LIST = [
    "{anomaly_description}",
    "值得注意的是，{anomaly_description}",
    "特别提醒，{anomaly_description}",
    "需要特别关注，{anomaly_description}"
]

# 趋势解读模板
TREND_TEMPLATES = [
    "从历史数据来看，{metric_name}呈{trend_type}趋势。",
    "分析历史数据，{metric_name}整体{trend_type}。",
    "{metric_name}的历史表现显示其{trend_type}。",
    "纵观历史数据，{metric_name}总体呈{trend_type}的发展态势。"
]

# 原因分析模板（列表）
REASON_TEMPLATES_LIST = [
    "造成这一变化的可能原因包括：{reasons}",
    "导致{metric_name}{change_direction}的主要因素可能有：{reasons}",
    "分析表明，{reasons}可能是引起{metric_name}变化的关键因素。",
    "{metric_name}的这一变化，可能与以下因素有关：{reasons}"
]

# 建议行动模板（列表）
ACTION_TEMPLATES_LIST = [
    "建议采取以下措施：{actions}",
    "针对这一情况，可以考虑：{actions}",
    "为了应对这一变化，建议：{actions}",
    "基于以上分析，推荐以下行动方案：{actions}"
]

# 整合洞察
def generate_metric_insight_template(
    has_anomaly: bool = False, 
    has_trend: bool = False, 
    has_reason: bool = False,
    has_action: bool = False
) -> str:
    """
    生成整合的指标洞察模板
    
    参数:
        has_anomaly (bool): 是否包含异常情况解读
        has_trend (bool): 是否包含趋势解读
        has_reason (bool): 是否包含原因分析
        has_action (bool): 是否包含建议行动
        
    返回:
        str: 整合后的模板
    """
    import random
    
    # 基础变化描述
    template = random.choice(METRIC_CHANGE_TEMPLATES) + " "
    
    # 添加异常情况描述
    if has_anomaly:
        template += random.choice(ANOMALY_TEMPLATES_LIST) + " "
    
    # 添加趋势描述
    if has_trend:
        template += random.choice(TREND_TEMPLATES) + " "
    
    # 添加原因分析
    if has_reason:
        template += random.choice(REASON_TEMPLATES_LIST) + " "
    
    # 添加建议行动
    if has_action:
        template += random.choice(ACTION_TEMPLATES_LIST)
    
    return template.strip()

# 指标变化描述模板
CHANGE_TEMPLATES = {
    "positive_significant": [
        "显著增长了{change_rate}%",
        "大幅上升了{change_rate}%",
        "增幅明显，提升了{change_rate}%",
        "有显著提高，增长了{change_rate}%"
    ],
    "positive_moderate": [
        "增长了{change_rate}%",
        "上升了{change_rate}%",
        "提高了{change_rate}%",
        "有所增长，涨幅为{change_rate}%"
    ],
    "positive_slight": [
        "小幅增长了{change_rate}%",
        "略有上升，增长了{change_rate}%",
        "微增{change_rate}%",
        "有小幅提升，增长了{change_rate}%"
    ],
    "negative_significant": [
        "显著下降了{change_rate_abs}%",
        "大幅下跌了{change_rate_abs}%",
        "降幅明显，下降了{change_rate_abs}%",
        "明显减少，降低了{change_rate_abs}%"
    ],
    "negative_moderate": [
        "下降了{change_rate_abs}%",
        "减少了{change_rate_abs}%",
        "降低了{change_rate_abs}%",
        "有所下降，降幅为{change_rate_abs}%"
    ],
    "negative_slight": [
        "小幅下降了{change_rate_abs}%",
        "略有下降，减少了{change_rate_abs}%",
        "微降{change_rate_abs}%",
        "有小幅下降，降低了{change_rate_abs}%"
    ],
    "unchanged": [
        "基本保持稳定，变化不大",
        "几乎保持不变",
        "基本维持原水平，波动很小",
        "保持平稳，变化率接近于0"
    ]
}

# 异常分析模板（字典）
ANOMALY_TEMPLATES = {
    "high_anomaly": [
        "出现了显著高于正常范围的异常值",
        "数据出现了异常高峰",
        "存在明显的正向异常值",
        "观察到高于预期的异常数据点"
    ],
    "low_anomaly": [
        "出现了显著低于正常范围的异常值",
        "数据出现了异常低谷",
        "存在明显的负向异常值",
        "观察到低于预期的异常数据点"
    ]
}

# 原因分析模板（字典）
REASON_TEMPLATES = {
    "positive_change": [
        "可能与市场需求增加有关",
        "可能得益于产品质量提升",
        "可能与营销活动效果良好有关",
        "可能与行业整体向好趋势相关",
        "可能是季节性因素导致的正常增长",
        "可能与客户满意度提升有关",
        "可能是新市场开拓取得成效"
    ],
    "negative_change": [
        "可能与市场竞争加剧有关",
        "可能受到经济下行影响",
        "可能与产品周期进入衰退期有关",
        "可能是季节性波动导致的正常下降",
        "可能与客户流失有关",
        "可能受到外部环境变化的负面影响",
        "可能与营销策略调整不当有关"
    ],
    "anomaly_high": [
        "可能是特殊促销活动带来的短期高峰",
        "可能与重大事件或节假日有关",
        "可能是大客户一次性大额交易导致",
        "可能存在统计口径变化或数据错误",
        "可能是市场突发事件引起的短期波动"
    ],
    "anomaly_low": [
        "可能受到突发事件负面影响",
        "可能与系统故障或服务中断有关",
        "可能是重要客户流失导致",
        "可能存在统计口径变化或数据错误",
        "可能是市场突发事件引起的短期波动"
    ]
}

# 行动建议模板（字典）
ACTION_TEMPLATES = {
    "positive_insight": [
        "建议继续保持现有策略，巩固良好态势",
        "可以考虑扩大成功经验，复制到其他领域",
        "建议深入分析成功因素，进一步提升表现",
        "可以适当增加资源投入，扩大优势"
    ],
    "negative_insight": [
        "建议分析下降原因，及时调整相关策略",
        "可以考虑加强市场调研，了解客户需求变化",
        "建议评估产品或服务是否需要优化升级",
        "可以考虑调整资源分配，加强薄弱环节"
    ],
    "anomaly_insight": [
        "建议进一步验证数据准确性，排除统计误差",
        "可以深入调查异常原因，评估是否需要干预",
        "建议密切监控后续数据变化，判断是否为趋势变化",
        "可以制定应急预案，应对可能的风险或机遇"
    ],
    "general_insight": [
        "建议持续监控指标变化，保持对市场的敏感度",
        "可以加强数据分析能力，提升决策效率",
        "建议与行业标杆对比，找出改进空间",
        "可以建立预警机制，及时发现潜在问题"
    ]
}

# 指标解读完整模板
METRIC_TEMPLATES = {
    "metric_basic": [
        "{metric_name}当前值为{current_value}{unit}，相比上一期的{previous_value}{unit}，{change_description}。",
        "{metric_name}最新数据为{current_value}{unit}，与上期{previous_value}{unit}相比，{change_description}。",
        "{metric_name}本期达到{current_value}{unit}，相较于上期的{previous_value}{unit}，{change_description}。"
    ],
    "metric_with_anomaly": [
        "{metric_name}当前值为{current_value}{unit}，相比上一期的{previous_value}{unit}，{change_description}。{anomaly_description}",
        "{metric_name}最新数据为{current_value}{unit}，与上期{previous_value}{unit}相比，{change_description}。{anomaly_description}",
        "{metric_name}本期达到{current_value}{unit}，相较于上期的{previous_value}{unit}，{change_description}。{anomaly_description}"
    ],
    "metric_with_trend": [
        "{metric_name}当前值为{current_value}{unit}，相比上一期的{previous_value}{unit}，{change_description}。从历史数据来看，该指标{trend_description}。",
        "{metric_name}最新数据为{current_value}{unit}，与上期{previous_value}{unit}相比，{change_description}。从趋势上看，该指标{trend_description}。",
        "{metric_name}本期达到{current_value}{unit}，相较于上期的{previous_value}{unit}，{change_description}。从长期来看，该指标{trend_description}。"
    ],
    "metric_comprehensive": [
        "{metric_name}当前值为{current_value}{unit}，相比上一期的{previous_value}{unit}，{change_description}。{anomaly_description}从历史数据来看，该指标{trend_description}。{reason_description}{action_suggestion}",
        "{metric_name}最新数据为{current_value}{unit}，与上期{previous_value}{unit}相比，{change_description}。{anomaly_description}从趋势上看，该指标{trend_description}。{reason_description}{action_suggestion}",
        "{metric_name}本期达到{current_value}{unit}，相较于上期的{previous_value}{unit}，{change_description}。{anomaly_description}从长期来看，该指标{trend_description}。{reason_description}{action_suggestion}"
    ]
}

# 添加图表解读相关的模板
CHART_TEMPLATES = {
    "chart_overall_trend": [
        "《{chart_title}》显示，整体趋势{analysis[整体分析][整体趋势]}。图表中共包含{analysis[基本信息][系列数]}个数据系列，在{x_axis_label}维度上展示了{y_axis_label}的变化情况。",
        "从《{chart_title}》可以看出，数据整体{analysis[整体分析][整体趋势]}。该图表包含{analysis[基本信息][系列数]}个数据系列，横轴为{x_axis_label}，纵轴为{y_axis_label}。",
        "整体来看，《{chart_title}》中的数据呈{analysis[整体分析][整体趋势]}特征。图表展示了{analysis[基本信息][系列数]}个系列在{x_axis_label}维度上的{y_axis_label}情况。"
    ],
    
    "chart_series_trend": [
        "{analysis[系列分析][0][系列名称]}的趋势为{analysis[系列分析][0][趋势分析][趋势类型]}，整体{analysis[系列分析][0][趋势分析][趋势强度]}。",
        "{analysis[系列分析][0][系列名称]}呈{analysis[系列分析][0][趋势分析][趋势类型]}趋势，变化幅度{analysis[系列分析][0][趋势分析][趋势强度]}。",
        "{analysis[系列分析][0][系列名称]}的整体表现{analysis[系列分析][0][趋势分析][趋势类型]}，幅度{analysis[系列分析][0][趋势分析][趋势强度]}。"
    ],
    
    "chart_anomaly": [
        "数据中{analysis[系列分析][0][异常点数量]}个异常点，最显著的异常出现在{analysis[系列分析][0][异常点][0][位置]}，其值为{analysis[系列分析][0][异常点][0][值]}，{analysis[系列分析][0][异常点][0][描述]}。",
        "分析发现{analysis[系列分析][0][异常点数量]}处明显异常，其中最突出的是{analysis[系列分析][0][异常点][0][位置]}处的{analysis[系列分析][0][异常点][0][值]}，{analysis[系列分析][0][异常点][0][描述]}。",
        "数据存在{analysis[系列分析][0][异常点数量]}个异常波动，最主要的异常为{analysis[系列分析][0][异常点][0][位置]}的{analysis[系列分析][0][异常点][0][值]}，{analysis[系列分析][0][异常点][0][描述]}。"
    ],
    
    "chart_distribution": [
        "{analysis[系列分析][0][系列名称]}的数据分布特征为\"{analysis[系列分析][0][分布特征]}\"。在{analysis[基本信息][X轴类别数]}个{x_axis_label}中，最高值出现在{analysis[系列分析][0][统计信息][最大值类别]}，为{analysis[系列分析][0][统计信息][最大值]}；最低值出现在{analysis[系列分析][0][统计信息][最小值类别]}，为{analysis[系列分析][0][统计信息][最小值]}。",
        "从分布来看，{analysis[系列分析][0][系列名称]}表现为\"{analysis[系列分析][0][分布特征]}\"。在全部{analysis[基本信息][X轴类别数]}个{x_axis_label}中，{analysis[系列分析][0][统计信息][最大值类别]}的{y_axis_label}最高，达到{analysis[系列分析][0][统计信息][最大值]}；而{analysis[系列分析][0][统计信息][最小值类别]}的{y_axis_label}最低，仅为{analysis[系列分析][0][统计信息][最小值]}。",
        "{analysis[系列分析][0][系列名称]}的数据分布呈现\"{analysis[系列分析][0][分布特征]}\"的特点。在{analysis[基本信息][X轴类别数]}个{x_axis_label}中，{analysis[系列分析][0][统计信息][最大值类别]}以{analysis[系列分析][0][统计信息][最大值]}的{y_axis_label}领先，而{analysis[系列分析][0][统计信息][最小值类别]}以{analysis[系列分析][0][统计信息][最小值]}的{y_axis_label}垫底。"
    ],
    
    "chart_category_comparison": [
        "对比来看，{analysis[类别对比][0][主体类别]}和{analysis[类别对比][0][对比类别]}的差异最为显著，相差{analysis[类别对比][0][差异比例]}。",
        "在各{x_axis_label}中，{analysis[类别对比][0][主体类别]}与{analysis[类别对比][0][对比类别]}的差距最大，为{analysis[类别对比][0][差异比例]}。",
        "{analysis[类别对比][0][主体类别]}相比{analysis[类别对比][0][对比类别]}高出{analysis[类别对比][0][差异比例]}，差异最为明显。"
    ],
    
    "chart_multi_series_comparison": [
        "比较{analysis[系列分析][0][系列名称]}和{analysis[系列分析][1][系列名称]}可以看出，二者{analysis[系列间关系][相关性描述]}，{analysis[系列间关系][差异描述]}。",
        "{analysis[系列分析][0][系列名称]}与{analysis[系列分析][1][系列名称]}的关系表现为{analysis[系列间关系][相关性描述]}，主要{analysis[系列间关系][差异描述]}。",
        "从{analysis[系列分析][0][系列名称]}和{analysis[系列分析][1][系列名称]}的对比来看，两个系列{analysis[系列间关系][相关性描述]}，并且{analysis[系列间关系][差异描述]}。"
    ]
}

# 指标对比模板
METRIC_COMPARISON_TEMPLATES = {
    "metric_comparison": [
        "{comparison[指标1][名称]}的当前值为{comparison[指标1][当前值]}{comparison[指标1][单位]}，{comparison[差异方向]}{comparison[指标2][名称]}的{comparison[指标2][当前值]}{comparison[指标2][单位]}，{comparison[描述]}。",
        "从数据上看，{comparison[指标1][名称]}({comparison[指标1][当前值]}{comparison[指标1][单位]})与{comparison[指标2][名称]}({comparison[指标2][当前值]}{comparison[指标2][单位]})相比，{comparison[描述]}。",
        "{comparison[指标1][名称]}与{comparison[指标2][名称]}的对比结果显示，{comparison[描述]}，差异程度为{comparison[差异大小]}。"
    ],
    
    "metric_correlation": [
        "{correlation[指标1]}与{correlation[指标2]}之间{correlation[描述]}。",
        "通过相关性分析可以看出，{correlation[指标1]}和{correlation[指标2]}{correlation[描述]}。",
        "{correlation[指标1]}和{correlation[指标2]}的关系分析表明，二者{correlation[描述]}。"
    ],
    
    "metric_group": [
        "在当前指标组中，有{group_stats[增长指标数量]}个指标呈增长趋势，{group_stats[下降指标数量]}个指标呈下降趋势，{group_stats[稳定指标数量]}个指标保持稳定。",
        "所有指标中，增长的有{group_stats[增长指标数量]}个，下降的有{group_stats[下降指标数量]}个，稳定的有{group_stats[稳定指标数量]}个。",
        "当前监控的指标中，{group_stats[增长指标数量]}个指标在增长，{group_stats[下降指标数量]}个指标在下降，{group_stats[稳定指标数量]}个指标相对稳定。"
    ],
    
    "top_growers": [
        "增长最快的指标是{top_grower[指标名称]}，增长了{top_grower[变化率百分比]}。",
        "{top_grower[指标名称]}表现最为突出，增长率达到{top_grower[变化率百分比]}。",
        "在所有指标中，{top_grower[指标名称]}的增长最为显著，达到{top_grower[变化率百分比]}。"
    ],
    
    "top_decliners": [
        "下降最快的指标是{top_decliner[指标名称]}，下降了{top_decliner[变化率百分比]}。",
        "{top_decliner[指标名称]}下滑最为明显，降幅达到{top_decliner[变化率百分比]}。",
        "在所有指标中，{top_decliner[指标名称]}的下降最为显著，降幅达到{top_decliner[变化率百分比]}。"
    ],
    
    "anomaly_group": [
        "检测到{anomaly_count}个异常指标，其中异常程度最高的是{top_anomaly[指标名称]}。",
        "有{anomaly_count}个指标出现异常，最值得关注的是{top_anomaly[指标名称]}。",
        "{anomaly_count}个指标显示异常情况，特别是{top_anomaly[指标名称]}异常程度最高。"
    ]
}

# 将所有模板合并
ALL_TEMPLATES = {
    **CHANGE_TEMPLATES,
    **REASON_TEMPLATES,
    **ACTION_TEMPLATES,
    **METRIC_TEMPLATES,
    **CHART_TEMPLATES,
    **METRIC_COMPARISON_TEMPLATES
} 