#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能建议路由模块
============

提供生成智能行动建议的API接口。
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from pydantic import BaseModel

from data_insight.api.middlewares.auth import token_required
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.utils.response_formatter import format_success_response, format_error_response
from data_insight.utils.metrics import increment_request_count, record_request_duration
from data_insight.utils.performance import time_it
from data_insight.core import SuggestionGenerator

# 创建路由器
router = APIRouter(tags=["智能建议"])

# 创建日志记录器
logger = logging.getLogger(__name__)

# 创建建议生成器实例
suggestion_generator = SuggestionGenerator()


class SuggestionRequest(BaseModel):
    """智能建议请求模型"""
    metric_analysis: Dict[str, Any]
    chart_analysis: Optional[Dict[str, Any]] = None
    attribution_analysis: Optional[Dict[str, Any]] = None
    root_cause_analysis: Optional[Dict[str, Any]] = None
    prediction_analysis: Optional[Dict[str, Any]] = None
    min_confidence: Optional[float] = 0.6
    max_suggestions: Optional[int] = 5
    priority_threshold: Optional[float] = 0.7


@router.post("", summary="生成智能建议",
           description="基于多维度分析结果生成智能行动建议")
@rate_limit
@token_required
@time_it(name="generate_suggestions")
async def generate_suggestions(request: SuggestionRequest) -> Dict[str, Any]:
    """
    生成智能行动建议
    
    参数:
        request: 建议请求参数，包含各种分析结果
        
    返回:
        Dict[str, Any]: 建议结果
    """
    # 记录请求
    increment_request_count("/suggestion", "POST", 200)
    
    try:
        # 创建自定义建议生成器（使用请求参数覆盖默认配置）
        custom_generator = SuggestionGenerator(
            min_confidence=request.min_confidence,
            max_suggestions=request.max_suggestions,
            priority_threshold=request.priority_threshold
        )
        
        # 准备分析数据
        analysis_data = {
            "metric_analysis": request.metric_analysis,
        }
        
        # 添加可选分析结果
        if request.chart_analysis:
            analysis_data["chart_analysis"] = request.chart_analysis
        
        if request.attribution_analysis:
            analysis_data["attribution_analysis"] = request.attribution_analysis
        
        if request.root_cause_analysis:
            analysis_data["root_cause_analysis"] = request.root_cause_analysis
        
        if request.prediction_analysis:
            analysis_data["prediction_analysis"] = request.prediction_analysis
        
        # 生成建议
        suggestion_results = custom_generator.analyze(analysis_data)
        
        # 计算高优先级建议的比例
        high_priority_ratio = len([s for s in suggestion_results["建议列表"] if s["优先级"] == "高"]) / len(suggestion_results["建议列表"]) if suggestion_results["建议列表"] else 0
        
        # 格式化响应
        return format_success_response(
            data={
                "suggestions": suggestion_results["建议列表"],
                "overall_effect": suggestion_results["总体效果"],
                "suggestion_count": suggestion_results["建议数量"],
                "high_priority_count": suggestion_results["高优先级建议数"],
                "high_priority_ratio": high_priority_ratio
            },
            message="智能建议生成成功",
            status_code=200
        )
        
    except ValueError as e:
        logger.error(f"建议生成失败: {str(e)}", exc_info=True)
        return format_error_response(
            message="建议生成失败",
            status_code=400,
            error_type="InvalidInputError",
            error_detail={"reason": str(e)}
        )
    
    except Exception as e:
        logger.error(f"建议生成失败: {str(e)}", exc_info=True)
        return format_error_response(
            message="建议生成失败",
            status_code=500,
            error_type="SuggestionError",
            error_detail={"reason": str(e)}
        )


@router.get("/sample", summary="获取示例建议",
          description="基于预设数据生成示例建议")
@rate_limit
async def get_sample_suggestions() -> Dict[str, Any]:
    """
    获取示例建议
    
    返回:
        Dict[str, Any]: 示例建议结果
    """
    # 记录请求
    increment_request_count("/suggestion/sample", "GET", 200)
    
    try:
        # 创建示例分析数据
        sample_data = {
            "metric_analysis": {
                "基本信息": {
                    "指标名称": "销售额",
                    "当前值": 12000,
                    "上一期值": 10000,
                    "单位": "元"
                },
                "变化分析": {
                    "变化量": 2000,
                    "变化率": 0.2,
                    "变化类别": "显著上升",
                    "变化方向": "上升"
                },
                "异常分析": {
                    "是否异常": False,
                    "异常程度": 0.0,
                    "异常类型": ""
                }
            },
            "chart_analysis": {
                "基本信息": {
                    "图表标题": "月度销售趋势",
                    "图表类型": "line"
                },
                "趋势分析": {
                    "趋势类型": "上升",
                    "趋势强度": 0.65
                },
                "异常点分析": [
                    {
                        "位置": 3,
                        "异常程度": 1.2,
                        "异常描述": "轻微异常"
                    }
                ]
            },
            "root_cause_analysis": {
                "目标指标": "销售额",
                "根因列表": [
                    {
                        "根因描述": "促销活动效果显著",
                        "根因类型": "营销活动",
                        "影响程度": 0.75
                    },
                    {
                        "根因描述": "市场需求增加",
                        "根因类型": "市场因素",
                        "影响程度": 0.45
                    }
                ]
            }
        }
        
        # 生成建议
        suggestion_results = suggestion_generator.analyze(sample_data)
        
        # 计算高优先级建议的比例
        high_priority_ratio = len([s for s in suggestion_results["建议列表"] if s["优先级"] == "高"]) / len(suggestion_results["建议列表"]) if suggestion_results["建议列表"] else 0
        
        # 格式化响应
        return format_success_response(
            data={
                "suggestions": suggestion_results["建议列表"],
                "overall_effect": suggestion_results["总体效果"],
                "suggestion_count": suggestion_results["建议数量"],
                "high_priority_count": suggestion_results["高优先级建议数"],
                "high_priority_ratio": high_priority_ratio,
                "sample_data": sample_data
            },
            message="示例建议生成成功",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"示例建议生成失败: {str(e)}", exc_info=True)
        return format_error_response(
            message="示例建议生成失败",
            status_code=500,
            error_type="SuggestionError",
            error_detail={"reason": str(e)}
        ) 