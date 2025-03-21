"""
指标服务
======

提供指标分析相关的服务功能，作为API和核心分析模块之间的桥梁。
"""

import logging
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache

from ..core.analysis.metric import MetricAnalyzer
from ..core.analysis.comparison import ComparisonAnalyzer
from ..core.prediction.time_series import TimeSeriesPredictor
from ..core.generation.text import TextGenerator
from ..config import settings


class MetricService:
    """
    指标服务
    
    封装指标分析相关功能，提供高级服务接口。
    """
    
    def __init__(self):
        """初始化指标服务"""
        self.logger = logging.getLogger("data_insight.services.metric")
        self.metric_analyzer = MetricAnalyzer()
        self.comparison_analyzer = ComparisonAnalyzer()
        self.predictor = TimeSeriesPredictor()
        self.text_generator = TextGenerator()
        
        # 设置缓存
        self.cache_enabled = True
        self.cache_size = 100
    
    @lru_cache(maxsize=100)
    def analyze_metric(self, metric_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析单个指标数据
        
        参数:
            metric_data (Dict[str, Any]): 指标数据
            context (Dict[str, Any], optional): 上下文信息
            
        返回:
            Dict[str, Any]: 分析结果，包括分析数据和文本解读
        """
        try:
            self.logger.info(f"开始分析指标: {metric_data.get('name', '未命名指标')}")
            
            # 准备分析数据
            analysis_data = {
                "metric": metric_data,
                "context": context or {}
            }
            
            # 分析指标
            analysis_result = self.metric_analyzer.analyze(analysis_data)
            
            # 生成解读文本
            insight_text = self.text_generator.generate(analysis_result)
            
            # 构建结果
            result = {
                "analysis": analysis_result,
                "insight": insight_text
            }
            
            self.logger.info(f"指标分析完成: {metric_data.get('name', '未命名指标')}")
            return result
            
        except Exception as e:
            self.logger.error(f"指标分析异常: {str(e)}", exc_info=True)
            raise
    
    @lru_cache(maxsize=50)
    def compare_metrics(self, metrics_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        比较多个指标数据
        
        参数:
            metrics_data (Dict[str, Any]): 多个指标数据
            context (Dict[str, Any], optional): 上下文信息
            
        返回:
            Dict[str, Any]: 对比分析结果，包括分析数据和文本解读
        """
        try:
            metrics = metrics_data.get("metrics", [])
            self.logger.info(f"开始对比分析 {len(metrics)} 个指标")
            
            # 准备分析数据
            analysis_data = {
                "metrics": metrics,
                "context": context or {}
            }
            
            # 分析指标对比
            analysis_result = self.comparison_analyzer.analyze(analysis_data)
            
            # 生成对比解读文本
            insight_text = self.text_generator.generate(analysis_result)
            
            # 构建结果
            result = {
                "analysis": analysis_result,
                "insight": insight_text
            }
            
            self.logger.info(f"指标对比分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"指标对比分析异常: {str(e)}", exc_info=True)
            raise
    
    @lru_cache(maxsize=50)
    def predict_metric(self, metric_data: Dict[str, Any], horizon: int = 7, 
                      confidence_level: float = 0.95) -> Dict[str, Any]:
        """
        预测指标未来值
        
        参数:
            metric_data (Dict[str, Any]): 指标数据
            horizon (int, optional): 预测步长，默认为7
            confidence_level (float, optional): 置信水平，默认为0.95
            
        返回:
            Dict[str, Any]: 预测结果，包括预测值和置信区间
        """
        try:
            self.logger.info(f"开始预测指标: {metric_data.get('name', '未命名指标')}, 步长: {horizon}")
            
            # 准备预测数据
            prediction_data = {
                "metric": metric_data,
                "historical_values": metric_data.get("historical_values", [])
            }
            
            # 预测指标
            prediction_result = self.predictor.predict(
                prediction_data, 
                horizon=horizon,
                confidence_level=confidence_level
            )
            
            # 生成预测解读文本
            insight_text = self.text_generator.generate(prediction_result)
            
            # 构建结果
            result = {
                "prediction": prediction_result,
                "insight": insight_text
            }
            
            self.logger.info(f"指标预测完成: {metric_data.get('name', '未命名指标')}")
            return result
            
        except Exception as e:
            self.logger.error(f"指标预测异常: {str(e)}", exc_info=True)
            raise
    
    def validate_metric_data(self, metric_data: Dict[str, Any]) -> bool:
        """
        验证指标数据格式
        
        参数:
            metric_data (Dict[str, Any]): 指标数据
            
        返回:
            bool: 数据格式是否有效
            
        异常:
            ValueError: 如果数据格式无效
        """
        # 基本字段验证
        required_fields = ["name", "value"]
        
        if not isinstance(metric_data, dict):
            raise ValueError("指标数据必须是字典类型")
        
        # 检查必需字段
        for field in required_fields:
            if field not in metric_data:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 验证value是数值类型
        value = metric_data.get("value")
        if not isinstance(value, (int, float)):
            raise ValueError(f"指标值必须是数值类型，但实际是{type(value)}")
        
        # 如果有历史值，验证是列表类型
        if "historical_values" in metric_data:
            historical_values = metric_data.get("historical_values")
            if not isinstance(historical_values, list):
                raise ValueError("historical_values必须是列表类型")
            
            # 验证列表中的所有元素都是数值
            if not all(isinstance(x, (int, float)) for x in historical_values):
                raise ValueError("historical_values中所有元素必须是数值类型")
        
        return True
    
    def invalidate_cache(self):
        """清除缓存"""
        self.analyze_metric.cache_clear()
        self.compare_metrics.cache_clear()
        self.predict_metric.cache_clear()
        self.logger.info("指标服务缓存已清除") 