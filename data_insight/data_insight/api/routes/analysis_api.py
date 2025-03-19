#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析API路由
===========

提供数据指标分析相关的API路由，包括原因分析、归因分析和根因分析等功能。
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, Unauthorized

from data_insight.core.reason_analyzer import ReasonAnalyzer
from data_insight.core.attribution_analyzer import AttributionAnalyzer
from data_insight.core.root_cause_analyzer import RootCauseAnalyzer
from data_insight.core.correlation_analyzer import CorrelationAnalyzer
from data_insight.models.insight_model import AnalysisResult
from data_insight.api.utils.response_formatter import format_success_response, format_error_response
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.middlewares.auth import token_required

# 创建蓝图
bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


@bp.route('/reason', methods=['POST'])
@rate_limit
@token_required
def analyze_reason():
    """
    原因分析API
    
    分析指标变化的可能原因，基于历史数据和相关指标
    
    请求体:
    {
        "metric_name": "用户活跃度",
        "metric_value": 65000,
        "previous_value": 70000,
        "comparison_period": "环比",
        "time_period": "2023-07",
        "dimensions": [
            {"name": "渠道", "value": "自然流量"},
            {"name": "用户类型", "value": "新用户"}
        ],
        "related_metrics": [
            {
                "name": "广告支出",
                "value": 50000,
                "previous_value": 60000
            }
        ],
        "context": {
            "industry": "电商",
            "season": "夏季"
        },
        "analysis_depth": "standard"
    }
    
    返回:
    {
        "success": true,
        "data": {
            "reasons": [
                {
                    "reason": "广告支出减少导致新用户减少",
                    "confidence": 0.85,
                    "impact": 0.65,
                    "evidence": [
                        "广告支出减少了16.7%",
                        "广告支出与新用户活跃度呈正相关"
                    ]
                }
            ],
            "summary": "用户活跃度下降主要受广告支出减少影响",
            "analysis_id": "ra-20230725-001"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证必要字段
        required_fields = ["metric_name", "metric_value", "previous_value"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"缺少必要字段: {field}")
        
        # 创建分析器实例
        analyzer = ReasonAnalyzer()
        
        # 设置分析深度
        analysis_depth = data.get("analysis_depth", "standard")
        if analysis_depth not in ["basic", "standard", "advanced"]:
            analysis_depth = "standard"
        
        # 执行分析
        result = analyzer.analyze(
            metric_name=data["metric_name"],
            current_value=data["metric_value"],
            previous_value=data["previous_value"],
            time_period=data.get("time_period"),
            dimensions=data.get("dimensions", []),
            related_metrics=data.get("related_metrics", []),
            context=data.get("context", {}),
            analysis_depth=analysis_depth
        )
        
        # 生成分析ID
        analysis_id = f"ra-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 格式化响应
        response_data = {
            "reasons": result.reasons,
            "summary": result.summary,
            "analysis_id": analysis_id
        }
        
        return jsonify(format_success_response(
            data=response_data,
            message="原因分析完成"
        ))
    
    except Exception as e:
        current_app.logger.error(f"原因分析API错误: {str(e)}")
        return jsonify(format_error_response(
            message=f"分析过程中发生错误: {str(e)}",
            status_code=500
        )), 500


@bp.route('/attribution', methods=['POST'])
@rate_limit
@token_required
def analyze_attribution():
    """
    归因分析API
    
    分析指标变化的归因因素，基于历史数据和多维度因素
    
    请求体:
    {
        "metric_name": "转化率",
        "metric_value": 3.2,
        "previous_value": 2.8,
        "time_period": "2023-07",
        "factors": [
            {"name": "页面优化", "value": "已实施"},
            {"name": "促销活动", "value": "双11活动"},
            {"name": "产品更新", "value": "V2.5发布"}
        ],
        "data_points": [
            {"date": "2023-07-01", "value": 3.0, "factors": {...}},
            {"date": "2023-07-02", "value": 3.1, "factors": {...}}
        ],
        "attribution_method": "shapley",
        "confidence_level": 0.95
    }
    
    返回:
    {
        "success": true,
        "data": {
            "attributions": [
                {
                    "factor": "页面优化",
                    "contribution": 0.45,
                    "confidence_interval": [0.38, 0.52]
                }
            ],
            "model_accuracy": 0.87,
            "summary": "页面优化贡献了45%的转化率提升",
            "attribution_id": "at-20230725-001"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证必要字段
        required_fields = ["metric_name", "metric_value"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"缺少必要字段: {field}")
        
        # 创建分析器实例
        analyzer = AttributionAnalyzer()
        
        # 设置归因方法
        attribution_method = data.get("attribution_method", "shapley")
        if attribution_method not in ["linear", "shapley", "random_forest"]:
            attribution_method = "shapley"
        
        # 执行分析
        result = analyzer.analyze(
            metric_name=data["metric_name"],
            current_value=data["metric_value"],
            previous_value=data.get("previous_value"),
            time_period=data.get("time_period"),
            factors=data.get("factors", []),
            data_points=data.get("data_points", []),
            attribution_method=attribution_method,
            confidence_level=data.get("confidence_level", 0.95)
        )
        
        # 生成分析ID
        attribution_id = f"at-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 格式化响应
        response_data = {
            "attributions": result.attributions,
            "model_accuracy": result.model_accuracy,
            "summary": result.summary,
            "attribution_id": attribution_id
        }
        
        return jsonify(format_success_response(
            data=response_data,
            message="归因分析完成"
        ))
    
    except Exception as e:
        current_app.logger.error(f"归因分析API错误: {str(e)}")
        return jsonify(format_error_response(
            message=f"分析过程中发生错误: {str(e)}",
            status_code=500
        )), 500


@bp.route('/root-cause', methods=['POST'])
@rate_limit
@token_required
def analyze_root_cause():
    """
    根因分析API
    
    分析指标变化的根本原因，基于因果关系图和路径分析
    
    请求体:
    {
        "metric_name": "客户流失率",
        "metric_value": 5.2,
        "previous_value": 3.8,
        "time_period": "2023-Q3",
        "factors": [
            {"name": "客户满意度", "value": 3.5, "previous_value": 4.2},
            {"name": "服务响应时间", "value": 48, "previous_value": 24},
            {"name": "产品质量评分", "value": 4.0, "previous_value": 4.5}
        ],
        "causal_links": [
            {"from": "服务响应时间", "to": "客户满意度", "strength": 0.7},
            {"from": "产品质量评分", "to": "客户满意度", "strength": 0.8}
        ],
        "analysis_depth": "advanced"
    }
    
    返回:
    {
        "success": true,
        "data": {
            "root_causes": [
                {
                    "cause": "服务响应时间增加",
                    "impact": 0.65,
                    "path": ["服务响应时间", "客户满意度", "客户流失率"],
                    "evidence": [
                        "服务响应时间增加了100%",
                        "响应时间与满意度呈负相关"
                    ]
                }
            ],
            "causal_graph": {...},
            "summary": "服务响应时间增加是客户流失率上升的主要根因",
            "analysis_id": "rc-20230725-001"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证必要字段
        required_fields = ["metric_name", "metric_value"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"缺少必要字段: {field}")
        
        # 创建分析器实例
        analyzer = RootCauseAnalyzer()
        
        # 设置分析深度
        analysis_depth = data.get("analysis_depth", "standard")
        if analysis_depth not in ["basic", "standard", "advanced"]:
            analysis_depth = "standard"
        
        # 执行分析
        result = analyzer.analyze(
            metric_name=data["metric_name"],
            current_value=data["metric_value"],
            previous_value=data.get("previous_value"),
            time_period=data.get("time_period"),
            factors=data.get("factors", []),
            causal_links=data.get("causal_links", []),
            analysis_depth=analysis_depth
        )
        
        # 生成分析ID
        analysis_id = f"rc-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 格式化响应
        response_data = {
            "root_causes": result.root_causes,
            "causal_graph": result.causal_graph,
            "summary": result.summary,
            "analysis_id": analysis_id
        }
        
        return jsonify(format_success_response(
            data=response_data,
            message="根因分析完成"
        ))
    
    except Exception as e:
        current_app.logger.error(f"根因分析API错误: {str(e)}")
        return jsonify(format_error_response(
            message=f"分析过程中发生错误: {str(e)}",
            status_code=500
        )), 500


@bp.route('/correlation', methods=['POST'])
@rate_limit
@token_required
def analyze_correlation():
    """
    相关性分析API
    
    分析指标之间的相关性，支持多种相关性计算方法
    
    请求体:
    {
        "primary_metric": {
            "name": "销售额",
            "values": [100, 120, 140, 130, 150]
        },
        "secondary_metrics": [
            {
                "name": "广告投入",
                "values": [50, 60, 65, 70, 75]
            },
            {
                "name": "网站访问量",
                "values": [1000, 1200, 1400, 1300, 1500]
            }
        ],
        "time_periods": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
        "correlation_method": "pearson",
        "lag": 0,
        "significance_level": 0.05
    }
    
    返回:
    {
        "success": true,
        "data": {
            "correlations": [
                {
                    "primary_metric": "销售额",
                    "secondary_metric": "广告投入",
                    "correlation": 0.92,
                    "p_value": 0.01,
                    "is_significant": true
                }
            ],
            "summary": "销售额与广告投入存在显著的强正相关",
            "analysis_id": "co-20230725-001"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证必要字段
        required_fields = ["primary_metric", "secondary_metrics"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"缺少必要字段: {field}")
        
        # 创建分析器实例
        analyzer = CorrelationAnalyzer()
        
        # 设置相关性方法
        correlation_method = data.get("correlation_method", "pearson")
        if correlation_method not in ["pearson", "spearman", "kendall"]:
            correlation_method = "pearson"
        
        # 执行分析
        result = analyzer.analyze(
            primary_metric=data["primary_metric"],
            secondary_metrics=data["secondary_metrics"],
            time_periods=data.get("time_periods", []),
            correlation_method=correlation_method,
            lag=data.get("lag", 0),
            significance_level=data.get("significance_level", 0.05)
        )
        
        # 生成分析ID
        correlation_id = f"co-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 格式化响应
        response_data = {
            "correlations": result.correlations,
            "summary": result.summary,
            "analysis_id": correlation_id
        }
        
        return jsonify(format_success_response(
            data=response_data,
            message="相关性分析完成"
        ))
    
    except Exception as e:
        current_app.logger.error(f"相关性分析API错误: {str(e)}")
        return jsonify(format_error_response(
            message=f"分析过程中发生错误: {str(e)}",
            status_code=500
        )), 500 