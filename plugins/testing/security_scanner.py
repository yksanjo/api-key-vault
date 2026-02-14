"""
Security scanner plugin.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class SecurityScannerConfig(BasePluginConfig):
    """Configuration for security scanner."""
    language: str = Field(default="python", description="Programming language")
    scan_dependencies: bool = Field(
        default=True,
        description="Scan dependencies for vulnerabilities"
    )


class SecurityScanner(BasePlugin):
    """
    Scan code for security vulnerabilities.
    """
    
    name = "security_scanner"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Scan code for security vulnerabilities"
    tags = ["testing", "security", "vulnerability"]
    config_class = SecurityScannerConfig
    
    # Security patterns for different languages
    VULNERABILITIES = {
        "python": [
            {
                "id": "SEC001",
                "message": "Use of 'eval()' - code injection risk",
                "pattern": r'\beval\s*\(',
                "severity": "high",
                "cwe": "CWE-95"
            },
            {
                "id": "SEC002",
                "message": "Use of 'exec()' - code injection risk",
                "pattern": r'\bexec\s*\(',
                "severity": "high",
                "cwe": "CWE-95"
            },
            {
                "id": "SEC003",
                "message": "Hardcoded password detected",
                "pattern": r'password\s*=\s*["\'][^"\']+["\']',
                "severity": "high",
                "cwe": "CWE-259"
            },
            {
                "id": "SEC004",
                "message": "Hardcoded API key detected",
                "pattern": r'(api[_-]?key|apikey)\s*=\s*["\'][^"\']+["\']',
                "severity": "high",
                "cwe": "CWE-798"
            },
            {
                "id": "SEC005",
                "message": "SQL query built from user input - use parameterized queries",
                "pattern": r'(execute|cursor\.execute)\s*\(\s*["\'].*%.*["\']',
                "severity": "high",
                "cwe": "CWE-89"
            },
            {
                "id": "SEC006",
                "message": "Use of 'pickle.loads()' - deserialization vulnerability",
                "pattern": r'pickle\.loads\s*\(',
                "severity": "medium",
                "cwe": "CWE-502"
            },
            {
                "id": "SEC007",
                "message": "Use of 'subprocess' with shell=True",
                "pattern": r'subprocess\.\w+\s*\([^)]*shell\s*=\s*True',
                "severity": "medium",
                "cwe": "CWE-78"
            },
            {
                "id": "SEC008",
                "message": "Weak cryptographic algorithm detected",
                "pattern": r'(md5|sha1)\s*\(',
                "severity": "medium",
                "cwe": "CWE-327"
            },
        ],
        "javascript": [
            {
                "id": "JSEC001",
                "message": "Use of 'eval()' - code injection risk",
                "pattern": r'\beval\s*\(',
                "severity": "high",
                "cwe": "CWE-95"
            },
            {
                "id": "JSEC002",
                "message": "innerHTML used - potential XSS",
                "pattern": r'innerHTML\s*=',
                "severity": "high",
                "cwe": "CWE-79"
            },
            {
                "id": "JSEC003",
                "message": "Hardcoded secret detected",
                "pattern": r'(secret|token|api[_-]?key)\s*=\s*["\'][^"\']+["\']',
                "severity": "high",
                "cwe": "CWE-798"
            },
            {
                "id": "JSEC004",
                "message": "Use of 'document.write()' - potential XSS",
                "pattern": r'document\.write\s*\(',
                "severity": "medium",
                "cwe": "CWE-79"
            },
        ],
    }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Scan code for security issues.
        
        Args:
            source_code: Code to scan
            source_file: Path to source file
            language: Programming language
            **kwargs: Additional options
            
        Returns:
            Dictionary with scan results
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
        
        return self._scan_code(source_code, language)
    
    def _scan_code(self, source_code: str, language: str) -> Dict[str, Any]:
        """Scan source code for vulnerabilities."""
        vulnerabilities = []
        lines = source_code.split('\n')
        
        patterns = self.VULNERABILITIES.get(language, [])
        
        for line_num, line in enumerate(lines, 1):
            for vuln in patterns:
                pattern = vuln["pattern"]
                
                try:
                    if re.search(pattern, line):
                        vulnerabilities.append({
                            "id": vuln["id"],
                            "message": vuln["message"],
                            "line": line_num,
                            "severity": vuln["severity"],
                            "cwe": vuln.get("cwe", ""),
                            "code": line.strip()
                        })
                except re.error:
                    pass
        
        # Calculate summary
        high = [v for v in vulnerabilities if v["severity"] == "high"]
        medium = [v for v in vulnerabilities if v["severity"] == "medium"]
        low = [v for v in vulnerabilities if v["severity"] == "low"]
        
        return {
            "vulnerabilities": vulnerabilities,
            "summary": {
                "total": len(vulnerabilities),
                "high": len(high),
                "medium": len(medium),
                "low": len(low)
            },
            "language": language,
            "safe": len(vulnerabilities) == 0
        }
    
    def scan_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Scan a file."""
        return self.execute(source_file=file_path, language=language)
    
    def scan_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Scan code string."""
        return self.execute(source_code=code, language=language)
