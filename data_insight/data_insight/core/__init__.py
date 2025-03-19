"""
核心功能模块
===========

本模块包含数据分析与文本生成的核心组件。

子模块:
    base_analyzer: 基础分析器类
    metric_analyzer: 指标卡分析器
    chart_analyzer: 图表分析器
    metric_comparison_analyzer: 指标对比分析器
    reason_analyzer: 原因分析器
    predictor: 预测分析器
    attribution_analyzer: 归因分析器
    root_cause_analyzer: 根因分析器
    correlation_analyzer: 相关性分析器
    trend_analyzer: 趋势分析器
    text_generator: 文本生成器
    suggestion_generator: 智能建议生成器
"""

from .base_analyzer import BaseAnalyzer
from .metric_analyzer import MetricAnalyzer
from .chart_analyzer import ChartAnalyzer
from .reason_analyzer import ReasonAnalyzer
from .predictor import Predictor
from .attribution_analyzer import AttributionAnalyzer
from .root_cause_analyzer import RootCauseAnalyzer
from .correlation_analyzer import CorrelationAnalyzer
from .trend_analyzer import TrendAnalyzer
from .suggestion_generator import SuggestionGenerator
from .text_generator import TextGenerator

__all__ = [
    'BaseAnalyzer',
    'MetricAnalyzer',
    'ChartAnalyzer',
    'ReasonAnalyzer',
    'Predictor',
    'AttributionAnalyzer',
    'RootCauseAnalyzer',
    'CorrelationAnalyzer',
    'TrendAnalyzer',
    'SuggestionGenerator',
    'TextGenerator'
] 