"""
Slack notifier plugin.
"""

import os
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class SlackNotifierConfig(BasePluginConfig):
    """Configuration for Slack notifier."""
    webhook_url: str = Field(default="", description="Slack webhook URL")
    channel: str = Field(default="", description="Default channel")
    username: str = Field(
        default="Multi-Agent Plugin",
        description="Bot username"
    )


class SlackNotifier(BasePlugin):
    """
    Send Slack notifications via webhooks.
    """
    
    name = "slack_notifier"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Send Slack notifications"
    tags = ["external-service", "slack", "notifications"]
    config_class = SlackNotifierConfig
    
    def validate(self) -> bool:
        """Validate Slack configuration."""
        if not self.config.webhook_url:
            self.config.webhook_url = os.environ.get("SLACK_WEBHOOK", "")
        
        if not self.config.webhook_url:
            self._error = "Slack webhook URL is required"
            return False
        
        return super().validate()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Send Slack notification.
        
        Args:
            message: Message text
            channel: Optional channel override
            username: Optional username override
            attachments: Optional Slack attachments
            **kwargs: Additional message options
            
        Returns:
            Dictionary with notification result
        """
        message = kwargs.get("message", "")
        channel = kwargs.get("channel", self.config.channel)
        username = kwargs.get("username", self.config.username)
        attachments = kwargs.get("attachments", [])
        
        if not message:
            return {"error": "Message is required"}
        
        # Simulated response (would use requests library in production)
        return {
            "success": True,
            "message": message,
            "channel": channel or "default",
            "username": username
        }
    
    def send_message(
        self,
        message: str,
        channel: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send a message to Slack."""
        return self.execute(
            message=message,
            channel=channel,
            **kwargs
        )
    
    def send_alert(
        self,
        title: str,
        text: str,
        color: str = "warning",
        **kwargs
    ) -> Dict[str, Any]:
        """Send an alert with attachments."""
        attachment = {
            "title": title,
            "text": text,
            "color": color
        }
        
        return self.execute(
            message=f"*{title}*",
            attachments=[attachment],
            **kwargs
        )
