"""
智能建议生成器
============

基于多维度分析结果生成智能建议，帮助用户从数据洞察转化为实际行动。
"""

from typing import Dict, Any, List, Optional
import numpy as np
from data_insight.core.base_analyzer import BaseAnalyzer


class SuggestionGenerator(BaseAnalyzer):
    """
    智能建议生成器
    
    基于多维度分析结果（指标分析、图表分析、归因分析、根因分析等）生成智能建议。
    """
    
    def __init__(
        self,
        min_confidence: float = 0.6,
        max_suggestions: int = 5,
        priority_threshold: float = 0.7
    ):
        """
        初始化建议生成器
        
        参数:
            min_confidence (float): 建议的最小置信度阈值
            max_suggestions (int): 每个维度最多生成的建议数量
            priority_threshold (float): 高优先级建议的阈值
        """
        super().__init__()
        self.min_confidence = min_confidence
        self.max_suggestions = max_suggestions
        self.priority_threshold = priority_threshold
        
        # 建议模板库
        self.suggestion_templates = {
            "指标提升": [
                "针对{metric}的{change_type}，建议{action}，预期可{effect}",
                "为提高{metric}，可以考虑{action}，预计能{effect}",
                "为改善{metric}的{change_type}，建议{action}，预期效果{effect}"
            ],
            "异常处理": [
                "发现{metric}出现{anomaly_type}异常，建议{action}，预期可{effect}",
                "针对{metric}的异常波动，建议{action}，预计能{effect}",
                "为应对{metric}的异常情况，建议{action}，预期效果{effect}"
            ],
            "趋势优化": [
                "针对{metric}的{trend_type}趋势，建议{action}，预期可{effect}",
                "为优化{metric}的{trend_type}趋势，建议{action}，预计能{effect}",
                "为改善{metric}的发展趋势，建议{action}，预期效果{effect}"
            ],
            "根因解决": [
                "针对{metric}的根本原因{root_cause}，建议{action}，预期可{effect}",
                "为解决{metric}的{root_cause}问题，建议{action}，预计能{effect}",
                "为消除{metric}的{root_cause}影响，建议{action}，预期效果{effect}"
            ]
        }
        
        # 行动建议库
        self.action_templates = {
            "销售提升": [
                "加强市场营销力度",
                "优化产品定价策略",
                "提升客户服务质量",
                "扩大销售渠道",
                "增加促销活动"
            ],
            "成本控制": [
                "优化供应链管理",
                "提高生产效率",
                "减少资源浪费",
                "加强成本核算",
                "实施精益管理"
            ],
            "质量改进": [
                "加强质量控制",
                "优化生产流程",
                "提升员工技能",
                "改进设备维护",
                "完善质量管理体系"
            ],
            "效率提升": [
                "优化工作流程",
                "加强团队协作",
                "提升自动化水平",
                "改进管理方式",
                "加强培训学习"
            ]
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据并生成建议
        
        参数:
            data (Dict[str, Any]): 输入数据，包含各种分析结果
                - metric_analysis: 指标分析结果
                - chart_analysis: 图表分析结果
                - attribution_analysis: 归因分析结果
                - root_cause_analysis: 根因分析结果
                - prediction_analysis: 预测分析结果
                
        返回:
            Dict[str, Any]: 生成的建议结果
        """
        # 验证输入数据
        required_fields = ["metric_analysis"]
        self.validate_input(data, required_fields)
        
        # 提取分析结果
        metric_analysis = data["metric_analysis"]
        chart_analysis = data.get("chart_analysis")
        attribution_analysis = data.get("attribution_analysis")
        root_cause_analysis = data.get("root_cause_analysis")
        prediction_analysis = data.get("prediction_analysis")
        
        # 生成各类建议
        suggestions = []
        
        # 1. 基于指标分析的建议
        metric_suggestions = self._generate_metric_suggestions(metric_analysis)
        suggestions.extend(metric_suggestions)
        
        # 2. 基于图表分析的建议
        if chart_analysis:
            chart_suggestions = self._generate_chart_suggestions(chart_analysis)
            suggestions.extend(chart_suggestions)
        
        # 3. 基于归因分析的建议
        if attribution_analysis:
            attribution_suggestions = self._generate_attribution_suggestions(attribution_analysis)
            suggestions.extend(attribution_suggestions)
        
        # 4. 基于根因分析的建议
        if root_cause_analysis:
            root_cause_suggestions = self._generate_root_cause_suggestions(root_cause_analysis)
            suggestions.extend(root_cause_suggestions)
        
        # 5. 基于预测分析的建议
        if prediction_analysis:
            prediction_suggestions = self._generate_prediction_suggestions(prediction_analysis)
            suggestions.extend(prediction_suggestions)
        
        # 对建议进行排序和筛选
        sorted_suggestions = self._sort_and_filter_suggestions(suggestions)
        
        # 计算建议的总体效果
        overall_effect = self._calculate_overall_effect(sorted_suggestions)
        
        return {
            "建议列表": sorted_suggestions,
            "总体效果": overall_effect,
            "建议数量": len(sorted_suggestions),
            "高优先级建议数": len([s for s in sorted_suggestions if s["优先级"] == "高"])
        }
    
    def _generate_metric_suggestions(self, metric_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于指标分析生成建议
        
        参数:
            metric_analysis (Dict[str, Any]): 指标分析结果
            
        返回:
            List[Dict[str, Any]]: 生成的建议列表
        """
        suggestions = []
        
        # 提取指标信息
        metric_name = metric_analysis["基本信息"]["指标名称"]
        change_analysis = metric_analysis["变化分析"]
        anomaly_analysis = metric_analysis["异常分析"]
        
        # 1. 基于变化分析的建议
        if change_analysis["变化类别"] != "基本持平":
            suggestion = self._create_suggestion(
                template_type="指标提升",
                metric=metric_name,
                change_type=change_analysis["变化类别"],
                action=self._get_relevant_action(metric_name),
                effect=self._estimate_effect(change_analysis["变化率"])
            )
            suggestions.append(suggestion)
        
        # 2. 基于异常分析的建议
        if anomaly_analysis["是否异常"]:
            suggestion = self._create_suggestion(
                template_type="异常处理",
                metric=metric_name,
                anomaly_type="显著" if anomaly_analysis["异常程度"] > 1.5 else "轻微",
                action=self._get_relevant_action(metric_name),
                effect=self._estimate_effect(-anomaly_analysis["异常程度"])
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_chart_suggestions(self, chart_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于图表分析生成建议
        
        参数:
            chart_analysis (Dict[str, Any]): 图表分析结果
            
        返回:
            List[Dict[str, Any]]: 生成的建议列表
        """
        suggestions = []
        
        # 提取图表信息
        chart_title = chart_analysis["基本信息"]["图表标题"]
        trends = chart_analysis.get("趋势分析", {})
        anomalies = chart_analysis.get("异常点分析", [])
        
        # 1. 基于趋势的建议
        if trends.get("趋势类型"):
            suggestion = self._create_suggestion(
                template_type="趋势优化",
                metric=chart_title,
                trend_type=trends["趋势类型"],
                action=self._get_relevant_action(chart_title),
                effect=self._estimate_effect(trends.get("趋势强度", 0))
            )
            suggestions.append(suggestion)
        
        # 2. 基于异常点的建议
        for anomaly in anomalies:
            suggestion = self._create_suggestion(
                template_type="异常处理",
                metric=chart_title,
                anomaly_type="显著" if anomaly["异常程度"] > 1.5 else "轻微",
                action=self._get_relevant_action(chart_title),
                effect=self._estimate_effect(-anomaly["异常程度"])
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_attribution_suggestions(self, attribution_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于归因分析生成建议
        
        参数:
            attribution_analysis (Dict[str, Any]): 归因分析结果
            
        返回:
            List[Dict[str, Any]]: 生成的建议列表
        """
        suggestions = []
        
        # 提取归因信息
        target_metric = attribution_analysis["目标指标"]
        factors = attribution_analysis["因素贡献"]
        
        # 为每个主要因素生成建议
        for factor in factors:
            if factor["贡献度"] > 0.1:  # 只考虑贡献度超过10%的因素
                suggestion = self._create_suggestion(
                    template_type="指标提升",
                    metric=target_metric,
                    change_type=f"受{factor['因素名称']}影响",
                    action=self._get_relevant_action(factor["因素名称"]),
                    effect=self._estimate_effect(factor["贡献度"])
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_root_cause_suggestions(self, root_cause_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于根因分析生成建议
        
        参数:
            root_cause_analysis (Dict[str, Any]): 根因分析结果
            
        返回:
            List[Dict[str, Any]]: 生成的建议列表
        """
        suggestions = []
        
        # 提取根因信息
        target_metric = root_cause_analysis["目标指标"]
        root_causes = root_cause_analysis["根因列表"]
        
        # 为每个根因生成建议
        for root_cause in root_causes:
            suggestion = self._create_suggestion(
                template_type="根因解决",
                metric=target_metric,
                root_cause=root_cause["根因描述"],
                action=self._get_relevant_action(root_cause["根因类型"]),
                effect=self._estimate_effect(root_cause["影响程度"])
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_prediction_suggestions(self, prediction_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于预测分析生成建议
        
        参数:
            prediction_analysis (Dict[str, Any]): 预测分析结果
            
        返回:
            List[Dict[str, Any]]: 生成的建议列表
        """
        suggestions = []
        
        # 提取预测信息
        metric_name = prediction_analysis["基本信息"]["指标名称"]
        forecast_result = prediction_analysis["预测结果"]
        anomaly_forecast = prediction_analysis["异常预测"]
        
        # 1. 基于预测趋势的建议
        if forecast_result.get("预测值"):
            trend = "上升" if forecast_result["预测值"][-1] > forecast_result["预测值"][0] else "下降"
            suggestion = self._create_suggestion(
                template_type="趋势优化",
                metric=metric_name,
                trend_type=trend,
                action=self._get_relevant_action(metric_name),
                effect=self._estimate_effect(abs(forecast_result["预测值"][-1] - forecast_result["预测值"][0]))
            )
            suggestions.append(suggestion)
        
        # 2. 基于异常预测的建议
        if anomaly_forecast["风险等级"] != "低":
            suggestion = self._create_suggestion(
                template_type="异常处理",
                metric=metric_name,
                anomaly_type=f"{anomaly_forecast['风险等级']}风险",
                action=self._get_relevant_action(metric_name),
                effect=self._estimate_effect(-1.0 if anomaly_forecast["风险等级"] == "高" else -0.5)
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _create_suggestion(
        self,
        template_type: str,
        metric: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建建议
        
        参数:
            template_type (str): 建议模板类型
            metric (str): 指标名称
            **kwargs: 其他参数
            
        返回:
            Dict[str, Any]: 生成的建议
        """
        # 选择模板
        template = np.random.choice(self.suggestion_templates[template_type])
        
        # 生成建议文本
        suggestion_text = template.format(metric=metric, **kwargs)
        
        # 计算优先级
        priority = self._calculate_priority(kwargs.get("effect", 0))
        
        # 计算置信度
        confidence = self._calculate_confidence(kwargs)
        
        return {
            "建议内容": suggestion_text,
            "优先级": priority,
            "置信度": confidence,
            "预期效果": kwargs.get("effect", 0),
            "建议类型": template_type
        }
    
    def _get_relevant_action(self, metric_name: str) -> str:
        """
        获取相关的行动建议
        
        参数:
            metric_name (str): 指标名称
            
        返回:
            str: 行动建议
        """
        # 根据指标名称选择相关的行动建议
        if any(keyword in metric_name for keyword in ["销售", "收入", "营业额"]):
            return np.random.choice(self.action_templates["销售提升"])
        elif any(keyword in metric_name for keyword in ["成本", "费用", "支出"]):
            return np.random.choice(self.action_templates["成本控制"])
        elif any(keyword in metric_name for keyword in ["质量", "合格率", "良品率"]):
            return np.random.choice(self.action_templates["质量改进"])
        else:
            return np.random.choice(self.action_templates["效率提升"])
    
    def _estimate_effect(self, change_rate: float) -> float:
        """
        估算建议的预期效果
        
        参数:
            change_rate (float): 变化率
            
        返回:
            float: 预期效果（0-1之间）
        """
        # 基于变化率估算效果
        if abs(change_rate) > 0.5:
            return 0.8
        elif abs(change_rate) > 0.2:
            return 0.6
        else:
            return 0.4
    
    def _calculate_priority(self, effect: float) -> str:
        """
        计算建议优先级
        
        参数:
            effect (float): 预期效果
            
        返回:
            str: 优先级（高/中/低）
        """
        if effect >= self.priority_threshold:
            return "高"
        elif effect >= self.priority_threshold * 0.7:
            return "中"
        else:
            return "低"
    
    def _calculate_confidence(self, kwargs: Dict[str, Any]) -> float:
        """
        计算建议置信度
        
        参数:
            kwargs (Dict[str, Any]): 建议参数
            
        返回:
            float: 置信度（0-1之间）
        """
        # 基于多个因素计算置信度
        effect = kwargs.get("effect", 0)
        anomaly_type = kwargs.get("anomaly_type", "")
        risk_level = kwargs.get("risk_level", "")
        
        confidence = 0.5  # 基础置信度
        
        # 根据效果调整置信度
        confidence += effect * 0.3
        
        # 根据异常类型调整置信度
        if "显著" in anomaly_type or "高" in risk_level:
            confidence += 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _sort_and_filter_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对建议进行排序和筛选
        
        参数:
            suggestions (List[Dict[str, Any]]): 原始建议列表
            
        返回:
            List[Dict[str, Any]]: 排序和筛选后的建议列表
        """
        # 按优先级和置信度排序
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: (x["优先级"] == "高", x["置信度"], x["预期效果"]),
            reverse=True
        )
        
        # 筛选置信度高于阈值且数量不超过限制的建议
        filtered_suggestions = [
            s for s in sorted_suggestions
            if s["置信度"] >= self.min_confidence
        ][:self.max_suggestions]
        
        return filtered_suggestions
    
    def _calculate_overall_effect(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算建议的总体效果
        
        参数:
            suggestions (List[Dict[str, Any]]): 建议列表
            
        返回:
            Dict[str, Any]: 总体效果评估
        """
        if not suggestions:
            return {
                "总体效果": 0.0,
                "效果评估": "无有效建议",
                "建议数量": 0
            }
        
        # 计算加权平均效果
        total_effect = sum(s["预期效果"] * s["置信度"] for s in suggestions)
        total_confidence = sum(s["置信度"] for s in suggestions)
        average_effect = total_effect / total_confidence if total_confidence > 0 else 0
        
        # 评估总体效果
        if average_effect >= 0.7:
            effect_evaluation = "显著改善"
        elif average_effect >= 0.4:
            effect_evaluation = "有所改善"
        else:
            effect_evaluation = "轻微改善"
        
        return {
            "总体效果": average_effect,
            "效果评估": effect_evaluation,
            "建议数量": len(suggestions)
        } 