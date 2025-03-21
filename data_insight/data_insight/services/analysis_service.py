"""
分析服务
======

提供综合分析相关的服务功能，作为API和核心分析模块之间的桥梁。
"""

import logging
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache

from ..core.analysis.base import BaseAnalyzer
from ..core.analysis.metric import MetricAnalyzer
from ..core.analysis.chart import ChartAnalyzer
from ..core.analysis.comparison import ComparisonAnalyzer
from ..core.generation.text import TextGenerator
from ..config import settings


class AnalysisService:
    """
    分析服务
    
    封装综合分析相关功能，提供高级服务接口。
    """
    
    def __init__(self):
        """初始化分析服务"""
        self.logger = logging.getLogger("data_insight.services.analysis")
        self.metric_analyzer = MetricAnalyzer()
        self.chart_analyzer = ChartAnalyzer()
        self.comparison_analyzer = ComparisonAnalyzer()
        self.text_generator = TextGenerator()
        
        # 设置缓存
        self.cache_enabled = True
        self.cache_size = 100
    
    @lru_cache(maxsize=100)
    def analyze_data(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        综合分析数据
        
        参数:
            data (Dict[str, Any]): 待分析数据
            context (Dict[str, Any], optional): 上下文信息
            
        返回:
            Dict[str, Any]: 分析结果，包括分析数据和文本解读
        """
        try:
            self.logger.info(f"开始综合分析数据")
            
            # 准备分析数据
            analysis_data = {
                "data": data,
                "context": context or {}
            }
            
            # 根据数据类型选择合适的分析器
            data_type = data.get("type", "general")
            
            if data_type == "metric":
                analyzer = self.metric_analyzer
            elif data_type == "chart":
                analyzer = self.chart_analyzer
            elif data_type == "comparison":
                analyzer = self.comparison_analyzer
            else:
                # 默认使用通用分析方法
                analyzer = self._get_appropriate_analyzer(data)
            
            # 分析数据
            analysis_result = analyzer.analyze(analysis_data)
            
            # 生成解读文本
            insight_text = self.text_generator.generate(analysis_result)
            
            # 构建结果
            result = {
                "analysis": analysis_result,
                "insight": insight_text
            }
            
            self.logger.info(f"综合分析数据完成")
            return result
            
        except Exception as e:
            self.logger.error(f"综合分析数据异常: {str(e)}", exc_info=True)
            raise
    
    def _get_appropriate_analyzer(self, data: Dict[str, Any]) -> BaseAnalyzer:
        """
        根据数据特征选择合适的分析器
        
        参数:
            data (Dict[str, Any]): 待分析数据
            
        返回:
            BaseAnalyzer: 适合的分析器实例
        """
        # 简单启发式选择分析器
        if "metrics" in data:
            return self.comparison_analyzer
        elif "chart" in data:
            return self.chart_analyzer
        else:
            return self.metric_analyzer
    
    @lru_cache(maxsize=50)
    def multi_dimensional_analysis(self, data: Dict[str, Any], dimensions: List[str], 
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        多维度分析
        
        参数:
            data (Dict[str, Any]): 待分析数据
            dimensions (List[str]): 分析维度列表
            context (Dict[str, Any], optional): 上下文信息
            
        返回:
            Dict[str, Any]: 分析结果，包括分析数据和文本解读
        """
        try:
            self.logger.info(f"开始多维度分析，维度: {dimensions}")
            
            # 准备分析数据
            analysis_data = {
                "data": data,
                "dimensions": dimensions,
                "context": context or {}
            }
            
            # 使用比较分析器进行多维度分析
            analysis_result = self.comparison_analyzer.analyze(analysis_data)
            
            # 生成解读文本
            insight_text = self.text_generator.generate(analysis_result)
            
            # 构建结果
            result = {
                "analysis": analysis_result,
                "insight": insight_text,
                "dimensions": dimensions
            }
            
            self.logger.info(f"多维度分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"多维度分析异常: {str(e)}", exc_info=True)
            raise
    
    def get_analysis_methods(self) -> List[str]:
        """
        获取支持的分析方法
        
        返回:
            List[str]: 支持的分析方法列表
        """
        return ["general", "metric", "chart", "comparison", "multi_dimensional"]
    
    def get_supported_data_types(self) -> List[str]:
        """
        获取支持的数据类型
        
        返回:
            List[str]: 支持的数据类型列表
        """
        return ["metric", "chart", "time_series", "tabular", "categorical"] 