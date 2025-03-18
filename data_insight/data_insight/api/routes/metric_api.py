"""
指标API路由
=========

提供指标分析和指标对比相关的API端点。
"""

from flask import Blueprint, request, jsonify
import json
from datetime import datetime
import logging

from data_insight.core.metric_analyzer import MetricAnalyzer
from data_insight.core.metric_comparison_analyzer import MetricComparisonAnalyzer
from data_insight.core.text_generator import TextGenerator
from data_insight.api.middlewares.auth import require_api_token
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.utils.validator import validate_json_request, Validator
from data_insight.api.utils.response_formatter import (
    format_success_response, format_error_response
)
from data_insight.api.utils.async_task import run_async, task_manager

# 创建蓝图
bp = Blueprint('metric_api', __name__, url_prefix='/api/metric')

# 初始化分析器和生成器
metric_analyzer = MetricAnalyzer()
comparison_analyzer = MetricComparisonAnalyzer()
text_generator = TextGenerator()

# 配置日志
logger = logging.getLogger('metric_api')


# 指标分析验证模式
metric_schema = {
    "name": {
        "type": "string",
        "required": True,
        "minlength": 1,
        "maxlength": 100
    },
    "value": {
        "type": "number",
        "required": True
    },
    "previous_value": {
        "type": "number",
        "required": True
    },
    "unit": {
        "type": "string",
        "required": False
    },
    "time_period": {
        "type": "string",
        "required": False
    },
    "previous_time_period": {
        "type": "string",
        "required": False
    },
    "historical_values": {
        "type": "array",
        "items": {
            "type": "number"
        },
        "required": False
    },
    "is_positive_better": {
        "type": "boolean",
        "required": False
    }
}

# 指标对比验证模式
comparison_schema = {
    "metrics": {
        "type": "array",
        "required": True,
        "minlength": 2,
        "items": {
            "type": "object",
            "properties": metric_schema
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


@bp.route('/analyze', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(metric_schema)
def analyze_metric():
    """
    分析单个指标数据
    
    请求体应为JSON格式，包含指标数据。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到指标分析请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 分析指标
        analysis_result = metric_analyzer.analyze(data)
        
        # 生成文本解读
        text_insight = text_generator.generate_metric_insight(analysis_result)
        
        # 构建响应
        response_data = {
            "analysis": analysis_result,
            "insight": text_insight
        }
        
        # 返回结果
        return jsonify(format_success_response(
            data=response_data,
            message="指标分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"指标分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"指标分析失败: {str(e)}",
            error_code="ANALYSIS_ERROR",
            status_code=500
        )), 500


@bp.route('/analyze-async', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(metric_schema)
def analyze_metric_async():
    """
    异步分析单个指标数据
    
    请求体应为JSON格式，包含指标数据。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到异步指标分析请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建异步任务
        @run_async(timeout=60)  # 设置超时时间为60秒
        def analyze_metric_task(data):
            # 分析指标
            analysis_result = metric_analyzer.analyze(data)
            
            # 生成文本解读
            text_insight = text_generator.generate_metric_insight(analysis_result)
            
            # 构建响应
            return {
                "analysis": analysis_result,
                "insight": text_insight
            }
        
        # 启动异步任务
        task_result = analyze_metric_task(data)
        
        # 返回任务信息
        return jsonify(format_success_response(
            data=task_result,
            message="指标分析任务已提交",
            status_code=202
        )), 202
    
    except Exception as e:
        # 记录错误
        logger.error(f"提交指标分析任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"提交指标分析任务失败: {str(e)}",
            error_code="TASK_SUBMISSION_ERROR",
            status_code=500
        )), 500


@bp.route('/compare', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(comparison_schema)
def compare_metrics():
    """
    比较多个指标数据
    
    请求体应为JSON格式，包含多个指标数据。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到指标对比请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 分析指标对比
        analysis_result = comparison_analyzer.analyze(data)
        
        # 生成对比解读文本
        text_insight = text_generator.generate_metric_comparison_insight(analysis_result)
        
        # 构建响应
        response_data = {
            "analysis": analysis_result,
            "insight": text_insight
        }
        
        # 返回结果
        return jsonify(format_success_response(
            data=response_data,
            message="指标对比分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"指标对比分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"指标对比分析失败: {str(e)}",
            error_code="COMPARISON_ERROR",
            status_code=500
        )), 500


@bp.route('/compare-async', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(comparison_schema)
def compare_metrics_async():
    """
    异步比较多个指标数据
    
    请求体应为JSON格式，包含多个指标数据。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到异步指标对比请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建异步任务
        @run_async(timeout=120)  # 设置超时时间为120秒
        def compare_metrics_task(data):
            # 分析指标对比
            analysis_result = comparison_analyzer.analyze(data)
            
            # 生成对比解读文本
            text_insight = text_generator.generate_metric_comparison_insight(analysis_result)
            
            # 构建响应
            return {
                "analysis": analysis_result,
                "insight": text_insight
            }
        
        # 启动异步任务
        task_result = compare_metrics_task(data)
        
        # 返回任务信息
        return jsonify(format_success_response(
            data=task_result,
            message="指标对比分析任务已提交",
            status_code=202
        )), 202
    
    except Exception as e:
        # 记录错误
        logger.error(f"提交指标对比分析任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"提交指标对比分析任务失败: {str(e)}",
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


@bp.route('/task/<task_id>/cancel', methods=['POST'])
@require_api_token
def cancel_task(task_id):
    """
    取消任务
    
    参数:
        task_id (str): 任务ID
    """
    try:
        # 取消任务
        success = task_manager.cancel_task(task_id)
        
        if not success:
            return jsonify(format_error_response(
                message=f"取消任务 {task_id} 失败",
                error_code="TASK_CANCEL_FAILED",
                status_code=400
            )), 400
        
        # 返回成功响应
        return jsonify(format_success_response(
            data={"task_id": task_id},
            message="任务已取消"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"取消任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"取消任务失败: {str(e)}",
            error_code="TASK_CANCEL_ERROR",
            status_code=500
        )), 500 