from flask import Blueprint, request, jsonify
from ..services.analysis.reason_analyzer import ReasonAnalyzer
from ..services.analysis.attribution_analyzer import AttributionAnalyzer
from ..services.analysis.root_cause_analyzer import RootCauseAnalyzer
from ..utils.error_handlers import handle_api_error

# 创建蓝图
analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/analysis/reason', methods=['POST'])
@handle_api_error
def analyze_reason():
    """
    原因分析API接口
    分析指标变化的原因，包括内部因素和外部因素
    """
    data = request.get_json()
    
    # 参数验证
    required_fields = ['metric_name', 'current_value', 'previous_value', 'change_rate']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要参数: {field}'}), 400
    
    # 创建分析器实例
    analyzer = ReasonAnalyzer()
    
    # 执行分析
    result = analyzer.analyze(
        metric_name=data['metric_name'],
        current_value=data['current_value'],
        previous_value=data['previous_value'],
        change_rate=data['change_rate'],
        historical_data=data.get('historical_data', []),
        external_factors=data.get('external_factors', {})
    )
    
    return jsonify(result)

@analysis_bp.route('/api/analysis/attribution', methods=['POST'])
@handle_api_error
def analyze_attribution():
    """
    归因分析API接口
    分析指标变化中各因素的贡献度
    """
    data = request.get_json()
    
    # 参数验证
    required_fields = ['metric_name', 'factors', 'values']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要参数: {field}'}), 400
    
    # 创建分析器实例
    analyzer = AttributionAnalyzer()
    
    # 执行分析
    result = analyzer.analyze(
        metric_name=data['metric_name'],
        factors=data['factors'],
        values=data['values'],
        weights=data.get('weights', None)
    )
    
    return jsonify(result)

@analysis_bp.route('/api/analysis/root-cause', methods=['POST'])
@handle_api_error
def analyze_root_cause():
    """
    根因分析API接口
    分析指标异常的根本原因
    """
    data = request.get_json()
    
    # 参数验证
    required_fields = ['metric_name', 'current_value', 'threshold', 'historical_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要参数: {field}'}), 400
    
    # 创建分析器实例
    analyzer = RootCauseAnalyzer()
    
    # 执行分析
    result = analyzer.analyze(
        metric_name=data['metric_name'],
        current_value=data['current_value'],
        threshold=data['threshold'],
        historical_data=data['historical_data'],
        related_metrics=data.get('related_metrics', []),
        time_window=data.get('time_window', 30)
    )
    
    return jsonify(result) 