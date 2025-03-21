"""
API模块
======

提供API服务的创建和初始化功能。
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS

from data_insight.config import settings
from data_insight.api.error_handling import register_error_handlers
from data_insight.services import init_services

# 获取日志记录器
logger = logging.getLogger(__name__)

# API端点信息 (从docs.py移植过来)
API_ENDPOINTS = {
    "trend": {
        "title": "趋势分析API",
        "description": "分析时间序列数据的变化趋势，识别上升、下降、周期性和季节性模式。",
        "endpoints": [
            {
                "path": "/api/v1/trend/analyze",
                "method": "POST",
                "summary": "分析时间序列数据的变化趋势"
            },
            {
                "path": "/api/v1/trend/analyze-async",
                "method": "POST",
                "summary": "异步分析时间序列数据的变化趋势"
            }
        ],
        "doc_url": "/api/docs/trend"
    },
    "attribution": {
        "title": "归因分析API",
        "description": "分析指标变化的归因因素，确定哪些因素对指标变化贡献最大。",
        "endpoints": [
            {
                "path": "/api/v1/attribution",
                "method": "POST",
                "summary": "分析指标变化的归因因素"
            },
            {
                "path": "/api/v1/attribution-async",
                "method": "POST",
                "summary": "异步分析指标变化的归因因素"
            }
        ],
        "doc_url": "/api/docs/attribution"
    },
    "root-cause": {
        "title": "根因分析API",
        "description": "深入挖掘指标变化的根本原因，通过多层次因果分析找出深层次原因。",
        "endpoints": [
            {
                "path": "/api/v1/root-cause",
                "method": "POST",
                "summary": "分析指标变化的根本原因"
            },
            {
                "path": "/api/v1/root-cause-async",
                "method": "POST",
                "summary": "异步分析指标变化的根本原因"
            }
        ],
        "doc_url": "/api/docs/root-cause"
    },
    "correlation": {
        "title": "相关性分析API",
        "description": "分析指标之间的相关性，识别强相关、弱相关和无相关的指标对。",
        "endpoints": [
            {
                "path": "/api/v1/correlation",
                "method": "POST",
                "summary": "分析指标之间的相关性"
            },
            {
                "path": "/api/v1/correlation-async",
                "method": "POST",
                "summary": "异步分析指标之间的相关性"
            }
        ],
        "doc_url": "/api/docs/correlation"
    },
    "prediction": {
        "title": "预测分析API",
        "description": "预测指标的未来走势，支持时间序列预测和异常检测。",
        "endpoints": [
            {
                "path": "/api/v1/forecast",
                "method": "POST",
                "summary": "预测指标未来值"
            },
            {
                "path": "/api/v1/forecast-async",
                "method": "POST",
                "summary": "异步预测指标未来值"
            },
            {
                "path": "/api/v1/anomaly",
                "method": "POST",
                "summary": "检测时间序列中的异常值"
            },
            {
                "path": "/api/v1/anomaly-async",
                "method": "POST",
                "summary": "异步检测时间序列中的异常值"
            }
        ],
        "doc_url": "/api/docs/prediction"
    },
    "metric": {
        "title": "指标分析API",
        "description": "分析单个指标的特征和变化，并比较多个指标之间的差异和关系。",
        "endpoints": [
            {
                "path": "/api/v1/analyze",
                "method": "POST",
                "summary": "分析单个指标的特征和变化"
            },
            {
                "path": "/api/v1/analyze-async",
                "method": "POST",
                "summary": "异步分析单个指标的特征和变化"
            },
            {
                "path": "/api/v1/compare",
                "method": "POST",
                "summary": "比较多个指标之间的差异和关系"
            }
        ],
        "doc_url": "/api/docs/metric"
    },
    "chart": {
        "title": "图表分析API",
        "description": "分析图表数据，自动生成适合数据特征的可视化图表。",
        "endpoints": [
            {
                "path": "/api/v1/chart/analyze",
                "method": "POST",
                "summary": "分析图表数据"
            },
            {
                "path": "/api/v1/chart/generate",
                "method": "POST",
                "summary": "生成可视化图表"
            }
        ],
        "doc_url": "/api/docs/chart"
    }
}

def create_app(config=None, register_routes=True):
    """
    创建Flask应用实例
    
    参数:
        config (dict, optional): 自定义配置
        register_routes (bool, optional): 是否注册路由，默认为True
        
    返回:
        Flask: Flask应用实例
    """
    app = Flask(__name__)
    
    # 允许跨域请求
    CORS(app)
    
    # 配置应用
    app.config.update(
        DEBUG=settings.debug,
        SECRET_KEY=settings.__dict__.get('secret_key', 'data_insight_default_key')
    )
    
    # 应用自定义配置
    if config is not None:
        app.config.update(config)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 初始化服务
    init_services()
    
    # 注册路由
    if register_routes:
        register_blueprints(app)
    
    logger.info("Flask应用创建完成")
    
    @app.route('/api/health')
    def health_check():
        """健康检查端点"""
        return {"status": "ok", "version": settings.version}
    
    @app.route('/api/docs')
    def api_docs():
        """API文档首页"""
        # 获取所有已注册的路由
        flask_routes = []
        for rule in app.url_map.iter_rules():
            # 排除静态资源和内部路由
            if not rule.endpoint.startswith('static') and not rule.rule.startswith('/static'):
                methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
                flask_routes.append({
                    "path": rule.rule,
                    "methods": methods,
                    "endpoint": rule.endpoint
                })
        
        # 按路径排序
        flask_routes.sort(key=lambda x: x["path"])
        
        # 返回API文档信息
        return jsonify({
            "success": True,
            "message": "数据指标分析API文档",
            "data": {
                "title": "数据指标分析API文档",
                "version": settings.version,
                "description": "提供数据指标分析相关的API，包括趋势分析、归因分析、根因分析、相关性分析、预测分析和指标分析。",
                "base_url": "/api",
                "registered_routes": flask_routes,
                "apis": API_ENDPOINTS
            }
        })
    
    @app.route('/api/docs/<api_name>')
    def api_specific_docs(api_name):
        """获取特定API的详细文档信息"""
        if api_name not in API_ENDPOINTS:
            return jsonify({
                "success": False,
                "message": f"未找到API: {api_name}",
                "error": "NOT_FOUND"
            }), 404
        
        return jsonify({
            "success": True,
            "message": f"{API_ENDPOINTS[api_name]['title']}文档",
            "data": API_ENDPOINTS[api_name]
        })
    
    @app.route('/api/docs/endpoints')
    def endpoints_list():
        """获取所有API端点列表"""
        all_endpoints = []
        
        for api_group in API_ENDPOINTS.values():
            all_endpoints.extend(api_group["endpoints"])
        
        return jsonify({
            "success": True,
            "message": "API端点列表",
            "data": {
                "total": len(all_endpoints),
                "endpoints": all_endpoints
            }
        })
    
    return app

def register_blueprints(app):
    """
    注册蓝图路由
    
    参数:
        app (Flask): Flask应用实例
    """
    logger.info("注册API路由...")
    
    # 导入蓝图
    from data_insight.api.routes.metric import bp as metric_bp
    from data_insight.api.routes.chart import bp as chart_bp
    from data_insight.api.routes.api_docs import bp as api_docs_bp

    # 注册蓝图
    app.register_blueprint(metric_bp)
    app.register_blueprint(chart_bp)
    app.register_blueprint(api_docs_bp)
    
    # 如果以后还有更多蓝图，在这里继续注册
    # app.register_blueprint(analysis_bp)
    # app.register_blueprint(prediction_bp)
    # app.register_blueprint(recommendation_bp)
    
    logger.info("API路由注册完成") 