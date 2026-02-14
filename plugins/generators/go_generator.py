"""
Go code generator plugin.
"""

from typing import Any, Dict, List
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class GoGeneratorConfig(BasePluginConfig):
    """Configuration for Go generator."""
    go_version: str = Field(
        default="1.21",
        description="Go version to use"
    )


class GoGenerator(BasePlugin):
    """
    Generate Go code for various application types.
    
    Supports HTTP servers, CLI tools, libraries, and more.
    """
    
    name = "go_generator"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Generate Go code for various application types"
    tags = ["code-generation", "go", "golang", "programming"]
    config_class = GoGeneratorConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate Go code.
        
        Args:
            type: Type of code to generate (http, cli, lib, struct)
            name: Name for the application/library
            **kwargs: Additional generation options
            
        Returns:
            Dictionary with generated code
        """
        code_type = kwargs.get("type", "http")
        
        if code_type == "http":
            return self._generate_http(kwargs)
        elif code_type == "cli":
            return self._generate_cli(kwargs)
        elif code_type == "lib":
            return self._generate_lib(kwargs)
        elif code_type == "struct":
            return self._generate_struct(kwargs)
        else:
            return {"error": f"Unknown code type: {code_type}"}
    
    def _generate_http(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Go HTTP server code."""
        name = kwargs.get("name", "my_server")
        endpoints = kwargs.get("endpoints", [])
        
        handler_code = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET")
            handler = ep.get("handler", "handler")
            
            handler_code.append(f'''func {handler}(w http.ResponseWriter, r *http.Request) {{
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{{"message": "Hello, World!"}}`))
}}
''')
        
        route_code = []
        for ep in endpoints:
            route_code.append(f'    http.HandleFunc("{ep.get("path", "/")}", {ep.get("handler", "handler")})')
        
        code = f'''package main

import (
    "encoding/json"
    "log"
    "net/http"
)

{chr(10).join(handler_code)}

func main() {{
    {chr(10).join(route_code)}
    
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}}
'''
        
        return {
            "code": code,
            "language": "go",
            "type": "http",
            "filename": "main.go"
        }
    
    def _generate_cli(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Go CLI code."""
        name = kwargs.get("name", "my_cli")
        
        code = f'''package main

import (
    "flag"
    "fmt"
    "os"
)

func main() {{
    version := flag.Bool("version", false, "Show version")
    verbose := flag.Bool("v", false, "Verbose output")
    name := flag.String("name", "", "Name to greet")
    flag.Parse()
    
    if *version {{
        fmt.Println("{name} v1.0.0")
        os.Exit(0)
    }}
    
    if *verbose {{
        fmt.Println("Running in verbose mode")
    }}
    
    if *name == "" {{
        fmt.Println("Please provide a name using -name flag")
        os.Exit(1)
    }}
    
    fmt.Printf("Hello, %s!\\n", *name)
}}
'''
        
        return {
            "code": code,
            "language": "go",
            "type": "cli",
            "filename": "main.go"
        }
    
    def _generate_lib(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Go library code."""
        name = kwargs.get("name", "mylib")
        
        code = f'''package {name}

// Add your library code here

func Init() error {{
    return nil
}}
'''
        
        return {
            "code": code,
            "language": "go",
            "type": "lib",
            "filename": f"{name}.go"
        }
    
    def _generate_struct(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Go struct code."""
        name = kwargs.get("name", "MyStruct")
        fields = kwargs.get("fields", [])
        
        field_code = []
        for field in fields:
            field_name = field.get("name", "Field")
            field_type = field.get("type", "string")
            json_tag = field.get("name", "field").lower()
            field_code.append(f"    {field_name} {field_type} `json:\"{json_tag}\"`")
        
        code = f'''package main

import "encoding/json"

type {name} struct {{
{chr(10).join(field_code)}
}}

func New{name}() *{name} {{
    return &{name}{{}}
}}

func (s *{name}) ToJSON() ([]byte, error) {{
    return json.Marshal(s)
}}

func (s *{name}) FromJSON(data []byte) error {{
    return json.Unmarshal(data, s)
}}
'''
        
        return {
            "code": code,
            "language": "go",
            "type": "struct",
            "filename": f"{name.lower()}.go"
        }
