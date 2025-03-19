#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标分析系统端到端测试
测试完整的分析流程，从数据输入到结果输出
"""

import pytest
import json
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
import requests
from pathlib import Path
import time
import uuid

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"
TIMEOUT = 30  # 请求超时时间（秒）
TEST_DATA_DIR = Path(__file__).parent / "test_data"
RESULTS_DIR = Path(__file__).parent / "results"

# 确保测试数据和结果目录存在
TEST_DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


# 测试前的准备工作
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """设置测试环境"""
    logger.info("设置端到端测试环境")
    
    # 检查API服务是否正常运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code != 200:
            logger.error(f"API服务未正常运行，状态码: {response.status_code}")
            pytest.skip("API服务未正常运行，跳过测试")
    except requests.RequestException as e:
        logger.error(f"无法连接到API服务: {e}")
        pytest.skip("无法连接到API服务，跳过测试")
    
    # 生成测试数据文件
    generate_test_data()
    
    yield
    
    # 测试结束后的清理工作
    logger.info("清理端到端测试环境")


def generate_test_data():
    """生成测试所需的各类数据集"""
    logger.info("生成测试数据")
    
    # 生成趋势分析测试数据
    generate_trend_data()
    
    # 生成归因分析测试数据
    generate_attribution_data()
    
    # 生成相关性分析测试数据
    generate_correlation_data()


def generate_trend_data():
    """生成趋势分析测试数据"""
    # 创建四种不同类型的趋势数据
    
    # 1. 上升趋势
    dates = pd.date_range('2022-01-01', periods=90, freq='D')
    increasing_trend = np.linspace(100, 300, 90) + np.random.normal(0, 15, 90)
    df_increasing = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'value': increasing_trend
    })
    
    # 2. 下降趋势
    decreasing_trend = np.linspace(300, 100, 90) + np.random.normal(0, 15, 90)
    df_decreasing = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'value': decreasing_trend
    })
    
    # 3. 稳定趋势
    stable_trend = np.ones(90) * 200 + np.random.normal(0, 15, 90)
    df_stable = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'value': stable_trend
    })
    
    # 4. 季节性趋势
    t = np.arange(90)
    seasonal_trend = 200 + 50 * np.sin(2 * np.pi * t / 30) + np.linspace(0, 50, 90) + np.random.normal(0, 10, 90)
    df_seasonal = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'value': seasonal_trend
    })
    
    # 保存数据集
    df_increasing.to_csv(TEST_DATA_DIR / "trend_increasing.csv", index=False)
    df_decreasing.to_csv(TEST_DATA_DIR / "trend_decreasing.csv", index=False)
    df_stable.to_csv(TEST_DATA_DIR / "trend_stable.csv", index=False)
    df_seasonal.to_csv(TEST_DATA_DIR / "trend_seasonal.csv", index=False)


def generate_attribution_data():
    """生成归因分析测试数据"""
    # 创建一个包含多个影响因素的数据集
    np.random.seed(42)
    dates = pd.date_range('2022-01-01', periods=90, freq='D')
    
    # 基础因素
    advertising = 100 + np.random.normal(0, 20, 90)
    price = 50 + np.random.normal(0, 5, 90)
    promotion = np.random.choice([0, 1], size=90, p=[0.7, 0.3])
    competitor_price = 55 + np.random.normal(0, 8, 90)
    season_effect = 10 * np.sin(2 * np.pi * np.arange(90) / 30)
    
    # 创建销售数据，受多种因素影响
    sales = (
        2 * advertising +  # 广告效果
        -3 * price +       # 价格效果（负相关）
        100 * promotion +  # 促销效果
        2 * competitor_price +  # 竞争对手价格效果
        season_effect +    # 季节效果
        np.random.normal(0, 100, 90)  # 随机噪声
    )
    
    # 确保数据为正
    sales = np.maximum(sales, 0)
    advertising = np.maximum(advertising, 0)
    price = np.maximum(price, 0)
    competitor_price = np.maximum(competitor_price, 0)
    
    # 创建DataFrame
    df_attribution = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'sales': sales,
        'advertising': advertising,
        'price': price,
        'promotion': promotion,
        'competitor_price': competitor_price
    })
    
    # 保存数据集
    df_attribution.to_csv(TEST_DATA_DIR / "attribution_data.csv", index=False)


def generate_correlation_data():
    """生成相关性分析测试数据"""
    np.random.seed(42)
    n = 1000
    
    # 创建相关的变量
    x1 = np.random.normal(0, 1, n)
    x2 = 0.8 * x1 + 0.2 * np.random.normal(0, 1, n)  # 强相关
    x3 = 0.4 * x1 + 0.6 * np.random.normal(0, 1, n)  # 中等相关
    x4 = 0.1 * x1 + 0.9 * np.random.normal(0, 1, n)  # 弱相关
    x5 = -0.7 * x1 + 0.3 * np.random.normal(0, 1, n)  # 负相关
    x6 = np.random.normal(0, 1, n)  # 不相关
    
    # 创建DataFrame
    df_correlation = pd.DataFrame({
        'x1': x1,
        'x2': x2,
        'x3': x3,
        'x4': x4,
        'x5': x5,
        'x6': x6
    })
    
    # 保存数据集
    df_correlation.to_csv(TEST_DATA_DIR / "correlation_data.csv", index=False)


# 辅助函数
def wait_for_analysis_completion(analysis_id, max_wait=180):
    """等待分析完成并获取结果"""
    url = f"{BASE_URL}{API_PREFIX}/analyses/{analysis_id}/status"
    start_time = time.time()
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > max_wait:
            raise TimeoutError(f"等待分析完成超时，已等待{max_wait}秒")
        
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            status_data = response.json()
            status = status_data.get("status")
            
            if status == "COMPLETED":
                return True
            elif status == "FAILED":
                error_msg = status_data.get("error", "未知错误")
                raise Exception(f"分析失败: {error_msg}")
            
            # 继续等待
            logger.info(f"分析进行中，状态: {status}，已等待: {int(elapsed_time)}秒")
            time.sleep(3)
            
        except requests.RequestException as e:
            logger.error(f"检查分析状态时出错: {e}")
            time.sleep(5)


def save_test_result(test_name, result_data):
    """保存测试结果到文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{test_name}_{timestamp}.json"
    file_path = RESULTS_DIR / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"测试结果已保存到: {file_path}")
    return file_path


# 测试用例 - 趋势分析
@pytest.mark.parametrize(
    "trend_type,expected_direction", 
    [
        ("increasing", "上升"),
        ("decreasing", "下降"),
        ("stable", "稳定"),
        ("seasonal", "季节性")
    ]
)
def test_trend_analysis_pipeline(trend_type, expected_direction):
    """测试趋势分析完整流程"""
    logger.info(f"开始测试趋势分析流程: {trend_type}")
    
    # 1. 读取测试数据
    data_file = TEST_DATA_DIR / f"trend_{trend_type}.csv"
    if not data_file.exists():
        pytest.skip(f"测试数据文件不存在: {data_file}")
    
    df = pd.read_csv(data_file)
    data = df.to_dict(orient="records")
    
    # 2. 发送趋势分析请求
    analysis_request = {
        "data": data,
        "date_column": "date",
        "value_column": "value",
        "analysis_type": "trend",
        "options": {
            "detect_seasonality": True,
            "detect_change_points": True,
            "forecast_periods": 30
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/analyses/trend",
            json=analysis_request,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        analysis_data = response.json()
        analysis_id = analysis_data.get("analysis_id")
        
        assert analysis_id, "响应中缺少analysis_id"
        logger.info(f"趋势分析已提交，分析ID: {analysis_id}")
        
        # 3. 等待分析完成
        wait_for_analysis_completion(analysis_id)
        
        # 4. 获取分析结果
        result_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/analyses/{analysis_id}/result",
            timeout=TIMEOUT
        )
        result_response.raise_for_status()
        
        result_data = result_response.json()
        
        # 5. 验证结果
        assert "trend_info" in result_data, "结果中缺少trend_info"
        assert "trend_direction" in result_data["trend_info"], "结果中缺少trend_direction"
        
        # 汉化后的趋势方向
        trend_direction = result_data["trend_info"]["trend_direction"]
        
        # 保存测试结果
        save_test_result(f"trend_analysis_{trend_type}", result_data)
        
        # 验证趋势方向是否符合预期
        assert expected_direction in trend_direction, f"预期趋势方向为'{expected_direction}'，实际为'{trend_direction}'"
        
        logger.info(f"趋势分析测试通过: {trend_type}, 检测到的趋势: {trend_direction}")
        
        # 6. 获取智能建议
        suggestion_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/suggestion/generate",
            json={
                "analysis_id": analysis_id,
                "analysis_type": "trend",
                "metric_name": "测试指标"
            },
            timeout=TIMEOUT
        )
        
        if suggestion_response.status_code == 200:
            suggestion_data = suggestion_response.json()
            save_test_result(f"trend_suggestion_{trend_type}", suggestion_data)
            logger.info(f"成功获取智能建议，建议数量: {len(suggestion_data.get('suggestions', []))}")
        else:
            logger.warning(f"获取智能建议失败，状态码: {suggestion_response.status_code}")
        
    except requests.RequestException as e:
        logger.error(f"请求过程中出错: {e}")
        raise
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        raise


# 测试用例 - 归因分析
def test_attribution_analysis_pipeline():
    """测试归因分析完整流程"""
    logger.info("开始测试归因分析流程")
    
    # 1. 读取测试数据
    data_file = TEST_DATA_DIR / "attribution_data.csv"
    if not data_file.exists():
        pytest.skip(f"测试数据文件不存在: {data_file}")
    
    df = pd.read_csv(data_file)
    data = df.to_dict(orient="records")
    
    # 2. 发送归因分析请求
    analysis_request = {
        "data": data,
        "target_column": "sales",
        "factor_columns": ["advertising", "price", "promotion", "competitor_price"],
        "date_column": "date",
        "analysis_type": "attribution",
        "options": {
            "time_window": "all",  # 分析整个时间段
            "significance_threshold": 0.05  # 显著性阈值
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/analyses/attribution",
            json=analysis_request,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        analysis_data = response.json()
        analysis_id = analysis_data.get("analysis_id")
        
        assert analysis_id, "响应中缺少analysis_id"
        logger.info(f"归因分析已提交，分析ID: {analysis_id}")
        
        # 3. 等待分析完成
        wait_for_analysis_completion(analysis_id)
        
        # 4. 获取分析结果
        result_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/analyses/{analysis_id}/result",
            timeout=TIMEOUT
        )
        result_response.raise_for_status()
        
        result_data = result_response.json()
        
        # 5. 验证结果
        assert "factors" in result_data, "结果中缺少factors信息"
        factors = result_data["factors"]
        assert len(factors) > 0, "归因分析没有返回任何因素"
        
        # 保存测试结果
        save_test_result("attribution_analysis", result_data)
        
        # 验证结果包含所有因素
        factor_names = [factor["name"] for factor in factors]
        expected_factors = ["advertising", "price", "promotion", "competitor_price"]
        for expected in expected_factors:
            assert expected in factor_names, f"预期因素'{expected}'不在结果中"
        
        logger.info(f"归因分析测试通过，识别到的因素数量: {len(factors)}")
        
        # 6. 获取智能建议
        suggestion_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/suggestion/generate",
            json={
                "analysis_id": analysis_id,
                "analysis_type": "attribution",
                "metric_name": "销售额"
            },
            timeout=TIMEOUT
        )
        
        if suggestion_response.status_code == 200:
            suggestion_data = suggestion_response.json()
            save_test_result("attribution_suggestion", suggestion_data)
            logger.info(f"成功获取智能建议，建议数量: {len(suggestion_data.get('suggestions', []))}")
        else:
            logger.warning(f"获取智能建议失败，状态码: {suggestion_response.status_code}")
        
    except requests.RequestException as e:
        logger.error(f"请求过程中出错: {e}")
        raise
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        raise


# 测试用例 - 相关性分析
def test_correlation_analysis_pipeline():
    """测试相关性分析完整流程"""
    logger.info("开始测试相关性分析流程")
    
    # 1. 读取测试数据
    data_file = TEST_DATA_DIR / "correlation_data.csv"
    if not data_file.exists():
        pytest.skip(f"测试数据文件不存在: {data_file}")
    
    df = pd.read_csv(data_file)
    data = df.to_dict(orient="records")
    
    # 2. 发送相关性分析请求
    analysis_request = {
        "data": data,
        "columns": ["x1", "x2", "x3", "x4", "x5", "x6"],
        "analysis_type": "correlation",
        "options": {
            "method": "pearson",  # 使用Pearson相关系数
            "show_p_values": True  # 显示p值
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/analyses/correlation",
            json=analysis_request,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        analysis_data = response.json()
        analysis_id = analysis_data.get("analysis_id")
        
        assert analysis_id, "响应中缺少analysis_id"
        logger.info(f"相关性分析已提交，分析ID: {analysis_id}")
        
        # 3. 等待分析完成
        wait_for_analysis_completion(analysis_id)
        
        # 4. 获取分析结果
        result_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/analyses/{analysis_id}/result",
            timeout=TIMEOUT
        )
        result_response.raise_for_status()
        
        result_data = result_response.json()
        
        # 5. 验证结果
        assert "correlation_matrix" in result_data, "结果中缺少correlation_matrix"
        corr_matrix = result_data["correlation_matrix"]
        
        # 保存测试结果
        save_test_result("correlation_analysis", result_data)
        
        # 验证相关性结果
        # x1 和 x2 应该高度相关
        assert abs(corr_matrix["x1"]["x2"]) > 0.7, "x1和x2应该高度相关"
        # x1 和 x5 应该负相关
        assert corr_matrix["x1"]["x5"] < -0.5, "x1和x5应该负相关"
        # x1 和 x6 应该几乎不相关
        assert abs(corr_matrix["x1"]["x6"]) < 0.2, "x1和x6应该几乎不相关"
        
        logger.info(f"相关性分析测试通过")
        
        # 6. 获取智能建议
        suggestion_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/suggestion/generate",
            json={
                "analysis_id": analysis_id,
                "analysis_type": "correlation",
                "metric_names": ["x1", "x2", "x3", "x4", "x5", "x6"]
            },
            timeout=TIMEOUT
        )
        
        if suggestion_response.status_code == 200:
            suggestion_data = suggestion_response.json()
            save_test_result("correlation_suggestion", suggestion_data)
            logger.info(f"成功获取智能建议，建议数量: {len(suggestion_data.get('suggestions', []))}")
        else:
            logger.warning(f"获取智能建议失败，状态码: {suggestion_response.status_code}")
            
    except requests.RequestException as e:
        logger.error(f"请求过程中出错: {e}")
        raise
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        raise


# 测试用例 - 结果导出功能
def test_export_functionality():
    """测试分析结果导出功能"""
    logger.info("开始测试结果导出功能")
    
    # 1. 先进行一次趋势分析，获取分析ID
    data_file = TEST_DATA_DIR / "trend_increasing.csv"
    if not data_file.exists():
        pytest.skip(f"测试数据文件不存在: {data_file}")
    
    df = pd.read_csv(data_file)
    data = df.to_dict(orient="records")
    
    analysis_request = {
        "data": data,
        "date_column": "date",
        "value_column": "value",
        "analysis_type": "trend",
        "options": {"forecast_periods": 30}
    }
    
    try:
        # 提交分析请求
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/analyses/trend",
            json=analysis_request,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        analysis_data = response.json()
        analysis_id = analysis_data.get("analysis_id")
        assert analysis_id, "响应中缺少analysis_id"
        
        # 等待分析完成
        wait_for_analysis_completion(analysis_id)
        
        # 2. 测试各种格式的导出
        export_formats = ["csv", "json", "excel", "pdf"]
        
        for export_format in export_formats:
            logger.info(f"测试导出格式: {export_format}")
            
            export_response = requests.get(
                f"{BASE_URL}{API_PREFIX}/export/result/{analysis_id}",
                params={"format": export_format},
                timeout=TIMEOUT
            )
            
            # 检查状态码
            assert export_response.status_code == 200, f"导出{export_format}格式失败，状态码: {export_response.status_code}"
            
            # 检查内容类型
            if export_format == "csv":
                assert "text/csv" in export_response.headers.get("Content-Type", ""), "CSV导出Content-Type不正确"
            elif export_format == "json":
                assert "application/json" in export_response.headers.get("Content-Type", ""), "JSON导出Content-Type不正确"
            elif export_format == "excel":
                assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in export_response.headers.get("Content-Type", ""), "Excel导出Content-Type不正确"
            elif export_format == "pdf":
                assert "application/pdf" in export_response.headers.get("Content-Type", ""), "PDF导出Content-Type不正确"
            
            # 保存导出文件
            export_file = RESULTS_DIR / f"export_test_{export_format}_{uuid.uuid4()}.{export_format}"
            with open(export_file, "wb") as f:
                f.write(export_response.content)
            
            logger.info(f"导出文件已保存到: {export_file}")
            
            # 检查文件大小
            assert os.path.getsize(export_file) > 0, f"导出的{export_format}文件大小为0"
        
        logger.info("导出功能测试通过")
        
    except requests.RequestException as e:
        logger.error(f"请求过程中出错: {e}")
        raise
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        raise


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 