"""
API documentation generator plugin.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class APIDocsConfig(BasePluginConfig):
    """Configuration for API docs generator."""
    format: str = Field(default="markdown", description="Output format (markdown, openapi, swagger)")


class APIDocs(BasePlugin):
    """
    Generate API documentation from code.
    """
    
    name = "api_docs"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Generate API documentation"
    tags = ["documentation", "api", "docs"]
    config_class = APIDocsConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate API documentation.
        
        Args:
            source_code: Source code to document
            source_file: Path to source file
            format: Output format (markdown, openapi)
            language: Programming language
            **kwargs: Additional options
            
        Returns:
            Dictionary with generated documentation
        """
        format_name = kwargs.get("format", self.config.format)
        source_code = kwargs.get("source_code")
        source_file = kwargs.get("source_file")
        
        if not source_code and source_file:
            try:
                with open(source_file, 'r') as f:
                    source_code = f.read()
            except FileNotFoundError:
                return {"error": f"File not found: {source_file}"}
        
        if not source_code:
            return {"error": "No source code provided"}
        
        if format_name == "markdown":
            return self._generate_markdown(source_code)
        elif format_name == "openapi":
            return self._generate_openapi(source_code)
        else:
            return {"error": f"Unknown format: {format_name}"}
    
    def _generate_markdown(self, source_code: str) -> Dict[str, Any]:
        """Generate Markdown API documentation."""
        endpoints = self._extract_endpoints(source_code)
        
        doc = "# API Documentation\n\n"
        
        for endpoint in endpoints:
            doc += f"## {endpoint['method']} {endpoint['path']}\n\n"
            doc += f"{endpoint.get('description', 'No description')}\n\n"
            
            if endpoint.get('parameters'):
                doc += "### Parameters\n\n"
                doc += "| Name | Type | Required | Description |\n"
                doc += "|------|------|----------|-------------|\n"
                for param in endpoint['parameters']:
                    required = "Yes" if param.get('required') else "No"
                    doc += f"| {param['name']} | {param.get('type', 'string')} | {required} | {param.get('description', '')} |\n"
                doc += "\n"
            
            if endpoint.get('responses'):
                doc += "### Responses\n\n"
                for status, response in endpoint['responses'].items():
                    doc += f"- **{status}**: {response}\n"
                doc += "\n"
        
        return {
            "content": doc,
            "format": "markdown",
            "endpoints": len(endpoints)
        }
    
    def _generate_openapi(self, source_code: str) -> Dict[str, Any]:
        """Generate OpenAPI documentation."""
        endpoints = self._extract_endpoints(source_code)
        
        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": "API",
                "version": "1.0.0",
                "description": "API Documentation"
            },
            "paths": {}
        }
        
        for endpoint in endpoints:
            path = endpoint['path']
            method = endpoint['method'].lower()
            
            openapi["paths"][path] = {
                method: {
                    "summary": endpoint.get('description', ''),
                    "parameters": [],
                    "responses": {
                        "200": {
                            "description": "Successful response"
                        }
                    }
                }
            }
        
        return {
            "content": openapi,
            "format": "openapi",
            "endpoints": len(endpoints)
        }
    
    def _extract_endpoints(self, source_code: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from code."""
        endpoints = []
        
        # Flask style routes
        flask_pattern = r'@(?:app|Blueprint)\.(?:route|get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(flask_pattern, source_code):
            path = match.group(1)
            method = "GET"
            
            # Check for method decorator
            method_match = re.search(r'@[^@]*\.(' + '|'.join(['get', 'post', 'put', 'delete', 'patch']) + r')\s*\(', source_code[:match.start()])
            if method_match:
                method = method_match.group(1).upper()
            
            endpoints.append({
                "path": path,
                "method": method,
                "description": "",
                "parameters": [],
                "responses": {}
            })
        
        # FastAPI style routes
        fastapi_pattern = r'@(?:app|APIRouter)\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(fastapi_pattern, source_code):
            path = match.group(1)
            method = "GET"
            
            # Find the actual decorator
            decorator_start = source_code.rfind('@', 0, match.start())
            decorator = source_code[decorator_start:match.start()]
            for m in ['get', 'post', 'put', 'delete', 'patch']:
                if m in decorator.lower():
                    method = m.upper()
                    break
            
            endpoints.append({
                "path": path,
                "method": method,
                "description": "",
                "parameters": [],
                "responses": {}
            })
        
        return endpoints
