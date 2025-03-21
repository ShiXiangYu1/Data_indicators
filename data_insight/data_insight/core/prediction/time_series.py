"""
时间序列预测器
==========

用于预测时间序列数据的未来趋势，支持多种预测算法。
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import numpy as np
from datetime import datetime, timedelta
import statistics
import math
from collections import deque

from data_insight.core.interfaces.predictor import PredictorInterface


class TimeSeriesPredictor(PredictorInterface):
    """
    时间序列预测器
    
    用于预测指标的未来趋势，支持多种预测算法，如移动平均、指数平滑、线性回归等。
    """
    
    def __init__(self):
        """初始化时间序列预测器"""
        self.logger = logging.getLogger("data_insight.prediction.time_series")
        self.method = "auto"  # 默认自动选择最佳预测方法
        self.forecast_period = 5  # 默认预测未来5个周期
        self.history_cache = {}  # 缓存历史预测结果
        self.methods = {
            "移动平均": self._moving_average,
            "指数平滑": self._exponential_smoothing,
            "线性回归": self._linear_regression,
            "自适应": self._adaptive_forecasting,
        }
    
    def predict(self, data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        预测时间序列数据的未来趋势
        
        参数:
            data (Dict[str, Any]): 待预测的数据，包含历史数据点
            config (Dict[str, Any], optional): 预测配置，包括预测方法、期数等
            
        返回:
            Dict[str, Any]: 预测结果，包含预测值、预测区间、算法信息等
            
        异常:
            ValueError: 如果输入数据不符合要求或不支持的预测方法
        """
        # 验证输入数据
        self._validate_input(data)
        
        # 提取配置
        config = config or {}
        method = config.get("method", self.method)
        periods = config.get("periods", self.forecast_period)
        
        # 提取指标信息和历史数据
        metric_name = data.get("metric_name", "未知指标")
        metric_unit = data.get("unit", "")
        time_series = data.get("data", [])
        timestamps = data.get("timestamps", [])
        
        # 预处理时间序列数据
        values, dates = self._preprocess_data(time_series, timestamps)
        
        # 检查数据是否足够进行预测
        if len(values) < 3:
            return {
                "status": "error",
                "message": "时间序列数据点不足，至少需要3个数据点进行预测",
                "prediction": []
            }
        
        # 自动选择最佳预测方法
        if method == "auto":
            method = self._select_best_method(values)
        
        # 检查预测方法是否支持
        if method not in self.methods:
            supported_methods = list(self.methods.keys())
            raise ValueError(f"不支持的预测方法: {method}，支持的方法有: {', '.join(supported_methods)}")
        
        # 执行预测
        forecast_values, confidence = self.methods[method](values, periods)
        
        # 生成预测时间戳
        forecast_dates = self._generate_forecast_dates(dates, periods)
        
        # 准备预测结果
        result = {
            "status": "success",
            "指标名称": metric_name,
            "单位": metric_unit,
            "预测方法": method,
            "预测期数": periods,
            "预测值": forecast_values,
            "预测时间": forecast_dates,
            "置信区间": confidence,
            "原始数据点数": len(values),
            "历史数据": values[-10:] if len(values) > 10 else values  # 只返回最近10个历史数据点
        }
        
        # 缓存结果
        cache_key = f"{metric_name}_{periods}"
        self.history_cache[cache_key] = result
        
        return result
    
    def get_supported_methods(self) -> List[str]:
        """
        获取支持的预测方法列表
        
        返回:
            List[str]: 支持的预测方法列表
        """
        return list(self.methods.keys())
    
    def set_default_method(self, method: str) -> bool:
        """
        设置默认预测方法
        
        参数:
            method (str): 预测方法名称
            
        返回:
            bool: 是否成功设置
            
        异常:
            ValueError: 如果不支持该预测方法
        """
        if method not in self.methods and method != "auto":
            supported_methods = list(self.methods.keys())
            raise ValueError(f"不支持的预测方法: {method}，支持的方法有: {', '.join(supported_methods)}")
        
        self.method = method
        return True
    
    def set_forecast_period(self, periods: int) -> bool:
        """
        设置默认预测期数
        
        参数:
            periods (int): 预测期数
            
        返回:
            bool: 是否成功设置
            
        异常:
            ValueError: 如果期数不合法
        """
        if not isinstance(periods, int) or periods <= 0:
            raise ValueError(f"预测期数必须是正整数，但收到了 {periods}")
        
        self.forecast_period = periods
        return True
    
    def clear_cache(self) -> None:
        """清除预测结果缓存"""
        self.history_cache.clear()
    
    def get_cache_keys(self) -> List[str]:
        """
        获取缓存的预测结果键列表
        
        返回:
            List[str]: 缓存的预测结果键列表
        """
        return list(self.history_cache.keys())
    
    def get_cached_prediction(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的预测结果
        
        参数:
            key (str): 缓存键，通常为 "指标名称_预测期数"
            
        返回:
            Optional[Dict[str, Any]]: 缓存的预测结果，如果不存在则返回None
        """
        return self.history_cache.get(key)
    
    def _validate_input(self, data: Dict[str, Any]) -> bool:
        """
        验证输入数据是否符合要求
        
        参数:
            data (Dict[str, Any]): 待验证的数据
            
        返回:
            bool: 验证是否通过
            
        异常:
            ValueError: 如果输入数据不符合要求
        """
        if not isinstance(data, dict):
            raise TypeError(f"输入数据必须是字典类型，但收到了 {type(data)}")
        
        # 检查必需字段
        required_fields = ["data"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
        
        # 检查数据字段
        if not isinstance(data["data"], (list, tuple)) or not data["data"]:
            raise ValueError("数据字段必须是非空列表或元组")
        
        # 检查时间戳字段（如果存在）
        if "timestamps" in data and len(data["timestamps"]) != len(data["data"]):
            raise ValueError("时间戳数量与数据点数量不匹配")
        
        return True
    
    def _preprocess_data(self, values: List[Any], timestamps: Optional[List[Any]] = None) -> Tuple[List[float], List[str]]:
        """
        预处理时间序列数据
        
        参数:
            values (List[Any]): 数据点列表
            timestamps (List[Any], optional): 时间戳列表
            
        返回:
            Tuple[List[float], List[str]]: 处理后的数据点和时间戳
        """
        # 转换数据点为浮点数
        processed_values = []
        for value in values:
            try:
                processed_values.append(float(value))
            except (ValueError, TypeError):
                self.logger.warning(f"跳过无法转换为浮点数的数据点: {value}")
        
        # 处理时间戳
        processed_timestamps = []
        if timestamps and len(timestamps) == len(values):
            for ts in timestamps:
                if isinstance(ts, (datetime, str)):
                    if isinstance(ts, str):
                        try:
                            # 尝试解析时间戳字符串
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            processed_timestamps.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                        except (ValueError, TypeError):
                            processed_timestamps.append(str(ts))
                    else:
                        processed_timestamps.append(ts.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    processed_timestamps.append(str(ts))
        else:
            # 如果没有时间戳，创建连续的整数索引
            processed_timestamps = [str(i) for i in range(len(processed_values))]
        
        return processed_values, processed_timestamps
    
    def _select_best_method(self, values: List[float]) -> str:
        """
        自动选择最佳预测方法
        
        参数:
            values (List[float]): 时间序列数据
            
        返回:
            str: 最佳预测方法名称
        """
        # 简单规则：
        # 1. 少于5个数据点，使用移动平均
        # 2. 数据波动较大，使用指数平滑
        # 3. 数据有明显趋势，使用线性回归
        # 4. 其他情况使用自适应方法
        
        if len(values) < 5:
            return "移动平均"
        
        # 计算波动性（标准差与均值的比值，即变异系数）
        mean = sum(values) / len(values)
        if mean == 0:
            variation = float('inf')
        else:
            variation = statistics.stdev(values) / abs(mean)
        
        # 检查趋势
        has_trend = False
        if len(values) >= 10:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            # 如果后半部分与前半部分相差超过20%，认为有趋势
            if abs(second_avg - first_avg) > 0.2 * first_avg:
                has_trend = True
        
        if has_trend:
            return "线性回归"
        elif variation > 0.3:  # 波动较大
            return "指数平滑"
        else:
            return "自适应"
    
    def _generate_forecast_dates(self, dates: List[str], periods: int) -> List[str]:
        """
        生成预测时间戳
        
        参数:
            dates (List[str]): 历史时间戳
            periods (int): 预测期数
            
        返回:
            List[str]: 预测时间戳
        """
        # 尝试从最后一个日期推断下一个日期
        try:
            last_date = datetime.strptime(dates[-1], '%Y-%m-%d %H:%M:%S')
            interval = None
            
            # 至少需要两个日期来推断间隔
            if len(dates) >= 2:
                prev_date = datetime.strptime(dates[-2], '%Y-%m-%d %H:%M:%S')
                interval = last_date - prev_date
            
            if interval:
                return [(last_date + interval * (i + 1)).strftime('%Y-%m-%d %H:%M:%S') for i in range(periods)]
            else:
                # 默认间隔为1天
                return [(last_date + timedelta(days=i + 1)).strftime('%Y-%m-%d %H:%M:%S') for i in range(periods)]
        except (ValueError, TypeError):
            # 如果日期格式无法解析，使用简单递增
            last_idx = int(dates[-1]) if dates[-1].isdigit() else len(dates) - 1
            return [str(last_idx + i + 1) for i in range(periods)]
    
    def _moving_average(self, values: List[float], periods: int) -> Tuple[List[float], List[Dict[str, float]]]:
        """
        移动平均预测
        
        参数:
            values (List[float]): 历史数据点
            periods (int): 预测期数
            
        返回:
            Tuple[List[float], List[Dict[str, float]]]: 预测值和置信区间
        """
        # 确定窗口大小，通常使用数据长度的三分之一或5（取较小者）
        window_size = min(5, len(values) // 3)
        if window_size < 1:
            window_size = 1
        
        # 计算移动平均
        window = deque(values[-window_size:])
        forecast = []
        
        for _ in range(periods):
            # 计算窗口内的平均值
            next_val = sum(window) / len(window)
            forecast.append(next_val)
            
            # 更新窗口
            window.popleft()
            window.append(next_val)
        
        # 计算置信区间
        # 使用历史数据的标准差来估计预测误差
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        confidence = []
        
        for i, val in enumerate(forecast):
            # 置信区间随着预测期数增加而扩大
            interval = std_dev * (1 + 0.1 * i)
            confidence.append({
                "lower": val - 1.96 * interval,  # 95%置信区间
                "upper": val + 1.96 * interval
            })
        
        return forecast, confidence
    
    def _exponential_smoothing(self, values: List[float], periods: int) -> Tuple[List[float], List[Dict[str, float]]]:
        """
        指数平滑预测
        
        参数:
            values (List[float]): 历史数据点
            periods (int): 预测期数
            
        返回:
            Tuple[List[float], List[Dict[str, float]]]: 预测值和置信区间
        """
        # 确定平滑系数，通常在0.1-0.3之间
        alpha = 0.2
        
        # 初始化预测值为最后一个观测值
        last_value = values[-1]
        forecast = []
        
        for _ in range(periods):
            # 计算下一个预测值
            next_val = alpha * last_value + (1 - alpha) * (forecast[-1] if forecast else last_value)
            forecast.append(next_val)
            
            # 更新"最后一个观测值"为刚刚预测的值
            last_value = next_val
        
        # 计算置信区间
        # 使用历史预测误差的平方和来估计预测误差
        errors = []
        for i in range(1, len(values)):
            pred = alpha * values[i-1] + (1 - alpha) * (values[i-2] if i > 1 else values[i-1])
            errors.append((values[i] - pred) ** 2)
        
        mse = sum(errors) / len(errors) if errors else 0
        rmse = math.sqrt(mse)
        
        confidence = []
        for i, val in enumerate(forecast):
            # 置信区间随着预测期数增加而扩大
            interval = rmse * (1 + 0.15 * i)
            confidence.append({
                "lower": val - 1.96 * interval,  # 95%置信区间
                "upper": val + 1.96 * interval
            })
        
        return forecast, confidence
    
    def _linear_regression(self, values: List[float], periods: int) -> Tuple[List[float], List[Dict[str, float]]]:
        """
        线性回归预测
        
        参数:
            values (List[float]): 历史数据点
            periods (int): 预测期数
            
        返回:
            Tuple[List[float], List[Dict[str, float]]]: 预测值和置信区间
        """
        # 准备数据
        x = np.array(range(len(values)))
        y = np.array(values)
        
        # 计算线性回归参数
        n = len(values)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xx = np.sum(x * x)
        sum_xy = np.sum(x * y)
        
        # 计算斜率和截距
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # 预测未来值
        forecast = []
        for i in range(1, periods + 1):
            next_x = len(values) + i - 1
            next_val = slope * next_x + intercept
            forecast.append(next_val)
        
        # 计算置信区间
        # 计算残差平方和
        y_pred = slope * x + intercept
        residuals = y - y_pred
        sse = np.sum(residuals ** 2)
        
        # 标准误差
        stderr = math.sqrt(sse / (n - 2))
        
        confidence = []
        for i, val in enumerate(forecast):
            # 预测区间系数
            t_value = 1.96  # 近似95%置信度的t值
            
            # 这里用简化公式估计预测区间
            interval = t_value * stderr * math.sqrt(1 + 1/n + (i + 1)**2 / sum_xx)
            confidence.append({
                "lower": val - interval,
                "upper": val + interval
            })
        
        return forecast, confidence
    
    def _adaptive_forecasting(self, values: List[float], periods: int) -> Tuple[List[float], List[Dict[str, float]]]:
        """
        自适应预测方法
        
        参数:
            values (List[float]): 历史数据点
            periods (int): 预测期数
            
        返回:
            Tuple[List[float], List[Dict[str, float]]]: 预测值和置信区间
        """
        # 简单实现：组合多种方法的结果
        ma_forecast, ma_conf = self._moving_average(values, periods)
        es_forecast, es_conf = self._exponential_smoothing(values, periods)
        lr_forecast, lr_conf = self._linear_regression(values, periods)
        
        # 计算加权平均
        forecast = []
        confidence = []
        
        # 确定权重（这里可以根据历史表现动态调整）
        ma_weight = 0.3
        es_weight = 0.3
        lr_weight = 0.4
        
        for i in range(periods):
            # 加权平均预测值
            weighted_val = (ma_forecast[i] * ma_weight + 
                           es_forecast[i] * es_weight + 
                           lr_forecast[i] * lr_weight)
            forecast.append(weighted_val)
            
            # 合并置信区间（简单取平均）
            lower = (ma_conf[i]["lower"] * ma_weight + 
                    es_conf[i]["lower"] * es_weight + 
                    lr_conf[i]["lower"] * lr_weight)
            upper = (ma_conf[i]["upper"] * ma_weight + 
                    es_conf[i]["upper"] * es_weight + 
                    lr_conf[i]["upper"] * lr_weight)
            confidence.append({"lower": lower, "upper": upper})
        
        return forecast, confidence

    # 添加缺少的抽象方法实现
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证输入数据是否包含所有必需字段
        
        参数:
            data (Dict[str, Any]): 需要验证的数据
            required_fields (List[str]): 必需字段列表
            
        返回:
            bool: 验证是否通过
            
        异常:
            ValueError: 如果缺少必需字段
        """
        if not isinstance(data, dict):
            raise ValueError("输入数据必须是字典类型")
            
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")
                
        return True
    
    def get_supported_models(self) -> List[str]:
        """
        获取预测器支持的模型列表
        
        返回:
            List[str]: 支持的模型名称列表
        """
        return self.get_supported_methods()
    
    def set_model(self, model_name: str, model_params: Optional[Dict[str, Any]] = None) -> bool:
        """
        设置预测模型
        
        参数:
            model_name (str): 模型名称
            model_params (Dict[str, Any], optional): 模型参数
            
        返回:
            bool: 是否成功设置模型
            
        异常:
            ValueError: 如果模型名称不受支持
        """
        return self.set_default_method(model_name)
    
    def evaluate(self, test_data: Dict[str, Any], metrics: List[str]) -> Dict[str, float]:
        """
        评估预测模型性能
        
        参数:
            test_data (Dict[str, Any]): 测试数据
            metrics (List[str]): 评估指标列表
            
        返回:
            Dict[str, float]: 各评估指标的值
            
        异常:
            ValueError: 如果评估指标不受支持
        """
        # 临时实现，返回空评估结果
        self.logger.warning("evaluate方法尚未完全实现")
        return {metric: 0.0 for metric in metrics}
    
    def detect_anomalies(self, data: Dict[str, Any], threshold: float = 0.05) -> Dict[str, Any]:
        """
        检测数据中的异常点
        
        参数:
            data (Dict[str, Any]): 数据
            threshold (float, optional): 异常阈值，默认为0.05
            
        返回:
            Dict[str, Any]: 异常检测结果
        """
        # 临时实现，返回空异常检测结果
        self.logger.warning("detect_anomalies方法尚未完全实现")
        return {
            "anomalies": [],
            "threshold": threshold,
            "status": "warning",
            "message": "异常检测功能尚未完全实现"
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取预测器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、支持的模型等
        """
        return {
            "name": "时间序列预测器",
            "version": "0.1.0",
            "description": "用于预测时间序列数据的未来趋势，支持多种预测算法",
            "supported_models": self.get_supported_models(),
            "default_method": self.method,
            "forecast_period": self.forecast_period
        } 