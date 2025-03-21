"""
指标对比路由模块
==============

提供指标对比相关的API端点。
"""

from flask import request, jsonify
from data_insight.services import MetricService
from data_insight.api.routes.metric import bp
from data_insight.api.validation import validate_request_json
from data_insight.api.error_handling import handle_exceptions, APIError

# 创建服务实例
metric_service = MetricService()

@bp.route('/compare', methods=['POST'])
@validate_request_json(['metrics'])
@handle_exceptions
def compare_metrics():
    """对比多个指标的API端点
    
    接受包含多个指标数据的JSON请求，返回对比分析结果
    ---
    tags:
      - 指标对比
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - metrics
          properties:
            metrics:
              type: array
              description: 指标数据数组
              minItems: 2
              items:
                type: object
                required:
                  - name
                  - value
                  - metric_id
                properties:
                  name:
                    type: string
                    description: 指标名称
                  value:
                    type: number
                    description: 指标当前值
                  previous_value:
                    type: number
                    description: 指标前期值
                  unit:
                    type: string
                    description: 度量单位
                  time_period:
                    type: string
                    description: 时间周期
                  previous_time_period:
                    type: string
                    description: 前期时间周期
                  metric_id:
                    type: string
                    description: 指标唯一标识
                  historical_values:
                    type: array
                    description: 历史值列表
                    items:
                      type: number
            comparison_type:
              type: string
              description: 对比类型(可选，默认为general)
              enum: [general, correlation, trend, performance]
            context:
              type: object
              description: 附加上下文信息(可选)
    responses:
      200:
        description: 对比分析结果
      400:
        description: 无效的请求数据
      500:
        description: 服务器错误
    """
    data = request.json
    metrics = data.get('metrics', [])
    comparison_type = data.get('comparison_type', 'general')
    context = data.get('context', {})
    
    # 检查指标数量
    if len(metrics) < 2:
        raise APIError('对比至少需要2个指标', 400)
    
    # 验证每个指标
    for metric in metrics:
        try:
            metric_service.validate_metric_data(metric)
        except ValueError as e:
            raise APIError(f'指标数据格式无效: {metric.get("metric_id", "未知")}, {str(e)}', 400)
    
    # 验证对比类型
    valid_comparison_types = ['general', 'correlation', 'trend', 'performance']
    if comparison_type not in valid_comparison_types:
        raise APIError(f'不支持的对比类型: {comparison_type}, 有效类型: {", ".join(valid_comparison_types)}', 400)
    
    # 添加对比类型到上下文
    context['comparison_type'] = comparison_type
    
    # 准备对比数据
    metrics_data = {
        'metrics': metrics
    }
    
    # 进行指标对比
    result = metric_service.compare_metrics(metrics_data, context)
    
    return jsonify(result)

@bp.route('/correlation', methods=['POST'])
@validate_request_json(['metrics'])
@handle_exceptions
def analyze_correlation():
    """分析多个指标之间相关性的API端点
    
    接受包含多个指标数据的JSON请求，返回相关性分析结果
    ---
    tags:
      - 指标对比
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - metrics
          properties:
            metrics:
              type: array
              description: 指标数据数组
              minItems: 2
              items:
                type: object
                required:
                  - name
                  - historical_values
                  - metric_id
                properties:
                  name:
                    type: string
                    description: 指标名称
                  historical_values:
                    type: array
                    description: 历史值列表
                    items:
                      type: number
                  metric_id:
                    type: string
                    description: 指标唯一标识
            context:
              type: object
              description: 附加上下文信息(可选)
    responses:
      200:
        description: 相关性分析结果
      400:
        description: 无效的请求数据
      500:
        description: 服务器错误
    """
    data = request.json
    metrics = data.get('metrics', [])
    context = data.get('context', {})
    
    # 检查指标数量
    if len(metrics) < 2:
        raise APIError('相关性分析至少需要2个指标', 400)
    
    # 验证每个指标
    for metric in metrics:
        # 确保有历史值
        if 'historical_values' not in metric or not isinstance(metric['historical_values'], list) or len(metric['historical_values']) < 3:
            raise APIError(f'指标 {metric.get("name", "未知")} 缺少足够的历史数据进行相关性分析，至少需要3个数据点', 400)
        
        try:
            metric_service.validate_metric_data(metric)
        except ValueError as e:
            raise APIError(f'指标数据格式无效: {metric.get("metric_id", "未知")}, {str(e)}', 400)
    
    # 设置对比类型为相关性分析
    context['comparison_type'] = 'correlation'
    
    # 准备对比数据
    metrics_data = {
        'metrics': metrics
    }
    
    # 进行指标相关性分析
    result = metric_service.compare_metrics(metrics_data, context)
    
    return jsonify(result) 