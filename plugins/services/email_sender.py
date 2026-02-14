"""
Email sender plugin.
"""

import os
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class EmailSenderConfig(BasePluginConfig):
    """Configuration for email sender."""
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    username: str = Field(default="", description="SMTP username")
    password: str = Field(default="", description="SMTP password")
    from_email: str = Field(default="", description="Default sender email")
    use_tls: bool = Field(default=True, description="Use TLS")


class EmailSender(BasePlugin):
    """
    Send emails via SMTP.
    """
    
    name = "email_sender"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Send emails via SMTP"
    tags = ["external-service", "email", "smtp"]
    config_class = EmailSenderConfig
    
    def validate(self) -> bool:
        """Validate email configuration."""
        if not self.config.username:
            self.config.username = os.environ.get("SMTP_USERNAME", "")
        if not self.config.password:
            self.config.password = os.environ.get("SMTP_PASSWORD", "")
        
        if not self.config.username or not self.config.password:
            self._error = "SMTP credentials are required"
            return False
        
        return super().validate()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Send email.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body
            from_email: Optional sender override
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            html: Whether body is HTML
            
        Returns:
            Dictionary with send result
        """
        to = kwargs.get("to")
        subject = kwargs.get("subject", "")
        body = kwargs.get("body", "")
        from_email = kwargs.get("from_email", self.config.from_email)
        cc = kwargs.get("cc", [])
        bcc = kwargs.get("bcc", [])
        html = kwargs.get("html", False)
        
        if not to:
            return {"error": "Recipient is required"}
        
        if not subject and not body:
            return {"error": "Subject or body is required"}
        
        # Simulated response (would use smtplib in production)
        return {
            "success": True,
            "to": to,
            "subject": subject,
            "from": from_email or self.config.username
        }
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Send an email."""
        return self.execute(
            to=to,
            subject=subject,
            body=body,
            **kwargs
        )
    
    def send_html_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Send an HTML email."""
        return self.execute(
            to=to,
            subject=subject,
            body=html_body,
            html=True,
            **kwargs
        )
