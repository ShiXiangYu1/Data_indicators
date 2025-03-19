#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心分析函数的性能测试
使用pytest-benchmark测试关键函数的性能
"""

import pytest
import pandas as pd
import numpy as np
import time
import psutil
import os
import gc
from datetime import datetime, timedelta

# 假设的导入路径，需根据实际项目结构调整
try:
    from data_insight.analysis.trend import detect_trends, quantify_trend, forecast_trend
    from data_insight.analysis.attribution import perform_attribution_analysis
    from data_insight.utils.performance import MemoryOptimizer, parallel_process, data_chunker
except ImportError:
    # 如果无法导入，创建模拟函数用于测试
    print("警告: 无法导入实际函数，使用模拟函数进行测试")
    
    def detect_trends(data, date_col='date', value_col='value', **kwargs):
        """模拟趋势检测函数"""
        values = data[value_col].values
        slope = np.polyfit(range(len(values)), values, 1)[0]
        direction = "increasing" if slope > 0.1 else "decreasing" if slope < -0.1 else "stable"
        return {"trend_direction": direction, "slope": slope, "confidence": 0.95}
    
    def quantify_trend(data, date_col='date', value_col='value', **kwargs):
        """模拟趋势量化函数"""
        time.sleep(0.01)  # 模拟计算延迟
        values = data[value_col].values
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        residuals = values - (intercept + slope * x)
        r_squared = 1 - (np.sum(residuals**2) / np.sum((values - np.mean(values))**2))
        return {"slope": slope, "intercept": intercept, "r_squared": r_squared}
    
    def forecast_trend(data, date_col='date', value_col='value', forecast_periods=30, **kwargs):
        """模拟趋势预测函数"""
        time.sleep(0.05)  # 模拟预测延迟
        values = data[value_col].values
        slope, intercept = np.polyfit(range(len(values)), values, 1)
        last_date = pd.to_datetime(data[date_col].iloc[-1])
        forecast_dates = [(last_date + timedelta(days=i+1)).strftime("%Y-%m-%d") for i in range(forecast_periods)]
        forecast = [intercept + slope * (len(values) + i) for i in range(1, forecast_periods+1)]
        return {"forecast": forecast, "forecast_dates": forecast_dates}
    
    def perform_attribution_analysis(data, target_col, factor_cols, **kwargs):
        """模拟归因分析函数"""
        time.sleep(0.03)  # 模拟分析延迟
        # 随机生成贡献度
        import random
        factors = []
        remaining = 1.0
        for col in factor_cols[:-1]:
            contrib = round(random.uniform(0.1, remaining), 2)
            remaining -= contrib
            factors.append({"name": col, "contribution": contrib})
        factors.append({"name": factor_cols[-1], "contribution": round(remaining, 2)})
        return {"factors": factors}
    
    class MemoryOptimizer:
        def optimize_dataframe(self, df):
            """模拟内存优化函数"""
            time.sleep(0.02)  # 模拟优化延迟
            return df
    
    def parallel_process(func, items, n_workers=None, chunk_size=None):
        """模拟并行处理函数"""
        return [func(item) for item in items]
    
    def data_chunker(data, chunk_size):
        """模拟数据分块函数"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i+chunk_size]


# 测试夹具：大型数据集
@pytest.fixture
def large_dataset():
    """创建大型测试数据集（10000行）"""
    # 创建日期序列
    dates = pd.date_range('2020-01-01', periods=10000, freq='D')
    
    # 创建有趋势、季节性和噪声的序列
    trend = np.arange(10000) * 0.1  # 线性趋势
    seasonality = 50 * np.sin(np.arange(10000) * 2 * np.pi / 365)  # 季节性波动
    noise = np.random.normal(0, 10, 10000)  # 随机噪声
    
    # 组合所有组件
    values = trend + seasonality + noise
    
    # 创建DataFrame
    return pd.DataFrame({'date': dates, 'value': values})


# 测试夹具：中型数据集
@pytest.fixture
def medium_dataset():
    """创建中型测试数据集（1000行）"""
    # 创建日期序列
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    
    # 创建有趋势、季节性和噪声的序列
    trend = np.arange(1000) * 0.1  # 线性趋势
    seasonality = 50 * np.sin(np.arange(1000) * 2 * np.pi / 365)  # 季节性波动
    noise = np.random.normal(0, 10, 1000)  # 随机噪声
    
    # 组合所有组件
    values = trend + seasonality + noise
    
    # 创建DataFrame
    return pd.DataFrame({'date': dates, 'value': values})


# 测试夹具：小型数据集
@pytest.fixture
def small_dataset():
    """创建小型测试数据集（100行）"""
    # 创建日期序列
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    
    # 创建有趋势、季节性和噪声的序列
    trend = np.arange(100) * 0.1  # 线性趋势
    seasonality = 50 * np.sin(np.arange(100) * 2 * np.pi / 365)  # 季节性波动
    noise = np.random.normal(0, 10, 100)  # 随机噪声
    
    # 组合所有组件
    values = trend + seasonality + noise
    
    # 创建DataFrame
    return pd.DataFrame({'date': dates, 'value': values})


# 测试夹具：多因素数据集
@pytest.fixture
def multi_factor_dataset():
    """创建包含多个因素的数据集，用于归因分析测试"""
    # 创建日期序列
    n_points = 1000
    dates = pd.date_range('2020-01-01', periods=n_points, freq='D')
    
    # 创建多个因素
    np.random.seed(42)  # 保证可重现性
    
    factor1 = np.random.normal(100, 20, n_points)
    factor2 = np.random.normal(50, 10, n_points)
    factor3 = np.random.normal(30, 5, n_points)
    factor4 = np.random.normal(20, 8, n_points)
    
    # 创建目标变量（销售额）
    # 销售额 = 2*factor1 + 1.5*factor2 + 0.8*factor3 + 0.5*factor4 + 噪声
    sales = 2 * factor1 + 1.5 * factor2 + 0.8 * factor3 + 0.5 * factor4 + np.random.normal(0, 50, n_points)
    
    # 确保所有值非负
    factor1 = np.maximum(0, factor1)
    factor2 = np.maximum(0, factor2)
    factor3 = np.maximum(0, factor3)
    factor4 = np.maximum(0, factor4)
    sales = np.maximum(0, sales)
    
    # 创建DataFrame
    return pd.DataFrame({
        'date': dates,
        'sales': sales,
        'advertising': factor1,
        'promotion': factor2,
        'price': factor3,
        'competitor_price': factor4
    })


# 趋势检测性能测试
def test_detect_trends_performance_small(small_dataset, benchmark):
    """测试小型数据集上的趋势检测性能"""
    result = benchmark(detect_trends, small_dataset, date_col='date', value_col='value')
    # 验证结果格式
    assert 'trend_direction' in result
    assert 'slope' in result


def test_detect_trends_performance_medium(medium_dataset, benchmark):
    """测试中型数据集上的趋势检测性能"""
    result = benchmark(detect_trends, medium_dataset, date_col='date', value_col='value')
    # 验证结果格式
    assert 'trend_direction' in result
    assert 'slope' in result


def test_detect_trends_performance_large(large_dataset, benchmark):
    """测试大型数据集上的趋势检测性能"""
    result = benchmark(detect_trends, large_dataset, date_col='date', value_col='value')
    # 验证结果格式
    assert 'trend_direction' in result
    assert 'slope' in result


# 趋势量化性能测试
def test_quantify_trend_performance(large_dataset, benchmark):
    """测试趋势量化函数的性能"""
    result = benchmark(quantify_trend, large_dataset, date_col='date', value_col='value')
    # 验证结果格式
    assert 'slope' in result
    assert 'r_squared' in result


# 趋势预测性能测试
def test_forecast_trend_performance(medium_dataset, benchmark):
    """测试趋势预测函数的性能"""
    # 测试不同预测周期的性能
    forecast_periods = 30
    result = benchmark(forecast_trend, medium_dataset, date_col='date', value_col='value', 
                      forecast_periods=forecast_periods)
    # 验证结果
    assert 'forecast' in result
    assert len(result['forecast']) == forecast_periods


# 归因分析性能测试
def test_attribution_analysis_performance(multi_factor_dataset, benchmark):
    """测试归因分析函数的性能"""
    target_col = 'sales'
    factor_cols = ['advertising', 'promotion', 'price', 'competitor_price']
    
    result = benchmark(perform_attribution_analysis, multi_factor_dataset, 
                      target_col=target_col, factor_cols=factor_cols)
    
    # 验证结果
    assert 'factors' in result
    assert len(result['factors']) == len(factor_cols)


# 内存优化性能测试
def test_memory_optimization_impact():
    """测试内存优化对性能的影响"""
    # 创建一个大型DataFrame
    df = pd.DataFrame({
        'id': range(1000000),
        'value': np.random.randint(0, 100, 1000000),
        'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], 1000000),
        'timestamp': pd.date_range('2020-01-01', periods=1000000, freq='T')
    })
    
    # 记录初始内存使用
    gc.collect()  # 强制垃圾回收
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 应用内存优化
    optimizer = MemoryOptimizer()
    start_time = time.time()
    df_optimized = optimizer.optimize_dataframe(df)
    optimization_time = time.time() - start_time
    
    # 记录优化后内存使用
    gc.collect()  # 强制垃圾回收
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 记录结果
    memory_saved = initial_memory - final_memory
    memory_saved_percent = (memory_saved / initial_memory) * 100 if initial_memory > 0 else 0
    
    print(f"\n内存优化性能结果:")
    print(f"原始内存使用: {initial_memory:.2f} MB")
    print(f"优化后内存使用: {final_memory:.2f} MB")
    print(f"内存节省: {memory_saved:.2f} MB ({memory_saved_percent:.2f}%)")
    print(f"优化耗时: {optimization_time:.4f} 秒")
    
    # 验证数据完整性
    assert len(df) == len(df_optimized)
    assert all(df['id'] == df_optimized['id'])


# 并行处理性能测试
def test_parallel_processing_performance(benchmark):
    """测试并行处理性能"""
    # 定义测试函数
    def process_func(x):
        """模拟耗时处理任务"""
        time.sleep(0.001)  # 小延迟，防止测试时间过长
        return x * x
    
    # 创建大量测试项
    items = list(range(1000))
    
    # 测试串行处理
    start_time = time.time()
    serial_results = [process_func(item) for item in items]
    serial_time = time.time() - start_time
    
    # 测试并行处理
    parallel_results = benchmark(parallel_process, process_func, items)
    
    # 验证结果一致性
    assert serial_results == parallel_results
    
    # 记录结果已在benchmark中自动完成


# 数据分块处理性能测试
def test_data_chunking_performance():
    """测试数据分块处理性能"""
    # 创建大量测试数据
    large_data = list(range(100000))
    
    # 测试不同分块大小
    chunk_sizes = [100, 1000, 10000]
    results = {}
    
    for chunk_size in chunk_sizes:
        start_time = time.time()
        chunks = list(data_chunker(large_data, chunk_size))
        processing_time = time.time() - start_time
        
        # 验证分块结果
        reconstructed_data = []
        for chunk in chunks:
            reconstructed_data.extend(chunk)
        
        assert large_data == reconstructed_data
        
        # 记录结果
        results[chunk_size] = {
            'processing_time': processing_time,
            'num_chunks': len(chunks)
        }
    
    # 打印性能对比
    print("\n数据分块性能结果:")
    for chunk_size, result in results.items():
        print(f"分块大小: {chunk_size}, 处理时间: {result['processing_time']:.6f} 秒, "
              f"分块数量: {result['num_chunks']}")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__, "--benchmark-only"]) 