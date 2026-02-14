"""
Docstring writer plugin.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class DocstringWriterConfig(BasePluginConfig):
    """Configuration for docstring writer."""
    style: str = Field(
        default="google",
        description="Docstring style (google, numpy, sphinx)"
    )


class DocstringWriter(BasePlugin):
    """
    Add docstrings to code.
    """
    
    name = "docstring_writer"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Add docstrings to code"
    tags = ["documentation", "docstring", "docs"]
    config_class = DocstringWriterConfig
    
    DOCSTRING_TEMPLATES = {
        "google": '''"""{description}

Args:
{args}

Returns:
{returns}

Raises:
{raises}
''',
        "numpy": '''"""
{description}

Parameters
----------
{args}

Returns
-------
{returns}

Raises
------
{raises}
''',
        "sphinx": '''"""
{description}

:param arg1: Description of arg1
:type arg1: type
:returns: Description of return value
:rtype: return type
:raises Exception: Description of exception
'''
    }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Add docstrings to code.
        
        Args:
            source_code: Source code
            source_file: Path to source file
            style: Docstring style (google, numpy, sphinx)
            **kwargs: Additional options
            
        Returns:
            Dictionary with annotated code
        """
        style = kwargs.get("style", self.config.style)
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
        
        return self._add_docstrings(source_code, style)
    
    def _add_docstrings(self, source_code: str, style: str) -> Dict[str, Any]:
        """Add docstrings to code."""
        lines = source_code.split('\n')
        result = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            result.append(line)
            
            # Check for function definition
            func_match = re.match(r'(def\s+(\w+)\s*\(([^)]*)\):)', line)
            if func_match:
                func_name = func_match.group(2)
                params = func_match.group(3)
                
                # Parse parameters
                param_list = []
                if params.strip():
                    for p in params.split(','):
                        p = p.strip()
                        if '=' in p:
                            param_list.append(p.split('=')[0].strip())
                        elif p:
                            param_list.append(p)
                
                # Generate docstring
                docstring = self._generate_docstring(
                    func_name,
                    param_list,
                    style
                )
                result.append(docstring)
            
            i += 1
        
        return {
            "code": '\n'.join(result),
            "style": style,
            "functions_annotated": len(re.findall(r'def\s+\w+', source_code))
        }
    
    def _generate_docstring(
        self,
        func_name: str,
        params: List[str],
        style: str
    ) -> str:
        """Generate docstring for a function."""
        template = self.DOCSTRING_TEMPLATES.get(style, self.DOCSTRING_TEMPLATES["google"])
        
        description = f"{func_name} function."
        
        # Format args
        args_str = ""
        for param in params:
            args_str += f"    {param}: Description of {param}.\n"
        
        if not args_str:
            args_str = "    args: Function arguments.\n"
        
        returns_str = "    Description of return value."
        raises_str = "    Description of raised exceptions."
        
        docstring = template.format(
            description=description,
            args=args_str,
            returns=returns_str,
            raises=raises_str
        )
        
        # Indent the docstring to match function level
        return '    ' + docstring.replace('\n', '\n    ')
    
    def add_docstrings(self, code: str, style: str = "google") -> Dict[str, Any]:
        """Add docstrings to code."""
        return self._add_docstrings(code, style)
