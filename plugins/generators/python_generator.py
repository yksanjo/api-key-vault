"""
Python code generator plugin.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from plugins.base import BasePlugin, BasePluginConfig


class PythonGeneratorConfig(BasePluginConfig):
    """Configuration for Python generator."""
    default_imports: List[str] = Field(
        default_factory=list,
        description="Default imports to include"
    )
    use_type_hints: bool = Field(
        default=True,
        description="Use type hints in generated code"
    )


class Endpoint(BaseModel):
    """API endpoint specification."""
    path: str
    method: str = "GET"
    handler: str = "handler"
    description: str = ""


class PythonGenerator(BasePlugin):
    """
    Generate Python code for various application types.
    
    Supports Flask APIs, Django apps, FastAPI services, CLI tools,
    and more.
    """
    
    name = "python_generator"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Generate Python code for various application types"
    tags = ["code-generation", "python", "programming"]
    config_class = PythonGeneratorConfig
    
    # Templates for different application types
    TEMPLATES = {
        "flask_api": '''"""Flask API Application"""
from flask import Flask, jsonify, request
app = Flask(__name__)


{endpoints}


if __name__ == "__main__":
    app.run(debug=True)
''',
        "fastapi": '''"""FastAPI Application"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


{endpoints}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        "cli": '''"""CLI Application"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="{description}")
    {args}
    
    args = parser.parse_args()
    {main_logic}


if __name__ == "__main__":
    main()
''',
        "class": '''"""Python Class"""
from typing import Optional, List


class {class_name}:
    """{description}"""
    
    def __init__(self{init_params}):
        {init_body}
    
    def __str__(self) -> str:
        return f"{class_name}({str_params})"
    
    def __repr__(self) -> str:
        return self.__str__()
''',
    }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate Python code.
        
        Args:
            type: Type of code to generate (flask_api, fastapi, cli, class)
            endpoints: List of endpoints for API types
            class_name: Name of class for class type
            description: Description for CLI or class
            **kwargs: Additional generation options
            
        Returns:
            Dictionary with generated code
        """
        code_type = kwargs.get("type", "flask_api")
        
        if code_type == "flask_api":
            return self._generate_flask_api(kwargs)
        elif code_type == "fastapi":
            return self._generate_fastapi(kwargs)
        elif code_type == "cli":
            return self._generate_cli(kwargs)
        elif code_type == "class":
            return self._generate_class(kwargs)
        else:
            return {"error": f"Unknown code type: {code_type}"}
    
    def _generate_flask_api(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Flask API code."""
        endpoints = kwargs.get("endpoints", [])
        
        endpoint_code = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET").lower()
            handler = ep.get("handler", "handler")
            desc = ep.get("description", "")
            
            code = f'''@app.route("{path}", methods=["{ep.get('method', 'GET')}"])
def {handler}():
    """{desc}"""
    return jsonify({{"message": "Hello, World!"}})
'''
            endpoint_code.append(code)
        
        template = self.TEMPLATES["flask_api"]
        code = template.format(endpoints="\n\n".join(endpoint_code))
        
        return {
            "code": code,
            "language": "python",
            "type": "flask_api",
            "filename": "app.py"
        }
    
    def _generate_fastapi(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate FastAPI code."""
        endpoints = kwargs.get("endpoints", [])
        
        endpoint_code = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET").lower()
            handler = ep.get("handler", "handler")
            desc = ep.get("description", "")
            
            code = f'''@app.{method}("{path}")
async def {handler}():
    """{desc}"""
    return {{"message": "Hello, World!"}}
'''
            endpoint_code.append(code)
        
        template = self.TEMPLATES["fastapi"]
        code = template.format(endpoints="\n\n".join(endpoint_code))
        
        return {
            "code": code,
            "language": "python",
            "type": "fastapi",
            "filename": "main.py"
        }
    
    def _generate_cli(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate CLI application code."""
        description = kwargs.get("description", "CLI Application")
        args = kwargs.get("args", [])
        
        args_code = []
        for arg in args:
            name = arg.get("name", "arg")
            help_text = arg.get("help", "")
            args_code.append(f'    parser.add_argument("--{name}", help="{help_text}")')
        
        main_logic = kwargs.get("main_logic", "pass")
        
        template = self.TEMPLATES["cli"]
        code = template.format(
            description=description,
            args="\n".join(args_code),
            main_logic=main_logic
        )
        
        return {
            "code": code,
            "language": "python",
            "type": "cli",
            "filename": "cli.py"
        }
    
    def _generate_class(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Python class code."""
        class_name = kwargs.get("class_name", "MyClass")
        description = kwargs.get("description", "A sample class")
        attributes = kwargs.get("attributes", [])
        
        init_params = []
        init_body = []
        str_params = []
        
        for attr in attributes:
            name = attr.get("name", "attr")
            init_params.append(f"{name}=None")
            init_body.append(f"        self.{name} = {name}")
            str_params.append(f"{name}=self.{name}")
        
        init_params_str = ", " + ", ".join(init_params) if init_params else ""
        init_body_str = "\n".join(init_body) if init_body else "        pass"
        str_params_str = ", ".join(str_params) if str_params else ""
        
        template = self.TEMPLATES["class"]
        code = template.format(
            class_name=class_name,
            description=description,
            init_params=init_params_str,
            init_body=init_body_str,
            str_params=str_params_str
        )
        
        return {
            "code": code,
            "language": "python",
            "type": "class",
            "filename": f"{class_name.lower()}.py"
        }
