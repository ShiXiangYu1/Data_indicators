"""
图表API路由模块
===========

提供图表分析、比较等API端点。
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field

from data_insight.api.models import ChartData, ComparisonData
from data_insight.services.chart_service import ChartService
from data_insight.core.analysis.chart import ChartAnalyzer
from data_insight.core.analysis.comparison import ComparisonAnalyzer

# 创建路由
router = APIRouter(prefix="/charts", tags=["图表分析"])
logger = logging.getLogger("data_insight.api.routes.chart")

# 创建服务实例
chart_service = ChartService()


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_chart(chart_data: ChartData = Body(...)):
    """
    分析单个图表数据，提供趋势、分布、异常等专业分析结果。
    
    参数:
        chart_data: 图表数据对象，包含标题、类型、数据等
        
    返回:
        Dict[str, Any]: 图表分析结果
    """
    logger.info(f"接收到图表分析请求，图表标题：{chart_data.title}")
    
    try:
        result = chart_service.analyze_chart(chart_data.dict())
        return result
    except Exception as e:
        logger.error(f"图表分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"图表分析失败: {str(e)}")


@router.post("/compare", response_model=Dict[str, Any])
async def compare_charts(comparison_data: ComparisonData = Body(...)):
    """
    比较多个图表数据，发现它们之间的相似性、差异性以及潜在的关联关系。
    
    参数:
        comparison_data: 比较数据对象，包含要比较的图表列表和比较类型
        
    返回:
        Dict[str, Any]: 图表比较分析结果
    """
    logger.info(f"接收到图表比较请求，比较类型：{comparison_data.comparison_type}")
    
    if len(comparison_data.charts) < 2:
        raise HTTPException(status_code=400, detail="比较分析至少需要两个图表数据")
    
    try:
        # 创建比较分析器
        analyzer = ComparisonAnalyzer()
        
        # 执行比较分析
        result = analyzer.analyze({
            "charts": [chart.dict() for chart in comparison_data.charts],
            "comparison_type": comparison_data.comparison_type,
            "context": comparison_data.context
        })
        
        return result
    except Exception as e:
        logger.error(f"图表比较失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"图表比较失败: {str(e)}")


@router.get("/types", response_model=List[str])
async def get_supported_chart_types():
    """
    获取系统支持的图表类型列表。
    
    返回:
        List[str]: 支持的图表类型列表
    """
    try:
        analyzer = ChartAnalyzer()
        return analyzer.get_supported_chart_types()
    except Exception as e:
        logger.error(f"获取支持的图表类型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取支持的图表类型失败: {str(e)}")


@router.get("/comparison-types", response_model=List[str])
async def get_supported_comparison_types():
    """
    获取系统支持的图表比较类型列表。
    
    返回:
        List[str]: 支持的比较类型列表
    """
    try:
        analyzer = ComparisonAnalyzer()
        return analyzer.get_supported_comparison_types()
    except Exception as e:
        logger.error(f"获取支持的比较类型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取支持的比较类型失败: {str(e)}") 