"""
图表分析路由模块
==============

提供图表分析相关的API端点。
"""

from flask import request, jsonify
from data_insight.services import ChartService
from data_insight.api.routes.chart import bp
from data_insight.api.validation import validate_request_json
from data_insight.api.error_handling import handle_exceptions

# 创建服务实例
chart_service = ChartService()

@bp.route('/analyze', methods=['POST'])
@validate_request_json(['chart_data', 'chart_type'])
@handle_exceptions
def analyze_chart():
    """分析单个图表的API端点
    
    接受包含图表数据和图表类型的JSON请求，返回分析结果
    ---
    tags:
      - 图表分析
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - chart_data
            - chart_type
          properties:
            chart_data:
              type: object
              description: 图表数据
            chart_type:
              type: string
              description: 图表类型(line, bar, scatter, pie)
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
    chart_data = data.get('chart_data')
    chart_type = data.get('chart_type')
    context = data.get('context', {})
    
    # 验证图表类型
    if chart_type not in chart_service.get_supported_chart_types():
        return jsonify({
            'error': f'不支持的图表类型: {chart_type}',
            'supported_types': chart_service.get_supported_chart_types()
        }), 400
    
    # 验证图表数据
    if not chart_service.validate_chart_data(chart_data, chart_type):
        return jsonify({
            'error': '图表数据格式无效'
        }), 400
    
    # 分析图表
    result = chart_service.analyze_chart(chart_data, chart_type, context)
    
    return jsonify(result)

@bp.route('/types', methods=['GET'])
@handle_exceptions
def get_chart_types():
    """获取支持的图表类型
    
    返回当前系统支持分析的所有图表类型
    ---
    tags:
      - 图表分析
    responses:
      200:
        description: 支持的图表类型列表
    """
    return jsonify({
        'supported_types': chart_service.get_supported_chart_types()
    })

@bp.route('/clear-cache', methods=['POST'])
@handle_exceptions
def clear_analysis_cache():
    """清除图表分析缓存
    
    清除服务中存储的分析缓存数据
    ---
    tags:
      - 图表分析
    responses:
      200:
        description: 缓存清除成功
      500:
        description: 服务器错误
    """
    chart_service.invalidate_cache()
    return jsonify({
        'status': 'success',
        'message': '图表分析缓存已清除'
    })