"""
Code linter plugin.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class CodeLinterConfig(BasePluginConfig):
    """Configuration for code linter."""
    language: str = Field(default="python", description="Programming language")
    severity_level: str = Field(
        default="warning",
        description="Minimum severity level (error, warning, info)"
    )


class CodeLinter(BasePlugin):
    """
    Lint code for style and potential issues.
    """
    
    name = "code_linter"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Lint code for style and issues"
    tags = ["testing", "linter", "code-quality"]
    config_class = CodeLinterConfig
    
    # Linting rules for different languages
    RULES = {
        "python": [
            {
                "id": "E001",
                "message": "Line too long (>{max_len} characters)",
                "pattern": r'.{{{max_len},}}',
                "severity": "warning"
            },
            {
                "id": "E002",
                "message": "Trailing whitespace",
                "pattern": r'[\t ]+$',
                "severity": "warning"
            },
            {
                "id": "E003",
                "message": "No newline at end of file",
                "pattern": r'[^\n]$',
                "severity": "info"
            },
            {
                "id": "W001",
                "message": "Avoid using 'eval()'",
                "pattern": r'\beval\s*\(',
                "severity": "warning"
            },
            {
                "id": "W002",
                "message": "Avoid using 'exec()'",
                "pattern": r'\bexec\s*\(',
                "severity": "warning"
            },
            {
                "id": "W003",
                "message": "TODO comment found",
                "pattern": r'#\s*TODO',
                "severity": "info"
            },
        ],
        "javascript": [
            {
                "id": "JS001",
                "message": "Avoid using 'eval()'",
                "pattern": r'\beval\s*\(',
                "severity": "warning"
            },
            {
                "id": "JS002",
                "message": "Console.log found",
                "pattern": r'console\.log\s*\(',
                "severity": "info"
            },
            {
                "id": "JS003",
                "message": "Avoid using 'var', use 'let' or 'const'",
                "pattern": r'\bvar\s+\w+',
                "severity": "warning"
            },
        ],
    }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Lint code.
        
        Args:
            source_code: Code to lint
            source_file: Path to source file
            language: Programming language
            **kwargs: Additional options
            
        Returns:
            Dictionary with linting results
        """
        language = kwargs.get("language", self.config.language)
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
        
        return self._lint_code(source_code, language)
    
    def _lint_code(self, source_code: str, language: str) -> Dict[str, Any]:
        """Lint source code."""
        issues = []
        lines = source_code.split('\n')
        
        rules = self.RULES.get(language, [])
        
        for line_num, line in enumerate(lines, 1):
            for rule in rules:
                pattern = rule["pattern"]
                
                try:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Format message with match if needed
                        message = rule["message"]
                        
                        issues.append({
                            "id": rule["id"],
                            "message": message,
                            "line": line_num,
                            "column": match.start() + 1,
                            "severity": rule["severity"],
                            "code": line.strip()
                        })
                except re.error:
                    pass
        
        # Calculate summary
        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]
        infos = [i for i in issues if i["severity"] == "info"]
        
        return {
            "issues": issues,
            "summary": {
                "total": len(issues),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(infos)
            },
            "language": language,
            "passed": len(issues) == 0
        }
    
    def lint_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Lint a file."""
        return self.execute(source_file=file_path, language=language)
    
    def lint_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Lint code string."""
        return self.execute(source_code=code, language=language)
