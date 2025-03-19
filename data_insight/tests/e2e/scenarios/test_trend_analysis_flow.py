#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
趋势分析流程的端到端测试
测试完整的用户操作流程：上传数据 -> 分析 -> 查看结果 -> 导出
"""

import pytest
import os
import requests
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect

# 设置最大等待时间（秒）
MAX_WAIT_TIME = 60


class TestTrendAnalysisFlow:
    """趋势分析完整流程的端到端测试类"""

    @pytest.fixture
    def api_base_url(self):
        """API基础URL"""
        return os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

    @pytest.fixture
    def web_base_url(self):
        """Web界面基础URL"""
        return os.environ.get("WEB_BASE_URL", "http://localhost:8000")

    @pytest.fixture
    def sample_data_path(self):
        """示例数据文件路径"""
        # 获取测试数据目录
        test_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data"
        )
        return os.path.join(test_data_dir, "sample_sales_data.csv")

    @pytest.fixture
    def generate_sample_data(self, sample_data_path):
        """生成示例数据文件（如果不存在）"""
        if not os.path.exists(os.path.dirname(sample_data_path)):
            os.makedirs(os.path.dirname(sample_data_path))

        if not os.path.exists(sample_data_path):
            # 创建示例销售数据
            start_date = datetime(2023, 1, 1)
            dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(365)]
            
            # 创建销售数据（包含趋势和季节性）
            import numpy as np
            base_value = 1000
            trend = np.arange(365) * 2  # 每天增加2
            weekday_effect = np.array([0, 50, 30, 20, 100, 200, 150] * 53)[:365]  # 周末销售高
            monthly_effect = np.array([np.sin(2 * np.pi * i / 30) * 100 for i in range(365)])  # 月度波动
            special_events = np.zeros(365)
            special_events[30:35] = 300  # 促销活动
            special_events[180:185] = 500  # 假日促销
            
            # 生成随机噪声
            np.random.seed(42)  # 确保可重现性
            noise = np.random.normal(0, 50, 365)
            
            # 组合所有影响因素
            sales = base_value + trend + weekday_effect + monthly_effect + special_events + noise
            sales = np.maximum(sales, 0)  # 确保销售额非负
            
            # 创建DataFrame
            df = pd.DataFrame({
                "date": dates,
                "sales": sales.astype(int),
                "channel": np.random.choice(["online", "store", "mobile"], 365),
                "region": np.random.choice(["north", "south", "east", "west"], 365)
            })
            
            # 保存为CSV
            df.to_csv(sample_data_path, index=False)
        
        return sample_data_path

    def test_complete_trend_analysis_flow(self, api_base_url, web_base_url, generate_sample_data, page: Page):
        """测试完整的趋势分析流程"""
        sample_data_path = generate_sample_data
        
        # 步骤1：通过API上传数据
        print("步骤1：上传数据")
        data_id = self._upload_data(api_base_url, sample_data_path)
        assert data_id, "数据上传失败"
        
        # 步骤2：通过API进行趋势分析
        print("步骤2：执行趋势分析")
        analysis_id = self._perform_analysis(api_base_url, data_id)
        assert analysis_id, "趋势分析失败"
        
        # 步骤3：通过Web界面查看结果
        print("步骤3：通过Web界面查看结果")
        self._view_analysis_result(page, web_base_url, analysis_id)
        
        # 步骤4：导出分析结果
        print("步骤4：导出分析结果")
        self._export_analysis_result(page)
        
        print("测试完成: 完整流程测试成功!")

    def _upload_data(self, api_base_url, sample_data_path):
        """上传数据文件"""
        with open(sample_data_path, "rb") as f:
            files = {"file": (os.path.basename(sample_data_path), f, "text/csv")}
            response = requests.post(
                f"{api_base_url}/data/upload",
                files=files
            )
        
        assert response.status_code == 200, f"上传数据失败: {response.text}"
        result = response.json()
        print(f"  * 数据上传成功，数据ID: {result.get('data_id')}")
        return result.get("data_id")

    def _perform_analysis(self, api_base_url, data_id):
        """执行趋势分析"""
        analysis_request = {
            "data_id": data_id,
            "date_column": "date",
            "value_column": "sales",
            "params": {
                "change_point_detection": True,
                "seasonality_analysis": True,
                "forecast_periods": 30
            }
        }
        
        # 发送分析请求
        response = requests.post(
            f"{api_base_url}/analysis/trend",
            json=analysis_request
        )
        
        assert response.status_code == 200, f"创建分析任务失败: {response.text}"
        result = response.json()
        analysis_id = result.get("analysis_id")
        print(f"  * 分析任务创建成功，分析ID: {analysis_id}")
        
        # 等待分析完成
        start_time = time.time()
        while time.time() - start_time < MAX_WAIT_TIME:
            response = requests.get(f"{api_base_url}/analysis/result/{analysis_id}")
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "completed":
                    print(f"  * 分析已完成, 耗时: {time.time() - start_time:.1f}秒")
                    return analysis_id
                elif result.get("status") == "failed":
                    assert False, f"分析失败: {result.get('error')}"
            
            # 等待一段时间再检查
            time.sleep(2)
            print("  * 等待分析完成...")
        
        assert False, "分析超时未完成"
        return None

    def _view_analysis_result(self, page: Page, web_base_url, analysis_id):
        """通过Web界面查看分析结果"""
        # 导航到分析结果页面
        page.goto(f"{web_base_url}/analysis/result/{analysis_id}")
        
        # 等待结果页面加载完成
        page.wait_for_selector(".analysis-result-container")
        
        # 验证页面标题包含"分析结果"
        expect(page).to_have_title(lambda title: "分析结果" in title)
        
        # 验证分析类型
        analysis_type = page.locator(".analysis-type")
        expect(analysis_type).to_contain_text("趋势分析")
        
        # 验证趋势图表已加载
        trend_chart = page.locator(".trend-chart")
        expect(trend_chart).to_be_visible()
        
        # 验证分析摘要已加载
        summary = page.locator(".analysis-summary")
        expect(summary).to_be_visible()
        
        # 验证趋势方向
        trend_direction = page.locator(".trend-direction")
        expect(trend_direction).to_be_visible()
        trend_direction_text = trend_direction.inner_text()
        print(f"  * 检测到的趋势方向: {trend_direction_text}")
        
        # 验证置信度
        confidence = page.locator(".confidence-level")
        expect(confidence).to_be_visible()
        
        # 验证变化点
        change_points = page.locator(".change-points")
        expect(change_points).to_be_visible()
        
        # 截图保存结果
        screenshot_path = f"trend_analysis_result_{analysis_id}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  * 结果页面截图已保存: {os.path.abspath(screenshot_path)}")

    def _export_analysis_result(self, page: Page):
        """导出分析结果"""
        # 查找导出按钮
        export_button = page.locator("button:has-text('导出结果')")
        expect(export_button).to_be_visible()
        
        # 点击导出按钮
        export_button.click()
        
        # 等待导出格式选项出现
        format_options = page.locator(".export-format-options")
        expect(format_options).to_be_visible()
        
        # 选择Excel格式
        excel_option = format_options.locator("text=Excel")
        expect(excel_option).to_be_visible()
        
        # 监听下载事件
        with page.expect_download() as download_info:
            excel_option.click()
            
            # 等待确认按钮并点击（如果存在）
            confirm_button = page.locator(".confirm-export-button")
            if confirm_button.is_visible():
                confirm_button.click()
        
        # 验证下载已开始
        download = download_info.value
        download_path = download.path()
        
        # 验证文件存在
        assert os.path.exists(download_path), "导出文件不存在"
        
        # 验证文件非空
        assert os.path.getsize(download_path) > 0, "导出文件为空"
        
        print(f"  * 文件已成功导出: {download.suggested_filename}")
        
        # 尝试读取Excel文件验证内容
        try:
            df = pd.read_excel(download_path)
            row_count = len(df)
            col_count = len(df.columns)
            print(f"  * 导出文件包含 {row_count} 行、{col_count} 列数据")
            assert row_count > 0, "导出文件没有数据行"
            assert col_count > 0, "导出文件没有数据列"
            assert "date" in df.columns or "日期" in df.columns, "导出文件缺少日期列"
            assert "sales" in df.columns or "销售额" in df.columns or "值" in df.columns, "导出文件缺少值列"
        except Exception as e:
            print(f"  * 警告: 无法验证导出文件内容: {e}")


def standalone_test():
    """作为独立脚本运行时的入口点"""
    import sys
    from playwright.sync_api import sync_playwright
    
    # 设置环境变量
    os.environ["API_BASE_URL"] = "http://localhost:8000/api/v1"
    os.environ["WEB_BASE_URL"] = "http://localhost:8000"
    
    # 创建测试实例
    test = TestTrendAnalysisFlow()
    
    # 获取基本URL
    api_base_url = test.api_base_url.__get__(test)
    web_base_url = test.web_base_url.__get__(test)
    
    # 创建示例数据
    sample_data_path = test.generate_sample_data.__get__(test, test.sample_data_path.__get__(test))
    
    # 运行测试
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            test.test_complete_trend_analysis_flow(api_base_url, web_base_url, sample_data_path, page)
            print("测试成功!")
        except Exception as e:
            print(f"测试失败: {e}")
            page.screenshot(path="error_screenshot.png")
            print(f"错误截图已保存: {os.path.abspath('error_screenshot.png')}")
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    standalone_test() 