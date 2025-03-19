#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
趋势分析 API 路由
===============

提供时间序列数据趋势分析相关的 API 路由，包括趋势检测、季节性分析和拐点检测等功能。
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, Unauthorized

from data_insight.core.trend_analyzer import TrendAnalyzer
from data_insight.models.insight_model import TrendResult
from data_insight.api.utils.response_formatter import format_success_response, format_error_response
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.middlewares.auth import token_required
from data_insight.api.utils.request_validator import validate_request_data

# 创建蓝图
bp = Blueprint('trend', __name__, url_prefix='/api/trend')


def _calculate_trend_similarity(trend_results: List[TrendResult]) -> float:
    """计算趋势相似度"""
    # 简化版：比较方向和模式的相似度
    if not trend_results or len(trend_results) < 2:
        return 0.0
    
    # 获取第一个趋势的方向和模式
    first_direction = trend_results[0].trend.direction
    first_pattern = trend_results[0].trend.pattern
    
    # 计算方向和模式匹配的比例
    direction_matches = sum(1 for r in trend_results if r.trend.direction == first_direction)
    pattern_matches = sum(1 for r in trend_results if r.trend.pattern == first_pattern)
    
    # 计算总体相似度
    similarity = 0.5 * (direction_matches / len(trend_results)) + 0.5 * (pattern_matches / len(trend_results))
    
    return similarity


def _generate_trend_differences(trend_results: List[TrendResult]) -> List[str]:
    """生成趋势差异点描述"""
    differences = []
    
    # 比较斜率
    slopes = [r.trend.slope for r in trend_results]
    metric_names = [r.trend.metric_name for r in trend_results]
    
    slope_description = "、".join([f"{name}增长率为{slope}/月" for name, slope in zip(metric_names, slopes)])
    differences.append(slope_description)
    
    # 比较模式
    patterns = [r.trend.pattern for r in trend_results]
    if all(p == patterns[0] for p in patterns):
        pattern_name = "线性增长" if "LINEAR_INCREASE" in str(patterns[0]) else \
                        "线性下降" if "LINEAR_DECREASE" in str(patterns[0]) else \
                        "波动" if "FLUCTUATING" in str(patterns[0]) else \
                        "平稳"
        differences.append(f"所有指标均呈{pattern_name}趋势")
    else:
        pattern_description = "、".join([f"{name}呈{pattern}趋势" for name, pattern in zip(metric_names, patterns)])
        differences.append(f"指标趋势模式不同: {pattern_description}")
    
    return differences


def _generate_comparison_summary(trend_results: List[TrendResult], similarity: float) -> str:
    """生成趋势对比摘要"""
    metric_names = [r.trend.metric_name for r in trend_results]
    metric_list = "、".join(metric_names)
    
    if similarity > 0.8:
        similarity_desc = "高度相似"
    elif similarity > 0.5:
        similarity_desc = "中度相似"
    else:
        similarity_desc = "差异较大"
    
    # 获取趋势方向
    directions = [r.trend.direction for r in trend_results]
    if all(d == directions[0] for d in directions):
        if directions[0] == "上升":
            direction_desc = "均呈现上升趋势"
        elif directions[0] == "下降":
            direction_desc = "均呈现下降趋势"
        else:
            direction_desc = "均呈现平稳趋势"
    else:
        direction_desc = "呈现不同的变化趋势"
    
    summary = f"{metric_list}趋势{similarity_desc}，{direction_desc}"
    return summary


@bp.route('/analyze', methods=['POST'])
@rate_limit
@token_required
def analyze_trend():
    """
    趋势分析 API
    
    分析时间序列数据的趋势特征，包括趋势方向、强度、季节性和拐点检测等
    
    请求体:
    {
        "metric_name": "日活跃用户",
        "values": [1000, 1050, 1100, 1150, 1250, 1200, 1300],
        "timestamps": ["2023-01-01", "2023-02-01", "2023-03-01", 
                      "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01"],
        "trend_method": "auto",  // 可选: "auto", "linear", "exponential", "lowess"
        "seasonality": true,
        "detect_inflections": true
    }
    
    返回:
    {
        "success": true,
        "data": {
            "trend": {
                "metric_name": "日活跃用户",
                "direction": "上升",
                "slope": 45.71,
                "significance": 0.89,
                "r_squared": 0.89,
                "pattern": "LINEAR_INCREASE",
                "method": "linear",
                "has_seasonality": false,
                "seasonality_strength": null,
                "seasonality_pattern": null
            },
            "inflections": [
                {
                    "date": "2023-05-01",
                    "index": 4,
                    "value": 1250,
                    "type": "高点",
                    "strength": 0.75
                }
            ],
            "summary": "日活跃用户整体呈持续上升趋势，趋势非常显著，在2023-05-01出现显著高点",
            "analysis_id": "tr-20230725-001"
        },
        "message": "趋势分析完成"
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证请求数据
        required_fields = ["metric_name", "values", "timestamps"]
        validate_request_data(data, required_fields)
        
        # 验证数据长度
        if len(data["values"]) != len(data["timestamps"]):
            raise BadRequest("值列表与时间戳列表长度必须一致")
        
        if len(data["values"]) < 3:
            raise BadRequest("趋势分析至少需要3个数据点")
        
        # 创建分析器实例
        analyzer = TrendAnalyzer()
        
        # 设置趋势分析方法
        trend_method = data.get("trend_method", "auto")
        if trend_method not in ["auto", "linear", "exponential", "lowess"]:
            trend_method = "auto"
        
        # 执行分析
        result = analyzer.analyze(
            metric_name=data["metric_name"],
            values=data["values"],
            timestamps=data["timestamps"],
            trend_method=trend_method,
            seasonality=data.get("seasonality", True),
            detect_inflections=data.get("detect_inflections", True)
        )
        
        # 生成分析ID
        analysis_id = f"tr-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 格式化响应
        response_data = {
            "trend": {
                "metric_name": result.trend.metric_name,
                "direction": result.trend.direction,
                "slope": result.trend.slope,
                "significance": result.trend.significance,
                "r_squared": result.trend.r_squared,
                "pattern": str(result.trend.pattern),
                "method": result.trend.method,
                "has_seasonality": result.trend.has_seasonality,
                "seasonality_strength": result.trend.seasonality_strength,
                "seasonality_pattern": result.trend.seasonality_pattern
            },
            "inflections": [
                {
                    "date": inflection.date,
                    "index": inflection.index,
                    "value": inflection.value,
                    "type": inflection.type,
                    "strength": inflection.strength
                } for inflection in result.inflections
            ],
            "summary": result.summary,
            "analysis_id": analysis_id
        }
        
        return jsonify(format_success_response(
            data=response_data,
            message="趋势分析完成"
        ))
    
    except Exception as e:
        current_app.logger.error(f"趋势分析API错误: {str(e)}")
        return jsonify(format_error_response(
            message=f"分析过程中发生错误: {str(e)}",
            status_code=500
        )), 500


@bp.route('/compare', methods=['POST'])
@rate_limit
@token_required
def compare_trends():
    """
    趋势对比 API
    
    对比多个指标的趋势特征，分析它们之间的相似性和差异性
    
    请求体:
    {
        "metrics": [
            {
                "name": "销售额",
                "values": [100, 120, 140, 150, 160, 180],
                "timestamps": ["2023-01-01", "2023-02-01", "2023-03-01", 
                              "2023-04-01", "2023-05-01", "2023-06-01"]
            },
            {
                "name": "用户数",
                "values": [1000, 1100, 1150, 1200, 1300, 1400],
                "timestamps": ["2023-01-01", "2023-02-01", "2023-03-01", 
                              "2023-04-01", "2023-05-01", "2023-06-01"]
            }
        ],
        "normalize": true,
        "trend_method": "linear"
    }
    
    返回:
    {
        "success": true,
        "data": {
            "trends": [
                {
                    "metric_name": "销售额",
                    "direction": "上升",
                    "slope": 15.4,
                    "pattern": "LINEAR_INCREASE"
                },
                {
                    "metric_name": "用户数",
                    "direction": "上升",
                    "slope": 80.0,
                    "pattern": "LINEAR_INCREASE"
                }
            ],
            "similarity": 0.92,
            "differences": [
                "销售额增长率为15.4/月，用户数增长率为80.0/月",
                "两个指标均呈线性增长趋势"
            ],
            "summary": "销售额和用户数趋势高度相似，均呈现稳定上升趋势",
            "analysis_id": "tc-20230725-001"
        },
        "message": "趋势对比分析完成"
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证请求数据
        if "metrics" not in data or not isinstance(data["metrics"], list):
            raise BadRequest("必须提供有效的指标列表")
        
        if len(data["metrics"]) < 2:
            raise BadRequest("趋势对比至少需要2个指标")
        
        # 验证每个指标的数据
        for i, metric in enumerate(data["metrics"]):
            if "name" not in metric or "values" not in metric or "timestamps" not in metric:
                raise BadRequest(f"指标 #{i+1} 必须包含name、values和timestamps字段")
            
            if len(metric["values"]) != len(metric["timestamps"]):
                raise BadRequest(f"指标 '{metric['name']}' 的值列表与时间戳列表长度必须一致")
            
            if len(metric["values"]) < 3:
                raise BadRequest(f"指标 '{metric['name']}' 至少需要3个数据点")
        
        # 创建分析器实例
        analyzer = TrendAnalyzer()
        
        # 设置趋势分析方法
        trend_method = data.get("trend_method", "auto")
        if trend_method not in ["auto", "linear", "exponential", "lowess"]:
            trend_method = "auto"
        
        # 存储每个指标的分析结果
        trend_results = []
        for metric in data["metrics"]:
            result = analyzer.analyze(
                metric_name=metric["name"],
                values=metric["values"],
                timestamps=metric["timestamps"],
                trend_method=trend_method,
                seasonality=False,
                detect_inflections=False
            )
            trend_results.append(result)
        
        # 计算趋势相似度（使用方向和模式进行比较）
        similarity = _calculate_trend_similarity(trend_results)
        
        # 生成趋势差异点描述
        differences = _generate_trend_differences(trend_results)
        
        # 生成摘要
        summary = _generate_comparison_summary(trend_results, similarity)
        
        # 生成分析ID
        analysis_id = f"tc-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 格式化响应
        response_data = {
            "trends": [
                {
                    "metric_name": result.trend.metric_name,
                    "direction": result.trend.direction,
                    "slope": result.trend.slope,
                    "pattern": str(result.trend.pattern)
                } for result in trend_results
            ],
            "similarity": round(float(similarity), 2),
            "differences": differences,
            "summary": summary,
            "analysis_id": analysis_id
        }
        
        return jsonify(format_success_response(
            data=response_data,
            message="趋势对比分析完成"
        ))
    
    except Exception as e:
        current_app.logger.error(f"趋势对比API错误: {str(e)}")
        return jsonify(format_error_response(
            message=f"分析过程中发生错误: {str(e)}",
            status_code=500
        )), 500 