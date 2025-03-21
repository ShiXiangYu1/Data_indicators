"""
图表对比路由模块
==============

提供图表对比相关的API端点。
"""

from flask import request, jsonify
from data_insight.services import ChartService
from data_insight.api.routes.chart import bp
from data_insight.api.validation import validate_request_json
from data_insight.api.error_handling import handle_exceptions

# 创建服务实例
chart_service = ChartService()

@bp.route('/compare', methods=['POST'])
@validate_request_json(['charts'])
@handle_exceptions
def compare_charts():
    """对比多个图表的API端点
    
    接受包含多个图表数据的JSON请求，返回对比分析结果
    ---
    tags:
      - 图表对比
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - charts
          properties:
            charts:
              type: array
              description: 图表数据数组
              items:
                type: object
                required:
                  - chart_data
                  - chart_type
                  - chart_id
                properties:
                  chart_data:
                    type: object
                    description: 图表数据
                  chart_type:
                    type: string
                    description: 图表类型
                  chart_id:
                    type: string
                    description: 图表唯一标识
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
    charts = data.get('charts', [])
    context = data.get('context', {})
    
    # 检查图表数量
    if len(charts) < 2:
        return jsonify({
            'error': '对比至少需要2个图表'
        }), 400
    
    # 验证每个图表
    for chart in charts:
        chart_type = chart.get('chart_type')
        chart_data = chart.get('chart_data')
        
        # 验证图表类型
        if chart_type not in chart_service.get_supported_chart_types():
            return jsonify({
                'error': f'不支持的图表类型: {chart_type}',
                'supported_types': chart_service.get_supported_chart_types()
            }), 400
        
        # 验证图表数据
        if not chart_service.validate_chart_data(chart_data, chart_type):
            return jsonify({
                'error': f'图表数据格式无效: {chart.get("chart_id", "未知")}'
            }), 400
    
    # 进行图表对比
    result = chart_service.compare_charts(charts, context)
    
    return jsonify(result) 