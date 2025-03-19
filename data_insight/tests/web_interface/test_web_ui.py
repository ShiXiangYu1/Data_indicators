#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标分析系统Web界面自动化测试
使用Selenium测试Web界面的功能和交互
"""

import pytest
import time
import os
import logging
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

# Selenium相关导入
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = os.getenv("TEST_WEB_URL", "http://localhost:8000")
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
TEST_DATA_DIR = Path(__file__).parent / "test_data"
WAIT_TIMEOUT = 30  # 页面加载等待超时时间（秒）

# 确保截图和测试数据目录存在
SCREENSHOT_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)


# 测试数据准备
def generate_test_data():
    """生成测试所需的示例数据文件"""
    # 生成趋势分析示例数据
    dates = pd.date_range('2022-01-01', periods=90, freq='D')
    values = np.linspace(100, 300, 90) + np.random.normal(0, 15, 90)
    
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'value': values
    })
    
    # 保存为CSV文件
    csv_path = TEST_DATA_DIR / "sample_trend_data.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"示例趋势数据已保存到: {csv_path}")
    
    # 生成归因分析示例数据
    np.random.seed(42)
    
    data = {
        'date': dates.strftime('%Y-%m-%d'),
        'sales': np.random.normal(1000, 200, 90),
        'advertising': np.random.normal(500, 100, 90),
        'price': np.random.normal(50, 5, 90),
        'promotion': np.random.choice([0, 1], size=90, p=[0.7, 0.3]),
        'competitor_price': np.random.normal(55, 8, 90)
    }
    
    df_attr = pd.DataFrame(data)
    
    # 保存为CSV文件
    csv_attr_path = TEST_DATA_DIR / "sample_attribution_data.csv"
    df_attr.to_csv(csv_attr_path, index=False)
    logger.info(f"示例归因数据已保存到: {csv_attr_path}")


# 浏览器配置
@pytest.fixture(scope="session")
def browser():
    """初始化浏览器实例"""
    # 根据环境变量决定使用哪种浏览器
    browser_type = os.getenv("TEST_BROWSER", "chrome").lower()
    
    if browser_type == "chrome":
        options = webdriver.ChromeOptions()
        # 如果在CI环境中运行，使用无头模式
        if os.getenv("CI") == "true":
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
    elif browser_type == "firefox":
        options = webdriver.FirefoxOptions()
        if os.getenv("CI") == "true":
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    elif browser_type == "edge":
        options = webdriver.EdgeOptions()
        if os.getenv("CI") == "true":
            options.add_argument("--headless")
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")
    
    driver.maximize_window()
    logger.info(f"已初始化{browser_type}浏览器")
    
    yield driver
    
    # 测试结束后关闭浏览器
    driver.quit()
    logger.info("已关闭浏览器")


# 测试辅助类
class WebUITestHelper:
    """Web界面测试辅助类，封装常用操作"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_TIMEOUT)
    
    def navigate_to(self, path):
        """导航到指定页面"""
        url = f"{BASE_URL}{path}"
        logger.info(f"导航到: {url}")
        self.driver.get(url)
    
    def take_screenshot(self, name):
        """截取当前页面截图"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.png"
        screenshot_path = SCREENSHOT_DIR / filename
        self.driver.save_screenshot(str(screenshot_path))
        logger.info(f"截图已保存到: {screenshot_path}")
        return screenshot_path
    
    def wait_for_element(self, by, value, timeout=None):
        """等待元素可见"""
        if timeout is None:
            timeout = WAIT_TIMEOUT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"超时等待元素: {by}={value}")
            self.take_screenshot(f"timeout_{value.replace(' ', '_')}")
            raise
    
    def wait_for_element_clickable(self, by, value, timeout=None):
        """等待元素可点击"""
        if timeout is None:
            timeout = WAIT_TIMEOUT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"超时等待元素可点击: {by}={value}")
            self.take_screenshot(f"timeout_clickable_{value.replace(' ', '_')}")
            raise
    
    def click_element(self, by, value):
        """点击元素"""
        element = self.wait_for_element_clickable(by, value)
        try:
            element.click()
            logger.info(f"点击元素: {by}={value}")
        except Exception as e:
            logger.error(f"点击元素失败: {by}={value}, 错误: {e}")
            self.take_screenshot(f"click_error_{value.replace(' ', '_')}")
            # 尝试使用JavaScript点击
            try:
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"使用JavaScript点击元素: {by}={value}")
            except Exception as js_e:
                logger.error(f"JavaScript点击失败: {js_e}")
                raise
    
    def fill_input(self, by, value, text):
        """填充输入框"""
        element = self.wait_for_element(by, value)
        element.clear()
        element.send_keys(text)
        logger.info(f"填充输入框 {by}={value}: {text}")
    
    def get_text(self, by, value):
        """获取元素文本"""
        element = self.wait_for_element(by, value)
        return element.text
    
    def select_file(self, by, value, file_path):
        """选择文件上传"""
        # 将相对路径转换为绝对路径
        abs_file_path = str(Path(file_path).resolve())
        element = self.wait_for_element(by, value)
        element.send_keys(abs_file_path)
        logger.info(f"选择文件: {abs_file_path}")
    
    def check_element_exists(self, by, value, timeout=5):
        """检查元素是否存在"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, element):
        """滚动到元素位置"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # 等待滚动完成
    
    def drag_and_drop(self, source, target):
        """拖放操作"""
        action = ActionChains(self.driver)
        action.drag_and_drop(source, target).perform()
    
    def switch_to_iframe(self, iframe_locator):
        """切换到iframe"""
        iframe = self.wait_for_element(*iframe_locator)
        self.driver.switch_to.frame(iframe)
    
    def switch_to_default_content(self):
        """切换回主文档"""
        self.driver.switch_to.default_content()
    
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )


# 测试前的准备工作
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """设置测试环境"""
    logger.info("设置Web界面测试环境")
    generate_test_data()
    yield
    logger.info("清理Web界面测试环境")


# 测试用例
def test_homepage_loads(browser):
    """测试首页加载"""
    helper = WebUITestHelper(browser)
    helper.navigate_to("/")
    
    # 等待页面加载
    helper.wait_for_page_load()
    helper.take_screenshot("homepage")
    
    # 检查页面标题
    assert "数据指标分析系统" in browser.title
    
    # 检查重要元素存在
    assert helper.check_element_exists(By.ID, "app-header"), "页面头部不存在"
    assert helper.check_element_exists(By.ID, "app-footer"), "页面底部不存在"
    
    # 检查导航菜单
    assert helper.check_element_exists(By.LINK_TEXT, "趋势分析"), "趋势分析菜单不存在"
    assert helper.check_element_exists(By.LINK_TEXT, "归因分析"), "归因分析菜单不存在"
    
    logger.info("首页加载测试通过")


def test_trend_analysis_workflow(browser):
    """测试趋势分析工作流程"""
    helper = WebUITestHelper(browser)
    
    # 1. 导航到趋势分析页面
    helper.navigate_to("/analyses/trend")
    helper.wait_for_page_load()
    helper.take_screenshot("trend_analysis_page")
    
    # 2. 上传数据文件
    file_upload = helper.wait_for_element(By.ID, "data-file-upload")
    helper.select_file(By.ID, "data-file-upload", TEST_DATA_DIR / "sample_trend_data.csv")
    
    # 3. 等待文件上传完成
    upload_success = helper.wait_for_element(By.CLASS_NAME, "upload-success")
    assert "上传成功" in upload_success.text
    helper.take_screenshot("file_uploaded")
    
    # 4. 配置分析参数
    helper.fill_input(By.ID, "date-column", "date")
    helper.fill_input(By.ID, "value-column", "value")
    
    # 选择需要检测季节性
    seasonality_checkbox = helper.wait_for_element(By.ID, "detect-seasonality")
    if not seasonality_checkbox.is_selected():
        helper.click_element(By.ID, "detect-seasonality")
    
    # 5. 提交分析
    helper.click_element(By.ID, "submit-analysis")
    
    # 6. 等待分析完成
    try:
        result_header = helper.wait_for_element(By.ID, "analysis-result-header", timeout=90)
        assert "分析结果" in result_header.text
        helper.take_screenshot("trend_analysis_result")
        
        # 7. 检查结果包含趋势图表
        assert helper.check_element_exists(By.ID, "trend-chart"), "趋势图表不存在"
        
        # 8. 检查结果包含预测图表
        assert helper.check_element_exists(By.ID, "forecast-chart"), "预测图表不存在"
        
        # 9. 检查结果包含趋势说明
        trend_info = helper.wait_for_element(By.ID, "trend-info")
        assert "趋势方向" in trend_info.text, "趋势信息不包含方向说明"
        
        # 10. 测试导出功能
        if helper.check_element_exists(By.ID, "export-dropdown"):
            helper.click_element(By.ID, "export-dropdown")
            helper.click_element(By.ID, "export-csv")
            time.sleep(2)  # 等待下载开始
            helper.take_screenshot("export_dropdown")
        
        logger.info("趋势分析工作流程测试通过")
        
    except TimeoutException:
        helper.take_screenshot("trend_analysis_timeout")
        assert False, "趋势分析结果加载超时"


def test_attribution_analysis_workflow(browser):
    """测试归因分析工作流程"""
    helper = WebUITestHelper(browser)
    
    # 1. 导航到归因分析页面
    helper.navigate_to("/analyses/attribution")
    helper.wait_for_page_load()
    helper.take_screenshot("attribution_analysis_page")
    
    # 2. 上传数据文件
    file_upload = helper.wait_for_element(By.ID, "data-file-upload")
    helper.select_file(By.ID, "data-file-upload", TEST_DATA_DIR / "sample_attribution_data.csv")
    
    # 3. 等待文件上传完成
    upload_success = helper.wait_for_element(By.CLASS_NAME, "upload-success")
    assert "上传成功" in upload_success.text
    helper.take_screenshot("attribution_file_uploaded")
    
    # 4. 配置分析参数
    helper.fill_input(By.ID, "target-column", "sales")
    
    # 选择影响因素
    factors = ["advertising", "price", "promotion", "competitor_price"]
    for factor in factors:
        if helper.check_element_exists(By.ID, f"factor-{factor}"):
            checkbox = helper.wait_for_element(By.ID, f"factor-{factor}")
            if not checkbox.is_selected():
                helper.click_element(By.ID, f"factor-{factor}")
    
    # 5. 提交分析
    helper.click_element(By.ID, "submit-analysis")
    
    # 6. 等待分析完成
    try:
        result_header = helper.wait_for_element(By.ID, "analysis-result-header", timeout=90)
        assert "分析结果" in result_header.text
        helper.take_screenshot("attribution_analysis_result")
        
        # 7. 检查结果包含归因图表
        assert helper.check_element_exists(By.ID, "attribution-chart"), "归因图表不存在"
        
        # 8. 检查结果包含因素列表
        factors_table = helper.wait_for_element(By.ID, "factors-table")
        assert "贡献度" in factors_table.text, "因素表格不包含贡献度信息"
        
        # 9. 测试交互功能 - 查看因素详情
        if helper.check_element_exists(By.CLASS_NAME, "factor-detail-btn"):
            helper.click_element(By.CLASS_NAME, "factor-detail-btn")
            factor_detail = helper.wait_for_element(By.ID, "factor-detail-panel")
            assert factor_detail.is_displayed(), "因素详情面板未显示"
            helper.take_screenshot("factor_detail")
        
        logger.info("归因分析工作流程测试通过")
        
    except TimeoutException:
        helper.take_screenshot("attribution_analysis_timeout")
        assert False, "归因分析结果加载超时"


def test_user_guide_access(browser):
    """测试用户指南访问"""
    helper = WebUITestHelper(browser)
    
    # 导航到用户指南页面
    helper.navigate_to("/user-guide")
    helper.wait_for_page_load()
    helper.take_screenshot("user_guide")
    
    # 检查用户指南内容
    guide_content = helper.wait_for_element(By.ID, "guide-content")
    assert guide_content.is_displayed(), "用户指南内容未显示"
    
    # 检查指南目录
    assert helper.check_element_exists(By.ID, "guide-toc"), "用户指南目录不存在"
    
    # 测试目录导航
    if helper.check_element_exists(By.CLASS_NAME, "toc-item"):
        first_toc_item = helper.wait_for_element(By.CLASS_NAME, "toc-item")
        helper.click_element(By.CLASS_NAME, "toc-item")
        time.sleep(1)  # 等待导航完成
        helper.take_screenshot("guide_navigation")
    
    logger.info("用户指南访问测试通过")


def test_responsive_design(browser):
    """测试响应式设计"""
    helper = WebUITestHelper(browser)
    
    # 测试不同屏幕尺寸下的布局
    screen_sizes = [
        (1920, 1080),  # 桌面端
        (1366, 768),   # 小型桌面/大型笔记本
        (768, 1024),   # 平板竖屏
        (375, 812)     # 移动设备
    ]
    
    for width, height in screen_sizes:
        browser.set_window_size(width, height)
        time.sleep(1)  # 等待布局调整
        
        # 导航到首页
        helper.navigate_to("/")
        helper.wait_for_page_load()
        helper.take_screenshot(f"responsive_{width}x{height}")
        
        # 检查导航菜单在不同尺寸下的可见性
        if width < 768:
            # 移动端通常有汉堡菜单
            if helper.check_element_exists(By.ID, "mobile-menu-toggle"):
                helper.click_element(By.ID, "mobile-menu-toggle")
                time.sleep(0.5)
                helper.take_screenshot(f"mobile_menu_{width}x{height}")
        else:
            # 桌面端应该直接显示菜单
            assert helper.check_element_exists(By.ID, "nav-menu"), f"在{width}x{height}尺寸下导航菜单不可见"
    
    # 恢复窗口大小
    browser.maximize_window()
    logger.info("响应式设计测试通过")


def test_error_handling(browser):
    """测试错误处理"""
    helper = WebUITestHelper(browser)
    
    # 测试404页面
    helper.navigate_to("/non-existent-page")
    helper.wait_for_page_load()
    helper.take_screenshot("error_404")
    
    # 检查404页面内容
    if helper.check_element_exists(By.ID, "error-code"):
        error_code = helper.get_text(By.ID, "error-code")
        assert "404" in error_code, "未显示404错误代码"
    
    # 测试表单提交错误
    helper.navigate_to("/analyses/trend")
    helper.wait_for_page_load()
    
    # 不上传文件直接提交
    if helper.check_element_exists(By.ID, "submit-analysis"):
        helper.click_element(By.ID, "submit-analysis")
        time.sleep(1)
        helper.take_screenshot("form_validation_error")
        
        # 检查错误提示
        assert helper.check_element_exists(By.CLASS_NAME, "error-message"), "未显示表单验证错误"
    
    logger.info("错误处理测试通过")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 