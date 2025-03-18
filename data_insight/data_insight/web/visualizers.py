"""
可视化辅助函数
===========

提供服务器端生成可视化内容的辅助函数。
"""

import json
import base64
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple, Union


# 设置matplotlib使用Agg后端，这样可以在没有GUI的环境中生成图表
matplotlib.use('Agg')

# 设置中文字体，确保中文显示正常
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def create_line_chart(
    x_values: List[str],
    y_values: List[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    series_name: str = "",
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100,
    colors: Optional[List[str]] = None
) -> str:
    """
    创建折线图
    
    参数:
        x_values (List[str]): X轴数据
        y_values (List[float]): Y轴数据
        title (str): 图表标题
        x_label (str): X轴标签
        y_label (str): Y轴标签
        series_name (str): 数据系列名称
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        colors (List[str], optional): 线条颜色列表
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 如果没有提供颜色，使用默认颜色
    if not colors:
        colors = ['#1f77b4']  # 默认蓝色
    
    # 绘制折线图
    plt.plot(x_values, y_values, marker='o', label=series_name, color=colors[0])
    
    # 添加标题和标签
    if title:
        plt.title(title, fontsize=16)
    if x_label:
        plt.xlabel(x_label, fontsize=12)
    if y_label:
        plt.ylabel(y_label, fontsize=12)
    
    # 添加图例（如果有系列名称）
    if series_name:
        plt.legend()
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_multi_line_chart(
    x_values: List[str],
    y_values_list: List[List[float]],
    series_names: List[str],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100,
    colors: Optional[List[str]] = None
) -> str:
    """
    创建多系列折线图
    
    参数:
        x_values (List[str]): X轴数据
        y_values_list (List[List[float]]): 多个Y轴数据序列
        series_names (List[str]): 数据系列名称列表
        title (str): 图表标题
        x_label (str): X轴标签
        y_label (str): Y轴标签
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        colors (List[str], optional): 线条颜色列表
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 如果没有提供颜色，使用默认颜色
    if not colors:
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # 确保颜色足够
    if len(colors) < len(y_values_list):
        # 循环使用颜色
        colors = colors * (len(y_values_list) // len(colors) + 1)
    
    # 绘制多系列折线图
    for i, y_values in enumerate(y_values_list):
        series_name = series_names[i] if i < len(series_names) else f"系列 {i+1}"
        plt.plot(x_values, y_values, marker='o', label=series_name, color=colors[i])
    
    # 添加标题和标签
    if title:
        plt.title(title, fontsize=16)
    if x_label:
        plt.xlabel(x_label, fontsize=12)
    if y_label:
        plt.ylabel(y_label, fontsize=12)
    
    # 添加图例
    plt.legend()
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_bar_chart(
    x_values: List[str],
    y_values: List[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    series_name: str = "",
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100,
    color: str = '#1f77b4'
) -> str:
    """
    创建柱状图
    
    参数:
        x_values (List[str]): X轴数据
        y_values (List[float]): Y轴数据
        title (str): 图表标题
        x_label (str): X轴标签
        y_label (str): Y轴标签
        series_name (str): 数据系列名称
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        color (str): 柱状图颜色
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 绘制柱状图
    plt.bar(x_values, y_values, color=color, label=series_name)
    
    # 添加数据标签
    for i, v in enumerate(y_values):
        # 格式化数字显示
        if v >= 10000:
            label = f"{v/10000:.1f}万"
        else:
            label = str(v)
        plt.text(i, v, label, ha='center', va='bottom', fontsize=10)
    
    # 添加标题和标签
    if title:
        plt.title(title, fontsize=16)
    if x_label:
        plt.xlabel(x_label, fontsize=12)
    if y_label:
        plt.ylabel(y_label, fontsize=12)
    
    # 添加图例（如果有系列名称）
    if series_name:
        plt.legend()
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_multi_bar_chart(
    x_values: List[str],
    y_values_list: List[List[float]],
    series_names: List[str],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100,
    colors: Optional[List[str]] = None
) -> str:
    """
    创建多系列柱状图
    
    参数:
        x_values (List[str]): X轴数据
        y_values_list (List[List[float]]): 多个Y轴数据序列
        series_names (List[str]): 数据系列名称列表
        title (str): 图表标题
        x_label (str): X轴标签
        y_label (str): Y轴标签
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        colors (List[str], optional): 柱状图颜色列表
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 如果没有提供颜色，使用默认颜色
    if not colors:
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # 确保颜色足够
    if len(colors) < len(y_values_list):
        # 循环使用颜色
        colors = colors * (len(y_values_list) // len(colors) + 1)
    
    # 计算柱状图宽度和位置
    n_series = len(y_values_list)
    bar_width = 0.8 / n_series
    
    # 绘制多系列柱状图
    for i, y_values in enumerate(y_values_list):
        series_name = series_names[i] if i < len(series_names) else f"系列 {i+1}"
        x_positions = [x + bar_width * (i - n_series / 2 + 0.5) for x in range(len(x_values))]
        plt.bar(x_positions, y_values, width=bar_width, label=series_name, color=colors[i])
    
    # 设置X轴标签位置和标签
    plt.xticks(range(len(x_values)), x_values)
    
    # 添加标题和标签
    if title:
        plt.title(title, fontsize=16)
    if x_label:
        plt.xlabel(x_label, fontsize=12)
    if y_label:
        plt.ylabel(y_label, fontsize=12)
    
    # 添加图例
    plt.legend()
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_pie_chart(
    values: List[float],
    labels: List[str],
    title: str = "",
    figsize: Tuple[int, int] = (8, 8),
    dpi: int = 100,
    colors: Optional[List[str]] = None,
    explode: Optional[List[float]] = None
) -> str:
    """
    创建饼图
    
    参数:
        values (List[float]): 数据值
        labels (List[str]): 标签
        title (str): 图表标题
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        colors (List[str], optional): 扇区颜色列表
        explode (List[float], optional): 扇区突出显示列表
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 如果没有提供颜色，使用默认颜色
    if not colors:
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # 确保颜色足够
    if len(colors) < len(values):
        # 循环使用颜色
        colors = colors * (len(values) // len(colors) + 1)
    
    # 如果没有提供突出显示列表，创建一个全零的列表
    if not explode:
        explode = [0] * len(values)
    
    # 绘制饼图
    plt.pie(
        values,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct='%1.1f%%',  # 显示百分比
        shadow=True,
        startangle=90
    )
    
    # 保持饼图为圆形
    plt.axis('equal')
    
    # 添加标题
    if title:
        plt.title(title, fontsize=16)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_scatter_chart(
    x_values: List[float],
    y_values: List[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    series_name: str = "",
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100,
    color: str = '#1f77b4',
    add_trend_line: bool = False
) -> str:
    """
    创建散点图
    
    参数:
        x_values (List[float]): X轴数据
        y_values (List[float]): Y轴数据
        title (str): 图表标题
        x_label (str): X轴标签
        y_label (str): Y轴标签
        series_name (str): 数据系列名称
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        color (str): 点的颜色
        add_trend_line (bool): 是否添加趋势线
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 绘制散点图
    plt.scatter(x_values, y_values, color=color, label=series_name, alpha=0.7)
    
    # 添加趋势线
    if add_trend_line and len(x_values) > 1:
        try:
            # 使用numpy的polyfit函数计算趋势线
            z = np.polyfit(x_values, y_values, 1)
            p = np.poly1d(z)
            
            # 生成趋势线的x和y值
            x_trend = np.linspace(min(x_values), max(x_values), 100)
            y_trend = p(x_trend)
            
            # 绘制趋势线
            plt.plot(x_trend, y_trend, 'r--', label='趋势线')
            
            # 添加相关系数
            correlation = np.corrcoef(x_values, y_values)[0, 1]
            plt.annotate(
                f'相关系数: {correlation:.2f}',
                xy=(0.05, 0.95),
                xycoords='axes fraction',
                fontsize=12,
                backgroundcolor='w',
                alpha=0.8
            )
        except Exception as e:
            # 趋势线计算失败，记录错误但继续
            print(f"趋势线计算失败: {e}")
    
    # 添加标题和标签
    if title:
        plt.title(title, fontsize=16)
    if x_label:
        plt.xlabel(x_label, fontsize=12)
    if y_label:
        plt.ylabel(y_label, fontsize=12)
    
    # 添加图例
    plt.legend()
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_prediction_chart(
    historical_values: List[float],
    predicted_values: List[float],
    confidence_intervals: List[Dict[str, float]],
    x_values: List[str],
    title: str = "预测结果",
    x_label: str = "时间",
    y_label: str = "值",
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 100
) -> str:
    """
    创建预测图表
    
    参数:
        historical_values (List[float]): 历史数据
        predicted_values (List[float]): 预测数据
        confidence_intervals (List[Dict[str, float]]): 置信区间
        x_values (List[str]): X轴数据
        title (str): 图表标题
        x_label (str): X轴标签
        y_label (str): Y轴标签
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 分割历史数据和预测数据的x轴
    historical_x = x_values[:len(historical_values)]
    future_x = x_values[len(historical_values):]
    
    # 绘制历史数据
    plt.plot(historical_x, historical_values, color='blue', marker='o', label='历史数据')
    
    # 绘制预测数据
    plt.plot(future_x, predicted_values, color='red', marker='o', linestyle='--', label='预测值')
    
    # 绘制置信区间
    upper_bounds = [ci['上限'] for ci in confidence_intervals]
    lower_bounds = [ci['下限'] for ci in confidence_intervals]
    
    plt.fill_between(
        future_x,
        lower_bounds,
        upper_bounds,
        color='red',
        alpha=0.2,
        label='预测区间'
    )
    
    # 添加标题和标签
    if title:
        plt.title(title, fontsize=16)
    if x_label:
        plt.xlabel(x_label, fontsize=12)
    if y_label:
        plt.ylabel(y_label, fontsize=12)
    
    # 添加图例
    plt.legend()
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 调整x轴标签
    if len(x_values) > 10:
        # 如果x轴标签太多，只显示部分
        plt.xticks(
            range(0, len(x_values), len(x_values) // 10 + 1),
            [x_values[i] for i in range(0, len(x_values), len(x_values) // 10 + 1)],
            rotation=45
        )
    else:
        plt.xticks(rotation=45)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def create_network_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    title: str = "因果关系网络",
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 100
) -> str:
    """
    创建网络图
    
    参数:
        nodes (List[Dict[str, Any]]): 节点列表，每个节点应包含id和label字段
        edges (List[Dict[str, Any]]): 边列表，每个边应包含source, target和weight字段
        title (str): 图表标题
        figsize (Tuple[int, int]): 图表尺寸
        dpi (int): 图表分辨率
        
    返回:
        str: Base64编码的图表数据，可直接用于img标签的src属性
    """
    try:
        import networkx as nx
    except ImportError:
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJOjR8JpgAAAABJRU5ErkJggg=="
    
    # 创建有向图
    G = nx.DiGraph()
    
    # 添加节点
    for node in nodes:
        node_id = node['id']
        node_label = node.get('label', node_id)
        node_size = node.get('size', 1000)
        node_color = node.get('color', '#1f77b4')
        node_importance = node.get('importance', 0.5)
        
        G.add_node(
            node_id,
            label=node_label,
            size=node_size,
            color=node_color,
            importance=node_importance
        )
    
    # 添加边
    for edge in edges:
        source = edge['source']
        target = edge['target']
        weight = edge.get('weight', 1.0)
        edge_type = edge.get('type', 'direct')
        
        G.add_edge(
            source,
            target,
            weight=weight,
            type=edge_type
        )
    
    # 创建图表
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 设置节点位置
    pos = nx.spring_layout(G, seed=42)
    
    # 获取节点属性
    node_sizes = [G.nodes[node].get('size', 1000) for node in G.nodes()]
    node_colors = [G.nodes[node].get('color', '#1f77b4') for node in G.nodes()]
    node_labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
    
    # 获取边属性
    edge_weights = [G[u][v].get('weight', 1.0) for u, v in G.edges()]
    edge_colors = []
    
    for u, v in G.edges():
        edge_type = G[u][v].get('type', 'direct')
        if edge_type == 'direct':
            edge_colors.append('blue')
        elif edge_type == 'inverse':
            edge_colors.append('red')
        else:
            edge_colors.append('gray')
    
    # 绘制节点
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        alpha=0.8
    )
    
    # 绘制边
    nx.draw_networkx_edges(
        G,
        pos,
        width=[w * 2 for w in edge_weights],
        edge_color=edge_colors,
        alpha=0.7,
        connectionstyle='arc3,rad=0.1',
        arrowsize=20
    )
    
    # 绘制标签
    nx.draw_networkx_labels(
        G,
        pos,
        labels=node_labels,
        font_size=12,
        font_weight='bold'
    )
    
    # 添加标题
    plt.title(title, fontsize=16)
    
    # 去除坐标轴
    plt.axis('off')
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表保存到内存中
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # 关闭图表，释放内存
    plt.close()
    
    # 将图表转换为Base64编码的字符串
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 返回可在HTML中使用的数据URL
    return f"data:image/png;base64,{image_data}"


def format_value(
    value: float,
    precision: int = 2,
    use_wan: bool = True,
    unit: str = ""
) -> str:
    """
    格式化数值显示
    
    参数:
        value (float): 要格式化的数值
        precision (int): 小数位数
        use_wan (bool): 是否使用万、亿等中文单位
        unit (str): 单位
        
    返回:
        str: 格式化后的字符串
    """
    # 处理0和None
    if value is None or value == 0:
        return f"0{unit}"
    
    # 负数处理
    is_negative = value < 0
    abs_value = abs(value)
    
    # 根据大小选择不同的格式化方式
    if use_wan:
        if abs_value >= 1e8:  # 亿
            formatted = f"{abs_value / 1e8:.{precision}f}亿"
        elif abs_value >= 1e4:  # 万
            formatted = f"{abs_value / 1e4:.{precision}f}万"
        else:
            formatted = f"{abs_value:.{precision}f}"
    else:
        if abs_value >= 1e9:  # 十亿
            formatted = f"{abs_value / 1e9:.{precision}f}B"
        elif abs_value >= 1e6:  # 百万
            formatted = f"{abs_value / 1e6:.{precision}f}M"
        elif abs_value >= 1e3:  # 千
            formatted = f"{abs_value / 1e3:.{precision}f}K"
        else:
            formatted = f"{abs_value:.{precision}f}"
    
    # 去除末尾的0和小数点
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
    
    # 添加负号和单位
    if is_negative:
        formatted = f"-{formatted}"
    
    # 添加单位
    if unit:
        formatted = f"{formatted}{unit}"
    
    return formatted


def format_percentage(
    value: Optional[float],
    precision: int = 2
) -> str:
    """
    格式化百分比显示
    
    参数:
        value (Optional[float]): 要格式化的数值，应为小数形式（如0.1表示10%）
        precision (int): 小数位数
        
    返回:
        str: 格式化后的百分比字符串
    """
    if value is None:
        return "N/A"
    
    # 转换为百分比并格式化
    percentage = value * 100
    formatted = f"{percentage:.{precision}f}%"
    
    # 去除末尾的0和小数点
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
        if formatted == '-%':
            formatted = '0%'
    
    return formatted 