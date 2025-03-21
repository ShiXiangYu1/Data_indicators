"""
操作推荐器
========

根据分析结果向用户提供行动建议，帮助用户采取下一步措施。
"""

from typing import Dict, Any, List, Optional, Union
import logging
import random

from data_insight.core.interfaces.recommender import RecommenderInterface


class ActionRecommender(RecommenderInterface):
    """
    操作推荐器
    
    根据指标分析和图表分析结果，向用户提供具体的行动建议。
    可以识别异常模式、关键趋势，并推荐相应的操作措施。
    """
    
    def __init__(self):
        """初始化操作推荐器"""
        self.logger = logging.getLogger("data_insight.recommendation.action")
        self.recommendation_templates = self._load_recommendation_templates()
        self.max_recommendations = 3  # 默认最多返回3条建议
        self.recommendation_threshold = 0.6  # 建议相关性阈值，高于此值的建议才会返回
    
    def recommend(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据分析数据生成行动建议
        
        参数:
            data (Dict[str, Any]): 分析数据
            context (Optional[Dict[str, Any]]): 上下文信息
            
        返回:
            Dict[str, Any]: 建议结果，包含建议列表、优先级等
        """
        # 验证输入数据
        self._validate_input(data)
        
        # 提取上下文信息
        ctx = context or {}
        
        # 判断数据类型
        data_type = self._determine_data_type(data)
        
        # 根据数据类型选择不同的处理方法
        if data_type == "metric":
            recommendations = self._recommend_for_metric(data, ctx)
        elif data_type == "chart":
            recommendations = self._recommend_for_chart(data, ctx)
        elif data_type == "comparison":
            recommendations = self._recommend_for_comparison(data, ctx)
        else:
            recommendations = self._recommend_generic(data, ctx)
        
        # 过滤并排序建议
        filtered_recommendations = self._filter_recommendations(recommendations, 
                                                             threshold=ctx.get("threshold", self.recommendation_threshold))
        
        # 按优先级排序
        sorted_recommendations = sorted(filtered_recommendations, key=lambda x: x["priority"], reverse=True)
        
        # 限制返回数量
        max_count = ctx.get("max_count", self.max_recommendations)
        final_recommendations = sorted_recommendations[:max_count]
        
        return {
            "status": "success",
            "recommendations": final_recommendations,
            "recommendation_count": len(final_recommendations),
            "data_type": data_type
        }
    
    def set_max_recommendations(self, count: int) -> bool:
        """
        设置最大建议数量
        
        参数:
            count (int): 最大建议数量
            
        返回:
            bool: 是否设置成功
            
        异常:
            ValueError: 如果数量不是正整数
        """
        if not isinstance(count, int) or count <= 0:
            raise ValueError(f"最大建议数量必须是正整数，但收到了 {count}")
        
        self.max_recommendations = count
        return True
    
    def set_recommendation_threshold(self, threshold: float) -> bool:
        """
        设置建议相关性阈值
        
        参数:
            threshold (float): 建议相关性阈值，范围[0, 1]
            
        返回:
            bool: 是否设置成功
            
        异常:
            ValueError: 如果阈值不在[0, 1]范围内
        """
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            raise ValueError(f"建议相关性阈值必须在0-1范围内，但收到了 {threshold}")
        
        self.recommendation_threshold = threshold
        return True
    
    def get_settings(self) -> Dict[str, Any]:
        """
        获取推荐器设置
        
        返回:
            Dict[str, Any]: 当前设置
        """
        return {
            "max_recommendations": self.max_recommendations,
            "recommendation_threshold": self.recommendation_threshold,
            "template_count": len(self.recommendation_templates)
        }
    
    def add_recommendation_template(self, template: Dict[str, Any]) -> bool:
        """
        添加建议模板
        
        参数:
            template (Dict[str, Any]): 建议模板
            
        返回:
            bool: 是否添加成功
            
        异常:
            ValueError: 如果模板格式不正确
        """
        required_fields = ["id", "type", "condition", "message", "action"]
        missing_fields = [field for field in required_fields if field not in template]
        
        if missing_fields:
            raise ValueError(f"建议模板缺少必需字段: {', '.join(missing_fields)}")
        
        if template["id"] in [t["id"] for t in self.recommendation_templates]:
            raise ValueError(f"已存在ID为 {template['id']} 的建议模板")
        
        self.recommendation_templates.append(template)
        return True
    
    def _validate_input(self, data: Dict[str, Any]) -> bool:
        """
        验证输入数据是否符合要求
        
        参数:
            data (Dict[str, Any]): 待验证的数据
            
        返回:
            bool: 验证是否通过
            
        异常:
            ValueError: 如果输入数据不符合要求
        """
        if not isinstance(data, dict):
            raise TypeError(f"输入数据必须是字典类型，但收到了 {type(data)}")
            
        # 尝试获取分析结果，如果不存在任何可识别的分析结果，则报错
        if not any(key in data for key in [
            "分析", "基本信息", "变化分析", "趋势分析", "异常检测", "统计信息", 
            "图表分析", "对比分析", "预测结果"
        ]):
            raise ValueError("输入数据不包含任何可识别的分析结果")
            
        return True
    
    def _determine_data_type(self, data: Dict[str, Any]) -> str:
        """
        确定数据类型
        
        参数:
            data (Dict[str, Any]): 分析数据
            
        返回:
            str: 数据类型，如"metric"、"chart"、"comparison"等
        """
        if "图表分析" in data or "chart_type" in data:
            return "chart"
        elif "对比分析" in data or "相关性分析" in data:
            return "comparison"
        elif "基本信息" in data and ("变化分析" in data or "趋势分析" in data):
            return "metric"
        else:
            return "generic"
    
    def _recommend_for_metric(self, data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为指标分析生成建议
        
        参数:
            data (Dict[str, Any]): 指标分析数据
            context (Dict[str, Any]): 上下文信息
            
        返回:
            List[Dict[str, Any]]: 建议列表
        """
        recommendations = []
        
        # 提取基本信息
        basic_info = data.get("基本信息", {})
        metric_name = basic_info.get("指标名称", "未知指标")
        metric_unit = basic_info.get("单位", "")
        current_value = basic_info.get("当前值", 0)
        
        # 提取变化分析信息
        change_analysis = data.get("变化分析", {})
        change_rate = change_analysis.get("环比变化率", 0)
        change_direction = change_analysis.get("变化方向", "")
        
        # 提取趋势分析信息
        trend_analysis = data.get("趋势分析", {})
        trend_type = trend_analysis.get("趋势类型", "")
        recent_trend = trend_analysis.get("最近趋势", "")
        
        # 提取异常检测信息
        anomaly_detection = data.get("异常检测", {})
        is_anomaly = anomaly_detection.get("是否异常", False)
        anomaly_degree = anomaly_detection.get("异常程度", "")
        
        # 根据不同情况生成建议
        
        # 1. 对异常情况的建议
        if is_anomaly:
            if anomaly_degree in ["严重", "高"]:
                recommendations.append({
                    "id": "anomaly_serious",
                    "title": f"{metric_name}出现严重异常",
                    "description": f"{metric_name}当前值({current_value}{metric_unit})存在{anomaly_degree}异常，建议立即分析原因并采取措施。",
                    "priority": 1.0,  # 最高优先级
                    "action": f"分析{metric_name}出现异常的原因，检查相关业务流程和系统运行状态。",
                    "relevance": 0.95
                })
            else:
                recommendations.append({
                    "id": "anomaly_moderate",
                    "title": f"{metric_name}出现异常波动",
                    "description": f"{metric_name}当前值显示异常波动，建议关注是否有业务变动或外部因素影响。",
                    "priority": 0.8,
                    "action": f"继续监控{metric_name}的变化趋势，分析是否是季节性波动或其他可解释因素。",
                    "relevance": 0.85
                })
        
        # 2. 对显著变化的建议
        if abs(change_rate) > 0.2:  # 变化率超过20%
            if change_direction == "上升":
                recommendations.append({
                    "id": "significant_increase",
                    "title": f"{metric_name}显著增长",
                    "description": f"{metric_name}环比增长了{abs(change_rate):.2f}%，显著高于正常波动范围。",
                    "priority": 0.9 if abs(change_rate) > 0.5 else 0.7,  # 变化越大优先级越高
                    "action": f"分析{metric_name}增长的驱动因素，评估是否需要调整资源配置或战略计划。",
                    "relevance": min(0.9, 0.5 + abs(change_rate) / 2)
                })
            elif change_direction == "下降":
                recommendations.append({
                    "id": "significant_decrease",
                    "title": f"{metric_name}显著下降",
                    "description": f"{metric_name}环比下降了{abs(change_rate):.2f}%，显著低于正常波动范围。",
                    "priority": 0.9 if abs(change_rate) > 0.5 else 0.7,
                    "action": f"排查{metric_name}下降的原因，制定挽回计划或调整预期。",
                    "relevance": min(0.9, 0.5 + abs(change_rate) / 2)
                })
        
        # 3. 对趋势的建议
        if trend_type == "上升" and recent_trend == "加速":
            recommendations.append({
                "id": "accelerating_uptrend",
                "title": f"{metric_name}增长加速",
                "description": f"{metric_name}呈加速上升趋势，可能预示着业务增长点或需求增加。",
                "priority": 0.75,
                "action": f"分析{metric_name}增长加速的原因，评估是否需要增加资源投入以满足增长需求。",
                "relevance": 0.8
            })
        elif trend_type == "下降" and recent_trend == "加速":
            recommendations.append({
                "id": "accelerating_downtrend",
                "title": f"{metric_name}下降加速",
                "description": f"{metric_name}呈加速下降趋势，可能存在潜在风险。",
                "priority": 0.85,
                "action": f"紧急评估{metric_name}下降加速的原因，制定应对措施防止进一步恶化。",
                "relevance": 0.85
            })
        elif trend_type == "上升" and recent_trend == "减速":
            recommendations.append({
                "id": "decelerating_uptrend",
                "title": f"{metric_name}增长放缓",
                "description": f"{metric_name}虽然仍在增长，但增速已经开始放缓。",
                "priority": 0.6,
                "action": f"分析{metric_name}增长放缓的因素，评估是否属于市场饱和或其他限制因素。",
                "relevance": 0.7
            })
        
        # 4. 根据数值范围的特定建议
        stats = data.get("统计信息", {})
        if stats:
            max_value = stats.get("最大值", None)
            min_value = stats.get("最小值", None)
            avg_value = stats.get("平均值", None)
            
            if current_value == max_value:
                recommendations.append({
                    "id": "historical_high",
                    "title": f"{metric_name}达到历史最高",
                    "description": f"{metric_name}已达到历史记录以来的最高值({current_value}{metric_unit})。",
                    "priority": 0.8,
                    "action": f"评估{metric_name}达到历史高点的可持续性，并考虑相应的资源配置和扩展计划。",
                    "relevance": 0.8
                })
            elif current_value == min_value and change_direction == "下降":
                recommendations.append({
                    "id": "historical_low",
                    "title": f"{metric_name}创历史新低",
                    "description": f"{metric_name}已创历史记录以来的最低值({current_value}{metric_unit})，且仍在下降。",
                    "priority": 0.85,
                    "action": f"分析{metric_name}降至历史低点的原因，制定恢复计划。",
                    "relevance": 0.85
                })
            elif avg_value is not None and current_value < avg_value * 0.7:
                recommendations.append({
                    "id": "significantly_below_average",
                    "title": f"{metric_name}显著低于平均水平",
                    "description": f"{metric_name}当前值({current_value}{metric_unit})显著低于历史平均水平({avg_value:.2f}{metric_unit})。",
                    "priority": 0.7,
                    "action": f"分析{metric_name}低于平均水平的原因，评估是短期波动还是长期趋势变化。",
                    "relevance": 0.75
                })
            elif avg_value is not None and current_value > avg_value * 1.3:
                recommendations.append({
                    "id": "significantly_above_average",
                    "title": f"{metric_name}显著高于平均水平",
                    "description": f"{metric_name}当前值({current_value}{metric_unit})显著高于历史平均水平({avg_value:.2f}{metric_unit})。",
                    "priority": 0.65,
                    "action": f"分析{metric_name}高于平均水平的驱动因素，评估是否为季节性波动或新的增长点。",
                    "relevance": 0.7
                })
        
        return recommendations
    
    def _recommend_for_chart(self, data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为图表分析生成建议
        
        参数:
            data (Dict[str, Any]): 图表分析数据
            context (Dict[str, Any]): 上下文信息
            
        返回:
            List[Dict[str, Any]]: 建议列表
        """
        recommendations = []
        
        # 提取图表基本信息
        chart_type = data.get("chart_type", "未知类型")
        chart_title = data.get("title", "未知图表")
        
        # 图表分析结果
        chart_analysis = data.get("图表分析", {})
        
        # 针对不同类型的图表生成不同的建议
        if chart_type == "line":
            trend_info = chart_analysis.get("趋势分析", {})
            trend_type = trend_info.get("主要趋势", "")
            seasonal = trend_info.get("季节性", False)
            outliers = chart_analysis.get("异常点", [])
            
            if trend_type == "上升":
                recommendations.append({
                    "id": "line_uptrend",
                    "title": f"{chart_title}呈上升趋势",
                    "description": f"图表显示数据整体呈上升趋势，建议关注增长的可持续性。",
                    "priority": 0.7,
                    "action": "分析上升趋势的驱动因素，评估未来增长空间和可能的瓶颈。",
                    "relevance": 0.75
                })
            elif trend_type == "下降":
                recommendations.append({
                    "id": "line_downtrend",
                    "title": f"{chart_title}呈下降趋势",
                    "description": f"图表显示数据整体呈下降趋势，建议排查原因并采取措施。",
                    "priority": 0.8,
                    "action": "分析下降趋势的根本原因，制定改进计划。",
                    "relevance": 0.8
                })
            
            if seasonal:
                recommendations.append({
                    "id": "seasonal_pattern",
                    "title": f"{chart_title}存在季节性模式",
                    "description": f"图表数据显示明显的季节性波动模式，建议据此调整资源分配。",
                    "priority": 0.6,
                    "action": "根据季节性模式优化资源配置和业务计划，提前应对高峰和低谷期。",
                    "relevance": 0.7
                })
            
            if outliers and len(outliers) > 0:
                recommendations.append({
                    "id": "multiple_outliers",
                    "title": f"{chart_title}存在多个异常点",
                    "description": f"图表中检测到{len(outliers)}个异常点，可能表明存在数据问题或特殊事件。",
                    "priority": 0.75,
                    "action": "调查这些异常点对应的时间点发生了什么事件，分析是否需要针对性处理。",
                    "relevance": min(0.9, 0.6 + len(outliers) * 0.05)
                })
        
        elif chart_type == "bar":
            distribution = chart_analysis.get("分布分析", {})
            skewness = distribution.get("偏度", 0)
            top_categories = distribution.get("主要类别", [])
            
            if abs(skewness) > 1.5:
                recommendations.append({
                    "id": "skewed_distribution",
                    "title": f"{chart_title}分布严重不均",
                    "description": f"柱状图显示数据分布严重偏向{'右侧' if skewness > 0 else '左侧'}，可能存在资源分配不均问题。",
                    "priority": 0.7,
                    "action": "分析分布不均的原因，评估是否需要调整资源分配策略。",
                    "relevance": min(0.85, 0.6 + abs(skewness) / 10)
                })
            
            if top_categories and len(top_categories) <= 3 and len(top_categories) / (distribution.get("类别总数", 10) or 10) < 0.3:
                recommendations.append({
                    "id": "dominated_by_few",
                    "title": f"{chart_title}被少数类别主导",
                    "description": f"图表中少数几个类别({', '.join(top_categories)})占据了主要份额，建议关注这种集中现象。",
                    "priority": 0.65,
                    "action": "评估是否需要为次要类别提供更多支持，或者深入挖掘主要类别的成功因素。",
                    "relevance": 0.75
                })
        
        elif chart_type == "scatter":
            correlation = chart_analysis.get("相关性分析", {})
            correlation_type = correlation.get("相关性类型", "")
            correlation_strength = correlation.get("相关性强度", 0)
            clusters = chart_analysis.get("聚类分析", {}).get("聚类数", 0)
            
            if correlation_type in ["正相关", "负相关"] and abs(correlation_strength) > 0.7:
                recommendations.append({
                    "id": "strong_correlation",
                    "title": f"{chart_title}显示强{correlation_type}",
                    "description": f"散点图显示变量间存在强{correlation_type}(r={correlation_strength:.2f})，可以用于预测和决策。",
                    "priority": 0.75,
                    "action": "考虑利用这种相关性建立预测模型，或在业务决策中考虑这种关系。",
                    "relevance": min(0.9, 0.5 + abs(correlation_strength))
                })
            
            if clusters and clusters > 1:
                recommendations.append({
                    "id": "multiple_clusters",
                    "title": f"{chart_title}存在多个数据簇",
                    "description": f"散点图中识别出{clusters}个不同的数据簇，表明可能存在不同的数据分组或细分市场。",
                    "priority": 0.7,
                    "action": "深入分析每个数据簇的特征，考虑针对不同簇采取差异化策略。",
                    "relevance": min(0.85, 0.6 + clusters * 0.05)
                })
        
        elif chart_type == "pie":
            distribution = chart_analysis.get("分布分析", {})
            dominant_slice = distribution.get("最大切片", {})
            even_distribution = distribution.get("分布均匀性", 0)
            
            if dominant_slice and dominant_slice.get("比例", 0) > 0.5:
                recommendations.append({
                    "id": "dominant_slice",
                    "title": f"{chart_title}存在主导切片",
                    "description": f"饼图中{dominant_slice.get('名称', '某一类别')}占比超过50%，显示出明显的主导地位。",
                    "priority": 0.65,
                    "action": f"评估是否需要更多关注{dominant_slice.get('名称', '主导类别')}的资源分配或风险集中问题。",
                    "relevance": 0.7
                })
            
            if even_distribution < 0.3:
                recommendations.append({
                    "id": "highly_uneven_pie",
                    "title": f"{chart_title}分布极不均匀",
                    "description": "饼图显示各部分分布极不均匀，可能表明资源分配或市场份额存在显著差异。",
                    "priority": 0.6,
                    "action": "分析分布不均的原因及其对业务的影响，考虑是否需要干预。",
                    "relevance": 0.65
                })
        
        return recommendations
    
    def _recommend_for_comparison(self, data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为对比分析生成建议
        
        参数:
            data (Dict[str, Any]): 对比分析数据
            context (Dict[str, Any]): 上下文信息
            
        返回:
            List[Dict[str, Any]]: 建议列表
        """
        recommendations = []
        
        # 提取对比分析信息
        comparison = data.get("对比分析", {})
        correlation = data.get("相关性分析", {})
        
        # 趋势对比
        if "趋势对比" in comparison:
            trend_comparisons = comparison["趋势对比"]
            for i, trend_comp in enumerate(trend_comparisons):
                consistency = trend_comp.get("趋势一致性", "")
                chart1 = trend_comp.get("图表1", {})
                chart2 = trend_comp.get("图表2", {})
                
                chart1_title = chart1.get("标题", f"指标{i*2+1}")
                chart2_title = chart2.get("标题", f"指标{i*2+2}")
                
                if consistency == "高度一致":
                    recommendations.append({
                        "id": f"highly_consistent_trends_{i}",
                        "title": f"{chart1_title}与{chart2_title}趋势高度一致",
                        "description": f"这两个指标显示高度一致的趋势变化，可能存在内在关联或共同受到某些因素影响。",
                        "priority": 0.7,
                        "action": f"深入分析{chart1_title}与{chart2_title}之间的关系，评估是否可以利用这种关系优化决策。",
                        "relevance": 0.75
                    })
                elif consistency == "明显不一致":
                    recommendations.append({
                        "id": f"inconsistent_trends_{i}",
                        "title": f"{chart1_title}与{chart2_title}趋势明显不一致",
                        "description": f"这两个原本可能相关的指标显示出不一致的趋势变化，建议调查可能的原因。",
                        "priority": 0.65,
                        "action": f"分析{chart1_title}与{chart2_title}趋势差异的原因，评估是否反映了业务模式的变化。",
                        "relevance": 0.7
                    })
        
        # 相关性分析
        if correlation:
            correlation_pairs = correlation.get("相关性对", [])
            for i, corr in enumerate(correlation_pairs):
                metric1 = corr.get("指标1", f"指标{i*2+1}")
                metric2 = corr.get("指标2", f"指标{i*2+2}")
                correlation_type = corr.get("相关性类型", "")
                correlation_strength = corr.get("相关性强度", 0)
                
                if correlation_type in ["正相关", "负相关"] and abs(correlation_strength) > 0.8:
                    recommendations.append({
                        "id": f"strong_{correlation_type}_{i}",
                        "title": f"{metric1}与{metric2}存在强{correlation_type}",
                        "description": f"分析显示这两个指标之间存在强{correlation_type}(r={correlation_strength:.2f})，可以用于预测和决策。",
                        "priority": 0.8,
                        "action": f"考虑利用{metric1}和{metric2}之间的{correlation_type}关系建立预测模型或优化业务流程。",
                        "relevance": min(0.9, 0.6 + abs(correlation_strength))
                    })
                elif correlation_type == "无明显相关" and abs(correlation_strength) < 0.2:
                    expected_correlation = context.get("expected_correlations", {}).get(f"{metric1}_{metric2}")
                    if expected_correlation in ["正相关", "负相关"]:
                        recommendations.append({
                            "id": f"unexpected_no_correlation_{i}",
                            "title": f"{metric1}与{metric2}缺乏预期的相关性",
                            "description": f"这两个指标之间没有显示出预期的{expected_correlation}，可能表明业务模式发生了变化。",
                            "priority": 0.75,
                            "action": f"调查{metric1}与{metric2}之间缺乏预期相关性的原因，评估是否需要调整业务假设。",
                            "relevance": 0.8
                        })
        
        return recommendations
    
    def _recommend_generic(self, data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为通用分析数据生成建议
        
        参数:
            data (Dict[str, Any]): 分析数据
            context (Dict[str, Any]): 上下文信息
            
        返回:
            List[Dict[str, Any]]: 建议列表
        """
        # 如果无法确定具体的数据类型，返回一些通用的建议
        data_type = next(iter(data)) if data else "未知类型"
        return [{
            "id": "generic_recommendation",
            "title": "建议进行更深入的分析",
            "description": f"基于当前的{data_type}数据，建议收集更多相关信息并进行更深入的分析。",
            "priority": 0.5,
            "action": "确定关键指标并跟踪其历史变化，寻找潜在的趋势和模式。",
            "relevance": 0.6
        }]
    
    def _filter_recommendations(self, recommendations: List[Dict[str, Any]], threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        过滤建议列表，只保留相关性高于阈值的建议
        
        参数:
            recommendations (List[Dict[str, Any]]): 建议列表
            threshold (float): 相关性阈值
            
        返回:
            List[Dict[str, Any]]: 过滤后的建议列表
        """
        return [rec for rec in recommendations if rec.get("relevance", 0) >= threshold]
    
    def _load_recommendation_templates(self) -> List[Dict[str, Any]]:
        """
        加载建议模板
        
        返回:
            List[Dict[str, Any]]: 建议模板列表
        """
        # 这里只是一些基本的模板示例，实际应用中可以从配置文件或数据库加载
        return [
            {
                "id": "anomaly_detection",
                "type": "metric",
                "condition": "is_anomaly == True",
                "message": "{metric_name}出现异常，建议调查原因。",
                "action": "分析异常原因并采取相应措施",
                "priority": 1.0
            },
            {
                "id": "trend_analysis",
                "type": "metric",
                "condition": "abs(change_rate) > 0.2",
                "message": "{metric_name}变化显著({change_direction}{change_rate:.2f}%)，建议关注。",
                "action": "分析变化原因，评估是否需要调整策略",
                "priority": 0.8
            },
            {
                "id": "correlation_insight",
                "type": "comparison",
                "condition": "abs(correlation_strength) > 0.7",
                "message": "{metric1}与{metric2}存在强{correlation_type}，可用于预测和决策。",
                "action": "利用相关性建立预测模型或优化业务流程",
                "priority": 0.75
            }
        ] 