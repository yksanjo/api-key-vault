"""
YAML handler plugin.
"""

import yaml
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class YAMLHandlerConfig(BasePluginConfig):
    """Configuration for YAML handler."""
    default_flow_style: bool = Field(
        default=False, 
        description="Use flow style for YAML"
    )


class YAMLHandler(BasePlugin):
    """
    Parse, read, write, and manipulate YAML files.
    """
    
    name = "yaml_handler"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Work with YAML files"
    tags = ["data-processing", "yaml", "data"]
    config_class = YAMLHandlerConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Process YAML data.
        
        Args:
            operation: Operation to perform (parse, dump, load, validate, merge)
            data: YAML data (string or dict)
            file_path: Path to YAML file
            **kwargs: Additional operation-specific arguments
            
        Returns:
            Dictionary with processing result
        """
        operation = kwargs.get("operation", "parse")
        
        if operation == "parse":
            return self._parse_yaml(kwargs)
        elif operation == "dump":
            return self._dump_yaml(kwargs)
        elif operation == "load":
            return self._load_yaml(kwargs)
        elif operation == "validate":
            return self._validate_yaml(kwargs)
        elif operation == "merge":
            return self._merge_yaml(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _parse_yaml(self, kwargs: Dict) -> Dict[str, Any]:
        """Parse YAML string."""
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        
        try:
            if file_path:
                with open(file_path, 'r') as f:
                    parsed = yaml.safe_load(f)
            elif data:
                if isinstance(data, str):
                    parsed = yaml.safe_load(data)
                else:
                    parsed = data
            else:
                return {"error": "No data or file_path provided"}
            
            return {"data": parsed, "success": True}
        except yaml.YAMLError as e:
            return {"error": f"YAML parse error: {str(e)}"}
    
    def _dump_yaml(self, kwargs: Dict) -> Dict[str, Any]:
        """Convert data to YAML string."""
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        flow_style = kwargs.get("flow_style", self.config.default_flow_style)
        
        if data is None:
            return {"error": "No data provided"}
        
        try:
            yaml_string = yaml.dump(
                data, 
                default_flow_style=flow_style,
                sort_keys=False
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(yaml_string)
                return {"success": True, "file": file_path}
            
            return {"data": yaml_string, "success": True}
        except yaml.YAMLError as e:
            return {"error": f"YAML dump error: {str(e)}"}
    
    def _load_yaml(self, kwargs: Dict) -> Dict[str, Any]:
        """Load YAML from file."""
        file_path = kwargs.get("file_path")
        
        if not file_path:
            return {"error": "No file_path provided"}
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            return {"data": data, "success": True}
        except yaml.YAMLError as e:
            return {"error": f"YAML load error: {str(e)}"}
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
    
    def _validate_yaml(self, kwargs: Dict) -> Dict[str, Any]:
        """Validate YAML syntax."""
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        
        yaml_content = None
        source = None
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    yaml_content = f.read()
                source = file_path
            except FileNotFoundError:
                return {"error": f"File not found: {file_path}"}
        elif data:
            if isinstance(data, str):
                yaml_content = data
            else:
                return {"valid": True, "message": "Dict is valid YAML-compatible data"}
            source = "string"
        else:
            return {"error": "No data or file_path provided"}
        
        try:
            yaml.safe_load(yaml_content)
            return {"valid": True, "source": source, "message": "Valid YAML"}
        except yaml.YAMLError as e:
            return {"valid": False, "source": source, "error": str(e)}
    
    def _merge_yaml(self, kwargs: Dict) -> Dict[str, Any]:
        """Merge multiple YAML files or data."""
        files = kwargs.get("files", [])
        data_list = kwargs.get("data", [])
        
        merged = {}
        
        # Merge from files
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        merged.update(content)
            except FileNotFoundError:
                return {"error": f"File not found: {file_path}"}
            except yaml.YAMLError as e:
                return {"error": f"YAML error in {file_path}: {str(e)}"}
        
        # Merge from data
        for data in data_list:
            if isinstance(data, dict):
                merged.update(data)
        
        return {"data": merged, "success": True}


# Add YAML SafeLoader customization for advanced types
def represent_dict(dumper, data):
    """Custom representer for dict."""
    return dumper.represent_mapping('tag:yaml.org,2002:map', data)


yaml.add_representer(dict, represent_dict)
