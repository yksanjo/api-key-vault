"""
JavaScript/TypeScript code generator plugin.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field

from plugins.base import BasePlugin, BasePluginConfig


class JavaScriptGeneratorConfig(BasePluginConfig):
    """Configuration for JavaScript generator."""
    use_typescript: bool = Field(
        default=False,
        description="Generate TypeScript instead of JavaScript"
    )
    use_esm: bool = Field(
        default=True,
        description="Use ES modules"
    )


class JavaScriptGenerator(BasePlugin):
    """
    Generate JavaScript/TypeScript code for various application types.
    
    Supports Express APIs, React components, Node.js CLI tools,
    and more.
    """
    
    name = "javascript_generator"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Generate JavaScript/TypeScript code for various application types"
    tags = ["code-generation", "javascript", "typescript", "programming"]
    config_class = JavaScriptGeneratorConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate JavaScript/TypeScript code.
        
        Args:
            type: Type of code to generate (express, react, node_cli, module)
            endpoints: List of endpoints for Express API
            component_name: Name of component for React
            **kwargs: Additional generation options
            
        Returns:
            Dictionary with generated code
        """
        code_type = kwargs.get("type", "express")
        use_typescript = kwargs.get("typescript", self.config.use_typescript)
        
        if code_type == "express":
            return self._generate_express(kwargs, use_typescript)
        elif code_type == "react":
            return self._generate_react(kwargs, use_typescript)
        elif code_type == "node_cli":
            return self._generate_node_cli(kwargs, use_typescript)
        elif code_type == "module":
            return self._generate_module(kwargs, use_typescript)
        else:
            return {"error": f"Unknown code type: {code_type}"}
    
    def _generate_express(self, kwargs: Dict, typescript: bool) -> Dict[str, Any]:
        """Generate Express.js API code."""
        ext = "ts" if typescript else "js"
        
        endpoints = kwargs.get("endpoints", [])
        
        endpoint_code = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET").lower()
            handler = ep.get("handler", "handler")
            
            code = f'''app.{method}("{path}", (req, res) => {{
  res.json({{ message: "Hello, World!" }});
}});'''
            endpoint_code.append(code)
        
        if typescript:
            code = f'''import express, {{ Request, Response }} from "express";
const app = express();
app.use(express.json());

{chr(10).join(endpoint_code)}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});
'''
        else:
            code = f'''const express = require("express");
const app = express();
app.use(express.json());

{chr(10).join(endpoint_code)}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});
'''
        
        return {
            "code": code,
            "language": "typescript" if typescript else "javascript",
            "type": "express",
            "filename": f"server.{ext}"
        }
    
    def _generate_react(self, kwargs: Dict, typescript: bool) -> Dict[str, Any]:
        """Generate React component code."""
        ext = "tsx" if typescript else "jsx"
        component_name = kwargs.get("component_name", "MyComponent")
        
        if typescript:
            code = f'''import React from "react";

interface {component_name}Props {{
  // Add props here
}}

const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component_name.lower()}">
      <h1>{component_name}</h1>
    </div>
  );
}};

export default {component_name};
'''
        else:
            code = f'''import React from "react";

const {component_name} = (props) => {{
  return (
    <div className="{component_name.lower()}">
      <h1>{component_name}</h1>
    </div>
  );
}};

export default {component_name};
'''
        
        return {
            "code": code,
            "language": "typescript" if typescript else "javascript",
            "type": "react",
            "filename": f"{component_name}.{ext}"
        }
    
    def _generate_node_cli(self, kwargs: Dict, typescript: bool) -> Dict[str, Any]:
        """Generate Node.js CLI code."""
        ext = "ts" if typescript else "js"
        
        if typescript:
            code = '''#!/usr/bin/env ts-node
import * as readline from "readline";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function main(): void {
  console.log("CLI Application");
  // Add your CLI logic here
}

main();
'''
        else:
            code = '''#!/usr/bin/env node
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function main() {
  console.log("CLI Application");
  // Add your CLI logic here
}

main();
'''
        
        return {
            "code": code,
            "language": "typescript" if typescript else "javascript",
            "type": "node_cli",
            "filename": f"cli.{ext}"
        }
    
    def _generate_module(self, kwargs: Dict, typescript: bool) -> Dict[str, Any]:
        """Generate JavaScript/TypeScript module code."""
        ext = "ts" if typescript else "js"
        exports = kwargs.get("exports", ["func1", "func2"])
        
        if typescript:
            code = f'''// {kwargs.get("description", "Module")}

export function {exports[0]}(): void {{
  // Implementation
}}

export function {exports[1]}(): void {{
  // Implementation
}}
'''
        else:
            code = f'''// {kwargs.get("description", "Module")}

exports.{exports[0]} = function() {{
  // Implementation
}};

exports.{exports[1]} = function() {{
  // Implementation
}};
'''
        
        return {
            "code": code,
            "language": "typescript" if typescript else "javascript",
            "type": "module",
            "filename": f"index.{ext}"
        }
