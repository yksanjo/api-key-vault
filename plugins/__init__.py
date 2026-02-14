"""
Multi-Agent Plugins - Plugin system for extending Multi-Agent Orchestrator

A flexible plugin architecture for adding new capabilities to agents.
"""

from plugins.base import BasePlugin, PluginMetadata
from plugins.manager import PluginManager

__version__ = "1.0.0"
__all__ = ["BasePlugin", "PluginMetadata", "PluginManager"]
