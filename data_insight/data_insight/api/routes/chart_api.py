"""
图表API路由
=========

提供图表分析和图表对比相关的API端点。
"""

from flask import Blueprint, request, jsonify
import json
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from data_insight.core.chart_analyzer import ChartAnalyzer
from data_insight.core.chart_comparison_analyzer import ChartComparisonAnalyzer
from data_insight.core.text_generator import TextGenerator
from data_insight.api.middlewares.auth import token_required
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.utils.validator import validate_json_request, Validator
from data_insight.api.utils.response_formatter import (
    format_success_response, format_error_response
)
from data_insight.api.utils.async_task import run_async, task_manager

# 创建Flask蓝图
bp = Blueprint('chart', __name__, url_prefix='/api/chart')

# 创建路由器
router = APIRouter()

# 初始化分析器和生成器
chart_analyzer = ChartAnalyzer()
comparison_analyzer = ChartComparisonAnalyzer()
text_generator = TextGenerator()

# 配置日志
logger = logging.getLogger('chart_api')


# 图表分析验证模式
chart_schema = {
    "title": {
        "type": "string",
        "required": True,
        "minlength": 1,
        "maxlength": 100
    },
    "type": {
        "type": "string",
        "required": True,
        "enum": ["line", "bar", "scatter", "pie"]
    },
    "data": {
        "type": "object",
        "required": True,
        "properties": {
            "x": {
                "type": "array",
                "required": True,
                "items": {
                    "type": ["string", "number"]
                }
            },
            "y": {
                "type": "array",
                "required": True,
                "items": {
                    "type": "number"
                }
            }
        }
    },
    "x_label": {
        "type": "string",
        "required": False
    },
    "y_label": {
        "type": "string",
        "required": False
    },
    "time_period": {
        "type": "string",
        "required": False
    }
}

# 图表对比验证模式
comparison_schema = {
    "charts": {
        "type": "array",
        "required": True,
        "minlength": 2,
        "items": {
            "type": "object",
            "properties": chart_schema
        }
    },
    "time_periods": {
        "type": "array",
        "required": False,
        "items": {
            "type": "string"
        }
    },
    "group_by": {
        "type": "string",
        "required": False,
        "enum": ["category", "dimension", "time"]
    }
}


@router.post('/analyze')
@rate_limit
@validate_json_request
@Validator.validate_request(chart_schema)
async def analyze_chart(request: Request, auth: bool = Depends(token_required)):
    """
    分析单个图表数据
    
    请求体应为JSON格式，包含图表数据。
    """
    try:
        # 获取请求数据
        data = await request.json()
        
        # 记录请求
        logger.info(f"接收到图表分析请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 分析图表
        analysis_result = chart_analyzer.analyze(data)
        
        # 生成文本解读
        text_insight = text_generator.generate_chart_insight(analysis_result)
        
        # 构建响应
        response_data = {
            "analysis": analysis_result,
            "insight": text_insight
        }
        
        # 返回结果
        return JSONResponse(content=format_success_response(
            data=response_data,
            message="图表分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"图表分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"图表分析失败: {str(e)}")


@router.post('/analyze-async')
@rate_limit
@validate_json_request
@Validator.validate_request(chart_schema)
async def analyze_chart_async(request: Request, auth: bool = Depends(token_required)):
    """
    异步分析单个图表数据
    
    请求体应为JSON格式，包含图表数据。
    """
    try:
        # 获取请求数据
        data = await request.json()
        
        # 记录请求
        logger.info(f"接收到异步图表分析请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建异步任务
        @run_async(timeout=60)  # 设置超时时间为60秒
        def analyze_chart_task(data):
            # 分析图表
            analysis_result = chart_analyzer.analyze(data)
            
            # 生成文本解读
            text_insight = text_generator.generate_chart_insight(analysis_result)
            
            # 构建响应
            return {
                "analysis": analysis_result,
                "insight": text_insight
            }
        
        # 启动异步任务
        task_result = analyze_chart_task(data)
        
        # 返回任务信息
        return JSONResponse(content=format_success_response(
            data=task_result,
            message="图表分析任务已提交",
            status_code=202
        ), status_code=202)
    
    except Exception as e:
        # 记录错误
        logger.error(f"提交图表分析任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"提交图表分析任务失败: {str(e)}")


@router.post('/compare')
@rate_limit
@validate_json_request
@Validator.validate_request(comparison_schema)
async def compare_charts(request: Request, auth: bool = Depends(token_required)):
    """
    比较多个图表数据
    
    请求体应为JSON格式，包含多个图表数据。
    """
    try:
        # 获取请求数据
        data = await request.json()
        
        # 记录请求
        logger.info(f"接收到图表对比请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 分析图表对比
        analysis_result = comparison_analyzer.analyze(data)
        
        # 生成对比解读文本
        text_insight = text_generator.generate_chart_comparison_insight(analysis_result)
        
        # 构建响应
        response_data = {
            "analysis": analysis_result,
            "insight": text_insight
        }
        
        # 返回结果
        return JSONResponse(content=format_success_response(
            data=response_data,
            message="图表对比分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"图表对比分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"图表对比分析失败: {str(e)}")


@router.post('/compare-async')
@rate_limit
@validate_json_request
@Validator.validate_request(comparison_schema)
async def compare_charts_async(request: Request, auth: bool = Depends(token_required)):
    """
    异步比较多个图表数据
    
    请求体应为JSON格式，包含多个图表数据。
    """
    try:
        # 获取请求数据
        data = await request.json()
        
        # 记录请求
        logger.info(f"接收到异步图表对比请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建异步任务
        @run_async(timeout=120)  # 设置超时时间为120秒
        def compare_charts_task(data):
            # 分析图表对比
            analysis_result = comparison_analyzer.analyze(data)
            
            # 生成对比解读文本
            text_insight = text_generator.generate_chart_comparison_insight(analysis_result)
            
            # 构建响应
            return {
                "analysis": analysis_result,
                "insight": text_insight
            }
        
        # 启动异步任务
        task_result = compare_charts_task(data)
        
        # 返回任务信息
        return JSONResponse(content=format_success_response(
            data=task_result,
            message="图表对比分析任务已提交",
            status_code=202
        ), status_code=202)
    
    except Exception as e:
        # 记录错误
        logger.error(f"提交图表对比分析任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"提交图表对比分析任务失败: {str(e)}")


@router.get('/task/{task_id}')
async def get_task_result(request: Request, task_id: str, auth: bool = Depends(token_required)):
    """
    获取任务结果
    
    参数:
        task_id (str): 任务ID
    """
    try:
        # 获取任务
        task_info = task_manager.get_task_info(task_id)
        
        # 检查任务是否存在
        if not task_info:
            raise HTTPException(
                status_code=404,
                detail=f"任务不存在: {task_id}"
            )
        
        # 检查任务状态
        status = task_info["status"]
        
        # 根据状态返回不同的响应
        if status == "completed":
            # 获取任务结果
            result = task_manager.get_task_result(task_id)
            
            return JSONResponse(content=format_success_response(
                data=result,
                message="任务完成"
            ))
            
        elif status == "failed":
            # 获取错误信息
            error = task_info.get("error", "未知错误")
            
            raise HTTPException(
                status_code=500,
                detail=f"任务失败: {error}"
            )
            
        elif status == "timeout":
            raise HTTPException(
                status_code=500,
                detail="任务超时"
            )
            
        else:  # pending or running
            return JSONResponse(content=format_success_response(
                data=task_info,
                message=f"任务{task_info['status']}中",
                status_code=202
            ), status_code=202)
    
    except HTTPException:
        raise
    except Exception as e:
        # 记录错误
        logger.error(f"获取任务结果异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")


@router.post('/task/{task_id}/cancel')
async def cancel_task(request: Request, task_id: str, auth: bool = Depends(token_required)):
    """
    取消任务
    
    参数:
        task_id (str): 任务ID
    """
    try:
        # 获取任务
        task_info = task_manager.get_task_info(task_id)
        
        # 检查任务是否存在
        if not task_info:
            raise HTTPException(
                status_code=404,
                detail=f"任务不存在: {task_id}"
            )
        
        # 检查任务状态
        status = task_info["status"]
        
        # 只能取消正在运行或等待中的任务
        if status not in ["pending", "running"]:
            raise HTTPException(
                status_code=400,
                detail=f"无法取消{status}状态的任务"
            )
        
        # 取消任务
        success = task_manager.cancel_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="取消任务失败"
            )
        
        return JSONResponse(content=format_success_response(
            message="任务已取消"
        ))
    
    except HTTPException:
        raise
    except Exception as e:
        # 记录错误
        logger.error(f"取消任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}") 