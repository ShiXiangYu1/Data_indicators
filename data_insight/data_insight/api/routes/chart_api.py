"""
图表API路由
=========

提供图表分析相关的API端点。
"""

from flask import Blueprint, request, jsonify
import json
from datetime import datetime
import logging

from data_insight.core.chart_analyzer import ChartAnalyzer
from data_insight.core.text_generator import TextGenerator
from data_insight.api.middlewares.auth import require_api_token
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.utils.validator import validate_json_request, Validator
from data_insight.api.utils.response_formatter import (
    format_success_response, format_error_response
)
from data_insight.api.utils.async_task import run_async, task_manager

# 创建蓝图
bp = Blueprint('chart_api', __name__, url_prefix='/api/chart')

# 初始化分析器和生成器
chart_analyzer = ChartAnalyzer()
text_generator = TextGenerator()

# 配置日志
logger = logging.getLogger('chart_api')


# 图表分析验证模式
chart_data_schema = {
    "x_axis": {
        "type": "object",
        "required": True,
        "properties": {
            "label": {
                "type": "string",
                "required": False
            },
            "values": {
                "type": "array",
                "required": True,
                "minlength": 1
            }
        }
    },
    "y_axis": {
        "type": "object",
        "required": True,
        "properties": {
            "label": {
                "type": "string",
                "required": False
            },
            "series": {
                "type": "array",
                "required": True,
                "minlength": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "required": True
                        },
                        "values": {
                            "type": "array",
                            "required": True,
                            "minlength": 1
                        }
                    }
                }
            }
        }
    }
}

chart_schema = {
    "chart_id": {
        "type": "string",
        "required": False
    },
    "chart_type": {
        "type": "string",
        "required": True,
        "enum": ["line", "bar", "pie", "scatter"]
    },
    "title": {
        "type": "string",
        "required": False
    },
    "data": {
        "type": "object",
        "required": True,
        "properties": chart_data_schema
    }
}


@bp.route('/analyze', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(chart_schema)
def analyze_chart():
    """
    分析图表数据
    
    请求体应为JSON格式，包含图表数据。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到图表分析请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 分析图表
        analysis_result = chart_analyzer.analyze(data)
        
        # 生成图表解读文本
        chart_type = data.get("chart_type", "").lower()
        text_insight = ""
        
        if chart_type == "line":
            text_insight = text_generator.generate_line_chart_insight(analysis_result, data)
        elif chart_type == "bar":
            text_insight = text_generator.generate_bar_chart_insight(analysis_result, data)
        else:
            text_insight = "暂不支持的图表类型，无法生成解读。"
        
        # 构建响应
        response_data = {
            "analysis": analysis_result,
            "insight": text_insight
        }
        
        # 返回结果
        return jsonify(format_success_response(
            data=response_data,
            message="图表分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"图表分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"图表分析失败: {str(e)}",
            error_code="ANALYSIS_ERROR",
            status_code=500
        )), 500


@bp.route('/analyze-async', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(chart_schema)
def analyze_chart_async():
    """
    异步分析图表数据
    
    请求体应为JSON格式，包含图表数据。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到异步图表分析请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建异步任务
        @run_async(timeout=90)  # 设置超时时间为90秒
        def analyze_chart_task(data):
            # 分析图表
            analysis_result = chart_analyzer.analyze(data)
            
            # 生成图表解读文本
            chart_type = data.get("chart_type", "").lower()
            text_insight = ""
            
            if chart_type == "line":
                text_insight = text_generator.generate_line_chart_insight(analysis_result, data)
            elif chart_type == "bar":
                text_insight = text_generator.generate_bar_chart_insight(analysis_result, data)
            else:
                text_insight = "暂不支持的图表类型，无法生成解读。"
            
            # 构建响应
            return {
                "analysis": analysis_result,
                "insight": text_insight
            }
        
        # 启动异步任务
        task_result = analyze_chart_task(data)
        
        # 返回任务信息
        return jsonify(format_success_response(
            data=task_result,
            message="图表分析任务已提交",
            status_code=202
        )), 202
    
    except Exception as e:
        # 记录错误
        logger.error(f"提交图表分析任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"提交图表分析任务失败: {str(e)}",
            error_code="TASK_SUBMISSION_ERROR",
            status_code=500
        )), 500


@bp.route('/task/<task_id>', methods=['GET'])
@require_api_token
def get_task_result(task_id):
    """
    获取任务结果
    
    参数:
        task_id (str): 任务ID
    """
    try:
        # 获取任务信息
        task_info = task_manager.get_task_info(task_id)
        if not task_info:
            return jsonify(format_error_response(
                message=f"任务 {task_id} 不存在",
                error_code="TASK_NOT_FOUND",
                status_code=404
            )), 404
        
        # 获取任务结果
        completed, result, error = task_manager.get_task_result(task_id)
        
        if not completed:
            # 任务仍在处理中
            return jsonify(format_success_response(
                data={
                    "task_id": task_id,
                    "status": task_info["status"],
                    "start_time": task_info["start_time"],
                    "message": error or "任务正在处理中"
                },
                message="任务正在处理中",
                status_code=202
            )), 202
        
        if error:
            # 任务失败
            return jsonify(format_error_response(
                message=f"任务执行失败: {error}",
                error_code="TASK_EXECUTION_ERROR",
                status_code=500
            )), 500
        
        # 任务成功
        return jsonify(format_success_response(
            data={
                "task_id": task_id,
                "status": task_info["status"],
                "start_time": task_info["start_time"],
                "end_time": task_info["end_time"],
                "duration": task_info["duration"],
                "result": result
            },
            message="任务已完成"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"获取任务结果异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"获取任务结果失败: {str(e)}",
            error_code="TASK_RESULT_ERROR",
            status_code=500
        )), 500 