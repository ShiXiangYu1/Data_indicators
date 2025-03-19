#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导出路由模块
==========

提供分析结果导出功能，支持多种格式。
"""

import os
import io
import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter, Request, Response, BackgroundTasks, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

from data_insight.api.middlewares.auth import token_required
from data_insight.api.middlewares.rate_limiter import rate_limit
from data_insight.api.utils.response_formatter import format_success_response, format_error_response
from data_insight.utils.metrics import increment_request_count, record_request_duration
from data_insight.utils.performance import time_it

# 创建一个路由器
router = APIRouter(prefix="/export", tags=["结果导出"])

# 创建日志记录器
logger = logging.getLogger(__name__)

# 导出格式
EXPORT_FORMATS = {
    "csv": {
        "content_type": "text/csv",
        "extension": "csv"
    },
    "excel": {
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "extension": "xlsx"
    },
    "json": {
        "content_type": "application/json",
        "extension": "json"
    },
    "pdf": {
        "content_type": "application/pdf",
        "extension": "pdf"
    }
}

# 临时文件存储路径
TEMP_DIR = os.environ.get("TEMP_EXPORT_DIR", "tmp/exports")

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

class ExportParams(BaseModel):
    """导出参数模型"""
    format: str
    data: Dict[str, Any]
    filename: Optional[str] = None
    include_metadata: bool = True
    page_title: Optional[str] = None
    page_orientation: str = "portrait"
    column_config: Optional[Dict[str, Dict[str, Any]]] = None


@router.post("/result", summary="导出分析结果", 
            description="将分析结果导出为指定格式的文件")
@rate_limit
@token_required
@time_it(name="export_result")
async def export_result(params: ExportParams, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    导出分析结果为指定格式
    
    支持的格式包括CSV、Excel、JSON和PDF
    
    参数:
        params: 导出参数，包括格式、数据和文件名等
        background_tasks: 后台任务
        
    返回:
        Dict[str, Any]: 导出结果，包括文件URL等信息
    """
    # 记录请求
    increment_request_count("/export/result", "POST", 200)
    
    # 检查导出格式是否有效
    if params.format not in EXPORT_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的导出格式: {params.format}。支持的格式有: {', '.join(EXPORT_FORMATS.keys())}"
        )
        
    # 创建唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_string = str(uuid.uuid4())[:8]
    extension = EXPORT_FORMATS[params.format]["extension"]
    
    if params.filename:
        # 移除不安全字符并添加时间戳
        safe_filename = "".join([c if c.isalnum() or c in "._- " else "_" for c in params.filename])
        filename = f"{safe_filename}_{timestamp}.{extension}"
    else:
        # 使用默认文件名格式
        filename = f"data_insight_export_{timestamp}_{random_string}.{extension}"
    
    # 完整的文件路径
    filepath = os.path.join(TEMP_DIR, filename)
    
    try:
        # 根据不同的格式导出数据
        if params.format == "csv":
            export_to_csv(params.data, filepath, params.column_config)
        elif params.format == "excel":
            export_to_excel(params.data, filepath, params.column_config)
        elif params.format == "json":
            export_to_json(params.data, filepath, params.include_metadata)
        elif params.format == "pdf":
            export_to_pdf(params.data, filepath, params.page_title, params.page_orientation, params.column_config)
        
        # 计算过期时间（24小时后）
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        
        # 注册清理任务（24小时后删除文件）
        background_tasks.add_task(cleanup_export_file, filepath)
        
        # 构建下载URL，注意这里应该是相对路径或完整的URL，取决于你的部署方式
        download_url = f"/api/v1/export/download?filename={filename}"
        
        # 返回导出结果
        return format_success_response(
            data={
                "file_url": download_url,
                "file_name": filename,
                "file_size": file_size,
                "file_type": EXPORT_FORMATS[params.format]["content_type"],
                "expires_at": expires_at
            },
            message="导出成功",
            status_code=200
        )
    
    except Exception as e:
        logger.error(f"导出失败: {str(e)}", exc_info=True)
        return format_error_response(
            message="导出失败",
            status_code=500,
            error_type="ExportError",
            error_detail={"reason": str(e)}
        )


@router.get("/download", summary="下载导出文件", 
            description="下载已导出的文件")
@rate_limit
async def download_export(filename: str = Query(..., description="文件名称")) -> Response:
    """
    下载已导出的文件
    
    参数:
        filename: 文件名称
        
    返回:
        Response: 文件下载响应
    """
    # 记录请求
    increment_request_count("/export/download", "GET", 200)
    
    # 构建文件路径
    filepath = os.path.join(TEMP_DIR, filename)
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"文件 {filename} 不存在或已过期"
        )
    
    # 根据文件扩展名确定内容类型
    extension = filename.split(".")[-1].lower()
    content_type = next(
        (v["content_type"] for k, v in EXPORT_FORMATS.items() if v["extension"] == extension),
        "application/octet-stream"
    )
    
    # 返回文件下载响应
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=content_type
    )


def export_to_csv(data: Dict[str, Any], filepath: str, column_config: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
    """
    导出数据为CSV格式
    
    参数:
        data: 要导出的数据
        filepath: 导出文件路径
        column_config: 列配置
    """
    # 提取数据并转换为DataFrame
    df = extract_data_to_dataframe(data, column_config)
    
    # 导出为CSV
    df.to_csv(filepath, index=False, encoding="utf-8-sig")


def export_to_excel(data: Dict[str, Any], filepath: str, column_config: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
    """
    导出数据为Excel格式
    
    参数:
        data: 要导出的数据
        filepath: 导出文件路径
        column_config: 列配置
    """
    # 提取数据并转换为DataFrame
    df = extract_data_to_dataframe(data, column_config)
    
    # 导出为Excel
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="数据分析结果")
        
        # 如果有多个数据集，则创建多个工作表
        if "data_sets" in data and isinstance(data["data_sets"], dict):
            for name, dataset in data["data_sets"].items():
                if isinstance(dataset, list) and len(dataset) > 0:
                    sub_df = pd.DataFrame(dataset)
                    sub_df.to_excel(writer, index=False, sheet_name=name[:31])  # Excel工作表名称最长31字符


def export_to_json(data: Dict[str, Any], filepath: str, include_metadata: bool = True) -> None:
    """
    导出数据为JSON格式
    
    参数:
        data: 要导出的数据
        filepath: 导出文件路径
        include_metadata: 是否包含元数据
    """
    # 如果不包含元数据，只导出数据部分
    if not include_metadata and "data" in data:
        export_data = data["data"]
    else:
        export_data = data
    
    # 导出为JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def export_to_pdf(data: Dict[str, Any], filepath: str, page_title: Optional[str] = None, 
                 page_orientation: str = "portrait", column_config: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
    """
    导出数据为PDF格式
    
    参数:
        data: 要导出的数据
        filepath: 导出文件路径
        page_title: 页面标题
        page_orientation: 页面方向（纵向或横向）
        column_config: 列配置
    """
    try:
        import matplotlib.pyplot as plt
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 尝试注册中文字体，确保中文正确显示
        try:
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
        except:
            pass  # 如果字体不可用，使用默认字体
        
        # 设置页面大小
        page_size = letter
        if page_orientation.lower() == "landscape":
            page_size = landscape(letter)
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            filepath,
            pagesize=page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 获取样式
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        normal_style = styles["Normal"]
        
        # 创建元素列表
        elements = []
        
        # 添加标题
        if page_title:
            elements.append(Paragraph(page_title, title_style))
        else:
            elements.append(Paragraph("数据分析结果", title_style))
        
        elements.append(Spacer(1, 12))
        
        # 提取数据并转换为DataFrame
        df = extract_data_to_dataframe(data, column_config)
        
        # 如果数据中包含图表，添加图表
        if "charts" in data and isinstance(data["charts"], list):
            for chart_data in data["charts"]:
                if "chart_type" in chart_data and "data" in chart_data:
                    # 使用matplotlib生成图表
                    try:
                        fig, ax = plt.subplots(figsize=(7, 5))
                        if chart_data["chart_type"] == "line":
                            x = chart_data["data"].get("x", range(len(chart_data["data"].get("y", []))))
                            y = chart_data["data"].get("y", [])
                            ax.plot(x, y)
                        elif chart_data["chart_type"] == "bar":
                            x = chart_data["data"].get("x", range(len(chart_data["data"].get("y", []))))
                            y = chart_data["data"].get("y", [])
                            ax.bar(x, y)
                        elif chart_data["chart_type"] == "scatter":
                            x = chart_data["data"].get("x", [])
                            y = chart_data["data"].get("y", [])
                            ax.scatter(x, y)
                        
                        # 添加标题和标签
                        if "title" in chart_data:
                            ax.set_title(chart_data["title"])
                        if "x_label" in chart_data:
                            ax.set_xlabel(chart_data["x_label"])
                        if "y_label" in chart_data:
                            ax.set_ylabel(chart_data["y_label"])
                        
                        # 保存图表到临时文件
                        img_path = os.path.join(TEMP_DIR, f"chart_{uuid.uuid4()}.png")
                        fig.savefig(img_path, dpi=300, bbox_inches="tight")
                        plt.close(fig)
                        
                        # 添加图表到PDF
                        elements.append(Spacer(1, 12))
                        elements.append(Image(img_path, width=400, height=300))
                        elements.append(Spacer(1, 12))
                        
                        # 添加图表描述
                        if "description" in chart_data:
                            elements.append(Paragraph(chart_data["description"], normal_style))
                            elements.append(Spacer(1, 12))
                    except Exception as e:
                        logger.warning(f"生成图表失败: {str(e)}")
        
        # 如果数据中包含表格，添加表格
        if not df.empty:
            # 将DataFrame转换为表格数据
            table_data = [df.columns.tolist()] + df.values.tolist()
            
            # 创建表格
            table = Table(table_data)
            
            # 设置表格样式
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            table.setStyle(style)
            
            # 添加表格到PDF
            elements.append(table)
        
        # 添加分析结果和建议
        if "analysis" in data and isinstance(data["analysis"], dict):
            elements.append(Spacer(1, 24))
            elements.append(Paragraph("分析结果", styles["Heading2"]))
            elements.append(Spacer(1, 12))
            
            for key, value in data["analysis"].items():
                if isinstance(value, str):
                    elements.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
                    elements.append(Spacer(1, 6))
        
        if "recommendations" in data and isinstance(data["recommendations"], list):
            elements.append(Spacer(1, 24))
            elements.append(Paragraph("建议", styles["Heading2"]))
            elements.append(Spacer(1, 12))
            
            for i, recommendation in enumerate(data["recommendations"], 1):
                elements.append(Paragraph(f"{i}. {recommendation}", normal_style))
                elements.append(Spacer(1, 6))
        
        # 生成PDF
        doc.build(elements)
        
    except ImportError as e:
        logger.error(f"PDF导出依赖库缺失: {str(e)}")
        raise RuntimeError(f"PDF导出需要额外的依赖库: {str(e)}")


def extract_data_to_dataframe(data: Dict[str, Any], column_config: Optional[Dict[str, Dict[str, Any]]] = None) -> pd.DataFrame:
    """
    从数据中提取表格数据并转换为DataFrame
    
    参数:
        data: 要提取的数据
        column_config: 列配置
        
    返回:
        pd.DataFrame: 转换后的DataFrame
    """
    # 如果数据中有data键，使用它
    if "data" in data and isinstance(data["data"], (list, dict)):
        if isinstance(data["data"], list):
            df = pd.DataFrame(data["data"])
        else:
            # 尝试找到数据中的列表
            for key, value in data["data"].items():
                if isinstance(value, list) and len(value) > 0:
                    df = pd.DataFrame(value)
                    break
            else:
                # 如果没有找到列表，将字典转换为单行DataFrame
                df = pd.DataFrame([data["data"]])
    # 如果有results键，使用它
    elif "results" in data and isinstance(data["results"], (list, dict)):
        if isinstance(data["results"], list):
            df = pd.DataFrame(data["results"])
        else:
            # 尝试找到结果中的列表
            for key, value in data["results"].items():
                if isinstance(value, list) and len(value) > 0:
                    df = pd.DataFrame(value)
                    break
            else:
                # 如果没有找到列表，将字典转换为单行DataFrame
                df = pd.DataFrame([data["results"]])
    # 如果有items键，使用它
    elif "items" in data and isinstance(data["items"], list):
        df = pd.DataFrame(data["items"])
    # 如果数据本身是列表，直接使用
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    # 如果什么都没有找到，创建空DataFrame
    else:
        df = pd.DataFrame()
    
    # 应用列配置
    if column_config and not df.empty:
        # 只保留配置中指定的列
        if "include_columns" in column_config:
            include_columns = column_config["include_columns"]
            df = df[[col for col in include_columns if col in df.columns]]
        
        # 重命名列
        if "rename_columns" in column_config:
            rename_map = column_config["rename_columns"]
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        
        # 排序列
        if "column_order" in column_config:
            column_order = column_config["column_order"]
            existing_columns = [col for col in column_order if col in df.columns]
            other_columns = [col for col in df.columns if col not in column_order]
            df = df[existing_columns + other_columns]
    
    return df


async def cleanup_export_file(filepath: str, delay_hours: int = 24) -> None:
    """
    清理导出文件
    
    参数:
        filepath: 文件路径
        delay_hours: 延迟时间（小时）
    """
    import asyncio
    
    # 延迟指定时间
    await asyncio.sleep(delay_hours * 3600)
    
    # 尝试删除文件
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"已清理过期导出文件: {filepath}")
    except Exception as e:
        logger.error(f"清理导出文件失败: {filepath}, 错误: {str(e)}") 