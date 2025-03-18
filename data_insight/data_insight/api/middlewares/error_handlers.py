"""
错误处理中间件
===========

定义API错误处理函数。
"""

from flask import jsonify


def register_error_handlers(app):
    """
    注册错误处理函数
    
    参数:
        app (Flask): Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(e):
        """处理400错误"""
        return jsonify({
            "error": "请求参数错误",
            "message": str(e),
            "status_code": 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        """处理401错误"""
        return jsonify({
            "error": "未授权访问",
            "message": str(e),
            "status_code": 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        """处理403错误"""
        return jsonify({
            "error": "禁止访问",
            "message": str(e),
            "status_code": 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(e):
        """处理404错误"""
        return jsonify({
            "error": "请求的资源不存在",
            "message": str(e),
            "status_code": 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """处理405错误"""
        return jsonify({
            "error": "请求方法不允许",
            "message": str(e),
            "status_code": 405
        }), 405
    
    @app.errorhandler(429)
    def too_many_requests(e):
        """处理429错误"""
        return jsonify({
            "error": "请求频率过高",
            "message": str(e),
            "status_code": 429
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """处理500错误"""
        return jsonify({
            "error": "服务器内部错误",
            "message": str(e),
            "status_code": 500
        }), 500 