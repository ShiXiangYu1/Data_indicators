"""
API数据模型
===========

定义API请求和响应的数据模型。
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ChartData(BaseModel):
    """图表数据模型"""
    title: str = Field(..., description="图表标题")
    type: str = Field(..., description="图表类型，如'line', 'bar', 'scatter', 'pie'等")
    data: Dict[str, Any] = Field(..., description="图表数据，格式根据图表类型不同而变化")
    x_label: Optional[str] = Field(None, description="X轴标签")
    y_label: Optional[str] = Field(None, description="Y轴标签")
    description: Optional[str] = Field(None, description="图表描述")
    
    @validator('type')
    def validate_chart_type(cls, v):
        allowed_types = ['line', 'bar', 'scatter', 'pie']
        if v not in allowed_types:
            raise ValueError(f"图表类型必须是以下之一: {', '.join(allowed_types)}")
        return v


class MetricData(BaseModel):
    """指标数据模型"""
    name: str = Field(..., description="指标名称")
    value: Union[float, int] = Field(..., description="当前值")
    previous_value: Optional[Union[float, int]] = Field(None, description="前期值")
    unit: Optional[str] = Field(None, description="单位")
    trend: Optional[str] = Field(None, description="趋势，如'up', 'down', 'stable'等")
    time_period: Optional[str] = Field(None, description="时间周期")
    previous_time_period: Optional[str] = Field(None, description="前期时间周期")
    historical_values: Optional[List[Union[float, int]]] = Field(None, description="历史值列表")
    description: Optional[str] = Field(None, description="指标描述")


class ComparisonData(BaseModel):
    """比较数据模型"""
    charts: List[ChartData] = Field(..., min_items=2, description="要比较的图表列表，至少需要两个图表")
    comparison_type: Optional[str] = Field("all", description="比较类型，可以是'trend', 'feature', 'anomaly', 'correlation'或'all'")
    context: Optional[Dict[str, Any]] = Field({}, description="比较上下文信息")
    
    @validator('comparison_type')
    def validate_comparison_type(cls, v):
        allowed_types = ['trend', 'feature', 'anomaly', 'correlation', 'all']
        if v not in allowed_types:
            raise ValueError(f"比较类型必须是以下之一: {', '.join(allowed_types)}")
        return v


class MetricComparisonData(BaseModel):
    """指标比较数据模型"""
    metrics: List[MetricData] = Field(..., min_items=2, description="要比较的指标列表，至少需要两个指标")
    comparison_type: Optional[str] = Field("all", description="比较类型，可以是'trend', 'feature', 'anomaly', 'correlation'或'all'")
    context: Optional[Dict[str, Any]] = Field({}, description="比较上下文信息")
    
    @validator('comparison_type')
    def validate_comparison_type(cls, v):
        allowed_types = ['trend', 'feature', 'anomaly', 'correlation', 'all']
        if v not in allowed_types:
            raise ValueError(f"比较类型必须是以下之一: {', '.join(allowed_types)}")
        return v


class PredictionRequest(BaseModel):
    """预测请求模型"""
    metric: MetricData = Field(..., description="要预测的指标数据")
    forecast_periods: int = Field(5, ge=1, le=30, description="预测周期数，范围1-30")
    method: Optional[str] = Field("auto", description="预测方法，如'auto', 'moving_average', 'exponential_smoothing', 'linear_regression'等")
    confidence_level: Optional[float] = Field(0.95, ge=0.5, le=0.99, description="置信水平，范围0.5-0.99")
    
    @validator('method')
    def validate_method(cls, v):
        allowed_methods = ['auto', 'moving_average', 'exponential_smoothing', 'linear_regression', 'arima']
        if v not in allowed_methods:
            raise ValueError(f"预测方法必须是以下之一: {', '.join(allowed_methods)}")
        return v


class TextGenerationRequest(BaseModel):
    """文本生成请求模型"""
    analysis_result: Dict[str, Any] = Field(..., description="分析结果")
    template: Optional[str] = Field("default", description="使用的模板")
    language: Optional[str] = Field("zh", description="语言，如'zh', 'en'等")
    style: Optional[str] = Field("normal", description="文本风格，如'normal', 'professional', 'simple'等")
    
    @validator('language')
    def validate_language(cls, v):
        allowed_languages = ['zh', 'en']
        if v not in allowed_languages:
            raise ValueError(f"语言必须是以下之一: {', '.join(allowed_languages)}")
        return v
        
    @validator('style')
    def validate_style(cls, v):
        allowed_styles = ['normal', 'professional', 'simple', 'detailed']
        if v not in allowed_styles:
            raise ValueError(f"文本风格必须是以下之一: {', '.join(allowed_styles)}")
        return v 