"""
Web页面路由
=========

定义Web界面的各个页面路由。
"""

import os
import json
import logging
from flask import render_template, redirect, url_for, request, jsonify, current_app

from data_insight.web import web_bp
from data_insight.api.utils.response_formatter import format_success_response, format_error_response

# 配置日志
logger = logging.getLogger(__name__)


@web_bp.route('/')
def index():
    """
    首页
    
    展示数据指标平台的概览和主要功能入口。
    """
    return render_template(
        'index.html',
        title='数据指标平台',
        page='index'
    )


@web_bp.route('/metric-analysis')
def metric_analysis():
    """
    指标分析页面
    
    提供单个指标分析功能，包括变化分析、异常检测等。
    """
    return render_template(
        'metric_analysis.html',
        title='指标分析 - 数据指标平台',
        page='metric_analysis'
    )


@web_bp.route('/chart-analysis')
def chart_analysis():
    """
    图表分析页面
    
    提供图表分析功能，支持线图和柱状图的分析。
    """
    return render_template(
        'chart_analysis.html',
        title='图表分析 - 数据指标平台',
        page='chart_analysis'
    )


@web_bp.route('/comparison-analysis')
def comparison_analysis():
    """
    对比分析页面
    
    提供多个指标的对比分析功能。
    """
    return render_template(
        'comparison_analysis.html',
        title='对比分析 - 数据指标平台',
        page='comparison_analysis'
    )


@web_bp.route('/root-cause-analysis')
def root_cause_analysis():
    """
    根因分析页面
    
    提供指标变化的根因分析功能。
    """
    return render_template(
        'root_cause_analysis.html',
        title='根因分析 - 数据指标平台',
        page='root_cause_analysis'
    )


@web_bp.route('/prediction-analysis')
def prediction_analysis():
    """
    预测分析页面
    
    提供基于历史数据的预测分析功能。
    """
    return render_template(
        'prediction_analysis.html',
        title='预测分析 - 数据指标平台',
        page='prediction_analysis'
    )


@web_bp.route('/suggestion-analysis')
def suggestion_analysis():
    """
    建议分析页面
    
    基于多维度分析结果，提供改进建议。
    """
    return render_template(
        'suggestion_analysis.html',
        title='建议分析 - 数据指标平台',
        page='suggestion_analysis'
    )


@web_bp.route('/api-proxy/<path:endpoint>', methods=['GET', 'POST'])
def api_proxy(endpoint):
    """
    API代理
    
    将前端请求代理到后端API，避免跨域问题。
    
    参数:
        endpoint (str): API端点路径
    """
    try:
        # 获取请求方法和参数
        method = request.method
        api_url = f"/api/{endpoint}"
        
        # 获取API令牌
        api_token = current_app.config.get('API_TOKEN')
        
        # 转发请求到API
        if method == 'GET':
            # 对于GET请求，通过Flask的request.args获取查询参数
            args = request.args.to_dict()
            
            # 记录请求
            logger.info(f"代理GET请求: {api_url}, 参数: {args}")
            
            # 构造新请求的环境
            environ = request.environ.copy()
            environ['PATH_INFO'] = api_url
            environ['QUERY_STRING'] = request.query_string.decode('utf-8')
            
            # 如果有API令牌，添加到请求头
            if api_token:
                environ['HTTP_X_API_TOKEN'] = api_token
            
            # 创建请求对象
            api_request = current_app.request_class(environ)
            
            # 分发请求到Flask应用
            response = current_app.full_dispatch_request()
            
        elif method == 'POST':
            # 对于POST请求，获取JSON数据
            data = request.get_json() if request.is_json else {}
            
            # 记录请求
            logger.info(f"代理POST请求: {api_url}, 数据: {json.dumps(data, ensure_ascii=False)[:500]}")
            
            # 构造新请求的环境
            environ = request.environ.copy()
            environ['PATH_INFO'] = api_url
            environ['CONTENT_TYPE'] = 'application/json'
            
            # 如果有API令牌，添加到请求头
            if api_token:
                environ['HTTP_X_API_TOKEN'] = api_token
            
            # 创建请求对象
            api_request = current_app.request_class(environ)
            api_request.data = json.dumps(data).encode('utf-8')
            
            # 分发请求到Flask应用
            response = current_app.full_dispatch_request()
        
        else:
            # 不支持的HTTP方法
            return jsonify(format_error_response(
                message=f"不支持的HTTP方法: {method}",
                error_code="METHOD_NOT_ALLOWED",
                status_code=405
            )), 405
        
        return response
    
    except Exception as e:
        # 记录错误
        logger.error(f"API代理异常: {str(e)}", exc_info=True)
        
        # 返回错误响应
        return jsonify(format_error_response(
            message=f"API请求失败: {str(e)}",
            error_code="PROXY_ERROR",
            status_code=500
        )), 500


@web_bp.route('/sample-data')
def sample_data():
    """
    获取示例数据
    
    提供示例数据用于演示。
    """
    # 定义各种示例数据
    data = {
        "metric": {
            "name": "月度销售额",
            "value": 1250000,
            "previous_value": 1000000,
            "unit": "元",
            "time_period": "2023年7月",
            "previous_time_period": "2023年6月",
            "historical_values": [920000, 980000, 950000, 1010000, 1000000],
            "is_positive_better": True
        },
        "comparison": {
            "metrics": [
                {
                    "name": "销售额",
                    "values": [980000, 1010000, 1000000, 1250000],
                    "unit": "元",
                    "time_periods": ["2023年4月", "2023年5月", "2023年6月", "2023年7月"]
                },
                {
                    "name": "客户数",
                    "values": [3200, 3300, 3180, 3850],
                    "unit": "人",
                    "time_periods": ["2023年4月", "2023年5月", "2023年6月", "2023年7月"]
                }
            ],
            "include_correlation": True
        },
        "chart": {
            "chart_type": "line",
            "title": "月度销售额趋势",
            "data": {
                "x_axis": {
                    "label": "月份",
                    "values": ["2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月", "2023年7月"]
                },
                "y_axis": {
                    "label": "销售额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [920000, 980000, 950000, 1010000, 1000000, 1250000]
                        }
                    ]
                }
            }
        },
        "bar_chart": {
            "chart_type": "bar",
            "title": "各产品销售额",
            "data": {
                "x_axis": {
                    "label": "产品",
                    "values": ["产品A", "产品B", "产品C", "产品D", "产品E"]
                },
                "y_axis": {
                    "label": "销售额(元)",
                    "series": [
                        {
                            "name": "销售额",
                            "values": [450000, 380000, 250000, 120000, 50000]
                        }
                    ]
                }
            }
        },
        "root_cause": {
            "target": "销售额",
            "target_values": [980000, 1010000, 1000000, 1250000],
            "factors": {
                "客户数": [3200, 3300, 3180, 3850],
                "客单价": [306.25, 306.06, 314.47, 324.68],
                "广告投入": [150000, 155000, 160000, 200000],
                "促销活动数": [2, 3, 2, 4]
            },
            "subfactors": {
                "客户数": {
                    "新客户": [800, 850, 780, 1200],
                    "回头客": [2400, 2450, 2400, 2650]
                }
            },
            "known_relationships": [
                {
                    "from": "广告投入",
                    "to": "新客户",
                    "type": "direct",
                    "strength": 0.7
                },
                {
                    "from": "促销活动数",
                    "to": "客单价",
                    "type": "inverse",
                    "strength": 0.5
                }
            ]
        },
        "prediction": {
            "values": [980000, 1010000, 1000000, 1250000],
            "target_periods": 3,
            "confidence_level": 0.95
        }
    }
    
    # 返回所有示例数据
    return jsonify(format_success_response(
        data=data,
        message="示例数据获取成功"
    )) 