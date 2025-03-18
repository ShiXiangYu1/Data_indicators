"""
归因分析器
========

分析指标变化的归因，确定哪些因素对结果产生了最大的影响，以及量化这些因素的贡献度。
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

from data_insight.core.base_analyzer import BaseAnalyzer


class AttributionAnalyzer(BaseAnalyzer):
    """
    归因分析器
    
    分析指标变化的归因，确定哪些因素对结果产生了最大的影响，以及量化这些因素的贡献度。
    """
    
    def __init__(self, method: str = "linear", min_correlation: float = 0.3, max_factors: int = 5):
        """
        初始化归因分析器
        
        参数:
            method (str): 归因方法，支持 "linear"(线性回归), "random_forest"(随机森林)
            min_correlation (float): 最小相关系数，低于此值的因素将被忽略
            max_factors (int): 结果中最多包含的因素数量
        """
        super().__init__()
        self.method = method
        self.min_correlation = min_correlation
        self.max_factors = max_factors
        
        # 分析方法映射
        self.method_mapping = {
            "linear": self._linear_attribution,
            "random_forest": self._random_forest_attribution
        }
        
        # 影响类型分类阈值
        self.impact_thresholds = {
            "主要": 0.5,  # 贡献度大于50%为主要因素
            "重要": 0.3,  # 贡献度大于30%为重要因素
            "次要": 0.1,  # 贡献度大于10%为次要因素
            "微弱": 0.0   # 贡献度大于0%为微弱影响
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析指标变化的归因
        
        参数:
            data (Dict[str, Any]): 输入数据，应包含以下字段:
                - target: 目标指标名称
                - target_values: 目标指标历史值列表
                - factors: 影响因素字典，每个因素包含其历史值列表
                - time_periods: 时间周期列表(可选)
                - current_period: 当前时间周期(可选)
                - method: 归因方法(可选)，覆盖默认方法
            
        返回:
            Dict[str, Any]: 分析结果，包含归因信息
        """
        # 验证必要字段
        required_fields = ["target", "target_values", "factors"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        target = data["target"]
        target_values = data["target_values"]
        factors = data["factors"]
        time_periods = data.get("time_periods", [f"T{i+1}" for i in range(len(target_values))])
        current_period = data.get("current_period", time_periods[-1] if time_periods else "当前")
        
        # 获取归因方法，优先使用输入数据中指定的方法
        method = data.get("method", self.method)
        if method not in self.method_mapping:
            raise ValueError(f"不支持的归因方法: {method}，支持的方法有: {list(self.method_mapping.keys())}")
        
        # 检查数据长度一致性
        for factor_name, factor_values in factors.items():
            if len(factor_values) != len(target_values):
                raise ValueError(f"因素 '{factor_name}' 的数据长度 ({len(factor_values)}) 与目标指标数据长度 ({len(target_values)}) 不一致")
        
        # 数据预处理
        processed_data = self._preprocess_data(target_values, factors)
        
        # 计算相关性，初步筛选因素
        correlations = self._calculate_correlations(processed_data)
        filtered_factors = self._filter_factors(correlations)
        
        # 归因分析
        attribution_result = self.method_mapping[method](
            processed_data, filtered_factors, target_values
        )
        
        # 对归因结果进行分类
        classified_attributions = self._classify_attributions(attribution_result)
        
        # 计算置信度
        confidence = self._calculate_confidence(attribution_result, processed_data)
        
        # 构建结果
        result = {
            "基本信息": {
                "目标指标": target,
                "分析方法": method,
                "当前周期": current_period,
                "数据周期数": len(target_values),
                "分析因素数": len(factors)
            },
            "归因结果": {
                "影响因素": classified_attributions,
                "覆盖度": attribution_result["total_explained"],
                "置信度": confidence,
                "未解释占比": 1.0 - attribution_result["total_explained"]
            },
            "相关性分析": {
                "因素相关性": {
                    factor: {
                        "相关系数": corr,
                        "相关方向": "正相关" if corr > 0 else "负相关"
                    } for factor, corr in correlations.items() if abs(corr) >= self.min_correlation
                }
            }
        }
        
        # 添加各时间周期的贡献数据(如果时间周期提供的话)
        if len(time_periods) == len(target_values):
            result["时间序列分析"] = {
                "时间周期": time_periods,
                "目标指标": target_values,
                "主要影响因素": attribution_result.get("time_series_impacts", {})
            }
        
        return result
    
    def _preprocess_data(self, target_values: List[float], factors: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        数据预处理
        
        参数:
            target_values (List[float]): 目标指标历史值列表
            factors (Dict[str, List[float]]): 影响因素字典，每个因素包含其历史值列表
            
        返回:
            Dict[str, Any]: 预处理后的数据
        """
        # 构建数据框
        data = {factor_name: factor_values for factor_name, factor_values in factors.items()}
        data["target"] = target_values
        df = pd.DataFrame(data)
        
        # 处理缺失值
        df = df.fillna(df.mean())
        
        # 标准化特征
        scaler = StandardScaler()
        features = list(factors.keys())
        df[features] = scaler.fit_transform(df[features])
        
        return {
            "df": df,
            "features": features,
            "scaler": scaler,
            "raw_data": {
                "target": target_values,
                "factors": factors
            }
        }
    
    def _calculate_correlations(self, processed_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算目标指标与各因素的相关性
        
        参数:
            processed_data (Dict[str, Any]): 预处理后的数据
            
        返回:
            Dict[str, float]: 各因素与目标指标的相关系数
        """
        df = processed_data["df"]
        correlations = {}
        
        # 计算各特征与目标的相关系数
        for feature in processed_data["features"]:
            correlations[feature] = df[feature].corr(df["target"])
        
        return correlations
    
    def _filter_factors(self, correlations: Dict[str, float]) -> List[str]:
        """
        基于相关性筛选因素
        
        参数:
            correlations (Dict[str, float]): 各因素与目标指标的相关系数
            
        返回:
            List[str]: 筛选后的因素列表
        """
        # 按相关系数绝对值排序
        sorted_factors = sorted(
            correlations.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        
        # 筛选相关系数大于阈值的因素，并限制数量
        filtered_factors = [
            factor for factor, corr in sorted_factors 
            if abs(corr) >= self.min_correlation
        ][:self.max_factors]
        
        return filtered_factors
    
    def _linear_attribution(
        self, 
        processed_data: Dict[str, Any], 
        filtered_factors: List[str],
        target_values: List[float]
    ) -> Dict[str, Any]:
        """
        使用线性回归进行归因分析
        
        参数:
            processed_data (Dict[str, Any]): 预处理后的数据
            filtered_factors (List[str]): 筛选后的因素列表
            target_values (List[float]): 目标指标历史值列表
            
        返回:
            Dict[str, Any]: 归因结果
        """
        df = processed_data["df"]
        
        # 如果没有足够的筛选因素，返回空结果
        if len(filtered_factors) == 0:
            return {
                "attributions": {},
                "total_explained": 0.0
            }
        
        # 构建特征矩阵和目标向量
        X = df[filtered_factors].values
        y = df["target"].values
        
        # 线性回归模型
        model = LinearRegression()
        model.fit(X, y)
        
        # 计算模型解释度
        r2 = model.score(X, y)
        
        # 计算各因素的贡献比例
        coefficients = model.coef_
        importance = np.abs(coefficients) / np.sum(np.abs(coefficients)) if np.sum(np.abs(coefficients)) > 0 else np.zeros_like(coefficients)
        
        # 构建归因结果
        attributions = {}
        for i, factor in enumerate(filtered_factors):
            attributions[factor] = {
                "贡献度": importance[i] * r2,  # 贡献度 = 重要性 * 模型解释度
                "系数": coefficients[i],
                "方向": "正向" if coefficients[i] > 0 else "负向"
            }
        
        # 计算各时间点的主要影响因素
        time_series_impacts = {}
        for i in range(len(target_values)):
            # 对于每个时间点，找出贡献最大的因素
            max_impact_factor = None
            max_impact_value = 0
            for factor in filtered_factors:
                impact = abs(df[factor].iloc[i] * model.coef_[filtered_factors.index(factor)])
                if impact > max_impact_value:
                    max_impact_value = impact
                    max_impact_factor = factor
            
            if max_impact_factor:
                time_series_impacts[i] = {
                    "因素": max_impact_factor,
                    "影响值": df[max_impact_factor].iloc[i] * model.coef_[filtered_factors.index(max_impact_factor)]
                }
        
        return {
            "attributions": attributions,
            "total_explained": r2,
            "model": model,
            "time_series_impacts": time_series_impacts
        }
    
    def _random_forest_attribution(
        self, 
        processed_data: Dict[str, Any], 
        filtered_factors: List[str],
        target_values: List[float]
    ) -> Dict[str, Any]:
        """
        使用随机森林进行归因分析
        
        参数:
            processed_data (Dict[str, Any]): 预处理后的数据
            filtered_factors (List[str]): 筛选后的因素列表
            target_values (List[float]): 目标指标历史值列表
            
        返回:
            Dict[str, Any]: 归因结果
        """
        df = processed_data["df"]
        
        # 如果没有足够的筛选因素，返回空结果
        if len(filtered_factors) == 0:
            return {
                "attributions": {},
                "total_explained": 0.0
            }
        
        # 构建特征矩阵和目标向量
        X = df[filtered_factors].values
        y = df["target"].values
        
        # 随机森林模型
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # 计算模型解释度
        r2 = model.score(X, y)
        
        # 获取特征重要性
        importance = model.feature_importances_
        
        # 构建归因结果
        attributions = {}
        for i, factor in enumerate(filtered_factors):
            # 计算特征方向(通过相关系数)
            direction = "正向" if df[factor].corr(df["target"]) > 0 else "负向"
            
            attributions[factor] = {
                "贡献度": importance[i] * r2,  # 贡献度 = 重要性 * 模型解释度
                "重要性": importance[i],
                "方向": direction
            }
        
        # 计算各时间点的主要影响因素
        # 对于随机森林，我们可以通过特征值和特征重要性的乘积来近似计算影响
        time_series_impacts = {}
        for i in range(len(target_values)):
            # 对于每个时间点，找出贡献最大的因素
            factor_impacts = {}
            for j, factor in enumerate(filtered_factors):
                # 使用特征值和特征重要性的乘积作为影响指标
                normalized_value = df[factor].iloc[i]  # 已经标准化的特征值
                impact = normalized_value * importance[j]
                factor_impacts[factor] = impact
            
            # 选择影响最大的因素
            max_impact_factor = max(factor_impacts.items(), key=lambda x: abs(x[1]), default=(None, 0))
            if max_impact_factor[0]:
                time_series_impacts[i] = {
                    "因素": max_impact_factor[0],
                    "影响值": max_impact_factor[1]
                }
        
        return {
            "attributions": attributions,
            "total_explained": r2,
            "model": model,
            "time_series_impacts": time_series_impacts
        }
    
    def _classify_attributions(self, attribution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        对归因结果进行分类
        
        参数:
            attribution_result (Dict[str, Any]): 归因分析结果
            
        返回:
            List[Dict[str, Any]]: 分类后的影响因素列表
        """
        # 获取归因结果
        attributions = attribution_result.get("attributions", {})
        
        # 对因素按贡献度排序
        sorted_factors = sorted(
            attributions.items(),
            key=lambda x: x[1]["贡献度"],
            reverse=True
        )
        
        # 分类结果
        classified_attributions = []
        
        for factor, attrs in sorted_factors:
            # 确定影响类型
            impact_type = "微弱"
            for level, threshold in self.impact_thresholds.items():
                if attrs["贡献度"] >= threshold:
                    impact_type = level
                    break
            
            # 构建分类结果
            classified_attrs = {
                "因素名称": factor,
                "贡献度": attrs["贡献度"],
                "影响类型": impact_type,
                "影响方向": attrs.get("方向", "未知")
            }
            
            # 添加系数(如果有)
            if "系数" in attrs:
                classified_attrs["系数"] = attrs["系数"]
            
            # 添加重要性(如果有)
            if "重要性" in attrs:
                classified_attrs["重要性"] = attrs["重要性"]
            
            classified_attributions.append(classified_attrs)
        
        return classified_attributions
    
    def _calculate_confidence(self, attribution_result: Dict[str, Any], processed_data: Dict[str, Any]) -> str:
        """
        计算归因结果的置信度
        
        参数:
            attribution_result (Dict[str, Any]): 归因分析结果
            processed_data (Dict[str, Any]): 预处理后的数据
            
        返回:
            str: 置信度级别描述
        """
        # 数据点数量
        data_points = len(processed_data["df"])
        
        # 模型解释度
        explained_variance = attribution_result.get("total_explained", 0)
        
        # 筛选因素数量
        factor_count = len(attribution_result.get("attributions", {}))
        
        # 根据数据点数量、模型解释度和因素数量综合评估置信度
        if data_points < 10:
            # 数据点太少，置信度低
            confidence = "低"
        elif data_points >= 30 and explained_variance >= 0.7 and factor_count >= 3:
            # 数据点充足，模型解释度高，因素覆盖全面
            confidence = "高"
        elif data_points >= 20 and explained_variance >= 0.5 and factor_count >= 2:
            # 数据点较多，模型解释度中等，因素覆盖较全面
            confidence = "中"
        else:
            confidence = "低"
        
        return confidence 