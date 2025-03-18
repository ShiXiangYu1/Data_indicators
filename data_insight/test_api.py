#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标平台API测试脚本
====================

用于测试数据指标平台的各个API端点。

使用方法:
    python test_api.py [--url URL] [--endpoint ENDPOINT] [--token TOKEN]

参数:
    --url URL: API基础URL，默认为http://localhost:5000
    --endpoint ENDPOINT: 要测试的端点，不指定则测试所有端点
    --token TOKEN: API令牌，如果API启用了令牌认证
"""

import os
import sys
import json
import time
import argparse
import requests
from dotenv import load_dotenv
from datetime import datetime


# 可用端点列表
AVAILABLE_ENDPOINTS = [
    "health",
    "docs",
    "metric_analyze",
    "metric_compare",
    "chart_analyze",
    "reason_analyze",
    "root_cause",
    "attribute",
    "suggest",
    "forecast",
    "anomaly"
]

# 示例数据
SAMPLE_DATA = {
    "metric_analyze": {
        "name": "月度销售额",
        "value": 1250000,
        "previous_value": 1000000,
        "unit": "元",
        "time_period": "2023年7月",
        "previous_time_period": "2023年6月",
        "historical_values": [920000, 980000, 950000, 1010000, 1000000],
        "is_positive_better": True
    },
    "metric_compare": {
        "metrics": [
            {
                "name": "销售额",
                "values": [980000, 1010000, 1000000, 1250000],
                "unit": "元",
                "time_periods": ["2023年4月", "2023年5月", "2023年6月", "2023年7月"]
            },
            {
                "name": "客户数",
                "values": [3200, 3300, 3180, 3850],
                "unit": "人",
                "time_periods": ["2023年4月", "2023年5月", "2023年6月", "2023年7月"]
            }
        ],
        "include_correlation": True
    },
    "chart_analyze": {
        "chart_type": "line",
        "title": "月度销售额趋势",
        "data": {
            "x_axis": {
                "label": "月份",
                "values": ["2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月", "2023年7月"]
            },
            "y_axis": {
                "label": "销售额(元)",
                "series": [
                    {
                        "name": "销售额",
                        "values": [920000, 980000, 950000, 1010000, 1000000, 1250000]
                    }
                ]
            }
        }
    },
    "reason_analyze": {
        "basic_info": {
            "指标名称": "月度销售额",
            "当前值": 1250000,
            "上一期值": 1000000,
            "单位": "元",
            "当前周期": "2023年7月",
            "上一周期": "2023年6月",
            "正向增长是否为好": True
        },
        "change_analysis": {
            "变化量": 250000,
            "变化率": 0.25,
            "变化类别": "大幅增长",
            "变化方向": "增加"
        },
        "historical_data": {
            "历史值": [920000, 980000, 950000, 1010000, 1000000]
        }
    },
    "root_cause": {
        "target": "销售额",
        "target_values": [980000, 1010000, 1000000, 1250000],
        "factors": {
            "客户数": [3200, 3300, 3180, 3850],
            "客单价": [306.25, 306.06, 314.47, 324.68],
            "广告投入": [150000, 155000, 160000, 200000],
            "促销活动数": [2, 3, 2, 4]
        },
        "subfactors": {
            "客户数": {
                "新客户": [800, 850, 780, 1200],
                "回头客": [2400, 2450, 2400, 2650]
            }
        },
        "known_relationships": [
            {
                "from": "广告投入",
                "to": "新客户",
                "type": "direct",
                "strength": 0.7
            },
            {
                "from": "促销活动数",
                "to": "客单价",
                "type": "inverse",
                "strength": 0.5
            }
        ]
    },
    "attribute": {
        "target_values": [980000, 1010000, 1000000, 1250000],
        "factors": {
            "客户数": [3200, 3300, 3180, 3850],
            "客单价": [306.25, 306.06, 314.47, 324.68],
            "广告投入": [150000, 155000, 160000, 200000],
            "促销活动数": [2, 3, 2, 4]
        },
        "method": "linear"
    },
    "suggest": {
        "metric_analysis": {
            "基本信息": {
                "指标名称": "月度销售额",
                "当前值": 1250000,
                "上一期值": 1000000,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月",
                "正向增长是否为好": True
            },
            "变化分析": {
                "变化量": 250000,
                "变化率": 0.25,
                "变化类别": "大幅增长",
                "变化方向": "增加"
            },
            "异常分析": {
                "是否异常": True,
                "异常程度": 2.3,
                "是否高于正常范围": True
            }
        },
        "attribution_analysis": {
            "归因分析结果": [
                {"因素": "广告投入", "贡献度": 0.45},
                {"因素": "促销活动", "贡献度": 0.30},
                {"因素": "季节因素", "贡献度": 0.15},
                {"因素": "其他", "贡献度": 0.10}
            ]
        },
        "root_cause_analysis": {
            "根因分析结果": {
                "根本原因": [
                    {"因素": "广告投入增加", "影响程度": "高"},
                    {"因素": "促销活动效果提升", "影响程度": "中"}
                ]
            }
        }
    },
    "forecast": {
        "values": [980000, 1010000, 1000000, 1250000],
        "target_periods": 3,
        "confidence_level": 0.95
    },
    "anomaly": {
        "values": [980000, 1010000, 1000000, 1250000],
        "threshold": 1.5,
        "lookback_periods": 3
    }
}


def parse_arguments():
    """
    解析命令行参数
    
    返回:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description='测试数据指标平台API')
    
    parser.add_argument('--url', 
                        type=str, 
                        default='http://localhost:5000',
                        help='API基础URL（默认: http://localhost:5000）')
    
    parser.add_argument('--endpoint', 
                        type=str,
                        choices=AVAILABLE_ENDPOINTS,
                        help='要测试的端点，不指定则测试所有端点')
    
    parser.add_argument('--token', 
                        type=str,
                        help='API令牌，如果API启用了令牌认证')
    
    return parser.parse_args()


def make_request(url, method='GET', data=None, headers=None):
    """
    发送HTTP请求
    
    参数:
        url (str): 请求URL
        method (str): HTTP方法
        data (dict, optional): 请求数据
        headers (dict, optional): 请求头
        
    返回:
        tuple: (响应对象, 响应时间)
    """
    start_time = time.time()
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        elapsed_time = time.time() - start_time
        return response, elapsed_time
    
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None, time.time() - start_time


def print_response(response, elapsed_time):
    """
    打印响应信息
    
    参数:
        response (Response): 响应对象
        elapsed_time (float): 响应时间
    """
    if not response:
        return
    
    print(f"状态码: {response.status_code}")
    print(f"响应时间: {elapsed_time:.4f}秒")
    
    try:
        json_data = response.json()
        print(f"响应内容: {json.dumps(json_data, ensure_ascii=False, indent=2)[:500]}...")
        
        # 如果是任务响应，记录任务ID
        if 'data' in json_data and 'task_id' in json_data['data']:
            task_id = json_data['data']['task_id']
            print(f"任务ID: {task_id}")
            return task_id
    
    except:
        print(f"响应内容: {response.text[:500]}...")


def test_health_endpoint(base_url, headers):
    """测试健康检查端点"""
    print("\n=== 测试健康检查端点 ===")
    url = f"{base_url}/health"
    response, elapsed_time = make_request(url, method='GET', headers=headers)
    print_response(response, elapsed_time)


def test_docs_endpoint(base_url, headers):
    """测试API文档端点"""
    print("\n=== 测试API文档端点 ===")
    url = f"{base_url}/api/docs"
    response, elapsed_time = make_request(url, method='GET', headers=headers)
    print_response(response, elapsed_time)


def test_metric_analyze_endpoint(base_url, headers):
    """测试指标分析端点"""
    print("\n=== 测试指标分析端点 ===")
    url = f"{base_url}/api/metric/analyze"
    data = SAMPLE_DATA["metric_analyze"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_metric_compare_endpoint(base_url, headers):
    """测试指标对比端点"""
    print("\n=== 测试指标对比端点 ===")
    url = f"{base_url}/api/metric/compare"
    data = SAMPLE_DATA["metric_compare"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_chart_analyze_endpoint(base_url, headers):
    """测试图表分析端点"""
    print("\n=== 测试图表分析端点 ===")
    url = f"{base_url}/api/chart/analyze"
    data = SAMPLE_DATA["chart_analyze"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_reason_analyze_endpoint(base_url, headers):
    """测试原因分析端点"""
    print("\n=== 测试原因分析端点 ===")
    url = f"{base_url}/api/analysis/reason"
    data = SAMPLE_DATA["reason_analyze"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_root_cause_endpoint(base_url, headers):
    """测试根因分析端点"""
    print("\n=== 测试根因分析端点 ===")
    url = f"{base_url}/api/analysis/root-cause"
    data = SAMPLE_DATA["root_cause"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_attribute_endpoint(base_url, headers):
    """测试归因分析端点"""
    print("\n=== 测试归因分析端点 ===")
    url = f"{base_url}/api/analysis/attribute"
    data = SAMPLE_DATA["attribute"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_suggest_endpoint(base_url, headers):
    """测试建议生成端点"""
    print("\n=== 测试建议生成端点 ===")
    url = f"{base_url}/api/analysis/suggest"
    data = SAMPLE_DATA["suggest"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_forecast_endpoint(base_url, headers):
    """测试预测分析端点"""
    print("\n=== 测试预测分析端点 ===")
    url = f"{base_url}/api/prediction/forecast"
    data = SAMPLE_DATA["forecast"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_anomaly_endpoint(base_url, headers):
    """测试异常预测端点"""
    print("\n=== 测试异常预测端点 ===")
    url = f"{base_url}/api/prediction/anomaly"
    data = SAMPLE_DATA["anomaly"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    print_response(response, elapsed_time)


def test_async_task(base_url, headers):
    """测试异步任务端点"""
    print("\n=== 测试异步任务 ===")
    
    # 创建一个异步分析任务
    url = f"{base_url}/api/metric/analyze-async"
    data = SAMPLE_DATA["metric_analyze"]
    response, elapsed_time = make_request(url, method='POST', data=data, headers=headers)
    
    # 获取任务ID
    task_id = print_response(response, elapsed_time)
    
    if not task_id:
        print("未获取到任务ID，无法测试任务状态")
        return
    
    # 获取任务状态
    print("\n正在获取任务状态...")
    for i in range(5):
        time.sleep(1)
        url = f"{base_url}/api/metric/task/{task_id}"
        response, elapsed_time = make_request(url, method='GET', headers=headers)
        status = print_response(response, elapsed_time)
        
        # 如果任务完成，退出循环
        try:
            if response.json().get('data', {}).get('status') == 'completed':
                break
        except:
            pass


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载环境变量
    load_dotenv()
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 如果提供了API令牌，添加到请求头
    if args.token:
        headers['X-API-Token'] = args.token
    elif os.environ.get('API_TOKEN'):
        headers['X-API-Token'] = os.environ.get('API_TOKEN')
    
    # 打印测试信息
    print(f"数据指标平台API测试开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API基础URL: {args.url}")
    print(f"测试端点: {args.endpoint or '所有端点'}")
    
    # 测试指定端点或所有端点
    if not args.endpoint or args.endpoint == 'health':
        test_health_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'docs':
        test_docs_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'metric_analyze':
        test_metric_analyze_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'metric_compare':
        test_metric_compare_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'chart_analyze':
        test_chart_analyze_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'reason_analyze':
        test_reason_analyze_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'root_cause':
        test_root_cause_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'attribute':
        test_attribute_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'suggest':
        test_suggest_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'forecast':
        test_forecast_endpoint(args.url, headers)
    
    if not args.endpoint or args.endpoint == 'anomaly':
        test_anomaly_endpoint(args.url, headers)
    
    # 测试异步任务（如果未指定端点）
    if not args.endpoint:
        test_async_task(args.url, headers)
    
    print(f"\n测试结束 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main() 