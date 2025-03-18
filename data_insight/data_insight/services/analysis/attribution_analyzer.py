import numpy as np
from typing import List, Dict, Any, Optional

class AttributionAnalyzer:
    """归因分析器类，用于分析指标变化中各因素的贡献度"""
    
    def __init__(self):
        """初始化归因分析器"""
        self.default_weights = {
            '产品': 0.3,
            '运营': 0.2,
            '技术': 0.2,
            '市场': 0.15,
            '其他': 0.15
        }
    
    def analyze(
        self,
        metric_name: str,
        factors: List[str],
        values: List[float],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        分析指标变化中各因素的贡献度
        
        Args:
            metric_name: 指标名称
            factors: 因素列表
            values: 各因素对应的值
            weights: 各因素的权重
            
        Returns:
            Dict: 分析结果，包含各因素的贡献度
        """
        # 参数验证
        if len(factors) != len(values):
            raise ValueError("因素列表和值列表长度必须相同")
        
        # 使用默认权重或自定义权重
        weights = weights or self.default_weights
        
        # 计算总变化
        total_change = sum(values)
        
        # 计算各因素的贡献度
        contributions = []
        for factor, value in zip(factors, values):
            weight = weights.get(factor, weights.get('其他', 0.15))
            contribution = value * weight / total_change if total_change != 0 else 0
            contributions.append({
                'factor': factor,
                'value': value,
                'weight': weight,
                'contribution': contribution,
                'contribution_rate': contribution / total_change if total_change != 0 else 0
            })
        
        # 计算关键因素
        key_factors = self._identify_key_factors(contributions)
        
        # 生成分析报告
        report = self._generate_report(
            metric_name,
            contributions,
            key_factors
        )
        
        return {
            'metric_name': metric_name,
            'total_change': total_change,
            'contributions': contributions,
            'key_factors': key_factors,
            'report': report
        }
    
    def _identify_key_factors(
        self,
        contributions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """识别关键因素"""
        # 按贡献度排序
        sorted_contributions = sorted(
            contributions,
            key=lambda x: x['contribution'],
            reverse=True
        )
        
        # 选择贡献度最高的前三个因素
        key_factors = []
        for i, contribution in enumerate(sorted_contributions[:3]):
            key_factors.append({
                'rank': i + 1,
                'factor': contribution['factor'],
                'contribution': contribution['contribution'],
                'contribution_rate': contribution['contribution_rate']
            })
        
        return key_factors
    
    def _generate_report(
        self,
        metric_name: str,
        contributions: List[Dict[str, Any]],
        key_factors: List[Dict[str, Any]]
    ) -> str:
        """生成分析报告"""
        report = f"指标 {metric_name} 的归因分析报告：\n\n"
        
        # 添加总体变化
        total_change = sum(c['value'] for c in contributions)
        report += f"总体变化：{total_change:.2f}\n\n"
        
        # 添加关键因素
        report += "关键因素分析：\n"
        for factor in key_factors:
            report += (
                f"{factor['rank']}. {factor['factor']}："
                f"贡献度 {factor['contribution_rate']:.2%}\n"
            )
        report += "\n"
        
        # 添加详细分析
        report += "详细分析：\n"
        for contribution in contributions:
            report += (
                f"- {contribution['factor']}："
                f"值 {contribution['value']:.2f}，"
                f"权重 {contribution['weight']:.2f}，"
                f"贡献度 {contribution['contribution_rate']:.2%}\n"
            )
        
        return report 