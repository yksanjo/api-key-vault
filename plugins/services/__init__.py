"""
External service plugins.
"""

from plugins.services.github_integration import GitHubIntegration
from plugins.services.slack_notifier import SlackNotifier
from plugins.services.email_sender import EmailSender
from plugins.services.webhook_caller import WebhookCaller

__all__ = [
    "GitHubIntegration",
    "SlackNotifier",
    "EmailSender",
    "WebhookCaller",
]
