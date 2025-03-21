"""
核心接口定义模块
=============

定义数据指标平台的核心组件接口，实现组件之间的松耦合。
"""

from data_insight.core.interfaces.analyzer import AnalyzerInterface
from data_insight.core.interfaces.predictor import PredictorInterface  
from data_insight.core.interfaces.recommender import RecommenderInterface
from data_insight.core.interfaces.generator import GeneratorInterface

__all__ = [
    'AnalyzerInterface',
    'PredictorInterface',
    'RecommenderInterface',
    'GeneratorInterface',
] 