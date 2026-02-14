"""
JSON transformer plugin.
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class JSONTransformerConfig(BasePluginConfig):
    """Configuration for JSON transformer."""
    indent: int = Field(default=2, description="JSON indentation")


class JSONTransformer(BasePlugin):
    """
    Transform, filter, and manipulate JSON data.
    """
    
    name = "json_transformer"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Transform and manipulate JSON data"
    tags = ["data-processing", "json", "data"]
    config_class = JSONTransformerConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Transform JSON data.
        
        Args:
            operation: Operation to perform (parse, stringify, filter, map, flatten, unflatten)
            data: JSON data (string or dict/list)
            file_path: Path to JSON file
            **kwargs: Additional operation-specific arguments
            
        Returns:
            Dictionary with transformation result
        """
        operation = kwargs.get("operation", "parse")
        
        if operation == "parse":
            return self._parse_json(kwargs)
        elif operation == "stringify":
            return self._stringify_json(kwargs)
        elif operation == "filter":
            return self._filter_json(kwargs)
        elif operation == "map":
            return self._map_json(kwargs)
        elif operation == "flatten":
            return self._flatten_json(kwargs)
        elif operation == "unflatten":
            return self._unflatten_json(kwargs)
        elif operation == "extract":
            return self._extract_json(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _parse_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Parse JSON string."""
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        
        if file_path:
            with open(file_path, 'r') as f:
                parsed = json.load(f)
        elif data:
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data
        else:
            return {"error": "No data or file_path provided"}
        
        return {"data": parsed, "success": True}
    
    def _stringify_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Convert JSON to string."""
        data = kwargs.get("data")
        indent = kwargs.get("indent", self.config.indent)
        
        if data is None:
            return {"error": "No data provided"}
        
        try:
            if isinstance(data, str):
                # Already a string, parse first then stringify
                data = json.loads(data)
            
            stringified = json.dumps(data, indent=indent)
            return {"data": stringified, "success": True}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}"}
    
    def _filter_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Filter JSON data based on conditions."""
        data = kwargs.get("data")
        path = kwargs.get("path", "")
        condition = kwargs.get("condition", {})
        
        if data is None:
            return {"error": "No data provided"}
        
        # Navigate to the path
        if path:
            try:
                data = self._get_nested(data, path)
            except KeyError:
                return {"error": f"Path not found: {path}"}
        
        # Apply filter
        key = condition.get("key")
        operator = condition.get("operator", "equals")
        value = condition.get("value")
        
        if isinstance(data, list):
            filtered = [
                item for item in data
                if self._evaluate_condition(item.get(key), operator, value)
            ]
            return {"data": filtered, "count": len(filtered)}
        elif isinstance(data, dict):
            filtered = {}
            for k, v in data.items():
                if k == key:
                    if self._evaluate_condition(v, operator, value):
                        filtered[k] = v
                else:
                    filtered[k] = v
            return {"data": filtered}
        
        return {"error": "Data must be list or dict"}
    
    def _map_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Map/transform JSON data."""
        data = kwargs.get("data")
        path = kwargs.get("path", "")
        transform = kwargs.get("transform", {})
        
        if data is None:
            return {"error": "No data provided"}
        
        # Navigate to the path
        if path:
            try:
                data = self._get_nested(data, path)
            except KeyError:
                return {"error": f"Path not found: {path}"}
        
        # Apply transformation
        if isinstance(data, list):
            transformed = []
            for item in data:
                new_item = item.copy()
                for key, transformation in transform.items():
                    if key in new_item:
                        new_item[key] = self._apply_transform(
                            new_item[key], 
                            transformation
                        )
                transformed.append(new_item)
            return {"data": transformed, "count": len(transformed)}
        
        return {"error": "Data must be a list for mapping"}
    
    def _flatten_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Flatten nested JSON."""
        data = kwargs.get("data")
        separator = kwargs.get("separator", ".")
        
        if data is None:
            return {"error": "No data provided"}
        
        flattened = self._flatten(data, separator)
        return {"data": flattened}
    
    def _unflatten_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Unflatten JSON to nested structure."""
        data = kwargs.get("data")
        separator = kwargs.get("separator", ".")
        
        if data is None:
            return {"error": "No data provided"}
        
        unflattened = self._unflatten(data, separator)
        return {"data": unflattened}
    
    def _extract_json(self, kwargs: Dict) -> Dict[str, Any]:
        """Extract values from JSON using paths."""
        data = kwargs.get("data")
        paths = kwargs.get("paths", [])
        
        if data is None:
            return {"error": "No data provided"}
        
        result = {}
        for path in paths:
            try:
                result[path] = self._get_nested(data, path)
            except KeyError:
                result[path] = None
        
        return {"data": result}
    
    def _get_nested(self, data: Any, path: str) -> Any:
        """Get nested value from data using dot notation."""
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                raise KeyError(f"Cannot navigate through {type(current)}")
        
        return current
    
    def _evaluate_condition(self, value: Any, operator: str, target: Any) -> bool:
        """Evaluate a condition against a value."""
        if operator == "equals":
            return value == target
        elif operator == "not_equals":
            return value != target
        elif operator == "contains":
            return target in str(value)
        elif operator == "greater":
            return float(value) > float(target) if value else False
        elif operator == "less":
            return float(value) < float(target) if value else False
        elif operator == "exists":
            return value is not None
        elif operator == "truthy":
            return bool(value)
        return False
    
    def _apply_transform(self, value: Any, transformation: str) -> Any:
        """Apply a transformation to a value."""
        if transformation == "upper":
            return str(value).upper()
        elif transformation == "lower":
            return str(value).lower()
        elif transformation == "title":
            return str(value).title()
        elif transformation == "abs":
            return abs(float(value))
        elif transformation == "str":
            return str(value)
        elif transformation == "int":
            return int(value)
        elif transformation == "float":
            return float(value)
        return value
    
    def _flatten(self, data: Any, separator: str = ".") -> Dict[str, Any]:
        """Flatten nested dictionary."""
        result = {}
        
        def _flatten_recursive(obj: Any, prefix: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    _flatten_recursive(value, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}[{i}]"
                    _flatten_recursive(item, new_key)
            else:
                result[prefix] = obj
        
        _flatten_recursive(data)
        return result
    
    def _unflatten(self, data: Dict[str, Any], separator: str = ".") -> Any:
        """Unflatten dictionary to nested structure."""
        result = {}
        
        for key, value in data.items():
            parts = key.replace("[", ".").replace("]", "").split(".")
            current = result
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        
        return result
