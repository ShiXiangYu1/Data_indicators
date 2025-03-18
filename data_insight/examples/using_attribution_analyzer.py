"""
归因分析器使用示例

演示如何使用data_insight包中的归因分析器进行指标变化的归因分析。
"""

import json
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 添加项目根目录到系统路径，以便能够导入data_insight包
sys.path.append(str(Path(__file__).parent.parent))

from data_insight.core.attribution_analyzer import AttributionAnalyzer
from data_insight.core.text_generator import TextGenerator


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


def generate_sales_attribution_data():
    """
    生成销售额归因分析示例数据
    
    返回:
        dict: 销售额及影响因素的数据
    """
    # 设置随机种子以保证结果可重复
    np.random.seed(42)
    
    # 生成时间周期
    time_periods = [f"2023年{i+1}月" for i in range(12)]
    
    # 生成广告支出数据（增长趋势）
    ad_spend = np.linspace(100, 200, 12) + np.random.normal(0, 5, 12)
    
    # 生成促销活动数据（随机波动）
    promotions = np.random.randint(0, 5, 12)
    
    # 生成季节性因素（夏季高，冬季低）
    seasonality = np.sin(np.linspace(0, 2*np.pi, 12)) * 50 + 100
    
    # 生成竞品价格数据（下降趋势）
    competitor_price = np.linspace(50, 30, 12) + np.random.normal(0, 2, 12)
    
    # 生成销售额数据（受以上因素综合影响）
    # 销售额 = 2 * 广告支出 + 20 * 促销活动 + 1.5 * 季节性因素 - 3 * 竞品价格 + 噪声
    sales = (
        2 * ad_spend + 
        20 * promotions + 
        1.5 * seasonality - 
        3 * competitor_price + 
        np.random.normal(0, 30, 12)
    )
    
    # 构建数据字典
    data = {
        "target": "月度销售额",
        "target_values": sales.tolist(),
        "factors": {
            "广告支出": ad_spend.tolist(),
            "促销活动次数": promotions.tolist(),
            "季节性因素": seasonality.tolist(),
            "竞品价格": competitor_price.tolist()
        },
        "time_periods": time_periods,
        "current_period": "2023年12月"
    }
    
    return data


def analyze_sales_attribution():
    """
    分析销售额归因
    """
    print("\n=== 销售额归因分析 ===\n")
    
    # 生成销售额归因数据
    data = generate_sales_attribution_data()
    
    # 创建归因分析器
    analyzer = AttributionAnalyzer(method="linear")
    
    # 运行归因分析
    result = analyzer.analyze(data)
    
    # 打印基本信息
    print("基本信息:")
    for key, value in result["基本信息"].items():
        print(f"{key}: {value}")
    
    # 打印归因结果
    print("\n归因结果:")
    attribution_result = result["归因结果"]
    
    print(f"覆盖度: {attribution_result['覆盖度']:.2f}")
    print(f"置信度: {attribution_result['置信度']}")
    print(f"未解释占比: {attribution_result['未解释占比']:.2f}")
    
    print("\n影响因素:")
    for factor in attribution_result["影响因素"]:
        print(f"- {factor['因素名称']}: 贡献度 {factor['贡献度']:.2f}, 影响类型 {factor['影响类型']}, 影响方向 {factor['影响方向']}")
    
    # 打印相关性分析
    print("\n相关性分析:")
    correlations = result["相关性分析"]["因素相关性"]
    for factor, corr_info in correlations.items():
        print(f"- {factor}: 相关系数 {corr_info['相关系数']:.2f}, {corr_info['相关方向']}")
    
    # 可视化归因结果
    visualize_attribution_result(attribution_result["影响因素"])
    
    return result


def generate_conversion_rate_attribution_data():
    """
    生成转化率归因分析示例数据（使用随机森林方法）
    
    返回:
        dict: 转化率及影响因素的数据
    """
    # 设置随机种子以保证结果可重复
    np.random.seed(43)
    
    # 生成数据点数
    n = 50
    
    # 生成页面加载时间（正态分布，单位秒）
    page_load_time = np.random.normal(3, 1, n)
    
    # 生成广告质量分数（1-10分）
    ad_quality = np.random.uniform(3, 9, n)
    
    # 生成访问设备类型（0: 手机, 1: 平板, 2: 电脑），非线性影响
    device_type = np.random.choice([0, 1, 2], n, p=[0.6, 0.2, 0.2])
    
    # 生成产品价格（正态分布）
    product_price = np.random.normal(100, 30, n)
    
    # 生成用户历史购买次数（泊松分布）
    purchase_history = np.random.poisson(2, n)
    
    # 创建非线性关系的转化率
    # 基础转化率 = 0.05，然后受到各种因素的非线性影响
    conversion_rate = (
        0.05 +  # 基础转化率
        -0.02 * np.log(page_load_time) +  # 页面加载时间越长，转化率越低（非线性）
        0.01 * ad_quality +  # 广告质量越高，转化率越高（线性）
        0.02 * (device_type == 2) +  # 电脑用户转化率更高
        0.01 * (device_type == 1) +  # 平板用户转化率略高
        -0.0001 * product_price +  # 价格越高，转化率越低（线性）
        0.01 * np.log(purchase_history + 1) +  # 购买历史越多，转化率越高（非线性）
        np.random.normal(0, 0.01, n)  # 添加随机噪声
    )
    
    # 确保转化率在有效范围内(0-1)
    conversion_rate = np.clip(conversion_rate, 0.01, 0.99)
    
    # 构建数据字典
    data = {
        "target": "用户转化率",
        "target_values": conversion_rate.tolist(),
        "factors": {
            "页面加载时间": page_load_time.tolist(),
            "广告质量分数": ad_quality.tolist(),
            "设备类型": device_type.tolist(),
            "产品价格": product_price.tolist(),
            "历史购买次数": purchase_history.tolist()
        },
        "method": "random_forest"  # 使用随机森林分析非线性关系
    }
    
    return data


def analyze_conversion_rate_attribution():
    """
    分析转化率归因（使用随机森林分析非线性关系）
    """
    print("\n=== 转化率归因分析（随机森林） ===\n")
    
    # 生成转化率归因数据
    data = generate_conversion_rate_attribution_data()
    
    # 创建归因分析器
    analyzer = AttributionAnalyzer(method="random_forest", min_correlation=0.1)
    
    # 运行归因分析
    result = analyzer.analyze(data)
    
    # 打印基本信息
    print("基本信息:")
    for key, value in result["基本信息"].items():
        print(f"{key}: {value}")
    
    # 打印归因结果
    print("\n归因结果:")
    attribution_result = result["归因结果"]
    
    print(f"覆盖度: {attribution_result['覆盖度']:.2f}")
    print(f"置信度: {attribution_result['置信度']}")
    
    print("\n影响因素:")
    for factor in attribution_result["影响因素"]:
        print(f"- {factor['因素名称']}: 贡献度 {factor['贡献度']:.2f}, 影响类型 {factor['影响类型']}, 影响方向 {factor['影响方向']}")
    
    # 打印相关性分析
    print("\n相关性分析:")
    correlations = result["相关性分析"]["因素相关性"]
    for factor, corr_info in correlations.items():
        print(f"- {factor}: 相关系数 {corr_info['相关系数']:.2f}, {corr_info['相关方向']}")
    
    # 可视化归因结果
    visualize_attribution_result(attribution_result["影响因素"])
    
    return result


def generate_cost_increase_attribution_data():
    """
    生成成本增长归因分析示例数据
    
    返回:
        dict: 成本及影响因素的数据
    """
    # 设置随机种子以保证结果可重复
    np.random.seed(44)
    
    # 生成时间周期
    months = 24
    time_periods = [f"{2022 + i//12}年{i%12+1}月" for i in range(months)]
    
    # 生成原材料价格数据（增长趋势）
    raw_material_price = np.linspace(100, 150, months) + np.random.normal(0, 5, months)
    
    # 生成劳动力成本数据（阶梯式增长）
    labor_cost = np.ones(months) * 200
    labor_cost[6:12] = 210  # 第7-12个月上涨
    labor_cost[12:18] = 220  # 第13-18个月上涨
    labor_cost[18:] = 230  # 第19-24个月上涨
    labor_cost += np.random.normal(0, 3, months)
    
    # 生成能源成本数据（季节性波动）
    energy_cost = np.sin(np.linspace(0, 4*np.pi, months)) * 20 + 80 + np.linspace(0, 20, months)
    
    # 生成运输成本数据（与油价相关，上升趋势）
    transportation_cost = np.linspace(50, 70, months) + np.random.normal(0, 2, months)
    
    # 生成生产效率数据（效率提升，成本下降）
    efficiency_improvement = np.linspace(1, 0.8, months) + np.random.normal(0, 0.03, months)
    
    # 生成总成本数据（受以上因素综合影响）
    total_cost = (
        1.2 * raw_material_price + 
        1.5 * labor_cost + 
        0.8 * energy_cost + 
        0.5 * transportation_cost
    ) * efficiency_improvement + np.random.normal(0, 20, months)
    
    # 构建数据字典
    data = {
        "target": "生产总成本",
        "target_values": total_cost.tolist(),
        "factors": {
            "原材料价格": raw_material_price.tolist(),
            "劳动力成本": labor_cost.tolist(),
            "能源成本": energy_cost.tolist(),
            "运输成本": transportation_cost.tolist(),
            "生产效率": efficiency_improvement.tolist()
        },
        "time_periods": time_periods,
        "current_period": time_periods[-1]
    }
    
    return data


def analyze_cost_increase_attribution():
    """
    分析成本增长归因
    """
    print("\n=== 成本增长归因分析 ===\n")
    
    # 生成成本归因数据
    data = generate_cost_increase_attribution_data()
    
    # 创建归因分析器
    analyzer = AttributionAnalyzer(method="linear", max_factors=4)
    
    # 运行归因分析
    result = analyzer.analyze(data)
    
    # 打印基本信息
    print("基本信息:")
    for key, value in result["基本信息"].items():
        print(f"{key}: {value}")
    
    # 打印归因结果
    print("\n归因结果:")
    attribution_result = result["归因结果"]
    
    print(f"覆盖度: {attribution_result['覆盖度']:.2f}")
    print(f"置信度: {attribution_result['置信度']}")
    
    print("\n影响因素:")
    for factor in attribution_result["影响因素"]:
        print(f"- {factor['因素名称']}: 贡献度 {factor['贡献度']:.2f}, 影响类型 {factor['影响类型']}, 影响方向 {factor['影响方向']}")
    
    # 可视化归因结果
    visualize_attribution_result(attribution_result["影响因素"])
    
    # 分析时间序列上的主要影响因素
    if "时间序列分析" in result:
        time_series = result["时间序列分析"]
        time_impacts = time_series["主要影响因素"]
        
        print("\n时间序列上的主要影响因素变化:")
        
        # 获取最近6个月的主要影响因素
        recent_months = time_periods[-6:]
        for i in range(len(time_periods)-6, len(time_periods)):
            if str(i) in time_impacts:
                impact = time_impacts[str(i)]
                print(f"- {time_periods[i]}: {impact['因素']} (影响值: {impact['影响值']:.2f})")
    
    return result


def visualize_attribution_result(factors):
    """
    可视化归因分析结果
    
    参数:
        factors (List[Dict]): 影响因素列表
    """
    # 提取因素名称和贡献度
    names = [factor["因素名称"] for factor in factors]
    contributions = [factor["贡献度"] for factor in factors]
    
    # 设置颜色映射
    impact_types = [factor["影响类型"] for factor in factors]
    colors = []
    for impact_type in impact_types:
        if impact_type == "主要":
            colors.append("#FF5733")  # 红色
        elif impact_type == "重要":
            colors.append("#FFC300")  # 黄色
        elif impact_type == "次要":
            colors.append("#36A2EB")  # 蓝色
        else:
            colors.append("#DCDCDC")  # 灰色
    
    # 创建横向条形图
    plt.figure(figsize=(10, 6))
    bars = plt.barh(names, contributions, color=colors)
    
    # 添加数值标签
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                 va='center', fontsize=10)
    
    # 添加图表标题和标签
    plt.title("因素贡献度分析", fontsize=14)
    plt.xlabel("贡献度", fontsize=12)
    plt.ylabel("影响因素", fontsize=12)
    plt.tight_layout()
    
    # 显示图表
    plt.show()


def main():
    """主函数"""
    # 运行销售额归因分析
    analyze_sales_attribution()
    print("\n" + "="*50 + "\n")
    
    # 运行转化率归因分析（随机森林）
    analyze_conversion_rate_attribution()
    print("\n" + "="*50 + "\n")
    
    # 运行成本增长归因分析
    analyze_cost_increase_attribution()


if __name__ == "__main__":
    main() 