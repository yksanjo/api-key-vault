"""
XML parser plugin.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class XMLParserConfig(BasePluginConfig):
    """Configuration for XML parser."""
    encoding: str = Field(default="utf-8", description="XML encoding")


class XMLParser(BasePlugin):
    """
    Parse, manipulate, and transform XML data.
    """
    
    name = "xml_parser"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Parse and manipulate XML data"
    tags = ["data-processing", "xml", "data"]
    config_class = XMLParserConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Process XML data.
        
        Args:
            operation: Operation to perform (parse, to_string, find, add, remove, transform)
            data: XML data (string or file_path)
            **kwargs: Additional operation-specific arguments
            
        Returns:
            Dictionary with processing result
        """
        operation = kwargs.get("operation", "parse")
        
        if operation == "parse":
            return self._parse_xml(kwargs)
        elif operation == "to_string":
            return self._to_string(kwargs)
        elif operation == "find":
            return self._find(kwargs)
        elif operation == "add":
            return self._add_element(kwargs)
        elif operation == "remove":
            return self._remove_element(kwargs)
        elif operation == "transform":
            return self._transform_xml(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _parse_xml(self, kwargs: Dict) -> Dict[str, Any]:
        """Parse XML string or file."""
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        
        try:
            if file_path:
                tree = ET.parse(file_path)
                root = tree.getroot()
            elif data:
                if isinstance(data, str):
                    root = ET.fromstring(data)
                else:
                    return {"error": "Data must be a string"}
            else:
                return {"error": "No data or file_path provided"}
            
            return {
                "data": self._element_to_dict(root),
                "tag": root.tag,
                "success": True
            }
        except ET.ParseError as e:
            return {"error": f"XML parse error: {str(e)}"}
    
    def _to_string(self, kwargs: Dict) -> Dict[str, Any]:
        """Convert XML element to string."""
        data = kwargs.get("data")
        
        if data is None:
            return {"error": "No data provided"}
        
        try:
            if isinstance(data, str):
                root = ET.fromstring(data)
            else:
                root = data
            
            xml_string = ET.tostring(root, encoding=self.config.encoding)
            return {"data": xml_string.decode() if isinstance(xml_string, bytes) else xml_string, "success": True}
        except ET.ParseError as e:
            return {"error": f"XML parse error: {str(e)}"}
    
    def _find(self, kwargs: Dict) -> Dict[str, Any]:
        """Find elements in XML."""
        data = kwargs.get("data")
        xpath = kwargs.get("xpath", ".")
        
        if data is None:
            return {"error": "No data provided"}
        
        try:
            if isinstance(data, str):
                root = ET.fromstring(data)
            else:
                root = data
            
            elements = root.findall(xpath)
            
            if len(elements) == 0:
                return {"data": None, "count": 0}
            elif len(elements) == 1:
                return {"data": self._element_to_dict(elements[0]), "count": 1}
            else:
                return {"data": [self._element_to_dict(el) for el in elements], "count": len(elements)}
        except ET.ParseError as e:
            return {"error": f"XML parse error: {str(e)}"}
    
    def _add_element(self, kwargs: Dict) -> Dict[str, Any]:
        """Add element to XML."""
        data = kwargs.get("data")
        parent_xpath = kwargs.get("parent_xpath", ".")
        tag = kwargs.get("tag")
        text = kwargs.get("text", "")
        attributes = kwargs.get("attributes", {})
        
        if data is None or tag is None:
            return {"error": "No data or tag provided"}
        
        try:
            if isinstance(data, str):
                root = ET.fromstring(data)
            else:
                root = data
            
            parent = root.find(parent_xpath)
            if parent is None:
                parent = root
            
            new_element = ET.SubElement(parent, tag, attributes)
            new_element.text = text
            
            xml_string = ET.tostring(root, encoding=self.config.encoding)
            return {"data": xml_string.decode() if isinstance(xml_string, bytes) else xml_string, "success": True}
        except ET.ParseError as e:
            return {"error": f"XML parse error: {str(e)}"}
    
    def _remove_element(self, kwargs: Dict) -> Dict[str, Any]:
        """Remove element from XML."""
        data = kwargs.get("data")
        xpath = kwargs.get("xpath")
        
        if data is None or xpath is None:
            return {"error": "No data or xpath provided"}
        
        try:
            if isinstance(data, str):
                root = ET.fromstring(data)
            else:
                root = data
            
            element = root.find(xpath)
            if element is not None:
                parent = root.find(f".//{element.tag}/..")
                if parent is not None:
                    parent.remove(element)
                else:
                    return {"error": "Cannot remove root element"}
            
            xml_string = ET.tostring(root, encoding=self.config.encoding)
            return {"data": xml_string.decode() if isinstance(xml_string, bytes) else xml_string, "success": True}
        except ET.ParseError as e:
            return {"error": f"XML parse error: {str(e)}"}
    
    def _transform_xml(self, kwargs: Dict) -> Dict[str, Any]:
        """Transform XML using XSLT-like operations."""
        data = kwargs.get("data")
        operations = kwargs.get("operations", [])
        
        if data is None:
            return {"error": "No data provided"}
        
        try:
            if isinstance(data, str):
                root = ET.fromstring(data)
            else:
                root = data
            
            for op in operations:
                op_type = op.get("type")
                
                if op_type == "rename":
                    old_tag = op.get("old_tag")
                    new_tag = op.get("new_tag")
                    for element in root.findall(f".//{old_tag}"):
                        element.tag = new_tag
                
                elif op_type == "set_attribute":
                    xpath = op.get("xpath", ".")
                    attr_name = op.get("attribute")
                    attr_value = op.get("value")
                    for element in root.findall(xpath):
                        element.set(attr_name, attr_value)
                
                elif op_type == "set_text":
                    xpath = op.get("xpath", ".")
                    text = op.get("text")
                    for element in root.findall(xpath):
                        element.text = text
            
            xml_string = ET.tostring(root, encoding=self.config.encoding)
            return {"data": xml_string.decode() if isinstance(xml_string, bytes) else xml_string, "success": True}
        except ET.ParseError as e:
            return {"error": f"XML parse error: {str(e)}"}
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {
            "tag": element.tag,
            "attributes": element.attrib,
            "text": element.text.strip() if element.text else ""
        }
        
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._element_to_dict(child)
                child_tag = child_data["tag"]
                
                if child_tag in child_dict:
                    if not isinstance(child_dict[child_tag], list):
                        child_dict[child_tag] = [child_dict[child_tag]]
                    child_dict[child_tag].append(child_data)
                else:
                    child_dict[child_tag] = child_data
            
            result["children"] = child_dict
        
        return result
