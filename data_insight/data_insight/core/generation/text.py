"""
文本生成器
========

将分析结果转换为易于理解的自然语言文本。
"""

from typing import Dict, Any, List, Optional, Union
import logging
import random

from data_insight.core.interfaces.generator import GeneratorInterface


class TextGenerator(GeneratorInterface):
    """
    文本生成器
    
    将分析结果转换为人类可读的自然语言文本。
    """
    
    def __init__(self):
        """初始化文本生成器"""
        self.logger = logging.getLogger("data_insight.generation.text")
        self.language = "zh-CN"
        self.style = "标准"
        self.templates = self._load_default_templates()
    
    def generate(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None,
                template_id: Optional[str] = None) -> str:
        """
        基于数据和上下文生成文本
        
        参数:
            data (Dict[str, Any]): 数据
            context (Dict[str, Any], optional): 上下文信息
            template_id (str, optional): 模板ID
            
        返回:
            str: 生成的文本
        """
        # 验证输入数据
        self.validate_input(data, ["data"])
        
        # 提取数据和上下文
        analysis_data = data.get("data", data)  # 支持直接传递分析数据或封装在data字段中
        ctx = context or {}
        
        # 确定要使用的模板
        template_to_use = template_id or self._determine_template(analysis_data, ctx)
        
        # 生成文本
        if "分析" in analysis_data:
            # 针对指标分析结果的处理
            return self._generate_metric_insight(analysis_data, template_to_use)
        elif "prediction" in data:
            # 针对预测结果的处理
            return self._generate_prediction_insight(data["prediction"], template_to_use)
        elif "对比分析" in analysis_data or "相关性分析" in analysis_data:
            # 针对对比分析结果的处理
            return self._generate_comparison_insight(analysis_data, template_to_use)
        else:
            # 默认处理
            return self._generate_generic_insight(analysis_data, template_to_use)
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证输入数据是否包含所有必需字段
        
        参数:
            data (Dict[str, Any]): 需要验证的数据
            required_fields (List[str]): 必需字段列表
            
        返回:
            bool: 验证是否通过
            
        异常:
            ValueError: 如果缺少必需字段
        """
        if not isinstance(data, dict):
            raise TypeError(f"输入数据必须是字典类型，但收到了 {type(data)}")
            
        # 检查所有必需字段
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
            
        return True
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        获取可用的模板列表
        
        返回:
            List[Dict[str, Any]]: 模板列表，每个模板包含ID、名称、描述等信息
        """
        return [
            {"id": template_id, "name": info["name"], "description": info["description"]}
            for template_id, info in self.templates.items()
        ]
    
    def add_template(self, template_id: str, template_content: str, 
                     template_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加新模板
        
        参数:
            template_id (str): 模板ID
            template_content (str): 模板内容
            template_metadata (Dict[str, Any], optional): 模板元数据
            
        返回:
            bool: 是否成功添加模板
            
        异常:
            ValueError: 如果模板ID已存在
        """
        if template_id in self.templates:
            raise ValueError(f"模板ID已存在: {template_id}")
        
        metadata = template_metadata or {}
        
        self.templates[template_id] = {
            "content": template_content,
            "name": metadata.get("name", template_id),
            "description": metadata.get("description", ""),
            "type": metadata.get("type", "通用")
        }
        
        return True
    
    def remove_template(self, template_id: str) -> bool:
        """
        移除模板
        
        参数:
            template_id (str): 模板ID
            
        返回:
            bool: 是否成功移除模板
            
        异常:
            ValueError: 如果模板ID不存在
        """
        if template_id not in self.templates:
            raise ValueError(f"模板ID不存在: {template_id}")
        
        del self.templates[template_id]
        
        return True
    
    def set_language(self, language: str) -> bool:
        """
        设置生成文本的语言
        
        参数:
            language (str): 语言代码，如"zh-CN"、"en-US"
            
        返回:
            bool: 是否成功设置语言
            
        异常:
            ValueError: 如果语言不受支持
        """
        supported_languages = ["zh-CN", "en-US"]
        if language not in supported_languages:
            raise ValueError(f"不支持的语言: {language}，支持的语言有: {', '.join(supported_languages)}")
        
        self.language = language
        
        return True
    
    def set_style(self, style: str) -> bool:
        """
        设置生成文本的风格
        
        参数:
            style (str): 风格名称，如"专业"、"通俗"、"简洁"
            
        返回:
            bool: 是否成功设置风格
            
        异常:
            ValueError: 如果风格不受支持
        """
        supported_styles = ["标准", "专业", "通俗", "简洁"]
        if style not in supported_styles:
            raise ValueError(f"不支持的风格: {style}，支持的风格有: {', '.join(supported_styles)}")
        
        self.style = style
        
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取生成器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、支持的语言和风格等
        """
        return {
            "name": "TextGenerator",
            "version": "1.0.0",
            "description": "将分析结果转换为易于理解的自然语言文本",
            "supported_languages": ["zh-CN", "en-US"],
            "supported_styles": ["标准", "专业", "通俗", "简洁"],
            "current_language": self.language,
            "current_style": self.style,
            "template_count": len(self.templates)
        }
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        加载默认模板
        
        返回:
            Dict[str, Dict[str, Any]]: 模板字典
        """
        return {
            "metric_standard": {
                "name": "指标标准模板",
                "description": "用于生成指标分析的标准文本",
                "type": "指标分析",
                "content": "{指标名称}为{当前值}{单位}，{变化描述}。{趋势描述}{异常描述}{统计描述}"
            },
            "metric_professional": {
                "name": "指标专业模板",
                "description": "用于生成指标分析的专业文本",
                "type": "指标分析",
                "content": "指标[{指标名称}]当前值为{当前值}{单位}，{时间周期}。{变化描述}。通过时间序列分析，{趋势描述}。{异常描述}{统计描述}"
            },
            "metric_simple": {
                "name": "指标简洁模板",
                "description": "用于生成指标分析的简洁文本",
                "type": "指标分析",
                "content": "{指标名称}: {当前值}{单位}, {变化描述简短}。{趋势描述简短}"
            },
            "comparison_standard": {
                "name": "对比标准模板",
                "description": "用于生成对比分析的标准文本",
                "type": "对比分析",
                "content": "{指标1}与{指标2}的对比：{差异描述}。{相关性描述}{趋势对比}"
            },
            "prediction_standard": {
                "name": "预测标准模板",
                "description": "用于生成预测结果的标准文本",
                "type": "预测分析",
                "content": "基于历史数据预测，{指标名称}在未来{预测期数}期的预测值为{预测值列表}。{趋势预测}{置信区间描述}"
            }
        }
    
    def _determine_template(self, data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        根据数据和上下文确定要使用的模板
        
        参数:
            data (Dict[str, Any]): 数据
            context (Dict[str, Any]): 上下文信息
            
        返回:
            str: 模板ID
        """
        # 根据数据类型选择模板类型
        if "基本信息" in data and "变化分析" in data:
            template_type = "指标分析"
        elif "prediction" in data:
            template_type = "预测分析"
        elif "对比分析" in data or "相关性分析" in data:
            template_type = "对比分析"
        else:
            template_type = "通用"
        
        # 根据文本风格选择具体模板
        if self.style == "专业" and template_type == "指标分析":
            return "metric_professional"
        elif self.style == "简洁" and template_type == "指标分析":
            return "metric_simple"
        elif template_type == "对比分析":
            return "comparison_standard"
        elif template_type == "预测分析":
            return "prediction_standard"
        else:
            return "metric_standard"
    
    def _generate_metric_insight(self, data: Dict[str, Any], template_id: str) -> str:
        """
        生成指标洞察文本
        
        参数:
            data (Dict[str, Any]): 指标分析数据
            template_id (str): 模板ID
            
        返回:
            str: 生成的文本
        """
        # 提取基本信息
        basic_info = data.get("基本信息", {})
        change_analysis = data.get("变化分析", {})
        trend_analysis = data.get("趋势分析", {})
        anomaly_detection = data.get("异常检测", {})
        stats = data.get("统计信息", {})
        
        # 指标名称和当前值
        metric_name = basic_info.get("指标名称", "未知指标")
        current_value = basic_info.get("当前值", 0)
        unit = basic_info.get("单位", "")
        time_period = basic_info.get("时间周期", "")
        
        # 格式化当前值
        if isinstance(current_value, (int, float)) and current_value >= 1000:
            current_value_str = f"{current_value:,}"
        else:
            current_value_str = str(current_value)
        
        # 变化描述
        change_desc = ""
        short_change_desc = ""
        if "环比变化率" in change_analysis:
            change_rate = change_analysis["环比变化率"]
            direction = change_analysis["变化方向"]
            previous_value = change_analysis["前期值"]
            previous_time_period = change_analysis["前期时间周期"]
            
            # 完整描述
            change_desc = f"相比{previous_time_period}的{previous_value}{unit}，{direction}了"
            if abs(change_rate) < 0.01:
                change_desc += f"不到0.01%"
            else:
                change_desc += f"{abs(change_rate):.2f}%"
            
            # 简短描述
            if direction == "上升":
                short_change_desc = f"环比增长{abs(change_rate):.2f}%"
            elif direction == "下降":
                short_change_desc = f"环比下降{abs(change_rate):.2f}%"
            else:
                short_change_desc = "环比持平"
        
        # 趋势描述
        trend_desc = ""
        short_trend_desc = ""
        if "趋势类型" in trend_analysis:
            trend_type = trend_analysis["趋势类型"]
            
            if trend_type == "上升":
                trend_desc = "总体呈上升趋势"
                short_trend_desc = "上升趋势"
            elif trend_type == "下降":
                trend_desc = "总体呈下降趋势"
                short_trend_desc = "下降趋势"
            elif trend_type == "稳定":
                trend_desc = "总体保持稳定"
                short_trend_desc = "趋势稳定"
            else:
                trend_desc = f"趋势为{trend_type}"
                short_trend_desc = f"{trend_type}"
            
            if "最近趋势" in trend_analysis:
                recent_trend = trend_analysis["最近趋势"]
                if recent_trend == "加速":
                    trend_desc += "，且近期增速加快"
                elif recent_trend == "减速":
                    trend_desc += "，但近期增速放缓"
                elif recent_trend == "波动":
                    trend_desc += "，但近期有所波动"
        
        # 异常描述
        anomaly_desc = ""
        if "是否异常" in anomaly_detection and anomaly_detection["是否异常"] is True:
            anomaly_degree = anomaly_detection.get("异常程度", "")
            z_score = anomaly_detection.get("Z分数", 0)
            
            if anomaly_degree:
                anomaly_desc = f"当前值存在{anomaly_degree}异常"
                if abs(z_score) > 0:
                    direction = "高于" if z_score > 0 else "低于"
                    anomaly_desc += f"，{direction}历史均值{abs(z_score):.2f}个标准差"
        
        # 统计描述
        stats_desc = ""
        if stats:
            max_value = stats.get("最大值", None)
            avg_value = stats.get("平均值", None)
            
            if current_value == max_value:
                stats_desc = "，达到历史最高水平"
            elif avg_value is not None and current_value > avg_value:
                stats_desc = f"，高于历史平均值({avg_value:.2f}{unit})"
        
        # 拼接文本
        template = self.templates[template_id]["content"]
        insight = template.format(
            指标名称=metric_name,
            当前值=current_value_str,
            单位=unit,
            时间周期=f"在{time_period}" if time_period else "",
            变化描述=change_desc,
            变化描述简短=short_change_desc,
            趋势描述=f"从长期来看，{trend_desc}。" if trend_desc else "",
            趋势描述简短=short_trend_desc,
            异常描述=f"{anomaly_desc}。" if anomaly_desc else "",
            统计描述=stats_desc
        )
        
        return insight
    
    def _generate_comparison_insight(self, data: Dict[str, Any], template_id: str) -> str:
        """
        生成对比分析洞察文本
        
        参数:
            data (Dict[str, Any]): 对比分析数据
            template_id (str): 模板ID
            
        返回:
            str: 生成的文本
        """
        # 简单实现
        if "对比分析" in data:
            comparisons = data["对比分析"]
            if "趋势对比" in comparisons and comparisons["趋势对比"]:
                trend_comparison = comparisons["趋势对比"][0]
                insight = (f"{trend_comparison['图表1']['标题']}和{trend_comparison['图表2']['标题']}的趋势"
                          f"{trend_comparison['趋势一致性']}，分别是{trend_comparison['图表1']['趋势']}和"
                          f"{trend_comparison['图表2']['趋势']}。")
                return insight
        
        # 如果没有找到合适的数据，返回通用描述
        return "对比分析显示各指标存在差异，详细结果请参考分析数据。"
    
    def _generate_prediction_insight(self, data: Dict[str, Any], template_id: str) -> str:
        """
        生成预测洞察文本
        
        参数:
            data (Dict[str, Any]): 预测数据
            template_id (str): 模板ID
            
        返回:
            str: 生成的文本
        """
        # 简单实现
        metric_name = data.get("指标名称", "未知指标")
        predictions = data.get("预测值", [])
        
        if predictions:
            prediction_str = "、".join([f"{p:,}" if isinstance(p, (int, float)) and p >= 1000 else str(p) for p in predictions])
            trend_desc = "预计将上升" if predictions[-1] > predictions[0] else "预计将下降" if predictions[-1] < predictions[0] else "预计将保持稳定"
            
            return f"{metric_name}在未来{len(predictions)}期的预测值为{prediction_str}，{trend_desc}。"
        
        return f"{metric_name}的预测分析需要更多历史数据才能给出可靠结果。"
    
    def _generate_generic_insight(self, data: Dict[str, Any], template_id: str) -> str:
        """
        生成通用洞察文本
        
        参数:
            data (Dict[str, Any]): 分析数据
            template_id (str): 模板ID
            
        返回:
            str: 生成的文本
        """
        # 简单实现
        data_type = next(iter(data)) if data else "未知类型"
        return f"分析完成，数据类型为{data_type}，详细结果请参考分析数据。" 