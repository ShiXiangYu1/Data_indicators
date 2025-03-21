"""
指标分析路由模块
==============

提供指标分析相关的API端点。
"""

from flask import request, jsonify
from data_insight.services import MetricService
from data_insight.api.routes.metric import bp
from data_insight.api.validation import validate_request_json
from data_insight.api.error_handling import handle_exceptions, APIError

# 创建服务实例
metric_service = MetricService()

@bp.route('/analyze', methods=['POST'])
@validate_request_json(['metric_data'])
@handle_exceptions
def analyze_metric():
    """分析单个指标的API端点
    
    接受包含指标数据的JSON请求，返回分析结果
    ---
    tags:
      - 指标分析
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - metric_data
          properties:
            metric_data:
              type: object
              description: 指标数据
              required:
                - name
                - value
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
                historical_values:
                  type: array
                  description: 历史值列表
                  items:
                    type: number
            context:
              type: object
              description: 附加上下文信息(可选)
    responses:
      200:
        description: 分析结果
      400:
        description: 无效的请求数据
      500:
        description: 服务器错误
    """
    data = request.json
    metric_data = data.get('metric_data')
    context = data.get('context', {})
    
    try:
        # 验证指标数据
        metric_service.validate_metric_data(metric_data)
    except ValueError as e:
        raise APIError(str(e), 400)
    
    # 分析指标
    result = metric_service.analyze_metric(metric_data, context)
    
    return jsonify(result)

@bp.route('/predict', methods=['POST'])
@validate_request_json(['metric_data'])
@handle_exceptions
def predict_metric():
    """预测指标未来值的API端点
    
    接受包含指标数据的JSON请求，返回预测结果
    ---
    tags:
      - 指标预测
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - metric_data
          properties:
            metric_data:
              type: object
              description: 指标数据
              required:
                - name
                - historical_values
              properties:
                name:
                  type: string
                  description: 指标名称
                historical_values:
                  type: array
                  description: 历史值列表
                  items:
                    type: number
                unit:
                  type: string
                  description: 度量单位
            horizon:
              type: integer
              description: 预测步长
              default: 7
            confidence_level:
              type: number
              description: 置信水平
              default: 0.95
    responses:
      200:
        description: 预测结果
      400:
        description: 无效的请求数据
      500:
        description: 服务器错误
    """
    data = request.json
    metric_data = data.get('metric_data')
    horizon = data.get('horizon', 7)
    confidence_level = data.get('confidence_level', 0.95)
    
    try:
        # 验证指标数据
        metric_service.validate_metric_data(metric_data)
        
        # 验证必须包含历史值
        if 'historical_values' not in metric_data or not metric_data['historical_values']:
            raise ValueError("预测必须提供历史值数据")
        
        # 验证预测参数
        if not isinstance(horizon, int) or horizon < 1:
            raise ValueError("预测步长必须是大于0的整数")
        
        if not isinstance(confidence_level, (int, float)) or not 0 < confidence_level < 1:
            raise ValueError("置信水平必须是0到1之间的小数")
    except ValueError as e:
        raise APIError(str(e), 400)
    
    # 执行预测
    result = metric_service.predict_metric(metric_data, horizon, confidence_level)
    
    return jsonify(result)

@bp.route('/clear-cache', methods=['POST'])
@handle_exceptions
def clear_analysis_cache():
    """清除指标分析缓存
    
    清除服务中存储的指标分析缓存数据
    ---
    tags:
      - 指标分析
    responses:
      200:
        description: 缓存清除成功
      500:
        description: 服务器错误
    """
    metric_service.invalidate_cache()
    return jsonify({
        'status': 'success',
        'message': '指标分析缓存已清除'
    }) 