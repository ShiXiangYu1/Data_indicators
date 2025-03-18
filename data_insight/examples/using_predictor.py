"""
预测分析器使用示例

演示如何使用data_insight包中的预测分析器进行时间序列预测。
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.core.predictor import Predictor


def load_sample_data(file_path):
    """
    加载示例数据
    
    参数:
        file_path (str): 数据文件路径
        
    返回:
        dict: 加载的数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_sales_forecast():
    """
    分析销售额预测
    """
    print("\n=== 销售额预测分析 ===\n")
    
    # 准备测试数据
    data = {
        "values": [100, 105, 98, 102, 95, 108, 103, 106, 99, 104, 97, 110],
        "time_periods": [f"2023年{i}月" for i in range(1, 13)],
        "current_value": 110,
        "current_period": "2023年12月",
        "name": "月度销售额",
        "unit": "万元"
    }
    
    # 创建预测分析器
    predictor = Predictor()
    
    # 运行预测分析
    result = predictor.analyze(data)
    
    # 打印基本信息
    print("基本信息:")
    for key, value in result["基本信息"].items():
        print(f"{key}: {value}")
    
    # 打印预测结果
    print("\n预测结果:")
    forecast_result = result["预测结果"]
    print(f"预测值: {forecast_result['预测值']}")
    print(f"预测区间: {forecast_result['预测区间']}")
    print(f"预测周期: {forecast_result['预测周期']}")
    print(f"置信度: {forecast_result['置信度']}")
    
    # 打印季节性分析
    seasonal_info = forecast_result["季节性"]
    print("\n季节性分析:")
    print(f"是否存在季节性: {seasonal_info['是否存在']}")
    if seasonal_info["是否存在"]:
        print(f"季节性周期: {seasonal_info['周期']}")
        print(f"季节性强度: {seasonal_info['强度']}")
    
    # 打印异常预测
    print("\n异常预测:")
    anomaly_forecast = result["异常预测"]
    print(f"风险等级: {anomaly_forecast['风险等级']}")
    print(f"异常趋势: {anomaly_forecast['异常趋势']}")
    print(f"建议: {anomaly_forecast['建议']}")


def analyze_seasonal_forecast():
    """
    分析季节性指标预测
    """
    print("\n=== 季节性指标预测分析 ===\n")
    
    # 准备带季节性的测试数据
    data = {
        "values": [80, 60, 40, 80, 60, 40, 80, 60, 40, 80, 60, 40],  # 明显的季度性
        "time_periods": [f"2023年{i}月" for i in range(1, 13)],
        "current_value": 40,
        "current_period": "2023年12月",
        "name": "季度性指标",
        "unit": "个"
    }
    
    # 创建预测分析器
    predictor = Predictor()
    
    # 运行预测分析
    result = predictor.analyze(data)
    
    # 打印基本信息
    print("基本信息:")
    for key, value in result["基本信息"].items():
        print(f"{key}: {value}")
    
    # 打印预测结果
    print("\n预测结果:")
    forecast_result = result["预测结果"]
    print(f"预测值: {forecast_result['预测值']}")
    print(f"预测区间: {forecast_result['预测区间']}")
    print(f"预测周期: {forecast_result['预测周期']}")
    
    # 打印季节性分析
    seasonal_info = forecast_result["季节性"]
    print("\n季节性分析:")
    print(f"是否存在季节性: {seasonal_info['是否存在']}")
    if seasonal_info["是否存在"]:
        print(f"季节性周期: {seasonal_info['周期']}")
        print(f"季节性强度: {seasonal_info['强度']}")


def analyze_trend_forecast():
    """
    分析趋势性指标预测
    """
    print("\n=== 趋势性指标预测分析 ===\n")
    
    # 准备带上升趋势的测试数据
    data = {
        "values": [100 + i * 5 for i in range(12)],  # 线性上升趋势
        "time_periods": [f"2023年{i}月" for i in range(1, 13)],
        "current_value": 155,
        "current_period": "2023年12月",
        "name": "趋势性指标",
        "unit": "个"
    }
    
    # 创建预测分析器
    predictor = Predictor()
    
    # 运行预测分析
    result = predictor.analyze(data)
    
    # 打印基本信息
    print("基本信息:")
    for key, value in result["基本信息"].items():
        print(f"{key}: {value}")
    
    # 打印预测结果
    print("\n预测结果:")
    forecast_result = result["预测结果"]
    print(f"预测值: {forecast_result['预测值']}")
    print(f"预测区间: {forecast_result['预测区间']}")
    print(f"预测周期: {forecast_result['预测周期']}")
    
    # 验证预测值是否保持上升趋势
    forecast_values = forecast_result["预测值"]
    is_increasing = all(forecast_values[i] <= forecast_values[i+1] for i in range(len(forecast_values)-1))
    print(f"\n预测值是否保持上升趋势: {is_increasing}")


def main():
    """主函数"""
    # 运行各种预测分析示例
    analyze_sales_forecast()
    print("\n" + "="*50 + "\n")
    analyze_seasonal_forecast()
    print("\n" + "="*50 + "\n")
    analyze_trend_forecast()


if __name__ == "__main__":
    main() 