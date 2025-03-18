"""
预测分析API路由
===========

提供时间序列预测和异常预测相关的API端点。
"""

from flask import Blueprint, request, jsonify
import json
from datetime import datetime
import logging

from data_insight.core.predictor import Predictor
from data_insight.api.middlewares.auth import require_api_token
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.utils.validator import validate_json_request, Validator
from data_insight.api.utils.response_formatter import (
    format_success_response, format_error_response
)
from data_insight.api.utils.async_task import run_async, task_manager

# 创建蓝图
bp = Blueprint('prediction_api', __name__, url_prefix='/api/prediction')

# 初始化预测器
predictor = Predictor()

# 配置日志
logger = logging.getLogger('prediction_api')


# 预测分析验证模式
prediction_schema = {
    "values": {
        "type": "array",
        "required": True,
        "minlength": 3,
        "items": {
            "type": "number"
        }
    },
    "target_periods": {
        "type": "integer",
        "required": False,
        "min": 1,
        "default": 3
    },
    "seasonality": {
        "type": "integer",
        "required": False,
        "min": 2
    },
    "confidence_level": {
        "type": "number",
        "required": False,
        "min": 0.5,
        "max": 0.99,
        "default": 0.95
    }
}

# 异常预测验证模式
anomaly_prediction_schema = {
    "values": {
        "type": "array",
        "required": True,
        "minlength": 3,
        "items": {
            "type": "number"
        }
    },
    "threshold": {
        "type": "number",
        "required": False,
        "min": 0.5,
        "max": 5.0,
        "default": 1.5
    },
    "lookback_periods": {
        "type": "integer",
        "required": False,
        "min": 1,
        "default": 3
    }
}


@bp.route('/forecast', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(prediction_schema)
def forecast():
    """
    预测未来值
    
    请求体应为JSON格式，包含历史值和预测参数。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到预测请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 预测
        prediction_result = predictor.analyze(data)
        
        # 返回结果
        return jsonify(format_success_response(
            data=prediction_result,
            message="预测分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"预测分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"预测分析失败: {str(e)}",
            error_code="PREDICTION_ERROR",
            status_code=500
        )), 500


@bp.route('/forecast-async', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(prediction_schema)
def forecast_async():
    """
    异步预测未来值
    
    请求体应为JSON格式，包含历史值和预测参数。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到异步预测请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建异步任务
        @run_async(timeout=60)  # 设置超时时间为60秒
        def forecast_task(data):
            # 预测分析
            return predictor.analyze(data)
        
        # 启动异步任务
        task_result = forecast_task(data)
        
        # 返回任务信息
        return jsonify(format_success_response(
            data=task_result,
            message="预测分析任务已提交",
            status_code=202
        )), 202
    
    except Exception as e:
        # 记录错误
        logger.error(f"提交预测分析任务异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"提交预测分析任务失败: {str(e)}",
            error_code="TASK_SUBMISSION_ERROR",
            status_code=500
        )), 500


@bp.route('/anomaly', methods=['POST'])
@require_api_token
@rate_limit
@validate_json_request
@Validator.validate_request(anomaly_prediction_schema)
def predict_anomaly():
    """
    预测异常可能性
    
    请求体应为JSON格式，包含历史值和异常检测参数。
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 记录请求
        logger.info(f"接收到异常预测请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 获取历史值
        values = data["values"]
        threshold = data.get("threshold", 1.5)
        lookback_periods = data.get("lookback_periods", 3)
        
        # 确保有足够的数据点
        if len(values) < lookback_periods + 1:
            return jsonify(format_error_response(
                message=f"历史数据点不足，至少需要 {lookback_periods + 1} 个数据点",
                error_code="INSUFFICIENT_DATA",
                status_code=400
            )), 400
        
        # 为异常预测准备数据
        forecast_data = {
            "values": values[:-1],  # 除最后一个点外的所有点
            "target_periods": 1
        }
        
        # 执行预测
        prediction_result = predictor.analyze(forecast_data)
        
        # 增加异常检测结果
        last_value = values[-1]
        predicted_value = prediction_result["预测结果"]["预测值"][0]
        confidence_intervals = prediction_result["预测结果"]["置信区间"][0]
        
        lower_bound = confidence_intervals["下限"]
        upper_bound = confidence_intervals["上限"]
        
        # 判断是否异常
        is_anomaly = last_value < lower_bound or last_value > upper_bound
        anomaly_degree = 0
        
        if is_anomaly:
            if last_value < lower_bound:
                anomaly_degree = (lower_bound - last_value) / (predicted_value - lower_bound) if predicted_value != lower_bound else 1.0
            else:
                anomaly_degree = (last_value - upper_bound) / (upper_bound - predicted_value) if upper_bound != predicted_value else 1.0
        
        # 构建结果
        anomaly_result = {
            "异常检测": {
                "是否异常": is_anomaly,
                "异常程度": min(max(anomaly_degree, 0), 5),  # 限制在0-5之间
                "当前值": last_value,
                "预期值": predicted_value,
                "预期范围": {
                    "下限": lower_bound,
                    "上限": upper_bound
                }
            },
            "预测结果": prediction_result["预测结果"]
        }
        
        # 返回结果
        return jsonify(format_success_response(
            data=anomaly_result,
            message="异常预测分析成功"
        ))
    
    except Exception as e:
        # 记录错误
        logger.error(f"异常预测分析异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"异常预测分析失败: {str(e)}",
            error_code="ANOMALY_PREDICTION_ERROR",
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
        # 获取任务
        task_info = task_manager.get_task_info(task_id)
        
        # 检查任务是否存在
        if not task_info:
            return jsonify(format_error_response(
                message=f"任务不存在: {task_id}",
                error_code="TASK_NOT_FOUND",
                status_code=404
            )), 404
        
        # 检查任务状态
        status = task_info["status"]
        
        # 根据状态返回不同的响应
        if status == "completed":
            # 获取任务结果
            result = task_manager.get_task_result(task_id)
            
            return jsonify(format_success_response(
                data=result,
                message="预测分析完成"
            ))
            
        elif status == "failed":
            # 获取错误信息
            error = task_info.get("error", "未知错误")
            
            return jsonify(format_error_response(
                message=f"预测分析失败: {error}",
                error_code="TASK_FAILED",
                status_code=500
            )), 500
            
        elif status == "timeout":
            return jsonify(format_error_response(
                message="预测分析任务超时",
                error_code="TASK_TIMEOUT",
                status_code=500
            )), 500
            
        else:  # pending or running
            return jsonify(format_success_response(
                data=task_info,
                message=f"预测分析任务{task_info['status']}中",
                status_code=202
            )), 202
    
    except Exception as e:
        # 记录错误
        logger.error(f"获取预测分析任务结果异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"获取预测分析任务结果失败: {str(e)}",
            error_code="TASK_RESULT_ERROR",
            status_code=500
        )), 500 