"""
分析模块
=======

提供各种数据分析功能，包括指标分析、图表分析、对比分析等。
"""

from data_insight.core.analysis.base import BaseAnalyzer
from data_insight.core.analysis.metric import MetricAnalyzer
from data_insight.core.analysis.chart import ChartAnalyzer
from data_insight.core.analysis.comparison import ComparisonAnalyzer

# 暂时未实现的模块先注释掉
# from data_insight.core.analysis.reason import ReasonAnalyzer
# from data_insight.core.analysis.trend import TrendAnalyzer
# from data_insight.core.analysis.correlation import CorrelationAnalyzer
# from data_insight.core.analysis.attribution import AttributionAnalyzer
# from data_insight.core.analysis.root_cause import RootCauseAnalyzer

__all__ = [
    'BaseAnalyzer',
    'MetricAnalyzer',
    'ChartAnalyzer',
    'ComparisonAnalyzer',
    # 'ReasonAnalyzer',
    # 'TrendAnalyzer',
    # 'CorrelationAnalyzer',
    # 'AttributionAnalyzer',
    # 'RootCauseAnalyzer',
] 