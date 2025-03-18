import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class RootCauseAnalyzer:
    """根因分析器类，用于分析指标异常的根本原因"""
    
    def __init__(self):
        """初始化根因分析器"""
        self.anomaly_threshold = 2.0  # 异常阈值（标准差倍数）
        self.correlation_threshold = 0.7  # 相关性阈值
    
    def analyze(
        self,
        metric_name: str,
        current_value: float,
        threshold: float,
        historical_data: List[float],
        related_metrics: Optional[List[Dict[str, Any]]] = None,
        time_window: int = 30
    ) -> Dict[str, Any]:
        """
        分析指标异常的根本原因
        
        Args:
            metric_name: 指标名称
            current_value: 当前值
            threshold: 异常阈值
            historical_data: 历史数据
            related_metrics: 相关指标数据
            time_window: 时间窗口大小
            
        Returns:
            Dict: 分析结果，包含异常原因和解决方案
        """
        # 计算基本统计量
        mean = np.mean(historical_data)
        std = np.std(historical_data)
        
        # 判断是否异常
        is_anomaly = abs(current_value - mean) > threshold * std
        anomaly_degree = abs(current_value - mean) / std if std != 0 else 0
        
        # 分析异常原因
        causes = self._analyze_causes(
            current_value,
            mean,
            std,
            historical_data,
            related_metrics
        )
        
        # 生成解决方案
        solutions = self._generate_solutions(causes)
        
        # 生成分析报告
        report = self._generate_report(
            metric_name,
            current_value,
            mean,
            std,
            is_anomaly,
            anomaly_degree,
            causes,
            solutions
        )
        
        return {
            'metric_name': metric_name,
            'is_anomaly': is_anomaly,
            'anomaly_degree': anomaly_degree,
            'current_value': current_value,
            'mean': mean,
            'std': std,
            'causes': causes,
            'solutions': solutions,
            'report': report
        }
    
    def _analyze_causes(
        self,
        current_value: float,
        mean: float,
        std: float,
        historical_data: List[float],
        related_metrics: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """分析异常原因"""
        causes = []
        
        # 分析数据趋势
        if len(historical_data) > 5:
            trend = np.polyfit(range(len(historical_data)), historical_data, 1)[0]
            if trend > 0:
                causes.append({
                    'type': '趋势',
                    'description': '存在持续上升趋势',
                    'confidence': 0.7
                })
            elif trend < 0:
                causes.append({
                    'type': '趋势',
                    'description': '存在持续下降趋势',
                    'confidence': 0.7
                })
        
        # 分析相关指标
        if related_metrics:
            for metric in related_metrics:
                correlation = self._calculate_correlation(
                    historical_data,
                    metric['values']
                )
                if abs(correlation) > self.correlation_threshold:
                    causes.append({
                        'type': '相关性',
                        'description': f"与指标 {metric['name']} 存在强相关性",
                        'confidence': abs(correlation),
                        'related_metric': metric['name']
                    })
        
        # 分析季节性因素
        if len(historical_data) > 30:
            seasonal_factor = self._detect_seasonality(historical_data)
            if seasonal_factor:
                causes.append({
                    'type': '季节性',
                    'description': f"存在{seasonal_factor}的季节性波动",
                    'confidence': 0.8
                })
        
        return causes
    
    def _calculate_correlation(
        self,
        data1: List[float],
        data2: List[float]
    ) -> float:
        """计算两个数据序列的相关性"""
        if len(data1) != len(data2):
            return 0
        return np.corrcoef(data1, data2)[0, 1]
    
    def _detect_seasonality(self, data: List[float]) -> Optional[str]:
        """检测季节性因素"""
        if len(data) < 30:
            return None
        
        # 使用FFT检测周期性
        fft = np.fft.fft(data)
        frequencies = np.fft.fftfreq(len(data))
        
        # 找到主要频率
        main_freq = frequencies[np.argmax(np.abs(fft[1:len(fft)//2])) + 1]
        period = 1 / main_freq if main_freq != 0 else 0
        
        if 5 <= period <= 7:
            return "周"
        elif 28 <= period <= 31:
            return "月"
        elif 90 <= period <= 92:
            return "季度"
        elif 360 <= period <= 365:
            return "年"
        
        return None
    
    def _generate_solutions(self, causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成解决方案"""
        solutions = []
        
        for cause in causes:
            if cause['type'] == '趋势':
                solutions.append({
                    'type': '趋势调整',
                    'description': '根据趋势调整业务策略',
                    'priority': '高'
                })
            elif cause['type'] == '相关性':
                solutions.append({
                    'type': '关联优化',
                    'description': f"优化与{cause['related_metric']}相关的业务环节",
                    'priority': '中'
                })
            elif cause['type'] == '季节性':
                solutions.append({
                    'type': '季节性应对',
                    'description': '制定季节性应对方案',
                    'priority': '中'
                })
        
        return solutions
    
    def _generate_report(
        self,
        metric_name: str,
        current_value: float,
        mean: float,
        std: float,
        is_anomaly: bool,
        anomaly_degree: float,
        causes: List[Dict[str, Any]],
        solutions: List[Dict[str, Any]]
    ) -> str:
        """生成分析报告"""
        report = f"指标 {metric_name} 的根因分析报告：\n\n"
        
        # 添加异常情况
        report += f"当前值：{current_value:.2f}\n"
        report += f"历史均值：{mean:.2f}\n"
        report += f"标准差：{std:.2f}\n"
        report += f"异常程度：{anomaly_degree:.2f}\n\n"
        
        # 添加原因分析
        if causes:
            report += "异常原因：\n"
            for cause in causes:
                report += f"- {cause['type']}：{cause['description']}\n"
            report += "\n"
        
        # 添加解决方案
        if solutions:
            report += "解决方案：\n"
            for solution in solutions:
                report += f"- {solution['type']}（优先级：{solution['priority']}）：{solution['description']}\n"
        
        return report 