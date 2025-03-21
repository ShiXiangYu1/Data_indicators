"""
比较分析器模块
===========

提供对多个图表或指标数据进行比较分析的功能。
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy import stats
import math
from datetime import datetime

from data_insight.core.analysis.base import BaseAnalyzer


class ComparisonAnalyzer(BaseAnalyzer):
    """
    比较分析器
    
    负责比较多个图表或指标数据，发现它们之间的相似性、差异性以及潜在的关联关系。
    """
    
    def __init__(self):
        """初始化比较分析器"""
        super().__init__(name="比较分析器", version="1.0.0")
        self.logger = logging.getLogger("data_insight.analysis.comparison")
        self.supported_comparison_types = ["trend", "feature", "anomaly", "correlation"]
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        比较分析多个图表或指标数据
        
        参数:
            data (Dict[str, Any]): 需要比较的数据，应包含以下字段：
                - charts/metrics: 图表或指标数据列表
                - comparison_type: 比较类型（可选）
                
        返回:
            Dict[str, Any]: 比较分析结果
            
        异常:
            ValueError: 如果输入数据格式不正确或不包含足够的数据
        """
        # 验证输入数据
        if "charts" in data:
            charts = data["charts"]
            data_type = "charts"
        elif "metrics" in data:
            charts = data["metrics"]
            data_type = "metrics"
        else:
            raise ValueError("输入数据必须包含'charts'或'metrics'字段")
            
        if not isinstance(charts, list) or len(charts) < 2:
            raise ValueError("比较分析至少需要两个图表或指标数据")
            
        # 获取比较类型
        comparison_type = data.get("comparison_type", "all")
        context = data.get("context", {})
        
        # 对每个图表或指标进行单独分析
        individual_analyses = []
        for chart in charts:
            try:
                # 假设存在相应的分析器
                if data_type == "charts":
                    from data_insight.core.analysis.chart import ChartAnalyzer
                    analyzer = ChartAnalyzer()
                else:
                    from data_insight.core.analysis.metric import MetricAnalyzer
                    analyzer = MetricAnalyzer()
                    
                analysis = analyzer.analyze(chart)
                individual_analyses.append(analysis)
            except Exception as e:
                self.logger.warning(f"单个{data_type[:-1]}分析失败: {str(e)}")
                # 创建最小分析结果
                individual_analyses.append({"error": str(e), "data": chart})
        
        # 执行比较分析
        comparison_results = {}
        
        # 根据比较类型执行不同的比较分析
        if comparison_type in ["all", "trend"]:
            comparison_results["trend_comparison"] = self._analyze_trend_comparison(charts, individual_analyses)
            
        if comparison_type in ["all", "feature"]:
            comparison_results["feature_comparison"] = self._analyze_feature_comparison(charts, individual_analyses)
            
        if comparison_type in ["all", "anomaly"]:
            comparison_results["anomaly_comparison"] = self._analyze_anomaly_comparison(charts, individual_analyses)
            
        if comparison_type in ["all", "correlation"]:
            comparison_results["correlation_analysis"] = self._analyze_correlations(charts)
        
        # 构建结果
        result = {
            "comparison_type": comparison_type,
            "data_type": data_type,
            "count": len(charts),
            "individual_analyses": individual_analyses,
            "comparison": comparison_results,
            "timestamp": self._get_timestamp()
        }
        
        # 添加元数据
        result["metadata"] = {
            "analyzer": self.get_metadata(),
            "context": context
        }
        
        return result
    
    def _analyze_trend_comparison(self, charts: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表或指标的趋势对比
        
        参数:
            charts (List[Dict[str, Any]]): 图表或指标数据列表
            analyses (List[Dict[str, Any]]): 个体分析结果列表
            
        返回:
            List[Dict[str, Any]]: 趋势对比分析结果
        """
        trend_comparisons = []
        
        # 确保至少有两个有效分析结果
        valid_analyses = [a for a in analyses if "error" not in a]
        if len(valid_analyses) < 2:
            return [{"error": "没有足够的有效分析结果进行趋势比较"}]
        
        # 提取趋势数据
        trend_data = []
        for i, analysis in enumerate(valid_analyses):
            if "analysis" in analysis and "trend" in analysis["analysis"]:
                trend = analysis["analysis"]["trend"]
                trend_data.append({
                    "chart_index": i,
                    "trend": trend
                })
            elif "trend" in analysis:
                trend_data.append({
                    "chart_index": i,
                    "trend": analysis["trend"]
                })
        
        # 如果没有足够的趋势数据，返回错误
        if len(trend_data) < 2:
            return [{"error": "没有足够的趋势数据进行比较"}]
        
        # 比较趋势方向
        direction_groups = {}
        for item in trend_data:
            direction = item["trend"].get("direction", "unknown")
            if direction not in direction_groups:
                direction_groups[direction] = []
            direction_groups[direction].append(item["chart_index"])
        
        # 生成趋势方向比较结果
        for direction, indices in direction_groups.items():
            trend_comparisons.append({
                "type": "trend_direction",
                "direction": direction,
                "chart_indices": indices,
                "count": len(indices)
            })
        
        # 比较趋势变化点
        change_point_similarities = []
        for i in range(len(trend_data)):
            for j in range(i+1, len(trend_data)):
                chart_i = trend_data[i]
                chart_j = trend_data[j]
                
                change_points_i = chart_i["trend"].get("change_points", [])
                change_points_j = chart_j["trend"].get("change_points", [])
                
                # 如果两者都有变化点，计算相似度
                if change_points_i and change_points_j:
                    # 简单计算：共同变化点数量/变化点总数
                    common_points = set(change_points_i).intersection(set(change_points_j))
                    total_points = set(change_points_i).union(set(change_points_j))
                    
                    similarity = len(common_points) / len(total_points) if total_points else 0
                    
                    change_point_similarities.append({
                        "chart_indices": [chart_i["chart_index"], chart_j["chart_index"]],
                        "similarity": similarity,
                        "common_points": list(common_points)
                    })
        
        if change_point_similarities:
            trend_comparisons.append({
                "type": "change_point_similarity",
                "comparisons": change_point_similarities
            })
        
        # 比较趋势强度
        strength_comparisons = []
        for i in range(len(trend_data)):
            for j in range(i+1, len(trend_data)):
                chart_i = trend_data[i]
                chart_j = trend_data[j]
                
                strength_i = chart_i["trend"].get("strength", 0)
                strength_j = chart_j["trend"].get("strength", 0)
                
                # 计算强度比例
                if strength_i and strength_j:
                    ratio = strength_i / strength_j if strength_j != 0 else float('inf')
                    if ratio < 1:
                        ratio = 1 / ratio
                        stronger = chart_j["chart_index"]
                    else:
                        stronger = chart_i["chart_index"]
                    
                    strength_comparisons.append({
                        "chart_indices": [chart_i["chart_index"], chart_j["chart_index"]],
                        "strength_ratio": ratio,
                        "stronger_trend": stronger
                    })
        
        if strength_comparisons:
            trend_comparisons.append({
                "type": "trend_strength_comparison",
                "comparisons": strength_comparisons
            })
        
        return trend_comparisons
    
    def _analyze_feature_comparison(self, charts: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表或指标的特征比较
        
        参数:
            charts (List[Dict[str, Any]]): 图表或指标数据列表
            analyses (List[Dict[str, Any]]): 个体分析结果列表
            
        返回:
            List[Dict[str, Any]]: 特征比较分析结果
        """
        feature_comparisons = []
        
        # 确保至少有两个有效分析结果
        valid_analyses = [a for a in analyses if "error" not in a]
        if len(valid_analyses) < 2:
            return [{"error": "没有足够的有效分析结果进行特征比较"}]
        
        # 提取统计特征
        stat_features = []
        for i, analysis in enumerate(valid_analyses):
            stats_data = {}
            
            # 尝试从不同位置提取统计数据
            if "analysis" in analysis and "statistics" in analysis["analysis"]:
                stats_data = analysis["analysis"]["statistics"]
            elif "statistics" in analysis:
                stats_data = analysis["statistics"]
            
            if stats_data:
                stat_features.append({
                    "chart_index": i,
                    "statistics": stats_data
                })
        
        # 如果没有足够的统计特征，返回错误
        if len(stat_features) < 2:
            return [{"error": "没有足够的统计特征数据进行比较"}]
        
        # 比较基本统计特征
        stat_keys = ["mean", "median", "min", "max", "variance", "std_dev"]
        
        # 对每个统计特征进行比较
        for key in stat_keys:
            values = []
            for feature in stat_features:
                if key in feature["statistics"]:
                    values.append({
                        "chart_index": feature["chart_index"],
                        "value": feature["statistics"][key]
                    })
            
            if len(values) >= 2:
                # 排序
                sorted_values = sorted(values, key=lambda x: x["value"])
                
                # 计算比例
                min_value = sorted_values[0]["value"]
                max_value = sorted_values[-1]["value"]
                
                # 避免除以零
                ratio = max_value / min_value if min_value != 0 else float('inf')
                
                feature_comparisons.append({
                    "type": f"{key}_comparison",
                    "values": sorted_values,
                    "min_value": min_value,
                    "max_value": max_value,
                    "ratio": ratio,
                    "range": max_value - min_value
                })
        
        # 比较分布特征（如果存在）
        distribution_features = []
        for i, analysis in enumerate(valid_analyses):
            dist_data = {}
            
            # 尝试从不同位置提取分布数据
            if "analysis" in analysis and "distribution" in analysis["analysis"]:
                dist_data = analysis["analysis"]["distribution"]
            elif "distribution" in analysis:
                dist_data = analysis["distribution"]
            
            if dist_data:
                distribution_features.append({
                    "chart_index": i,
                    "distribution": dist_data
                })
        
        # 如果有分布数据，进行分布比较
        if len(distribution_features) >= 2:
            # 比较分布形状（偏度、峰度）
            shape_comparisons = []
            for i in range(len(distribution_features)):
                for j in range(i+1, len(distribution_features)):
                    dist_i = distribution_features[i]["distribution"]
                    dist_j = distribution_features[j]["distribution"]
                    
                    # 比较偏度
                    if "skewness" in dist_i and "skewness" in dist_j:
                        skew_i = dist_i["skewness"]
                        skew_j = dist_j["skewness"]
                        
                        # 判断偏度方向是否一致
                        same_direction = (skew_i > 0 and skew_j > 0) or (skew_i < 0 and skew_j < 0)
                        
                        shape_comparisons.append({
                            "type": "skewness_comparison",
                            "chart_indices": [distribution_features[i]["chart_index"], distribution_features[j]["chart_index"]],
                            "values": [skew_i, skew_j],
                            "same_direction": same_direction,
                            "difference": abs(skew_i - skew_j)
                        })
                    
                    # 比较峰度
                    if "kurtosis" in dist_i and "kurtosis" in dist_j:
                        kurt_i = dist_i["kurtosis"]
                        kurt_j = dist_j["kurtosis"]
                        
                        # 是否都是尖峰或平峰
                        both_leptokurtic = kurt_i > 0 and kurt_j > 0
                        both_platykurtic = kurt_i < 0 and kurt_j < 0
                        
                        shape_comparisons.append({
                            "type": "kurtosis_comparison",
                            "chart_indices": [distribution_features[i]["chart_index"], distribution_features[j]["chart_index"]],
                            "values": [kurt_i, kurt_j],
                            "both_leptokurtic": both_leptokurtic,
                            "both_platykurtic": both_platykurtic,
                            "difference": abs(kurt_i - kurt_j)
                        })
            
            if shape_comparisons:
                feature_comparisons.append({
                    "type": "distribution_shape_comparison",
                    "comparisons": shape_comparisons
                })
        
        return feature_comparisons
    
    def _analyze_anomaly_comparison(self, charts: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表或指标的异常比较
        
        参数:
            charts (List[Dict[str, Any]]): 图表或指标数据列表
            analyses (List[Dict[str, Any]]): 个体分析结果列表
            
        返回:
            List[Dict[str, Any]]: 异常比较分析结果
        """
        anomaly_comparisons = []
        
        # 确保至少有两个有效分析结果
        valid_analyses = [a for a in analyses if "error" not in a]
        if len(valid_analyses) < 2:
            return [{"error": "没有足够的有效分析结果进行异常比较"}]
        
        # 提取异常数据
        anomaly_data = []
        for i, analysis in enumerate(valid_analyses):
            anomalies = []
            
            # 尝试从不同位置提取异常数据
            if "analysis" in analysis and "anomalies" in analysis["analysis"]:
                anomalies = analysis["analysis"]["anomalies"]
            elif "anomalies" in analysis:
                anomalies = analysis["anomalies"]
            
            if anomalies:
                anomaly_data.append({
                    "chart_index": i,
                    "anomalies": anomalies
                })
        
        # 如果没有异常数据，返回空结果
        if not anomaly_data:
            return [{"type": "no_anomalies_found", "message": "在分析的图表或指标中未发现异常"}]
        
        # 统计异常数量
        anomaly_counts = {}
        for item in anomaly_data:
            anomaly_counts[item["chart_index"]] = len(item["anomalies"])
        
        # 按异常数量排序
        sorted_counts = sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)
        
        anomaly_comparisons.append({
            "type": "anomaly_count_comparison",
            "counts": [{"chart_index": idx, "count": count} for idx, count in sorted_counts],
            "max_anomalies": sorted_counts[0][1] if sorted_counts else 0,
            "min_anomalies": sorted_counts[-1][1] if sorted_counts else 0
        })
        
        # 查找共同异常位置
        # 注意：这里假设anomalies中包含position或index字段表示异常位置
        if len(anomaly_data) >= 2:
            common_anomalies = []
            for i in range(len(anomaly_data)):
                for j in range(i+1, len(anomaly_data)):
                    anomalies_i = anomaly_data[i]["anomalies"]
                    anomalies_j = anomaly_data[j]["anomalies"]
                    
                    # 提取位置
                    positions_i = set()
                    positions_j = set()
                    
                    for anomaly in anomalies_i:
                        if "position" in anomaly:
                            positions_i.add(anomaly["position"])
                        elif "index" in anomaly:
                            positions_i.add(anomaly["index"])
                    
                    for anomaly in anomalies_j:
                        if "position" in anomaly:
                            positions_j.add(anomaly["position"])
                        elif "index" in anomaly:
                            positions_j.add(anomaly["index"])
                    
                    # 找出共同位置
                    common_positions = positions_i.intersection(positions_j)
                    
                    if common_positions:
                        common_anomalies.append({
                            "chart_indices": [anomaly_data[i]["chart_index"], anomaly_data[j]["chart_index"]],
                            "common_positions": list(common_positions),
                            "count": len(common_positions)
                        })
            
            if common_anomalies:
                anomaly_comparisons.append({
                    "type": "common_anomaly_positions",
                    "comparisons": common_anomalies
                })
        
        return anomaly_comparisons
    
    def _analyze_correlations(self, charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析多个图表或指标之间的相关性
        
        参数:
            charts (List[Dict[str, Any]]): 图表或指标数据列表
            
        返回:
            List[Dict[str, Any]]: 相关性分析结果
        """
        correlation_results = []
        
        # 确保至少有两个图表或指标
        if len(charts) < 2:
            return [{"error": "至少需要两个图表或指标进行相关性分析"}]
        
        # 提取数据
        extracted_data = []
        for i, chart in enumerate(charts):
            try:
                data = self._extract_chart_data(chart)
                if data:
                    extracted_data.append({
                        "chart_index": i,
                        "data": data,
                        "label": chart.get("name", chart.get("title", f"图表{i+1}"))
                    })
            except Exception as e:
                self.logger.warning(f"从图表{i}提取数据失败: {str(e)}")
        
        # 如果数据提取不足，返回错误
        if len(extracted_data) < 2:
            return [{"error": "无法从足够的图表或指标中提取数据"}]
        
        # 计算两两相关性
        correlations = []
        for i in range(len(extracted_data)):
            for j in range(i+1, len(extracted_data)):
                data_i = extracted_data[i]["data"]
                data_j = extracted_data[j]["data"]
                
                # 确保数据长度一致
                min_length = min(len(data_i), len(data_j))
                if min_length < 2:
                    continue
                
                data_i = data_i[:min_length]
                data_j = data_j[:min_length]
                
                try:
                    # 计算皮尔逊相关系数
                    correlation, p_value = stats.pearsonr(data_i, data_j)
                    
                    # 计算斯皮尔曼等级相关系数
                    spearman_corr, spearman_p = stats.spearmanr(data_i, data_j)
                    
                    # 描述相关性强度
                    strength_description = self._describe_correlation_strength(abs(correlation))
                    
                    correlations.append({
                        "chart_indices": [extracted_data[i]["chart_index"], extracted_data[j]["chart_index"]],
                        "chart_labels": [extracted_data[i]["label"], extracted_data[j]["label"]],
                        "pearson_correlation": correlation,
                        "p_value": p_value,
                        "spearman_correlation": spearman_corr,
                        "spearman_p_value": spearman_p,
                        "is_significant": p_value < 0.05,
                        "strength": strength_description,
                        "direction": "正相关" if correlation > 0 else "负相关" if correlation < 0 else "无相关"
                    })
                except Exception as e:
                    self.logger.warning(f"计算相关性失败: {str(e)}")
        
        # 对相关性进行排序
        if correlations:
            # 按相关性强度排序
            sorted_correlations = sorted(correlations, key=lambda x: abs(x["pearson_correlation"]), reverse=True)
            
            correlation_results.append({
                "type": "pairwise_correlations",
                "correlations": sorted_correlations,
                "strongest_correlation": sorted_correlations[0] if sorted_correlations else None,
                "count": len(sorted_correlations)
            })
            
            # 找出高度相关的图表组
            high_correlations = [c for c in correlations if abs(c["pearson_correlation"]) > 0.8]
            if high_correlations:
                correlation_results.append({
                    "type": "high_correlation_groups",
                    "correlations": high_correlations,
                    "count": len(high_correlations)
                })
            
            # 找出负相关的图表对
            negative_correlations = [c for c in correlations if c["pearson_correlation"] < -0.5]
            if negative_correlations:
                correlation_results.append({
                    "type": "negative_correlations",
                    "correlations": negative_correlations,
                    "count": len(negative_correlations)
                })
        
        return correlation_results
    
    def _extract_chart_data(self, chart: Dict[str, Any]) -> List[float]:
        """
        从图表数据中提取数值数据
        
        参数:
            chart (Dict[str, Any]): 图表数据
            
        返回:
            List[float]: 提取的数值列表
            
        异常:
            ValueError: 如果无法提取数据
        """
        # 对于指标数据
        if "value" in chart:
            # 如果有历史值，使用历史值
            if "historical_values" in chart and isinstance(chart["historical_values"], list):
                return [float(val) for val in chart["historical_values"] if isinstance(val, (int, float))]
            # 否则使用当前值和前期值
            elif "previous_value" in chart:
                return [float(chart["previous_value"]), float(chart["value"])]
            # 只有当前值
            else:
                return [float(chart["value"])]
        
        # 对于图表数据
        elif "data" in chart:
            data = chart["data"]
            
            # 线图和柱状图数据
            if isinstance(data, dict) and "y" in data and isinstance(data["y"], list):
                return [float(val) for val in data["y"] if isinstance(val, (int, float))]
            
            # 散点图数据
            elif isinstance(data, dict) and "values" in data and isinstance(data["values"], list):
                return [float(val) for val in data["values"] if isinstance(val, (int, float))]
            
            # 饼图数据
            elif isinstance(data, dict) and "slices" in data and isinstance(data["slices"], list):
                return [float(slice["value"]) for slice in data["slices"] 
                       if isinstance(slice, dict) and "value" in slice 
                       and isinstance(slice["value"], (int, float))]
                
            # 简单数组数据
            elif isinstance(data, list):
                return [float(val) for val in data if isinstance(val, (int, float))]
        
        # 无法提取数据
        raise ValueError(f"无法从图表数据中提取数值数据")
    
    def _describe_correlation_strength(self, correlation_abs: float) -> str:
        """
        描述相关性强度
        
        参数:
            correlation_abs (float): 相关系数的绝对值
            
        返回:
            str: 相关性强度描述
        """
        if correlation_abs >= 0.9:
            return "极强"
        elif correlation_abs >= 0.7:
            return "强"
        elif correlation_abs >= 0.5:
            return "中等"
        elif correlation_abs >= 0.3:
            return "弱"
        elif correlation_abs >= 0.1:
            return "极弱"
        else:
            return "无相关"
    
    def get_supported_comparison_types(self) -> List[str]:
        """
        获取支持的比较类型
        
        返回:
            List[str]: 支持的比较类型列表
        """
        return self.supported_comparison_types 