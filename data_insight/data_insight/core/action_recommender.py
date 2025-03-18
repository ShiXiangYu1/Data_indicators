#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
行动建议生成器
============

根据指标分析结果和原因分析结果，生成具体可行的行动建议。
"""

import os
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from data_insight.core.base_analyzer import BaseAnalyzer


class ActionRecommender(BaseAnalyzer):
    """
    行动建议生成器类
    
    根据指标分析和原因分析结果，生成针对性的行动建议。支持基于规则的推荐和大语言模型增强的推荐。
    """
    
    def __init__(self, use_llm: bool = True):
        """
        初始化行动建议生成器
        
        参数:
            use_llm (bool): 是否使用大语言模型增强推荐，默认为True
        """
        super().__init__()
        self.use_llm = use_llm
        
        # 预定义的行动建议模板 (按指标类别和变化方向分类)
        self.action_templates = {
            # 销售相关指标，积极变化
            "销售_积极": [
                "继续保持当前的营销策略，确保销售增长的可持续性。",
                "分析最畅销的产品类别，适当增加库存以满足需求。",
                "调研销售增长的具体来源渠道，考虑增加对高效渠道的投入。",
                "对销售团队进行表彰和激励，保持团队积极性。",
                "考虑适度扩大产品线，把握市场机会。"
            ],
            # 销售相关指标，消极变化
            "销售_消极": [
                "分析销售下滑的具体产品类别和客户群体，找出重点问题区域。",
                "审查当前营销策略，考虑调整推广渠道和方式。",
                "评估竞争对手的活动，制定差异化竞争策略。",
                "考虑推出促销活动，刺激短期销售增长。",
                "深入了解客户需求变化，调整产品或服务以更好地满足市场。"
            ],
            # 用户相关指标，积极变化
            "用户_积极": [
                "分析用户增长的来源渠道，加大对高效渠道的投入。",
                "研究新增用户的行为特征，优化用户引导流程。",
                "加强用户留存措施，确保新增用户能够转化为活跃用户。",
                "考虑推出会员福利计划，增强用户忠诚度。",
                "收集用户反馈，持续改进产品或服务体验。"
            ],
            # 用户相关指标，消极变化
            "用户_消极": [
                "进行用户流失原因调研，找出关键痛点。",
                "优化产品或服务的核心功能，提升用户体验。",
                "审查用户获取成本，调整获客策略。",
                "重新设计用户引导流程，降低使用门槛。",
                "考虑推出用户回流活动，吸引流失用户回归。"
            ],
            # 成本相关指标，积极变化
            "成本_积极": [
                "继续优化成本管理流程，保持良好的成本控制。",
                "分析各成本项目降低的原因，在其他领域推广成功经验。",
                "考虑将节省的成本部分用于产品创新或营销投入。",
                "与供应商协商更有利的长期合作条件。",
                "投资自动化技术，进一步降低运营成本。"
            ],
            # 成本相关指标，消极变化
            "成本_消极": [
                "详细审查各成本项目，找出成本上升的主要因素。",
                "与供应商重新谈判，寻求更优惠的条件。",
                "评估替代材料或服务提供商，降低采购成本。",
                "优化内部流程，减少浪费和冗余。",
                "考虑技术升级或流程自动化，降低长期运营成本。"
            ],
            # 效率相关指标，积极变化
            "效率_积极": [
                "分析效率提升的具体环节，推广成功经验。",
                "对表现优异的团队或个人给予表彰和激励。",
                "持续优化工作流程，消除潜在瓶颈。",
                "投资培训项目，进一步提升团队能力。",
                "考虑适度扩大规模，充分利用效率提升带来的优势。"
            ],
            # 效率相关指标，消极变化
            "效率_消极": [
                "详细梳理工作流程，找出效率降低的环节。",
                "评估当前工具和技术是否满足需求，考虑升级。",
                "进行团队技能评估，提供针对性培训。",
                "审查资源分配是否合理，调整以优化效率。",
                "建立明确的绩效指标，激励效率提升。"
            ],
            # 质量相关指标，积极变化
            "质量_积极": [
                "总结质量提升的经验，形成标准化流程。",
                "对质量管理团队给予表彰和激励。",
                "考虑申请行业质量认证，提升品牌形象。",
                "将质量优势融入营销内容，强化品牌差异化。",
                "进一步投资质量控制体系，确保长期稳定。"
            ],
            # 质量相关指标，消极变化
            "质量_消极": [
                "成立专项团队，深入分析质量问题的根本原因。",
                "审查质量控制流程，找出漏洞并修复。",
                "加强员工质量意识培训，建立质量文化。",
                "考虑引入更严格的质检标准和流程。",
                "评估是否需要更换供应商或原材料，以提高质量。"
            ],
            # 通用建议（适用于大多数指标）
            "通用_积极": [
                "持续监控指标变化，确保积极趋势能够持续。",
                "设立更高的目标，推动进一步改进。",
                "分析成功因素，形成可复制的最佳实践。",
                "将成功经验分享到其他业务领域。",
                "考虑适当调整资源分配，支持高效领域的进一步发展。"
            ],
            "通用_消极": [
                "成立跨部门工作组，全面分析问题并制定改进计划。",
                "设定明确的短期改进目标，并定期跟踪进展。",
                "征求一线员工和客户的反馈，获取实用改进建议。",
                "评估是否有外部因素影响，制定应对策略。",
                "考虑咨询专业顾问或引入行业最佳实践。"
            ],
            # 异常情况的建议
            "异常_积极": [
                "详细分析异常增长的原因，评估是否可持续。",
                "制定应急预案，防范可能的回落风险。",
                "暂时增加资源投入，把握异常增长带来的机会。",
                "调研市场环境变化，了解异常增长的外部因素。",
                "保持谨慎乐观，做好应对波动的准备。"
            ],
            "异常_消极": [
                "立即组织专项小组，分析异常下滑的具体原因。",
                "制定短期干预措施，遏制进一步恶化。",
                "加强数据监控频次，实时跟踪指标变化。",
                "评估是否需要启动危机公关，管理外部影响。",
                "重新评估年度目标，考虑调整计划以应对变化。"
            ]
        }
        
        # 初始化大语言模型(如果需要)
        self.llm = None
        if self.use_llm:
            self.init_llm()
    
    def init_llm(self):
        """
        初始化大语言模型
        
        如果设置了使用LLM，则初始化相应的模型接口
        """
        try:
            from langchain.llms import OpenAI
            from langchain.prompts import PromptTemplate
            
            # 检查环境变量中是否有API密钥
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("警告: 未找到OpenAI API密钥，无法使用LLM增强功能。将使用基于规则的推荐。")
                self.use_llm = False
                return
            
            # 初始化LLM
            self.llm = OpenAI(temperature=0.3)
            print("已成功初始化LLM模型接口。")
            
        except (ImportError, Exception) as e:
            print(f"初始化LLM失败: {e}")
            print("将使用基于规则的推荐。")
            self.use_llm = False
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据并生成行动建议
        
        参数:
            data (Dict[str, Any]): 输入数据，应包含指标分析结果和原因分析结果
            
        返回:
            Dict[str, Any]: 包含建议行动的结果字典
        """
        # 验证输入数据
        required_fields = ["基本信息", "变化分析"]
        self.validate_input(data, required_fields)
        
        # 提取基本信息
        basic_info = data["基本信息"]
        change_analysis = data["变化分析"]
        metric_name = basic_info["指标名称"]
        
        # 提取原因分析结果(如果有)
        reasons = []
        if "原因分析" in data and "可能原因" in data["原因分析"]:
            reasons = data["原因分析"]["可能原因"]
        
        # 判断指标类别和变化方向
        indicator_category = self._determine_indicator_category(metric_name)
        change_direction = self._determine_change_direction(
            change_analysis["变化方向"], 
            basic_info.get("正向增长是否为好", True)
        )
        
        # 是否存在异常
        has_anomaly = False
        if "异常分析" in data and data["异常分析"].get("是否异常", False):
            has_anomaly = True
        
        # 生成行动建议
        actions = []
        
        # 首先基于规则生成
        rule_based_actions = self._generate_rule_based_actions(
            indicator_category, 
            change_direction, 
            has_anomaly
        )
        actions.extend(rule_based_actions)
        
        # 根据原因生成针对性建议
        if reasons:
            reason_based_actions = self._generate_reason_based_actions(
                reasons, 
                indicator_category, 
                change_direction
            )
            actions.extend(reason_based_actions)
        
        # 如果启用了LLM，使用LLM生成更个性化的建议
        if self.use_llm and self.llm:
            llm_actions = self._generate_llm_actions(data, reasons)
            actions.extend(llm_actions)
        
        # 去重并限制建议数量
        actions = self._deduplicate_actions(actions)
        actions = self._prioritize_actions(actions, data)
        
        # 组装结果
        result = {
            "行动建议": {
                "建议列表": actions,
                "优先级": self._assign_priorities(actions),
                "建议数量": len(actions),
                "针对指标": metric_name,
                "基于原因分析": len(reasons) > 0
            }
        }
        
        return result
    
    def _determine_indicator_category(self, metric_name: str) -> str:
        """
        确定指标所属的类别
        
        参数:
            metric_name (str): 指标名称
            
        返回:
            str: 指标类别
        """
        # 销售相关指标
        if any(keyword in metric_name for keyword in ["销售", "营业", "收入", "营收", "GMV", "交易", "成交"]):
            return "销售"
        
        # 用户相关指标
        if any(keyword in metric_name for keyword in ["用户", "客户", "会员", "注册", "活跃", "留存", "转化"]):
            return "用户"
        
        # 成本相关指标
        if any(keyword in metric_name for keyword in ["成本", "费用", "支出", "花费", "投入", "消耗"]):
            return "成本"
        
        # 效率相关指标
        if any(keyword in metric_name for keyword in ["效率", "生产力", "周转", "速度", "时长", "耗时"]):
            return "效率"
        
        # 质量相关指标
        if any(keyword in metric_name for keyword in ["质量", "满意度", "评分", "好评", "差评", "投诉", "退款", "退货"]):
            return "质量"
        
        # 默认为通用类别
        return "通用"
    
    def _determine_change_direction(self, change_direction: str, is_positive_better: bool) -> str:
        """
        确定变化的评价方向
        
        参数:
            change_direction (str): 变化方向，如"增加"、"减少"
            is_positive_better (bool): 正向增长是否为好
            
        返回:
            str: "积极"或"消极"
        """
        # 如果变化方向是增加，且增长是好的，则为积极
        if change_direction == "增加" and is_positive_better:
            return "积极"
        
        # 如果变化方向是减少，且增长是好的，则为消极
        if change_direction == "减少" and is_positive_better:
            return "消极"
        
        # 如果变化方向是增加，且增长是坏的，则为消极
        if change_direction == "增加" and not is_positive_better:
            return "消极"
        
        # 如果变化方向是减少，且增长是坏的，则为积极
        if change_direction == "减少" and not is_positive_better:
            return "积极"
        
        # 如果保持不变，返回中性(使用积极模板但可能调整内容)
        return "积极"
    
    def _generate_rule_based_actions(self, category: str, direction: str, has_anomaly: bool) -> List[str]:
        """
        基于规则生成行动建议
        
        参数:
            category (str): 指标类别
            direction (str): 变化方向评价
            has_anomaly (bool): 是否存在异常
            
        返回:
            List[str]: 行动建议列表
        """
        actions = []
        
        # 确定模板键
        template_key = f"{category}_{direction}"
        
        # 如果是异常情况，添加异常建议
        if has_anomaly:
            anomaly_key = f"异常_{direction}"
            if anomaly_key in self.action_templates:
                # 从异常模板中随机选择1-2条
                anomaly_actions = random.sample(
                    self.action_templates[anomaly_key],
                    min(2, len(self.action_templates[anomaly_key]))
                )
                actions.extend(anomaly_actions)
        
        # 从对应类别的模板中选择建议
        if template_key in self.action_templates:
            # 随机选择2-3条建议
            category_actions = random.sample(
                self.action_templates[template_key],
                min(3, len(self.action_templates[template_key]))
            )
            actions.extend(category_actions)
        
        # 如果没有特定类别的模板，使用通用模板
        if not actions or len(actions) < 3:
            generic_key = f"通用_{direction}"
            if generic_key in self.action_templates:
                # 补充到至少3条建议
                needed = max(0, 3 - len(actions))
                if needed > 0:
                    generic_actions = random.sample(
                        self.action_templates[generic_key],
                        min(needed, len(self.action_templates[generic_key]))
                    )
                    actions.extend(generic_actions)
        
        return actions
    
    def _generate_reason_based_actions(self, reasons: List[str], category: str, direction: str) -> List[str]:
        """
        基于原因分析生成针对性的行动建议
        
        参数:
            reasons (List[str]): 可能原因列表
            category (str): 指标类别
            direction (str): 变化方向评价
            
        返回:
            List[str]: 行动建议列表
        """
        actions = []
        
        # 匹配常见原因模式并生成对应建议
        for reason in reasons:
            # 营销相关原因
            if any(term in reason for term in ["营销", "推广", "广告", "宣传"]):
                if direction == "积极":
                    actions.append("分析成功的营销活动要素，优化未来的营销策略。")
                else:
                    actions.append("审查当前营销策略效果，考虑调整推广渠道和内容。")
            
            # 价格相关原因
            if any(term in reason for term in ["价格", "定价", "促销", "折扣"]):
                if direction == "积极":
                    actions.append("评估当前定价策略的竞争优势，考虑如何保持价格竞争力。")
                else:
                    actions.append("进行市场价格调研，重新评估产品或服务的定价策略。")
            
            # 竞争相关原因
            if any(term in reason for term in ["竞争", "对手", "市场份额"]):
                if direction == "积极":
                    actions.append("持续监控竞争对手动态，保持市场领先优势。")
                else:
                    actions.append("深入分析竞争对手策略，制定差异化竞争方案。")
            
            # 产品相关原因
            if any(term in reason for term in ["产品", "服务", "功能", "特性", "质量"]):
                if direction == "积极":
                    actions.append("持续收集用户反馈，进一步提升产品或服务体验。")
                else:
                    actions.append("组织用户研究，找出产品或服务的关键改进点。")
            
            # 季节性相关原因
            if any(term in reason for term in ["季节", "节假日", "周期", "淡季", "旺季"]):
                if direction == "积极":
                    actions.append("制定季节性营销计划，最大化旺季收益。")
                else:
                    actions.append("开发淡季促销策略，平衡全年业务表现。")
            
            # 运营相关原因
            if any(term in reason for term in ["运营", "流程", "效率", "管理"]):
                if direction == "积极":
                    actions.append("梳理高效运营环节，形成标准化最佳实践。")
                else:
                    actions.append("审查运营流程中的瓶颈，优化内部工作流程。")
        
        return actions
    
    def _generate_llm_actions(self, data: Dict[str, Any], reasons: List[str]) -> List[str]:
        """
        使用大语言模型生成更个性化的行动建议
        
        参数:
            data (Dict[str, Any]): 完整的分析数据
            reasons (List[str]): 可能原因列表
            
        返回:
            List[str]: 行动建议列表
        """
        if not self.llm:
            return []
        
        try:
            # 提取关键信息
            basic_info = data["基本信息"]
            change_analysis = data["变化分析"]
            
            # 构建提示模板
            prompt_template = """
            作为一名数据分析和商业顾问，请为以下指标变化提供3-5条具体的行动建议。
            
            指标信息：
            - 指标名称：{metric_name}
            - 当前值：{current_value}{unit}
            - 上一期值：{previous_value}{unit}
            - 变化量：{change_value}{unit}
            - 变化率：{change_rate}
            - 变化方向：{change_direction}
            
            可能原因：
            {reasons_text}
            
            请提供具体、可执行的行动建议，每条建议应清晰明确，可直接付诸实施。
            将建议按优先级排序，并确保建议紧密结合指标性质和变化原因。
            避免泛泛而谈，直接以建议语句开头，不要编号和额外标记。
            """
            
            # 填充提示内容
            reasons_text = "\n".join([f"- {reason}" for reason in reasons]) if reasons else "- 没有提供可能原因"
            
            prompt_input = {
                "metric_name": basic_info["指标名称"],
                "current_value": basic_info["当前值"],
                "previous_value": basic_info["上一期值"],
                "unit": basic_info.get("单位", ""),
                "change_value": change_analysis["变化量"],
                "change_rate": f"{change_analysis['变化率']*100:.2f}%" if "变化率" in change_analysis else "未知",
                "change_direction": change_analysis["变化方向"],
                "reasons_text": reasons_text
            }
            
            # 构建完整提示
            from langchain.prompts import PromptTemplate
            prompt = PromptTemplate(
                input_variables=list(prompt_input.keys()),
                template=prompt_template
            )
            full_prompt = prompt.format(**prompt_input)
            
            # 调用LLM生成建议
            response = self.llm(full_prompt)
            
            # 处理响应，提取建议
            actions = []
            for line in response.split("\n"):
                line = line.strip()
                if line and not line.startswith("-") and len(line) > 10:
                    # 去除可能的序号
                    if line[0].isdigit() and line[1] in ['.', ')', '、']:
                        line = line[2:].strip()
                    actions.append(line)
            
            # 限制返回3-5条建议
            return actions[:5]
            
        except Exception as e:
            print(f"使用LLM生成建议时出错: {e}")
            return []
    
    def _deduplicate_actions(self, actions: List[str]) -> List[str]:
        """
        去除重复或高度相似的行动建议
        
        参数:
            actions (List[str]): 原始建议列表
            
        返回:
            List[str]: 去重后的建议列表
        """
        if not actions:
            return []
        
        # 使用集合去除完全相同的项
        unique_actions = list(set(actions))
        
        # 去除高度相似的项(简单实现，生产环境可用更复杂的文本相似度算法)
        result = []
        for action in unique_actions:
            # 检查是否与已添加的建议高度相似
            is_similar = False
            for added_action in result:
                # 简单文本相似度检查
                if (len(set(action.split()) & set(added_action.split())) / 
                    len(set(action.split()) | set(added_action.split()))) > 0.7:
                    is_similar = True
                    break
            
            if not is_similar:
                result.append(action)
        
        return result
    
    def _prioritize_actions(self, actions: List[str], data: Dict[str, Any]) -> List[str]:
        """
        对行动建议进行优先级排序，限制数量
        
        参数:
            actions (List[str]): 行动建议列表
            data (Dict[str, Any]): 分析数据
            
        返回:
            List[str]: 排序后的行动建议列表(最多5条)
        """
        # 实际项目中可以基于更复杂的逻辑进行排序
        # 简单实现：保留最多5条，确保没有过多重复
        return actions[:5]
    
    def _assign_priorities(self, actions: List[str]) -> List[str]:
        """
        为行动建议分配优先级标签
        
        参数:
            actions (List[str]): 行动建议列表
            
        返回:
            List[str]: 优先级标签列表
        """
        # 根据建议数量分配优先级
        priorities = []
        for i, _ in enumerate(actions):
            if i == 0:
                priorities.append("高")
            elif i < 2:
                priorities.append("中高")
            elif i < 4:
                priorities.append("中")
            else:
                priorities.append("低")
        
        return priorities 