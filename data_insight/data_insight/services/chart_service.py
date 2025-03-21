"""
图表服务
======

提供图表分析相关的服务功能，作为API和核心分析模块之间的桥梁。
"""

import logging
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache

from ..core.analysis.chart import ChartAnalyzer
from ..core.analysis.comparison import ComparisonAnalyzer
from ..core.generation.text import TextGenerator
from ..config import settings


class ChartService:
    """
    图表服务
    
    封装图表分析相关功能，提供高级服务接口。
    """
    
    def __init__(self):
        """初始化图表服务"""
        self.logger = logging.getLogger("data_insight.services.chart")
        self.chart_analyzer = ChartAnalyzer()
        self.comparison_analyzer = ComparisonAnalyzer()
        self.text_generator = TextGenerator()
        
        # 设置缓存
        self.cache_enabled = True
        self.cache_size = 100
    
    @lru_cache(maxsize=100)
    def analyze_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个图表数据
        
        参数:
            chart_data (Dict[str, Any]): 图表数据
            
        返回:
            Dict[str, Any]: 分析结果，包括分析数据和文本解读
        """
        try:
            self.logger.info(f"开始分析图表: {chart_data.get('title', '未命名图表')}")
            
            # 分析图表
            analysis_result = self.chart_analyzer.analyze(chart_data)
            
            # 生成解读文本
            insight_text = self.text_generator.generate(analysis_result)
            
            # 构建结果
            result = {
                "analysis": analysis_result,
                "insight": insight_text
            }
            
            self.logger.info(f"图表分析完成: {chart_data.get('title', '未命名图表')}")
            return result
            
        except Exception as e:
            self.logger.error(f"图表分析异常: {str(e)}", exc_info=True)
            raise
    
    @lru_cache(maxsize=50)
    def compare_charts(self, charts_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        比较多个图表数据
        
        参数:
            charts_data (Dict[str, Any]): 多个图表数据
            
        返回:
            Dict[str, Any]: 对比分析结果，包括分析数据和文本解读
        """
        try:
            self.logger.info(f"开始对比分析 {len(charts_data.get('charts', []))} 个图表")
            
            # 分析图表对比
            analysis_result = self.comparison_analyzer.analyze(charts_data)
            
            # 生成对比解读文本
            insight_text = self.text_generator.generate(analysis_result)
            
            # 构建结果
            result = {
                "analysis": analysis_result,
                "insight": insight_text
            }
            
            self.logger.info(f"图表对比分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"图表对比分析异常: {str(e)}", exc_info=True)
            raise
    
    def get_supported_chart_types(self) -> List[str]:
        """
        获取支持的图表类型
        
        返回:
            List[str]: 支持的图表类型列表
        """
        return ["line", "bar", "scatter", "pie"]
    
    def validate_chart_data(self, chart_data: Dict[str, Any]) -> bool:
        """
        验证图表数据格式
        
        参数:
            chart_data (Dict[str, Any]): 图表数据
            
        返回:
            bool: 数据格式是否有效
            
        异常:
            ValueError: 如果数据格式无效
        """
        # 基本字段验证
        required_fields = ["title", "type", "data"]
        
        if not isinstance(chart_data, dict):
            raise ValueError("图表数据必须是字典类型")
        
        # 检查必需字段
        for field in required_fields:
            if field not in chart_data:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 检查图表类型
        if chart_data["type"] not in self.get_supported_chart_types():
            raise ValueError(f"不支持的图表类型: {chart_data['type']}")
        
        # 检查数据字段
        data = chart_data["data"]
        if not isinstance(data, dict):
            raise ValueError("data字段必须是字典类型")
        
        # 根据图表类型进行不同验证
        chart_type = chart_data["type"]
        
        if chart_type in ["line", "bar"]:
            # 检查x和y字段
            if "x" not in data or "y" not in data:
                raise ValueError("线图或柱状图数据必须包含x和y字段")
                
            # 检查x和y是否为列表
            if not isinstance(data["x"], list) or not isinstance(data["y"], list):
                raise ValueError("x和y字段必须是列表类型")
                
            # 检查x和y长度是否一致
            if len(data["x"]) != len(data["y"]):
                raise ValueError("x和y字段长度必须一致")
        
        return True
    
    def invalidate_cache(self):
        """清除缓存"""
        self.analyze_chart.cache_clear()
        self.compare_charts.cache_clear()
        self.logger.info("图表服务缓存已清除") 