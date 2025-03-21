"""
洞察模型
=======

定义数据洞察的模型结构，用于保存和处理分析结果。
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import json


@dataclass
class MetricData:
    """指标数据模型"""
    
    name: str  # 指标名称
    value: float  # 当前值
    previous_value: float  # 上一期值
    unit: str = ""  # 单位
    time_period: str = ""  # 当前时间段
    previous_time_period: str = ""  # 上一时间段
    historical_values: List[float] = field(default_factory=list)  # 历史值
    is_positive_better: bool = True  # 值越大越好
    dimensions: Dict[str, Any] = field(default_factory=dict)  # 维度属性


@dataclass
class MetricAnalysisResult:
    """指标分析结果模型"""
    
    metric_data: MetricData  # 原始指标数据
    
    # 变化分析
    change_value: float  # 变化值
    change_rate: Optional[float]  # 变化率
    change_class: str  # 变化程度分类
    
    # 异常分析
    is_anomaly: bool = False  # 是否异常
    anomaly_degree: float = 0.0  # 异常程度
    is_higher_anomaly: bool = False  # 是否高于正常范围
    
    # 趋势分析
    trend_type: str = ""  # 趋势类型
    trend_strength: float = 0.0  # 趋势强度
    
    # 归因分析
    reasons: List[Dict[str, Any]] = field(default_factory=list)  # 可能原因
    
    # 建议行动
    actions: List[str] = field(default_factory=list)  # 建议行动


@dataclass
class ChartData:
    """图表数据模型"""
    
    chart_type: str  # 图表类型
    title: str  # 图表标题
    x_axis_title: str = ""  # X轴标题
    y_axis_title: str = ""  # Y轴标题
    x_values: List[Any] = field(default_factory=list)  # X值列表
    y_values: List[float] = field(default_factory=list)  # Y值列表
    series: List[Dict[str, Any]] = field(default_factory=list)  # 多系列数据
    unit: str = ""  # 单位


@dataclass
class ChartAnalysisResult:
    """图表分析结果模型"""
    
    chart_data: ChartData  # 原始图表数据
    
    # 趋势分析
    trends: List[Dict[str, Any]] = field(default_factory=list)  # 各系列趋势
    overall_trend: str = ""  # 整体趋势
    
    # 对比分析
    comparisons: List[Dict[str, Any]] = field(default_factory=list)  # 对比结果
    
    # 异常点分析
    anomalies: List[Dict[str, Any]] = field(default_factory=list)  # 异常点
    
    # 关键洞察
    insights: List[str] = field(default_factory=list)  # 关键洞察


@dataclass
class InsightResult:
    """综合洞察结果模型"""
    
    # 基本信息
    title: str  # 洞察标题
    summary: str  # 摘要文本
    
    # 详细解读
    main_text: str  # 主要解读文本
    
    # 相关分析结果
    analysis_results: Union[MetricAnalysisResult, ChartAnalysisResult, None] = None
    
    # 附加信息
    additional_info: Dict[str, Any] = field(default_factory=dict)  # 附加信息


@dataclass
class MetricInsight:
    """
    指标洞察数据类
    
    存储单个指标的分析结果和洞察内容。
    """
    # 基本信息
    metric_id: str
    metric_name: str
    current_value: float
    previous_value: float
    unit: str = ""
    time_period: str = ""
    previous_time_period: str = ""
    
    # 分析结果
    change_value: float = 0.0
    change_rate: Optional[float] = None
    change_class: str = ""
    is_anomaly: bool = False
    anomaly_degree: float = 0.0
    trend_type: Optional[str] = None
    trend_strength: float = 0.0
    
    # 洞察内容
    insight_text: str = ""
    reasons: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    
    # 元数据
    created_at: str = ""
    updated_at: str = ""
    analysis_version: str = "0.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        返回:
            Dict[str, Any]: 字典格式的数据
        """
        return {
            "基本信息": {
                "指标ID": self.metric_id,
                "指标名称": self.metric_name,
                "当前值": self.current_value,
                "上一期值": self.previous_value,
                "单位": self.unit,
                "当前周期": self.time_period,
                "上一周期": self.previous_time_period
            },
            "分析结果": {
                "变化量": self.change_value,
                "变化率": self.change_rate,
                "变化类别": self.change_class,
                "是否异常": self.is_anomaly,
                "异常程度": self.anomaly_degree,
                "趋势类型": self.trend_type,
                "趋势强度": self.trend_strength
            },
            "洞察内容": {
                "解读文本": self.insight_text,
                "可能原因": self.reasons,
                "建议行动": self.actions
            },
            "元数据": {
                "创建时间": self.created_at,
                "更新时间": self.updated_at,
                "分析版本": self.analysis_version
            }
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        返回:
            str: JSON格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricInsight':
        """
        从字典创建对象
        
        参数:
            data (Dict[str, Any]): 字典格式的数据
            
        返回:
            MetricInsight: 创建的对象
        """
        basic_info = data.get("基本信息", {})
        analysis_result = data.get("分析结果", {})
        insight_content = data.get("洞察内容", {})
        metadata = data.get("元数据", {})
        
        return cls(
            metric_id=basic_info.get("指标ID", ""),
            metric_name=basic_info.get("指标名称", ""),
            current_value=basic_info.get("当前值", 0.0),
            previous_value=basic_info.get("上一期值", 0.0),
            unit=basic_info.get("单位", ""),
            time_period=basic_info.get("当前周期", ""),
            previous_time_period=basic_info.get("上一周期", ""),
            change_value=analysis_result.get("变化量", 0.0),
            change_rate=analysis_result.get("变化率"),
            change_class=analysis_result.get("变化类别", ""),
            is_anomaly=analysis_result.get("是否异常", False),
            anomaly_degree=analysis_result.get("异常程度", 0.0),
            trend_type=analysis_result.get("趋势类型"),
            trend_strength=analysis_result.get("趋势强度", 0.0),
            insight_text=insight_content.get("解读文本", ""),
            reasons=insight_content.get("可能原因", []),
            actions=insight_content.get("建议行动", []),
            created_at=metadata.get("创建时间", ""),
            updated_at=metadata.get("更新时间", ""),
            analysis_version=metadata.get("分析版本", "0.1.0")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MetricInsight':
        """
        从JSON字符串创建对象
        
        参数:
            json_str (str): JSON格式的字符串
            
        返回:
            MetricInsight: 创建的对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class CorrelationItem:
    """相关性项模型"""
    
    item_name: str  # 指标名称
    correlation_value: float  # 相关性值
    p_value: float  # p值
    sample_size: int = 0  # 样本数量
    significance_level: float = 0.05  # 显著性水平
    is_significant: bool = False  # 是否显著相关
    correlation_type: str = "pearson"  # 相关性类型（pearson, spearman, kendall）
    insight_text: str = ""  # 相关性解读文本


@dataclass
class CorrelationResult:
    """相关性分析结果模型"""
    
    main_metric: str  # 主指标名称
    correlations: List[CorrelationItem] = field(default_factory=list)  # 相关性项列表
    time_period: str = ""  # 分析时间周期
    analysis_time: str = ""  # 分析时间
    insight_summary: str = ""  # 分析总结
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        返回:
            Dict[str, Any]: 字典格式的数据
        """
        return {
            "主指标": self.main_metric,
            "相关性列表": [
                {
                    "指标名称": item.item_name,
                    "相关性值": item.correlation_value,
                    "p值": item.p_value,
                    "样本数量": item.sample_size,
                    "显著性水平": item.significance_level,
                    "是否显著": item.is_significant,
                    "相关性类型": item.correlation_type,
                    "解读文本": item.insight_text
                }
                for item in self.correlations
            ],
            "时间周期": self.time_period,
            "分析时间": self.analysis_time,
            "分析总结": self.insight_summary
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        返回:
            str: JSON格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class TrendItem:
    """趋势项模型"""
    
    value: float  # 趋势值
    timestamp: str  # 时间戳
    confidence: float = 0.0  # 置信度
    is_anomaly: bool = False  # 是否异常点
    anomaly_degree: float = 0.0  # 异常程度


@dataclass
class TrendPattern:
    """趋势模式模型"""
    
    pattern_type: str  # 模式类型（上升、下降、波动等）
    start_time: str  # 开始时间
    end_time: str  # 结束时间
    strength: float = 0.0  # 模式强度
    confidence: float = 0.0  # 置信度
    description: str = ""  # 模式描述


@dataclass
class TrendInflection:
    """趋势拐点模型"""
    
    timestamp: str  # 拐点时间
    inflection_type: str  # 拐点类型（峰、谷）
    value: float  # 拐点值
    confidence: float = 0.0  # 置信度
    description: str = ""  # 拐点描述


@dataclass
class TrendResult:
    """趋势分析结果模型"""
    
    metric_name: str  # 指标名称
    time_period: str  # 时间周期
    trend_items: List[TrendItem] = field(default_factory=list)  # 趋势项列表
    patterns: List[TrendPattern] = field(default_factory=list)  # 趋势模式列表
    inflections: List[TrendInflection] = field(default_factory=list)  # 拐点列表
    overall_trend: str = ""  # 整体趋势
    trend_strength: float = 0.0  # 趋势强度
    confidence: float = 0.0  # 整体置信度
    insight_text: str = ""  # 趋势解读文本
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        返回:
            Dict[str, Any]: 字典格式的数据
        """
        return {
            "指标名称": self.metric_name,
            "时间周期": self.time_period,
            "趋势项列表": [
                {
                    "值": item.value,
                    "时间戳": item.timestamp,
                    "置信度": item.confidence,
                    "是否异常": item.is_anomaly,
                    "异常程度": item.anomaly_degree
                }
                for item in self.trend_items
            ],
            "趋势模式列表": [
                {
                    "模式类型": pattern.pattern_type,
                    "开始时间": pattern.start_time,
                    "结束时间": pattern.end_time,
                    "模式强度": pattern.strength,
                    "置信度": pattern.confidence,
                    "描述": pattern.description
                }
                for pattern in self.patterns
            ],
            "拐点列表": [
                {
                    "时间戳": inflection.timestamp,
                    "拐点类型": inflection.inflection_type,
                    "值": inflection.value,
                    "置信度": inflection.confidence,
                    "描述": inflection.description
                }
                for inflection in self.inflections
            ],
            "整体趋势": self.overall_trend,
            "趋势强度": self.trend_strength,
            "整体置信度": self.confidence,
            "趋势解读": self.insight_text
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        返回:
            str: JSON格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrendResult':
        """
        从字典创建对象
        
        参数:
            data (Dict[str, Any]): 字典格式的数据
            
        返回:
            TrendResult: 创建的对象
        """
        trend_items = [
            TrendItem(
                value=item["值"],
                timestamp=item["时间戳"],
                confidence=item["置信度"],
                is_anomaly=item["是否异常"],
                anomaly_degree=item["异常程度"]
            )
            for item in data.get("趋势项列表", [])
        ]
        
        patterns = [
            TrendPattern(
                pattern_type=pattern["模式类型"],
                start_time=pattern["开始时间"],
                end_time=pattern["结束时间"],
                strength=pattern["模式强度"],
                confidence=pattern["置信度"],
                description=pattern["描述"]
            )
            for pattern in data.get("趋势模式列表", [])
        ]
        
        inflections = [
            TrendInflection(
                timestamp=inflection["时间戳"],
                inflection_type=inflection["拐点类型"],
                value=inflection["值"],
                confidence=inflection["置信度"],
                description=inflection["描述"]
            )
            for inflection in data.get("拐点列表", [])
        ]
        
        return cls(
            metric_name=data.get("指标名称", ""),
            time_period=data.get("时间周期", ""),
            trend_items=trend_items,
            patterns=patterns,
            inflections=inflections,
            overall_trend=data.get("整体趋势", ""),
            trend_strength=data.get("趋势强度", 0.0),
            confidence=data.get("整体置信度", 0.0),
            insight_text=data.get("趋势解读", "")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TrendResult':
        """
        从JSON字符串创建对象
        
        参数:
            json_str (str): JSON格式的字符串
            
        返回:
            TrendResult: 创建的对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class AnalysisResult:
    """分析结果模型"""
    
    # 基本信息
    analysis_id: str  # 分析ID
    analysis_type: str  # 分析类型
    analysis_time: str  # 分析时间
    
    # 分析对象
    metric_name: str  # 指标名称
    time_period: str  # 时间周期
    
    # 分析结果
    trend_result: Optional[TrendResult] = None  # 趋势分析结果
    correlation_result: Optional[CorrelationResult] = None  # 相关性分析结果
    metric_insight: Optional[MetricInsight] = None  # 指标洞察结果
    
    # 综合洞察
    insight_summary: str = ""  # 洞察摘要
    insight_details: List[str] = field(default_factory=list)  # 详细洞察
    suggestions: List[Dict[str, Any]] = field(default_factory=list)  # 建议行动
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        返回:
            Dict[str, Any]: 字典格式的数据
        """
        return {
            "基本信息": {
                "分析ID": self.analysis_id,
                "分析类型": self.analysis_type,
                "分析时间": self.analysis_time,
                "指标名称": self.metric_name,
                "时间周期": self.time_period
            },
            "分析结果": {
                "趋势分析": self.trend_result.to_dict() if self.trend_result else None,
                "相关性分析": self.correlation_result.to_dict() if self.correlation_result else None,
                "指标洞察": self.metric_insight.to_dict() if self.metric_insight else None
            },
            "综合洞察": {
                "洞察摘要": self.insight_summary,
                "详细洞察": self.insight_details,
                "建议行动": self.suggestions
            }
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        返回:
            str: JSON格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """
        从字典创建对象
        
        参数:
            data (Dict[str, Any]): 字典格式的数据
            
        返回:
            AnalysisResult: 创建的对象
        """
        basic_info = data.get("基本信息", {})
        analysis_results = data.get("分析结果", {})
        insights = data.get("综合洞察", {})
        
        trend_data = analysis_results.get("趋势分析")
        correlation_data = analysis_results.get("相关性分析")
        metric_insight_data = analysis_results.get("指标洞察")
        
        return cls(
            analysis_id=basic_info.get("分析ID", ""),
            analysis_type=basic_info.get("分析类型", ""),
            analysis_time=basic_info.get("分析时间", ""),
            metric_name=basic_info.get("指标名称", ""),
            time_period=basic_info.get("时间周期", ""),
            trend_result=TrendResult.from_dict(trend_data) if trend_data else None,
            correlation_result=CorrelationResult.from_dict(correlation_data) if correlation_data else None,
            metric_insight=MetricInsight.from_dict(metric_insight_data) if metric_insight_data else None,
            insight_summary=insights.get("洞察摘要", ""),
            insight_details=insights.get("详细洞察", []),
            suggestions=insights.get("建议行动", [])
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisResult':
        """
        从JSON字符串创建对象
        
        参数:
            json_str (str): JSON格式的字符串
            
        返回:
            AnalysisResult: 创建的对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data) 