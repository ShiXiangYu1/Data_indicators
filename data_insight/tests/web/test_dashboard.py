#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
仪表板页面的Web界面测试
使用Playwright测试仪表板页面的功能和交互
"""

import pytest
import os
import re
from playwright.sync_api import Page, expect


class TestDashboard:
    """仪表板页面功能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """
        在每个测试前自动执行的设置
        导航到仪表板页面并等待加载完成
        """
        # 获取测试环境URL，默认为本地开发环境
        base_url = os.environ.get("TEST_WEB_URL", "http://localhost:8000")
        
        # 导航到仪表板页面
        page.goto(f"{base_url}/dashboard")
        
        # 等待页面加载完成（仪表板容器元素出现）
        page.wait_for_selector(".dashboard-container")
    
    def test_dashboard_title_and_header(self, page: Page):
        """测试仪表板标题和页眉"""
        # 检查页面标题
        expect(page).to_have_title("数据指标分析系统 - 仪表板")
        
        # 检查页面顶部导航栏
        header = page.locator("header.app-header")
        expect(header).to_be_visible()
        
        # 检查系统名称是否显示在导航栏中
        system_name = header.locator(".system-name")
        expect(system_name).to_have_text("数据指标分析系统")
        
        # 检查页面主标题
        main_title = page.locator("h1.dashboard-title")
        expect(main_title).to_have_text("数据分析仪表板")
    
    def test_metric_cards_display(self, page: Page):
        """测试指标卡片显示"""
        # 查找所有指标卡片
        metric_cards = page.locator(".metric-card")
        
        # 验证至少有4个指标卡片
        expect(metric_cards).to_have_count(4)
        
        # 检查第一个卡片的内容
        first_card = metric_cards.first
        
        # 验证卡片有标题
        card_title = first_card.locator(".card-title")
        expect(card_title).to_be_visible()
        
        # 验证卡片有数值
        card_value = first_card.locator(".card-value")
        expect(card_value).to_be_visible()
        
        # 验证数值是数字格式（使用正则表达式）
        card_value_text = card_value.inner_text()
        assert re.match(r'^[\d,.]+$', card_value_text.strip()) is not None
    
    def test_trend_chart_display(self, page: Page):
        """测试趋势图表显示"""
        # 查找趋势图表容器
        trend_chart = page.locator(".trend-chart-container")
        expect(trend_chart).to_be_visible()
        
        # 验证图表标题存在
        chart_title = trend_chart.locator(".chart-title")
        expect(chart_title).to_be_visible()
        
        # 验证图表图例存在
        chart_legend = trend_chart.locator(".chart-legend")
        expect(chart_legend).to_be_visible()
        
        # 验证图表本身存在
        chart_svg = trend_chart.locator("svg")
        expect(chart_svg).to_be_visible()
        
        # 验证图表有数据点
        data_points = chart_svg.locator(".data-point")
        expect(data_points).to_have_count(1)  # 至少有一个数据点
    
    def test_trend_chart_interaction(self, page: Page):
        """测试趋势图表交互"""
        # 查找趋势图表容器
        trend_chart = page.locator(".trend-chart-container")
        
        # 点击图表
        trend_chart.locator("svg").click()
        
        # 等待详情面板出现
        details_panel = page.locator(".chart-details-panel")
        expect(details_panel).to_be_visible()
        
        # 验证详情面板标题
        expect(details_panel.locator(".details-title")).to_contain_text("趋势详情")
        
        # 验证详情面板内容包含数据
        expect(details_panel.locator(".details-content")).to_be_visible()
        
        # 关闭详情面板
        details_panel.locator(".close-button").click()
        
        # 验证详情面板已关闭
        expect(details_panel).to_be_hidden()
    
    def test_date_range_filter(self, page: Page):
        """测试日期范围筛选器"""
        # 查找日期范围选择器
        date_range_selector = page.locator(".date-range-selector")
        expect(date_range_selector).to_be_visible()
        
        # 展开日期选择器
        date_range_selector.click()
        
        # 等待日期选项出现
        date_options = page.locator(".date-range-options")
        expect(date_options).to_be_visible()
        
        # 选择"最近30天"选项
        last_30_days_option = date_options.locator("text=最近30天")
        last_30_days_option.click()
        
        # 等待加载指示器消失
        page.wait_for_selector(".loading-indicator", state="hidden")
        
        # 验证日期范围已更新
        selected_range = date_range_selector.locator(".selected-range")
        expect(selected_range).to_contain_text("最近30天")
        
        # 验证图表已更新
        # 这里假设图表有一个更新时间戳元素
        chart_timestamp = page.locator(".chart-updated-timestamp")
        expect(chart_timestamp).to_be_visible()
    
    def test_metric_selector(self, page: Page):
        """测试指标选择器"""
        # 查找指标选择器
        metric_selector = page.locator(".metric-selector")
        expect(metric_selector).to_be_visible()
        
        # 展开指标选择器
        metric_selector.click()
        
        # 等待指标选项出现
        metric_options = page.locator(".metric-options")
        expect(metric_options).to_be_visible()
        
        # 找到第二个指标选项
        second_metric_option = metric_options.locator("li").nth(1)
        
        # 记录当前选定的指标名称
        second_metric_name = second_metric_option.inner_text()
        
        # 选择第二个指标
        second_metric_option.click()
        
        # 等待加载指示器消失
        page.wait_for_selector(".loading-indicator", state="hidden")
        
        # 验证选择器显示的是新选择的指标
        selected_metric = metric_selector.locator(".selected-metric")
        expect(selected_metric).to_have_text(second_metric_name)
        
        # 验证图表标题中包含新指标的名称
        chart_title = page.locator(".trend-chart-container .chart-title")
        expect(chart_title).to_contain_text(second_metric_name)
    
    def test_dashboard_responsive_layout(self, page: Page):
        """测试仪表板响应式布局"""
        # 测试桌面视图
        page.set_viewport_size({"width": 1200, "height": 800})
        # 验证指标卡片在一行显示
        cards_container = page.locator(".metrics-cards-container")
        expect(cards_container).to_have_css("grid-template-columns", re.compile(r'repeat\(.+, 1fr\)'))
        
        # 测试平板视图
        page.set_viewport_size({"width": 768, "height": 800})
        # 等待响应式布局调整
        page.wait_for_timeout(500)
        # 验证布局已调整
        expect(cards_container).to_have_css("grid-template-columns", re.compile(r'repeat\(.+, 1fr\)'))
        
        # 测试手机视图
        page.set_viewport_size({"width": 375, "height": 800})
        # 等待响应式布局调整
        page.wait_for_timeout(500)
        # 验证卡片在手机视图下是垂直排列的
        expect(cards_container).to_have_css("grid-template-columns", "1fr")
    
    def test_dashboard_navigation(self, page: Page):
        """测试仪表板导航链接"""
        # 查找导航栏
        navbar = page.locator("nav.main-navigation")
        expect(navbar).to_be_visible()
        
        # 检查"分析"链接
        analysis_link = navbar.locator("text=分析")
        expect(analysis_link).to_be_visible()
        
        # 检查"报表"链接
        reports_link = navbar.locator("text=报表")
        expect(reports_link).to_be_visible()
        
        # 检查"设置"链接
        settings_link = navbar.locator("text=设置")
        expect(settings_link).to_be_visible()
        
        # 点击"分析"链接
        # 使用page.expect_navigation防止测试过早继续
        with page.expect_navigation():
            analysis_link.click()
        
        # 验证已导航到分析页面
        expect(page).to_have_url(re.compile(r".*/analysis"))
        expect(page).to_have_title(re.compile("分析"))
    
    def test_dashboard_search(self, page: Page):
        """测试仪表板搜索功能"""
        # 导航回仪表板
        base_url = os.environ.get("TEST_WEB_URL", "http://localhost:8000")
        page.goto(f"{base_url}/dashboard")
        page.wait_for_selector(".dashboard-container")
        
        # 查找搜索框
        search_box = page.locator(".search-box")
        expect(search_box).to_be_visible()
        
        # 输入搜索关键词
        search_box.fill("销售额")
        search_box.press("Enter")
        
        # 等待搜索结果加载
        page.wait_for_selector(".search-results")
        
        # 验证搜索结果容器可见
        results_container = page.locator(".search-results")
        expect(results_container).to_be_visible()
        
        # 验证结果中包含搜索关键词
        result_items = results_container.locator(".result-item")
        expect(result_items).to_have_count(1)  # 至少有一个结果
        expect(result_items.first).to_contain_text("销售额")
    
    def test_export_dashboard(self, page: Page):
        """测试仪表板导出功能"""
        # 查找导出按钮
        export_button = page.locator("button:has-text('导出')")
        expect(export_button).to_be_visible()
        
        # 点击导出按钮
        export_button.click()
        
        # 等待导出选项出现
        export_options = page.locator(".export-options")
        expect(export_options).to_be_visible()
        
        # 选择PDF选项
        pdf_option = export_options.locator("text=PDF")
        
        # 监听下载事件
        with page.expect_download() as download_info:
            pdf_option.click()
        
        # 验证下载已开始
        download = download_info.value
        
        # 验证下载的文件名包含"dashboard"
        assert "dashboard" in download.suggested_filename.lower()
        assert download.suggested_filename.endswith(".pdf")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 