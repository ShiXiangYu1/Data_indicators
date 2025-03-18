"""
根因分析器
========

分析指标变化的根本原因，构建因果关系网络，识别关键节点和路径。
"""

import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict
import matplotlib.pyplot as plt

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.core.attribution_analyzer import AttributionAnalyzer


class RootCauseAnalyzer(BaseAnalyzer):
    """
    根因分析器
    
    分析指标变化的根本原因，构建因果关系网络，识别关键节点和路径。
    """
    
    def __init__(
        self, 
        min_causal_strength: float = 0.2, 
        max_depth: int = 3,
        attribution_method: str = "linear"
    ):
        """
        初始化根因分析器
        
        参数:
            min_causal_strength (float): 最小因果强度阈值，低于此值的关系将被忽略
            max_depth (int): 根因分析的最大深度
            attribution_method (str): 用于归因分析的方法，支持"linear"或"random_forest"
        """
        super().__init__()
        self.min_causal_strength = min_causal_strength
        self.max_depth = max_depth
        self.attribution_method = attribution_method
        
        # 初始化内部使用的归因分析器
        self.attribution_analyzer = AttributionAnalyzer(method=attribution_method)
        
        # 因果关系图
        self.causal_graph = None
        
        # 根因影响类型阈值
        self.root_cause_impact_thresholds = {
            "关键": 0.4,  # 总影响超过40%为关键根因
            "主要": 0.25,  # 总影响超过25%为主要根因
            "次要": 0.1,   # 总影响超过10%为次要根因
            "微弱": 0.0    # 总影响超过0%为微弱根因
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标变化的根本原因
        
        参数:
            data (Dict[str, Any]): 输入数据，应包含以下字段:
                - target: 目标指标名称
                - target_values: 目标指标历史值列表
                - factors: 一级因素字典，每个因素包含其历史值列表
                - subfactors: 子因素字典，每个一级因素可以有多个子因素 (可选)
                - relationships: 已知的因素间关系列表 (可选)
                - time_periods: 时间周期列表 (可选)
                - current_period: 当前时间周期 (可选)
                
        返回:
            Dict[str, Any]: 根因分析结果
        """
        # 验证必要字段
        required_fields = ["target", "target_values", "factors"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        target = data["target"]
        target_values = data["target_values"]
        factors = data["factors"]
        subfactors = data.get("subfactors", {})
        known_relationships = data.get("relationships", [])
        time_periods = data.get("time_periods", [f"T{i+1}" for i in range(len(target_values))])
        current_period = data.get("current_period", time_periods[-1] if time_periods else "当前")
        
        # 1. 首先进行一级归因分析
        attribution_data = {
            "target": target,
            "target_values": target_values,
            "factors": factors,
            "time_periods": time_periods,
            "current_period": current_period,
            "method": self.attribution_method
        }
        
        attribution_result = self.attribution_analyzer.analyze(attribution_data)
        
        # 2. 构建因果图
        self.causal_graph = self._build_causal_graph(
            target, 
            attribution_result, 
            factors, 
            subfactors, 
            known_relationships
        )
        
        # 3. 识别根本原因
        root_causes = self._identify_root_causes(target)
        
        # 4. 分析关键路径
        causal_paths = self._analyze_causal_paths(target, root_causes)
        
        # 5. 计算根因分析置信度
        confidence = self._calculate_confidence(
            attribution_result, 
            root_causes, 
            len(factors), 
            len(target_values)
        )
        
        # 6. 计算根因解释能力
        explanation_power = self._calculate_explanation_power(root_causes, attribution_result)
        
        # 构建结果
        result = {
            "基本信息": {
                "目标指标": target,
                "分析方法": self.attribution_method,
                "当前周期": current_period,
                "数据周期数": len(target_values),
                "分析深度": self.max_depth
            },
            "根因分析结果": {
                "根本原因": root_causes,
                "因果路径": causal_paths,
                "解释覆盖率": explanation_power,
                "置信度": confidence
            },
            "一级归因分析": attribution_result["归因结果"]
        }
        
        return result
    
    def _build_causal_graph(
        self, 
        target: str, 
        attribution_result: Dict[str, Any],
        factors: Dict[str, List[float]],
        subfactors: Dict[str, Dict[str, List[float]]],
        known_relationships: List[Dict[str, Any]]
    ) -> nx.DiGraph:
        """
        构建因果关系图
        
        参数:
            target (str): 目标指标名称
            attribution_result (Dict[str, Any]): 归因分析结果
            factors (Dict[str, List[float]]): 一级因素数据
            subfactors (Dict[str, Dict[str, List[float]]]): 子因素数据
            known_relationships (List[Dict[str, Any]]): 已知因素间关系
            
        返回:
            nx.DiGraph: 构建的因果关系图
        """
        # 初始化有向图
        G = nx.DiGraph()
        
        # 添加目标节点
        G.add_node(target, type="target")
        
        # 添加一级因素节点和边
        for factor_info in attribution_result["归因结果"]["影响因素"]:
            factor_name = factor_info["因素名称"]
            contribution = factor_info["贡献度"]
            
            # 仅当贡献度大于阈值时添加边
            if contribution >= self.min_causal_strength:
                G.add_node(factor_name, type="factor")
                G.add_edge(
                    factor_name, 
                    target, 
                    weight=contribution, 
                    type="direct", 
                    direction=factor_info["影响方向"]
                )
        
        # 处理子因素
        for factor_name, subfactor_dict in subfactors.items():
            # 如果父因素不在图中，则跳过
            if factor_name not in G.nodes:
                continue
                
            # 对子因素进行归因分析
            if len(subfactor_dict) > 0 and factor_name in factors:
                subfactor_data = {
                    "target": factor_name,
                    "target_values": factors[factor_name],
                    "factors": subfactor_dict,
                    "method": self.attribution_method
                }
                
                try:
                    subfactor_result = self.attribution_analyzer.analyze(subfactor_data)
                    
                    # 添加子因素节点和边
                    for subfactor_info in subfactor_result["归因结果"]["影响因素"]:
                        subfactor_name = subfactor_info["因素名称"]
                        subfactor_contribution = subfactor_info["贡献度"]
                        
                        if subfactor_contribution >= self.min_causal_strength:
                            # 计算对目标的间接贡献
                            edge_to_target = G.get_edge_data(factor_name, target)
                            if edge_to_target:
                                factor_weight = edge_to_target["weight"]
                                indirect_contribution = subfactor_contribution * factor_weight
                                
                                G.add_node(subfactor_name, type="subfactor")
                                G.add_edge(
                                    subfactor_name, 
                                    factor_name, 
                                    weight=subfactor_contribution, 
                                    type="subfactor", 
                                    direction=subfactor_info["影响方向"]
                                )
                except Exception as e:
                    # 处理可能的异常情况，如数据不足
                    print(f"分析子因素 {factor_name} 时出错: {str(e)}")
        
        # 添加已知关系
        for relation in known_relationships:
            source = relation.get("source")
            target_node = relation.get("target")
            strength = relation.get("strength", 0.5)  # 默认中等强度
            direction = relation.get("direction", "正向")
            
            if source and target_node and strength >= self.min_causal_strength:
                # 添加节点(如果不存在)
                if source not in G.nodes:
                    G.add_node(source, type="external")
                if target_node not in G.nodes:
                    G.add_node(target_node, type="external")
                
                # 添加边
                G.add_edge(
                    source, 
                    target_node, 
                    weight=strength, 
                    type="known", 
                    direction=direction
                )
        
        # 深入分析因素间的关系
        if len(factors) >= 3:  # 只有当因素足够多时才进行因素间关系分析
            self._analyze_inter_factor_relationships(G, factors)
        
        return G
    
    def _analyze_inter_factor_relationships(self, G: nx.DiGraph, factors: Dict[str, List[float]]):
        """
        分析因素之间的关系
        
        参数:
            G (nx.DiGraph): 因果关系图
            factors (Dict[str, List[float]]): 因素数据
        """
        # 因素之间的相关性分析
        factor_df = pd.DataFrame(factors)
        
        # 计算相关性矩阵
        corr_matrix = factor_df.corr()
        
        # 标识可能的因果关系
        for factor1 in corr_matrix.columns:
            for factor2 in corr_matrix.columns:
                if factor1 != factor2:
                    correlation = corr_matrix.loc[factor1, factor2]
                    
                    # 使用较高的阈值来确定因素间关系
                    if abs(correlation) >= max(0.7, self.min_causal_strength):
                        # 判断方向 - 这是一个简化的假设，实际上应该使用更复杂的因果推断
                        # 这里假设相关性高的因素对可能有因果关系，方向基于启发式规则
                        
                        # 检查是否有指向目标的边以及其权重
                        edge1_to_target = G.get_edge_data(factor1, G.graph.get("target", "target"))
                        edge2_to_target = G.get_edge_data(factor2, G.graph.get("target", "target"))
                        
                        # 如果两个因素都已经在图中
                        if factor1 in G.nodes and factor2 in G.nodes:
                            # 权重较低的因素可能受权重较高的因素影响
                            if (edge1_to_target and edge2_to_target and 
                                edge1_to_target["weight"] > edge2_to_target["weight"]):
                                G.add_edge(
                                    factor1, 
                                    factor2, 
                                    weight=abs(correlation), 
                                    type="inferred", 
                                    direction="正向" if correlation > 0 else "负向"
                                )
                            elif (edge1_to_target and edge2_to_target and 
                                  edge1_to_target["weight"] < edge2_to_target["weight"]):
                                G.add_edge(
                                    factor2, 
                                    factor1, 
                                    weight=abs(correlation), 
                                    type="inferred", 
                                    direction="正向" if correlation > 0 else "负向"
                                )
    
    def _identify_root_causes(self, target: str) -> List[Dict[str, Any]]:
        """
        识别根本原因
        
        参数:
            target (str): 目标指标名称
            
        返回:
            List[Dict[str, Any]]: 根本原因列表
        """
        # 确保图存在
        if not self.causal_graph:
            return []
        
        # 找出入度为0的节点(根节点)
        root_nodes = [node for node, in_degree in self.causal_graph.in_degree() if in_degree == 0]
        
        # 排除目标节点本身
        if target in root_nodes:
            root_nodes.remove(target)
        
        # 计算每个根节点到目标的总影响
        root_cause_impacts = []
        
        for root in root_nodes:
            # 查找所有从根到目标的路径
            try:
                paths = list(nx.all_simple_paths(self.causal_graph, root, target, cutoff=self.max_depth))
                
                # 对每条路径计算影响
                total_impact = 0
                path_details = []
                
                for path in paths:
                    path_impact = 1.0  # 初始影响为1
                    path_edges = []
                    
                    # 计算路径上的累积影响
                    for i in range(len(path) - 1):
                        source, dest = path[i], path[i+1]
                        edge_data = self.causal_graph.get_edge_data(source, dest)
                        edge_weight = edge_data.get("weight", 0)
                        edge_direction = edge_data.get("direction", "正向")
                        
                        path_impact *= edge_weight  # 累积影响
                        
                        # 记录路径上的边信息
                        path_edges.append({
                            "source": source,
                            "target": dest,
                            "weight": edge_weight,
                            "direction": edge_direction
                        })
                    
                    # 添加路径详情
                    path_details.append({
                        "path": path,
                        "impact": path_impact,
                        "edges": path_edges
                    })
                    
                    total_impact += path_impact
                
                # 只有总影响超过阈值的根因才添加到结果中
                if total_impact >= self.min_causal_strength:
                    # 确定根因类型
                    impact_type = "微弱"
                    for level, threshold in self.root_cause_impact_thresholds.items():
                        if total_impact >= threshold:
                            impact_type = level
                            break
                    
                    # 添加到根因列表
                    root_cause_impacts.append({
                        "根因名称": root,
                        "总影响度": total_impact,
                        "影响类型": impact_type,
                        "路径数量": len(paths),
                        "路径详情": path_details
                    })
            except nx.NetworkXNoPath:
                # 无路径到达目标，跳过
                continue
        
        # 按总影响度排序
        root_cause_impacts.sort(key=lambda x: x["总影响度"], reverse=True)
        
        return root_cause_impacts
    
    def _analyze_causal_paths(self, target: str, root_causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析关键因果路径
        
        参数:
            target (str): 目标指标名称
            root_causes (List[Dict[str, Any]]): 根本原因列表
            
        返回:
            List[Dict[str, Any]]: 关键因果路径列表
        """
        # 如果没有根因，返回空列表
        if not root_causes:
            return []
        
        # 查找最重要的路径
        critical_paths = []
        
        # 对每个根因找出最重要的路径
        for root_cause in root_causes:
            root = root_cause["根因名称"]
            path_details = root_cause["路径详情"]
            
            # 按影响度排序
            sorted_paths = sorted(path_details, key=lambda x: x["impact"], reverse=True)
            
            # 只取最重要的路径(影响最大)
            if sorted_paths:
                top_path = sorted_paths[0]
                
                # 添加到关键路径列表
                critical_paths.append({
                    "起点": root,
                    "终点": target,
                    "路径": top_path["path"],
                    "影响度": top_path["impact"],
                    "影响强度": self._classify_path_strength(top_path["impact"]),
                    "边信息": top_path["edges"]
                })
        
        # 按影响度排序
        critical_paths.sort(key=lambda x: x["影响度"], reverse=True)
        
        return critical_paths
    
    def _classify_path_strength(self, impact: float) -> str:
        """
        根据影响度分类路径强度
        
        参数:
            impact (float): 路径影响度
            
        返回:
            str: 路径强度分类
        """
        if impact >= 0.4:
            return "强"
        elif impact >= 0.2:
            return "中"
        else:
            return "弱"
    
    def _calculate_confidence(
        self, 
        attribution_result: Dict[str, Any],
        root_causes: List[Dict[str, Any]],
        factor_count: int,
        data_points: int
    ) -> str:
        """
        计算根因分析的置信度
        
        参数:
            attribution_result (Dict[str, Any]): 归因分析结果
            root_causes (List[Dict[str, Any]]): 根本原因列表
            factor_count (int): 因素数量
            data_points (int): 数据点数量
            
        返回:
            str: 置信度级别描述
        """
        # 归因覆盖度
        attribution_coverage = attribution_result["归因结果"].get("覆盖度", 0)
        
        # 归因分析置信度
        attribution_confidence = attribution_result["归因结果"].get("置信度", "低")
        confidence_map = {"高": 3, "中": 2, "低": 1}
        attribution_score = confidence_map.get(attribution_confidence, 1)
        
        # 根因数量适当性
        root_cause_count = len(root_causes)
        root_cause_ratio = root_cause_count / max(1, factor_count)
        root_cause_score = 3
        if root_cause_ratio > 0.8:  # 根因太多
            root_cause_score = 1
        elif root_cause_ratio > 0.5:  # 根因较多
            root_cause_score = 2
        
        # 数据点充足性
        data_score = 1
        if data_points >= 30:
            data_score = 3
        elif data_points >= 15:
            data_score = 2
        
        # 加权综合评分
        total_score = (
            attribution_score * 0.4 + 
            attribution_coverage * 0.3 + 
            root_cause_score * 0.2 + 
            data_score * 0.1
        )
        
        # 转换为置信度级别
        if total_score >= 2.5:
            return "高"
        elif total_score >= 1.7:
            return "中"
        else:
            return "低"
    
    def _calculate_explanation_power(
        self, 
        root_causes: List[Dict[str, Any]], 
        attribution_result: Dict[str, Any]
    ) -> float:
        """
        计算根因分析的解释能力
        
        参数:
            root_causes (List[Dict[str, Any]]): 根本原因列表
            attribution_result (Dict[str, Any]): 归因分析结果
            
        返回:
            float: 解释覆盖率
        """
        # 如果没有根因，解释能力为0
        if not root_causes:
            return 0.0
        
        # 归因分析的覆盖度
        attribution_coverage = attribution_result["归因结果"].get("覆盖度", 0)
        
        # 计算所有根因的总影响度
        total_impact = sum(rc["总影响度"] for rc in root_causes)
        
        # 实际解释力为归因覆盖度与根因总影响度的乘积
        explanation_power = min(attribution_coverage * total_impact, 1.0)
        
        return explanation_power
    
    def visualize_causal_graph(self, figsize=(12, 8), save_path=None):
        """
        可视化因果关系图
        
        参数:
            figsize (tuple): 图像大小
            save_path (str, optional): 保存路径，如果不提供则显示图像
        """
        if not self.causal_graph:
            print("没有可视化的因果图！请先运行分析。")
            return
        
        plt.figure(figsize=figsize)
        
        # 创建节点位置布局
        pos = nx.spring_layout(self.causal_graph, seed=42)
        
        # 设置节点颜色
        node_colors = []
        for node in self.causal_graph.nodes():
            node_type = self.causal_graph.nodes[node].get('type', '')
            if node_type == 'target':
                node_colors.append('red')
            elif node_type == 'factor':
                node_colors.append('blue')
            elif node_type == 'subfactor':
                node_colors.append('green')
            else:
                node_colors.append('gray')
        
        # 设置边的宽度和颜色
        edge_widths = []
        edge_colors = []
        for u, v, data in self.causal_graph.edges(data=True):
            weight = data.get('weight', 0.1)
            edge_type = data.get('type', '')
            direction = data.get('direction', '正向')
            
            # 边的宽度基于权重
            edge_widths.append(weight * 2)
            
            # 边的颜色基于类型和方向
            if direction == '负向':
                edge_colors.append('red')
            elif edge_type == 'direct':
                edge_colors.append('blue')
            elif edge_type == 'subfactor':
                edge_colors.append('green')
            elif edge_type == 'known':
                edge_colors.append('purple')
            elif edge_type == 'inferred':
                edge_colors.append('orange')
            else:
                edge_colors.append('gray')
        
        # 绘制节点
        nx.draw_networkx_nodes(
            self.causal_graph, 
            pos, 
            node_color=node_colors, 
            node_size=700,
            alpha=0.8
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.causal_graph, 
            pos, 
            width=edge_widths,
            edge_color=edge_colors,
            arrowsize=20,
            alpha=0.7
        )
        
        # 绘制标签
        nx.draw_networkx_labels(self.causal_graph, pos, font_size=10)
        
        # 添加图例
        node_types = {
            '目标': 'red',
            '一级因素': 'blue',
            '子因素': 'green',
            '其他': 'gray'
        }
        edge_types = {
            '正向关系': 'blue',
            '负向关系': 'red',
            '子因素关系': 'green',
            '已知关系': 'purple',
            '推断关系': 'orange'
        }
        
        # 创建图例句柄
        node_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) 
                       for color in node_types.values()]
        edge_handles = [plt.Line2D([0], [0], color=color, linewidth=2) 
                       for color in edge_types.values()]
        
        # 添加图例
        plt.legend(
            node_handles + edge_handles, 
            list(node_types.keys()) + list(edge_types.keys()),
            loc='upper right'
        )
        
        # 设置标题和其他参数
        plt.title('因果关系图', fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def get_root_cause_summary(self) -> str:
        """
        获取根因分析的摘要文本
        
        返回:
            str: 根因分析摘要
        """
        if not hasattr(self, 'last_result') or not self.last_result:
            return "请先运行分析以获得摘要！"
        
        result = self.last_result
        
        # 构建摘要文本
        summary = []
        summary.append(f"目标指标: {result['基本信息']['目标指标']}")
        summary.append(f"分析置信度: {result['根因分析结果']['置信度']}")
        summary.append(f"解释覆盖率: {result['根因分析结果']['解释覆盖率']:.2f}")
        
        # 添加根本原因
        root_causes = result['根因分析结果']['根本原因']
        if root_causes:
            summary.append("\n主要根本原因:")
            for i, rc in enumerate(root_causes[:3], 1):  # 只列出前三个
                summary.append(f"{i}. {rc['根因名称']} - 影响度: {rc['总影响度']:.2f}, 类型: {rc['影响类型']}")
        else:
            summary.append("\n未找到明确的根本原因。")
        
        # 添加关键路径
        causal_paths = result['根因分析结果']['因果路径']
        if causal_paths:
            summary.append("\n关键因果路径:")
            for i, path in enumerate(causal_paths[:3], 1):  # 只列出前三个
                path_str = " → ".join(path['路径'])
                summary.append(f"{i}. {path_str} (影响强度: {path['影响强度']}, 影响度: {path['影响度']:.2f})")
        
        return "\n".join(summary) 