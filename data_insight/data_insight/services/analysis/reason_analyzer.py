import numpy as np
from typing import List, Dict, Any

class ReasonAnalyzer:
    """原因分析器类，用于分析指标变化的原因"""
    
    def __init__(self):
        """初始化原因分析器"""
        self.internal_factors = [
            '产品策略调整',
            '运营活动',
            '技术优化',
            '资源投入',
            '团队变动'
        ]
        self.external_factors = [
            '市场环境',
            '竞争对手',
            '政策法规',
            '季节性因素',
            '突发事件'
        ]
    
    def analyze(
        self,
        metric_name: str,
        current_value: float,
        previous_value: float,
        change_rate: float,
        historical_data: List[float] = None,
        external_factors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        分析指标变化的原因
        
        Args:
            metric_name: 指标名称
            current_value: 当前值
            previous_value: 上期值
            change_rate: 变化率
            historical_data: 历史数据
            external_factors: 外部因素数据
            
        Returns:
            Dict: 分析结果，包含内部原因和外部原因
        """
        # 计算变化幅度
        change_value = current_value - previous_value
        
        # 分析内部原因
        internal_reasons = self._analyze_internal_reasons(
            change_rate,
            change_value,
            historical_data
        )
        
        # 分析外部原因
        external_reasons = self._analyze_external_reasons(
            change_rate,
            external_factors
        )
        
        # 生成分析报告
        report = self._generate_report(
            metric_name,
            change_rate,
            internal_reasons,
            external_reasons
        )
        
        return {
            'metric_name': metric_name,
            'change_rate': change_rate,
            'internal_reasons': internal_reasons,
            'external_reasons': external_reasons,
            'report': report
        }
    
    def _analyze_internal_reasons(
        self,
        change_rate: float,
        change_value: float,
        historical_data: List[float]
    ) -> List[Dict[str, Any]]:
        """分析内部原因"""
        reasons = []
        
        # 根据变化率判断可能的原因
        if abs(change_rate) > 0.5:  # 大幅变化
            reasons.append({
                'factor': '产品策略调整',
                'probability': 0.8,
                'description': '可能是由于产品策略的重大调整导致'
            })
        elif abs(change_rate) > 0.2:  # 中等变化
            reasons.append({
                'factor': '运营活动',
                'probability': 0.6,
                'description': '可能是由于运营活动的影响'
            })
        
        # 分析历史数据趋势
        if historical_data and len(historical_data) > 5:
            trend = np.polyfit(range(len(historical_data)), historical_data, 1)[0]
            if trend > 0:
                reasons.append({
                    'factor': '技术优化',
                    'probability': 0.7,
                    'description': '存在持续上升趋势，可能是技术优化的效果'
                })
        
        return reasons
    
    def _analyze_external_reasons(
        self,
        change_rate: float,
        external_factors: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析外部原因"""
        reasons = []
        
        if not external_factors:
            return reasons
        
        # 分析市场环境
        if 'market_condition' in external_factors:
            market_condition = external_factors['market_condition']
            if market_condition == 'growth':
                reasons.append({
                    'factor': '市场环境',
                    'probability': 0.6,
                    'description': '市场整体处于增长期'
                })
            elif market_condition == 'decline':
                reasons.append({
                    'factor': '市场环境',
                    'probability': 0.7,
                    'description': '市场整体处于下行期'
                })
        
        # 分析竞争对手
        if 'competitor_activity' in external_factors:
            competitor_activity = external_factors['competitor_activity']
            if competitor_activity == 'aggressive':
                reasons.append({
                    'factor': '竞争对手',
                    'probability': 0.8,
                    'description': '竞争对手采取激进策略'
                })
        
        return reasons
    
    def _generate_report(
        self,
        metric_name: str,
        change_rate: float,
        internal_reasons: List[Dict[str, Any]],
        external_reasons: List[Dict[str, Any]]
    ) -> str:
        """生成分析报告"""
        report = f"指标 {metric_name} 的变化分析报告：\n\n"
        
        # 添加变化情况
        report += f"变化率：{change_rate:.2%}\n\n"
        
        # 添加内部原因
        if internal_reasons:
            report += "内部原因：\n"
            for reason in internal_reasons:
                report += f"- {reason['factor']}：{reason['description']}\n"
            report += "\n"
        
        # 添加外部原因
        if external_reasons:
            report += "外部原因：\n"
            for reason in external_reasons:
                report += f"- {reason['factor']}：{reason['description']}\n"
        
        return report 