"""
生成器接口定义
===========

定义所有生成器组件必须实现的接口，确保组件之间的一致性和可替换性。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class GeneratorInterface(ABC):
    """
    生成器接口
    
    所有文本生成器必须实现的基础接口，定义生成器的基本行为。
    """
    
    @abstractmethod
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
            
        异常:
            ValueError: 如果输入数据格式不正确
            TypeError: 如果输入数据类型不支持
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        获取可用的模板列表
        
        返回:
            List[Dict[str, Any]]: 模板列表，每个模板包含ID、名称、描述等信息
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取生成器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、支持的语言和风格等
        """
        pass 