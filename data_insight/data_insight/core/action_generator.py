#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
行动建议生成器
===========

根据数据分析结果生成可行的行动建议，帮助用户做出决策。结合模板和大语言模型来提供针对性的建议。
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 加载环境变量
load_dotenv()


class ActionGenerator:
    """
    行动建议生成器
    
    基于数据分析结果，生成可行的行动建议，帮助用户根据洞察做出决策。
    结合预设模板和可选的大语言模型增强功能。
    """
    
    def __init__(self, use_llm: bool = True):
        """
        初始化行动建议生成器
        
        参数:
            use_llm (bool): 是否使用大语言模型来增强建议生成
        """
        self.use_llm = use_llm
        
        # 销售类指标上升的建议模板
        self.sales_increase_actions = [
            "继续保持当前的市场策略，关注客户反馈以确保可持续增长",
            "分析本次增长最主要的贡献因素，加大在该方面的投入",
            "提高售后服务质量，增强客户粘性和复购率",
            "扩大产品线或服务范围，挖掘潜在的交叉销售机会",
            "适当提高产品价格或减少促销力度，提升利润率",
            "开发新的分销渠道，进一步扩大市场覆盖"
        ]
        
        # 销售类指标下降的建议模板
        self.sales_decrease_actions = [
            "调研市场需求变化，优化产品或服务以更好满足客户需求",
            "分析销售漏斗各环节转化率，找出并改进关键瓶颈环节",
            "评估价格策略，考虑调整定价或推出限时促销活动",
            "加强营销推广力度，提高品牌曝光和市场认知度",
            "与客户进行深入沟通，了解流失原因并采取针对性措施",
            "检查销售团队绩效，提供必要的培训和激励机制",
            "关注竞争对手动向，制定差异化竞争策略"
        ]
        
        # 运营类指标上升的建议模板（如用户活跃度、转化率等）
        self.operation_increase_actions = [
            "分析用户行为数据，深入理解高活跃度背后的驱动因素",
            "针对高活跃用户群体，开发更多增值服务或功能",
            "优化用户路径，减少摩擦点，进一步提升转化效果",
            "开展用户调研，了解用户满意度和潜在需求",
            "引入A/B测试，持续优化关键流程和功能",
            "完善奖励机制，鼓励用户持续活跃和传播"
        ]
        
        # 运营类指标下降的建议模板
        self.operation_decrease_actions = [
            "排查产品或服务中可能存在的问题和障碍",
            "分析用户流失节点，找出关键痛点并优先改进",
            "重新评估目标用户群体，调整产品定位和营销策略",
            "加强用户沟通和反馈收集，及时响应用户需求",
            "推出用户留存计划，通过奖励或新功能吸引用户回归",
            "简化产品使用流程，降低用户使用门槛"
        ]
        
        # 成本类指标上升的建议模板
        self.cost_increase_actions = [
            "进行成本结构分析，识别主要成本增长点",
            "优化供应链管理，寻找更具成本效益的供应商或方案",
            "实施精益管理，减少浪费和冗余环节",
            "考虑自动化或技术升级，降低人力依赖和提高效率",
            "重新谈判供应合同条款，争取更有利的价格和条件",
            "建立成本监控机制，设定预警阈值及时干预"
        ]
        
        # 成本类指标下降的建议模板
        self.cost_decrease_actions = [
            "总结成本控制经验，形成标准化流程并在更广范围推广",
            "适当提高质量控制标准，确保成本降低不影响产品质量",
            "探索规模经济效应，扩大采购或生产规模以进一步降低单位成本",
            "投资新技术或设备，为长期成本控制打下基础",
            "设立成本优化激励机制，鼓励团队持续提出改进建议"
        ]
        
        # 异常值处理建议模板
        self.anomaly_actions = [
            "深入调查异常值产生的原因，区分系统性因素和偶发性因素",
            "制定异常监控机制，设置自动预警系统",
            "开展针对性的风险评估，制定应对极端情况的预案",
            "临时调整相关业务策略，降低异常波动带来的负面影响",
            "增加数据采集频率，提高异常情况的响应速度"
        ]
        
        # 季节性波动建议模板
        self.seasonality_actions = [
            "根据季节性波动规律，提前调整资源配置和库存水平",
            "开发反季节性产品或服务，平衡业务周期性波动",
            "针对不同季节特点，设计差异化的营销和促销策略",
            "利用淡季时机进行系统维护、团队培训和战略规划",
            "建立季节性预测模型，优化资源分配和财务规划"
        ]
        
        # 通用建议模板
        self.general_actions = [
            "持续监控核心指标变化，建立常态化分析机制",
            "加强跨部门协作，形成数据驱动的决策文化",
            "建立全面的指标监控体系，关注指标间的相互影响",
            "设定合理的目标值和阈值，形成规范化的管理流程",
            "投资数据分析能力建设，提升团队数据洞察水平"
        ]
        
        # 初始化LLM（仅当use_llm为True时）
        if self.use_llm:
            self.init_llm()
    
    def init_llm(self):
        """
        初始化大语言模型
        
        如果没有设置API密钥，将不使用LLM
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("警告: 未设置OPENAI_API_KEY，将不使用LLM进行建议生成")
            self.use_llm = False
            return
        
        try:
            self.llm = OpenAI(temperature=0.7)
            
            # 创建行动建议的提示模板
            action_template = """
            你是一位经验丰富的业务顾问，请根据以下数据分析结果，提出3-5条具体可行的行动建议:
            
            指标名称: {metric_name}
            当前值: {current_value} {unit}
            变化情况: {change_description}
            
            分析结果: {analysis_result}
            
            可能原因: {possible_reasons}
            
            请根据上述信息，提出具体的行动建议。建议应该:
            1. 具体且可操作，避免过于笼统
            2. 直接针对分析结果和可能原因
            3. 考虑行业特点和实际可行性
            4. 包括短期和中长期建议
            
            只输出行动建议清单，每条建议用一个段落表示，不要包含编号或其他格式。
            """
            
            self.action_prompt = PromptTemplate(
                input_variables=["metric_name", "current_value", "unit", 
                                "change_description", "analysis_result", 
                                "possible_reasons"],
                template=action_template
            )
            
            self.action_chain = LLMChain(llm=self.llm, prompt=self.action_prompt)
            
        except Exception as e:
            print(f"初始化LLM出错: {e}")
            self.use_llm = False
    
    def generate_actions(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据分析结果生成行动建议
        
        参数:
            analysis_result (Dict[str, Any]): 分析结果，包含:
                - basic_info: 指标基本信息
                - change_analysis: 变化分析结果
                - anomaly_analysis: 异常分析结果(可选)
                - trend_analysis: 趋势分析结果(可选)
                - reason_analysis: 原因分析结果(可选)
                
        返回:
            Dict[str, Any]: 包含行动建议的结果
        """
        # 提取必要信息
        if "basic_info" not in analysis_result or "change_analysis" not in analysis_result:
            raise ValueError("分析结果缺少必要信息: basic_info或change_analysis")
            
        basic_info = analysis_result.get("basic_info", {})
        change_analysis = analysis_result.get("change_analysis", {})
        anomaly_analysis = analysis_result.get("anomaly_analysis", {})
        trend_analysis = analysis_result.get("趋势分析", {})  # 注意与前面不同的键名
        reason_analysis = analysis_result.get("原因分析", {})
        
        actions = []
        
        # 1. 基于指标类型和变化添加模板建议
        template_actions = self._get_template_actions(basic_info, change_analysis)
        if template_actions:
            actions.extend(template_actions)
        
        # 2. 如果是异常值，添加异常处理建议
        if anomaly_analysis.get("是否异常", False):
            actions.extend(self._get_anomaly_actions(anomaly_analysis))
        
        # 3. 如果存在明显季节性，添加季节性建议
        if "季节性" in str(reason_analysis.get("可能原因", [])):
            actions.extend(self._get_seasonality_actions())
        
        # 4. 添加通用建议
        actions.extend(self._get_general_actions())
        
        # 5. 使用LLM生成更具针对性的建议
        if self.use_llm and "可能原因" in reason_analysis:
            llm_actions = self._generate_llm_actions(basic_info, change_analysis, reason_analysis)
            if llm_actions:
                # 用LLM生成的建议替换一部分模板建议，但保留异常处理和季节性建议
                template_count = len(template_actions)
                general_count = len(self._get_general_actions())
                if template_count > 0:
                    actions = actions[template_count:len(actions)-general_count] + llm_actions + actions[-general_count:]
                else:
                    actions = actions[:-general_count] + llm_actions + actions[-general_count:]
        
        # 去重并限制建议数量
        unique_actions = []
        for action in actions:
            # 简单去重：检查新建议是否与已有建议有显著重叠
            is_duplicate = False
            for existing in unique_actions:
                # 如果两个建议有超过50%的文本重叠，认为是重复
                if len(set(action.split()) & set(existing.split())) / len(set(action.split() + existing.split())) > 0.5:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_actions.append(action)
                
                # 限制最多8个建议
                if len(unique_actions) >= 8:
                    break
        
        # 构建结果
        result = {
            "行动建议": {
                "建议列表": unique_actions,
                "生成方法": "模板匹配" if not self.use_llm else "模板匹配+LLM增强",
                "优先级排序": self._prioritize_actions(unique_actions, basic_info, change_analysis)
            }
        }
        
        return result
    
    def _get_template_actions(self, basic_info: Dict[str, Any], 
                             change_analysis: Dict[str, Any]) -> List[str]:
        """
        基于指标类型和变化获取模板行动建议
        
        参数:
            basic_info (Dict[str, Any]): 指标基本信息
            change_analysis (Dict[str, Any]): 变化分析结果
            
        返回:
            List[str]: 行动建议列表
        """
        metric_name = basic_info["指标名称"]
        is_positive_better = basic_info.get("正向增长是否为好", True)
        change_direction = change_analysis["变化方向"]
        
        # 根据指标名称判断指标类型
        metric_type = self._determine_metric_type(metric_name)
        
        # 确定使用哪个行动建议库
        if is_positive_better:
            # 对于"值越大越好"的指标
            if change_direction == "增加":
                if metric_type == "销售":
                    return self.sales_increase_actions[:3]
                elif metric_type == "运营":
                    return self.operation_increase_actions[:3]
                else:
                    return self.sales_increase_actions[:2] + self.operation_increase_actions[:1]
            else:
                if metric_type == "销售":
                    return self.sales_decrease_actions[:3]
                elif metric_type == "运营":
                    return self.operation_decrease_actions[:3]
                else:
                    return self.sales_decrease_actions[:2] + self.operation_decrease_actions[:1]
        else:
            # 对于"值越小越好"的指标（如成本类）
            if change_direction == "增加":
                return self.cost_increase_actions[:3]
            else:
                return self.cost_decrease_actions[:3]
    
    def _determine_metric_type(self, metric_name: str) -> str:
        """
        根据指标名称判断指标类型
        
        参数:
            metric_name (str): 指标名称
            
        返回:
            str: 指标类型("销售", "运营", "成本", "其他")
        """
        sales_keywords = ["销售", "收入", "营收", "营业额", "订单", "客单价", "GMV"]
        operation_keywords = ["转化率", "活跃", "留存", "访问", "点击", "注册", "用户数", "时长", "频次"]
        cost_keywords = ["成本", "费用", "支出", "开销", "投入", "消耗"]
        
        for keyword in sales_keywords:
            if keyword in metric_name:
                return "销售"
                
        for keyword in operation_keywords:
            if keyword in metric_name:
                return "运营"
                
        for keyword in cost_keywords:
            if keyword in metric_name:
                return "成本"
        
        return "其他"
    
    def _get_anomaly_actions(self, anomaly_analysis: Dict[str, Any]) -> List[str]:
        """
        获取异常处理建议
        
        参数:
            anomaly_analysis (Dict[str, Any]): 异常分析结果
            
        返回:
            List[str]: 异常处理建议列表
        """
        # 根据异常程度选择不同数量的建议
        anomaly_degree = anomaly_analysis.get("异常程度", 0)
        
        if anomaly_degree > 3:  # 极端异常
            return self.anomaly_actions[:3]
        elif anomaly_degree > 1.5:  # 明显异常
            return self.anomaly_actions[:2]
        else:  # 轻微异常
            return self.anomaly_actions[:1]
    
    def _get_seasonality_actions(self) -> List[str]:
        """
        获取季节性波动处理建议
        
        返回:
            List[str]: 季节性处理建议列表
        """
        # 选择2个季节性建议
        return self.seasonality_actions[:2]
    
    def _get_general_actions(self) -> List[str]:
        """
        获取通用建议
        
        返回:
            List[str]: 通用建议列表
        """
        # 选择2个通用建议
        return self.general_actions[:2]
    
    def _generate_llm_actions(self, basic_info: Dict[str, Any], 
                             change_analysis: Dict[str, Any],
                             reason_analysis: Dict[str, Any]) -> List[str]:
        """
        使用大语言模型生成行动建议
        
        参数:
            basic_info (Dict[str, Any]): 指标基本信息
            change_analysis (Dict[str, Any]): 变化分析结果
            reason_analysis (Dict[str, Any]): 原因分析结果
            
        返回:
            List[str]: LLM生成的建议列表
        """
        if not self.use_llm:
            return []
        
        try:
            # 准备输入
            metric_name = basic_info["指标名称"]
            current_value = basic_info["当前值"]
            unit = basic_info.get("单位", "")
            
            # 构建变化描述
            change_rate = change_analysis.get("变化率", 0)
            change_value = change_analysis.get("变化量", 0)
            change_direction = change_analysis["变化方向"]
            change_class = change_analysis.get("变化类别", "")
            
            change_description = f"{change_direction}了{abs(change_value)}{unit}，变化率{change_rate*100:.2f}%，属于{change_class}"
            
            # 分析结果概述
            analysis_parts = []
            
            if "异常分析" in basic_info and basic_info["异常分析"].get("是否异常", False):
                anomaly = basic_info["异常分析"]
                is_higher = anomaly.get("是否高于正常范围", True)
                direction = "高于" if is_higher else "低于"
                analysis_parts.append(f"该值{direction}正常范围，异常程度为{anomaly.get('异常程度', 0)}")
            
            if "趋势分析" in basic_info:
                trend = basic_info["趋势分析"]
                analysis_parts.append(f"整体呈{trend.get('趋势类型', '未知')}趋势，趋势强度为{trend.get('趋势强度', 0)}")
            
            analysis_result = "；".join(analysis_parts) if analysis_parts else "无明显异常或特殊趋势"
            
            # 可能原因
            possible_reasons = "\n".join(reason_analysis.get("可能原因", ["原因未知"]))
            
            # 调用LLM生成建议
            response = self.action_chain.run(
                metric_name=metric_name,
                current_value=current_value,
                unit=unit,
                change_description=change_description,
                analysis_result=analysis_result,
                possible_reasons=possible_reasons
            )
            
            # 处理LLM响应
            if response:
                # 分割为单独的建议段落
                paragraphs = [p.strip() for p in response.split('\n') if p.strip()]
                return paragraphs
            
            return []
        except Exception as e:
            print(f"LLM生成行动建议出错: {e}")
            return []
    
    def _prioritize_actions(self, actions: List[str], 
                           basic_info: Dict[str, Any],
                           change_analysis: Dict[str, Any]) -> List[str]:
        """
        对行动建议进行优先级排序
        
        参数:
            actions (List[str]): 行动建议列表
            basic_info (Dict[str, Any]): 指标基本信息
            change_analysis (Dict[str, Any]): 变化分析结果
            
        返回:
            List[str]: 排序后的优先级列表("高", "中", "低")
        """
        # 简单判断优先级的逻辑
        priorities = []
        
        change_class = change_analysis.get("变化类别", "")
        is_positive_better = basic_info.get("正向增长是否为好", True)
        change_direction = change_analysis["变化方向"]
        
        # 判断变化是否需要重点关注
        need_attention = False
        if is_positive_better and change_direction == "减少":
            need_attention = True  # 正向指标下降需关注
        elif not is_positive_better and change_direction == "增加":
            need_attention = True  # 负向指标上升需关注
        
        # 变化程度
        is_significant = "大幅" in change_class
        
        # 是否异常
        is_anomaly = False
        if "anomaly_analysis" in basic_info:
            is_anomaly = basic_info["anomaly_analysis"].get("是否异常", False)
        
        # 为每个建议设置优先级
        for action in actions:
            # 异常处理的建议优先级高
            if any(key in action.lower() for key in ["异常", "监控", "预警", "风险"]) and (is_anomaly or is_significant):
                priorities.append("高")
            # 针对需要关注的变化的建议优先级较高
            elif need_attention and any(key in action.lower() for key in ["优化", "改进", "提升", "加强", "解决"]):
                priorities.append("高")
            # 长期战略性建议优先级通常较低
            elif any(key in action.lower() for key in ["长期", "战略", "规划", "体系", "机制"]):
                priorities.append("低")
            # 其他建议默认中等优先级
            else:
                priorities.append("中")
        
        return priorities 