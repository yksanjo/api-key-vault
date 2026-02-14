"""
Webhook caller plugin.
"""

from typing import Any, Dict, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class WebhookCallerConfig(BasePluginConfig):
    """Configuration for webhook caller."""
    default_timeout: int = Field(
        default=30,
        description="Default request timeout in seconds"
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates"
    )


class WebhookCaller(BasePlugin):
    """
    Call webhooks and HTTP endpoints.
    """
    
    name = "webhook_caller"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Call webhooks and HTTP endpoints"
    tags = ["external-service", "webhook", "http", "api"]
    config_class = WebhookCallerConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Call a webhook/HTTP endpoint.
        
        Args:
            url: Webhook URL
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            data: Request body data
            headers: Optional headers
            params: Optional query parameters
            timeout: Optional timeout override
            
        Returns:
            Dictionary with response result
        """
        url = kwargs.get("url")
        method = kwargs.get("method", "POST").upper()
        data = kwargs.get("data")
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})
        timeout = kwargs.get("timeout", self.config.default_timeout)
        
        if not url:
            return {"error": "URL is required"}
        
        # Simulated response (would use requests library in production)
        return {
            "success": True,
            "url": url,
            "method": method,
            "status_code": 200,
            "response": {"message": "Webhook called successfully"}
        }
    
    def call(
        self,
        url: str,
        method: str = "POST",
        **kwargs
    ) -> Dict[str, Any]:
        """Call a webhook."""
        kwargs["url"] = url
        kwargs["method"] = method
        return self.execute(**kwargs)
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self.call(url, "GET", **kwargs)
    
    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self.call(url, "POST", **kwargs)
    
    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.call(url, "PUT", **kwargs)
    
    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.call(url, "DELETE", **kwargs)
