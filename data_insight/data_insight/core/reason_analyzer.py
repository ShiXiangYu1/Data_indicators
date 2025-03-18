#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能原因分析器
===========

分析指标变化的可能原因，支持基于模板和大语言模型的混合分析。
"""

import re
import random
import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.utils.data_utils import detect_seasonal_pattern


class ReasonAnalyzer(BaseAnalyzer):
    """
    智能原因分析器
    
    分析指标变化的可能原因，结合历史数据、相关指标和异常检测结果，
    提供对指标变化背后可能原因的解释。
    
    支持基于模板的分析和大语言模型的智能分析。
    """
    
    def __init__(self, use_llm: bool = True):
        """
        初始化智能原因分析器
        
        参数:
            use_llm (bool): 是否使用大语言模型进行增强分析，默认为True
        """
        super().__init__()
        self.use_llm = use_llm
        
        # 初始化原因模板库
        # 正向指标上升的可能原因
        self.positive_change_reasons = {
            "销售额": [
                "市场营销活动取得了良好效果，吸引了更多客户",
                "新产品上市带动了整体销售增长",
                "销售团队绩效提升，成交率上升",
                "季节性需求增加，带动销售上升",
                "市场份额扩大，获得了竞争对手的客户"
            ],
            "利润": [
                "产品价格提升，保持了健康的利润率",
                "成本控制措施有效，降低了单位成本",
                "产品结构优化，高利润产品销售比例提升",
                "规模效应开始显现，摊薄了固定成本",
                "供应链优化，减少了中间环节成本"
            ],
            "用户数": [
                "营销渠道拓展，触达了更广泛的潜在用户",
                "产品体验改善，提高了转化率",
                "口碑传播效应增强，带来更多自然增长",
                "竞争策略调整，吸引了竞争对手用户",
                "促销活动效果显著，新用户获取成本降低"
            ],
            "default": [
                "市场环境变化带来的积极影响",
                "内部运营效率提升带来的正面结果",
                "策略调整产生的预期效果",
                "行业整体向好趋势的反映",
                "前期投入开始产生回报"
            ]
        }
        
        # 正向指标下降的可能原因
        self.negative_change_reasons = {
            "销售额": [
                "市场竞争加剧，面临价格压力",
                "营销策略效果不佳，客户获取受阻",
                "产品生命周期进入衰退期",
                "渠道管理问题影响了产品分销",
                "消费者需求变化，产品吸引力下降"
            ],
            "利润": [
                "原材料成本上升，压缩了利润空间",
                "市场竞争迫使降价，影响了利润率",
                "运营成本增加，未能有效控制费用",
                "产品结构变化，低利润产品占比上升",
                "销售额下降，固定成本摊销比例增加"
            ],
            "用户数": [
                "产品体验问题导致用户流失",
                "竞争对手推出更具吸引力的产品",
                "市场饱和，增长空间受限",
                "营销投入减少，新用户获取减缓",
                "用户需求变化，产品不再满足需求"
            ],
            "default": [
                "外部市场环境变化的负面影响",
                "内部运营管理面临的挑战",
                "行业竞争加剧带来的压力",
                "策略执行过程中的问题",
                "资源配置未能优化的结果"
            ]
        }
        
        # 成本类指标（负向指标）增加的原因
        self.cost_increase_reasons = [
            "原材料或服务采购价格上涨",
            "人力成本增加，可能是薪资上涨或人员扩充",
            "运营规模扩大带来的总成本增加",
            "新项目或业务线的启动投入",
            "通货膨胀因素导致的整体成本上升",
            "供应链中断或效率下降导致的额外支出",
            "合规或质量标准提升带来的成本增加"
        ]
        
        # 成本类指标（负向指标）减少的原因
        self.cost_decrease_reasons = [
            "成本控制措施有效实施",
            "供应链优化或采购策略调整",
            "自动化或流程改进带来的效率提升",
            "规模效应开始显现，单位成本下降",
            "资源利用效率提高",
            "组织结构优化，减少了冗余环节",
            "技术升级带来的生产效率提升"
        ]
        
        # 初始化LLM（如果需要）
        if self.use_llm:
            try:
                self.init_llm()
            except Exception as e:
                logging.warning(f"LLM初始化失败: {str(e)}，将回退到模板匹配模式")
                self.use_llm = False
    
    def init_llm(self):
        """
        初始化大语言模型
        
        如果环境变量中设置了相应的API密钥，则初始化LLM客户端
        """
        # 此处根据实际使用的LLM API进行初始化
        # 例如，如果使用OpenAI API:
        # from langchain.llms import OpenAI
        # self.llm = OpenAI(temperature=0.7)
        
        # 或者如果使用本地模型，可以使用其他方式初始化
        # 此处只是一个占位示例
        if "OPENAI_API_KEY" in os.environ:
            # 导入前检查环境依赖是否安装
            try:
                from langchain.llms import OpenAI
                self.llm = OpenAI(temperature=0.7)
                self.llm_type = "openai"
            except ImportError:
                logging.warning("缺少langchain或openai依赖，无法使用OpenAI LLM")
                self.use_llm = False
        else:
            logging.info("未配置LLM API密钥，将使用模板匹配模式")
            self.use_llm = False
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标变化的可能原因
        
        参数:
            data (Dict[str, Any]): 待分析的数据，应包含以下字段:
                - 基本信息: 包含指标名称、当前值、上一期值等
                - 变化分析: 包含变化量、变化率、变化类别等
                - 异常分析: 包含是否异常、异常程度等
                - 历史数据(可选): 包含历史值列表
                - 相关指标(可选): 包含与主指标相关的其他指标
            
        返回:
            Dict[str, Any]: 包含原因分析结果的字典
        """
        # 验证输入数据
        required_fields = ["基本信息", "变化分析", "异常分析"]
        self.validate_input(data, required_fields)
        
        # 检查基本信息必需字段
        basic_info_fields = ["指标名称", "当前值", "上一期值"]
        for field in basic_info_fields:
            if field not in data["基本信息"]:
                raise ValueError(f"基本信息缺少必需字段: {field}")
        
        # 检查变化分析必需字段
        change_fields = ["变化量", "变化率", "变化方向"]
        for field in change_fields:
            if field not in data["变化分析"]:
                raise ValueError(f"变化分析缺少必需字段: {field}")
        
        # 提取数据
        basic_info = data["基本信息"]
        change_analysis = data["变化分析"]
        anomaly_analysis = data["异常分析"]
        historical_data = data.get("历史数据", {})
        related_metrics = data.get("相关指标", [])
        
        # 收集可能的原因
        possible_reasons = []
        analysis_methods = []
        
        # 1. 基于模板获取可能原因
        template_reasons = self._get_template_reasons(basic_info, change_analysis)
        if template_reasons:
            possible_reasons.extend(template_reasons)
            analysis_methods.append("模板匹配")
        
        # 2. 季节性分析（如果有历史数据）
        seasonality_reason = None
        if historical_data and "values" in historical_data and len(historical_data["values"]) >= 8:
            seasonality_reason = self._analyze_seasonality(basic_info, historical_data)
            if seasonality_reason:
                possible_reasons.append(seasonality_reason)
                analysis_methods.append("季节性分析")
        
        # 3. 异常分析
        anomaly_reason = None
        if anomaly_analysis and anomaly_analysis.get("是否异常", False):
            anomaly_reason = self._analyze_anomaly_reason(basic_info, anomaly_analysis)
            if anomaly_reason:
                possible_reasons.append(anomaly_reason)
                analysis_methods.append("异常检测")
        
        # 4. 相关指标分析
        relation_reasons = []
        if related_metrics:
            relation_reasons = self._analyze_metric_relations(basic_info, change_analysis, related_metrics)
            if relation_reasons:
                possible_reasons.extend(relation_reasons)
                analysis_methods.append("相关性分析")
        
        # 5. 使用LLM增强分析（如果启用）
        if self.use_llm:
            llm_reasons = self._generate_llm_reasons(
                basic_info, change_analysis, historical_data, related_metrics
            )
            if llm_reasons:
                possible_reasons.extend(llm_reasons)
                analysis_methods.append("LLM智能分析")
        
        # 去重并限制原因数量
        possible_reasons = list(dict.fromkeys(possible_reasons))  # 去重但保持顺序
        possible_reasons = possible_reasons[:5]  # 最多返回5个原因
        
        # 计算置信度
        confidence = self._calculate_confidence(possible_reasons, basic_info, change_analysis)
        
        # 整合分析结果
        result = {
            "原因分析": {
                "可能原因": possible_reasons,
                "分析方法": "、".join(analysis_methods),
                "置信度": confidence
            }
        }
        
        return result
    
    def _get_template_reasons(self, basic_info: Dict[str, Any], change_analysis: Dict[str, Any]) -> List[str]:
        """
        基于模板获取可能的原因
        
        参数:
            basic_info (Dict[str, Any]): 基本信息
            change_analysis (Dict[str, Any]): 变化分析
            
        返回:
            List[str]: 可能的原因列表
        """
        metric_name = basic_info["指标名称"]
        change_direction = change_analysis["变化方向"]
        is_positive_better = basic_info.get("正向增长是否为好", True)
        
        reasons = []
        
        # 根据指标类型、变化方向和正负向选择合适的原因模板
        if "成本" in metric_name or "费用" in metric_name or not is_positive_better:
            # 成本类指标（负向指标）
            if change_direction == "增加":
                # 从成本增加原因中随机选择2-3个
                reasons = random.sample(self.cost_increase_reasons, 
                                          min(3, len(self.cost_increase_reasons)))
            else:
                # 从成本减少原因中随机选择2-3个
                reasons = random.sample(self.cost_decrease_reasons, 
                                          min(3, len(self.cost_decrease_reasons)))
        else:
            # 正向指标
            if change_direction == "增加":
                # 从对应指标类型或默认的正向变化原因中选择
                reason_pool = None
                for key in self.positive_change_reasons:
                    if key in metric_name:
                        reason_pool = self.positive_change_reasons[key]
                        break
                
                if not reason_pool:
                    reason_pool = self.positive_change_reasons["default"]
                
                # 随机选择2-3个原因
                reasons = random.sample(reason_pool, min(3, len(reason_pool)))
            else:
                # 从对应指标类型或默认的负向变化原因中选择
                reason_pool = None
                for key in self.negative_change_reasons:
                    if key in metric_name:
                        reason_pool = self.negative_change_reasons[key]
                        break
                
                if not reason_pool:
                    reason_pool = self.negative_change_reasons["default"]
                
                # 随机选择2-3个原因
                reasons = random.sample(reason_pool, min(3, len(reason_pool)))
        
        return reasons
    
    def _analyze_seasonality(self, basic_info: Dict[str, Any], historical_data: Dict[str, Any]) -> Optional[str]:
        """
        分析季节性因素
        
        参数:
            basic_info (Dict[str, Any]): 基本信息
            historical_data (Dict[str, Any]): 历史数据
            
        返回:
            Optional[str]: 季节性原因描述，如果没有检测到季节性返回None
        """
        values = historical_data["values"]
        if len(values) < 8:  # 季节性分析需要足够多的数据点
            return None
        
        # 检测季节性模式
        seasonality, strength = detect_seasonal_pattern(values)
        
        if not seasonality or strength < 0.2:  # 无明显季节性或季节性强度太弱
            return None
        
        # 获取当前在季节性周期中的位置
        current_position = self._get_seasonal_position(values, seasonality)
        
        # 构建季节性原因描述
        metric_name = basic_info["指标名称"]
        current_period = basic_info.get("当前周期", "当前周期")
        
        if strength >= 0.6:  # 强季节性
            if current_position == "高峰":
                return f"{metric_name}在{current_period}处于季节性周期的高峰期，呈现出明显的季节性增长特征"
            elif current_position == "低谷":
                return f"{metric_name}在{current_period}处于季节性周期的低谷期，符合季节性波动规律"
            elif current_position == "上升":
                return f"{metric_name}正处于季节性上升阶段，这符合历史季节性模式"
            elif current_position == "下降":
                return f"{metric_name}正处于季节性下降阶段，这符合历史季节性模式"
            else:
                return f"{metric_name}表现出明显的季节性波动特征，周期约为{seasonality}个时间单位"
        else:  # 中等季节性
            return f"{metric_name}存在一定的季节性因素影响，约{seasonality}个时间单位为一个周期"
    
    def _get_seasonal_position(self, values: List[float], seasonality: int) -> str:
        """
        确定当前在季节性周期中的位置
        
        参数:
            values (List[float]): 历史值列表
            seasonality (int): 季节性周期长度
            
        返回:
            str: 位置描述，可能是"高峰"、"低谷"、"上升"、"下降"或"波动"
        """
        if len(values) < seasonality * 2:
            return "未知"  # 数据不足以确定位置
        
        try:
            # 创建时间序列
            ts = pd.Series(values)
            
            # 季节性分解
            decomposition = seasonal_decompose(ts, model='additive', period=seasonality)
            seasonal_component = decomposition.seasonal
            
            # 获取最后一个季节位置的值
            last_seasonal_value = seasonal_component.iloc[-1]
            
            # 根据季节成分的值确定位置
            if last_seasonal_value > seasonal_component.quantile(0.8):
                return "高峰"
            elif last_seasonal_value < seasonal_component.quantile(0.2):
                return "低谷"
            elif last_seasonal_value > 0 and last_seasonal_value <= seasonal_component.quantile(0.8):
                # 检查趋势方向
                if seasonal_component.iloc[-1] > seasonal_component.iloc[-2]:
                    return "上升"
                else:
                    return "下降"
            elif last_seasonal_value < 0 and last_seasonal_value >= seasonal_component.quantile(0.2):
                # 检查趋势方向
                if seasonal_component.iloc[-1] > seasonal_component.iloc[-2]:
                    return "上升"
                else:
                    return "下降"
            else:
                return "波动"
                
        except Exception as e:
            logging.warning(f"季节性位置分析失败: {str(e)}")
            return "未知"
    
    def _analyze_metric_relations(self, basic_info: Dict[str, Any], 
                                 change_analysis: Dict[str, Any],
                                 related_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        分析指标间关系以找出可能的原因
        
        参数:
            basic_info (Dict[str, Any]): 基本信息
            change_analysis (Dict[str, Any]): 变化分析
            related_metrics (List[Dict[str, Any]]): 相关指标列表
            
        返回:
            List[str]: 基于指标关系的可能原因列表
        """
        if not related_metrics:
            return []
        
        reasons = []
        metric_name = basic_info["指标名称"]
        main_change_direction = change_analysis["变化方向"]
        
        # 筛选强相关的指标
        strong_correlations = []
        for metric in related_metrics:
            # 如果没有明确的相关性值，尝试计算
            correlation = metric.get("correlation", None)
            if correlation is None and "previous_value" in metric and "value" in metric:
                # 简单计算两个点的变化方向相关性
                metric_change = metric["value"] - metric["previous_value"]
                metric_direction = "增加" if metric_change > 0 else "减少"
                # 方向一致表示正相关，方向相反表示负相关
                correlation = 0.8 if metric_direction == main_change_direction else -0.8
                metric["correlation"] = correlation
            
            # 只考虑强相关的指标
            if correlation is not None and abs(correlation) >= 0.6:
                strong_correlations.append(metric)
        
        # 根据相关性生成原因解释
        for metric in strong_correlations:
            metric_name_related = metric["name"]
            correlation = metric["correlation"]
            
            # 计算指标变化
            if "value" in metric and "previous_value" in metric:
                related_change = metric["value"] - metric["previous_value"]
                related_direction = "增加" if related_change > 0 else "减少"
                
                # 构建关系描述
                if correlation > 0:  # 正相关
                    if main_change_direction == related_direction:
                        # 构建正相关且方向一致的描述
                        reason = f"{metric_name_related}的{related_direction}，与{metric_name}的{main_change_direction}呈正相关关系，可能是重要影响因素"
                    else:
                        # 方向不一致，可能是异常情况，不生成原因
                        continue
                else:  # 负相关
                    if main_change_direction != related_direction:
                        # 构建负相关且方向相反的描述
                        reason = f"{metric_name_related}的{related_direction}，与{metric_name}的{main_change_direction}呈负相关关系，可能导致了当前变化"
                    else:
                        # 方向一致，可能是异常情况，不生成原因
                        continue
                        
                reasons.append(reason)
        
        return reasons[:2]  # 最多返回前两个原因
    
    def _analyze_anomaly_reason(self, basic_info: Dict[str, Any], 
                               anomaly_analysis: Dict[str, Any]) -> Optional[str]:
        """
        分析异常值可能的原因
        
        参数:
            basic_info (Dict[str, Any]): 基本信息
            anomaly_analysis (Dict[str, Any]): 异常分析
            
        返回:
            Optional[str]: 异常原因描述，如果不是异常则返回None
        """
        if not anomaly_analysis.get("是否异常", False):
            return None
        
        metric_name = basic_info["指标名称"]
        anomaly_degree = anomaly_analysis.get("异常程度", 0.0)
        is_higher = anomaly_analysis.get("是否高于正常范围", True)
        
        # 构建异常描述
        degree_desc = ""
        if anomaly_degree >= 3.0:
            degree_desc = "极端"
        elif anomaly_degree >= 2.0:
            degree_desc = "明显"
        else:
            degree_desc = "一定"
            
        direction = "增长" if is_higher else "下降"
        
        return f"{metric_name}出现{degree_desc}的异常{direction}，这可能是由于突发事件、数据采集问题或环境因素显著变化导致"
    
    def _generate_llm_reasons(self, basic_info: Dict[str, Any], 
                             change_analysis: Dict[str, Any],
                             historical_data: Dict[str, Any],
                             related_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        使用大语言模型生成更智能的原因分析
        
        参数:
            basic_info (Dict[str, Any]): 基本信息
            change_analysis (Dict[str, Any]): 变化分析
            historical_data (Dict[str, Any]): 历史数据
            related_metrics (List[Dict[str, Any]]): 相关指标
            
        返回:
            List[str]: LLM生成的原因列表
        """
        if not self.use_llm:
            return []
        
        try:
            # 构建提示信息
            metric_name = basic_info["指标名称"]
            current_value = basic_info["当前值"]
            previous_value = basic_info["上一期值"]
            unit = basic_info.get("单位", "")
            time_period = basic_info.get("当前周期", "当前周期")
            previous_time_period = basic_info.get("上一周期", "上一周期")
            is_positive_better = basic_info.get("正向增长是否为好", True)
            
            change_value = change_analysis["变化量"]
            change_rate = change_analysis["变化率"]
            change_direction = change_analysis["变化方向"]
            
            prompt = f"""
            我需要分析以下指标变化的可能原因:
            
            指标名称: {metric_name}
            当前值: {current_value}{unit} ({time_period})
            上一期值: {previous_value}{unit} ({previous_time_period})
            变化: {change_value}{unit} ({change_rate:.2%})
            变化方向: {change_direction}
            对该指标，值{'增长' if is_positive_better else '下降'}通常被视为积极的
            
            """
            
            # 添加历史数据信息
            if historical_data and "values" in historical_data:
                values_str = ", ".join([str(v) for v in historical_data["values"]])
                time_periods = historical_data.get("time_periods", [])
                
                if time_periods and len(time_periods) == len(historical_data["values"]):
                    periods_str = ", ".join(time_periods)
                    prompt += f"\n历史数据:\n时间: {periods_str}\n值: {values_str}\n"
                else:
                    prompt += f"\n历史值: {values_str}\n"
            
            # 添加相关指标信息
            if related_metrics:
                prompt += "\n相关指标:\n"
                for i, metric in enumerate(related_metrics):
                    metric_name = metric["name"]
                    value = metric.get("value", "N/A")
                    previous_value = metric.get("previous_value", "N/A")
                    unit = metric.get("unit", "")
                    correlation = metric.get("correlation", "未知")
                    
                    prompt += f"{i+1}. {metric_name}: {previous_value}{unit} -> {value}{unit} (相关性: {correlation})\n"
            
            prompt += """
            请分析这一变化的可能原因。列出3-5个合理的可能原因，每个原因用一句话简要说明，不要超过40个汉字。
            只需给出原因列表，不要有其他任何输出。每个原因占一行。
            """
            
            # 调用LLM
            if hasattr(self, "llm"):
                if self.llm_type == "openai":
                    from langchain.schema import HumanMessage
                    messages = [HumanMessage(content=prompt)]
                    response = self.llm.generate([messages])
                    response_text = response.generations[0][0].text
                else:
                    response_text = self.llm(prompt)
                
                # 处理响应，提取原因
                reasons = []
                for line in response_text.strip().split("\n"):
                    line = line.strip()
                    # 去除序号和其他非内容字符
                    line = re.sub(r"^\d+\.?\s*", "", line)
                    if line and len(line) <= 100:  # 确保是合理长度的原因
                        reasons.append(line)
                
                return reasons[:3]  # 最多返回3个LLM生成的原因
            else:
                return []
                
        except Exception as e:
            logging.warning(f"LLM原因生成失败: {str(e)}")
            return []
    
    def _calculate_confidence(self, reasons: List[str], 
                             basic_info: Dict[str, Any],
                             change_analysis: Dict[str, Any]) -> str:
        """
        计算分析结果的置信度
        
        参数:
            reasons (List[str]): 分析得出的原因列表
            basic_info (Dict[str, Any]): 基本信息
            change_analysis (Dict[str, Any]): 变化分析
            
        返回:
            str: 置信度描述，可能是"高"、"中"或"低"
        """
        # 基于多种因素计算置信度
        confidence_score = 0.0
        
        # 1. 原因数量
        reason_count = len(reasons)
        if reason_count >= 4:
            confidence_score += 0.3
        elif reason_count >= 2:
            confidence_score += 0.2
        else:
            confidence_score += 0.1
        
        # 2. 变化大小 - 变化越大越容易分析
        change_rate = abs(change_analysis.get("变化率", 0.0))
        if change_rate >= 0.3:  # 30%以上的变化
            confidence_score += 0.3
        elif change_rate >= 0.1:  # 10%-30%的变化
            confidence_score += 0.2
        else:  # 小变化
            confidence_score += 0.1
        
        # 3. 分析方法 - 使用LLM提高置信度
        if self.use_llm:
            confidence_score += 0.2
        
        # 4. 历史数据丰富度
        has_history = "历史数据" in basic_info or hasattr(basic_info, "historical_values")
        if has_history:
            confidence_score += 0.2
        
        # 将分数转换为置信度级别
        if confidence_score >= 0.7:
            return "高"
        elif confidence_score >= 0.4:
            return "中"
        else:
            return "低" 