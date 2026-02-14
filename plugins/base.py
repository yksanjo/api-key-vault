"""
Base plugin classes and interfaces for the Multi-Agent Plugins system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginStatus(str, Enum):
    """Plugin lifecycle status."""
    CREATED = "created"
    VALIDATED = "validated"
    REGISTERED = "registered"
    EXECUTED = "executed"
    CLEANED = "cleaned"
    ERROR = "error"


class PluginMetadata(BaseModel):
    """Metadata for a plugin."""
    name: str = Field(..., description="Plugin name")
    version: str = Field(default="1.0.0", description="Plugin version")
    author: str = Field(default="Unknown", description="Plugin author")
    description: str = Field(default="", description="Plugin description")
    tags: List[str] = Field(default_factory=list, description="Plugin tags")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")


class BasePluginConfig(BaseModel):
    """Base configuration class for plugins."""
    enabled: bool = Field(default=True, description="Whether plugin is enabled")
    timeout: int = Field(default=30, description="Default timeout in seconds")
    cache_enabled: bool = Field(default=False, description="Enable result caching")


class BasePlugin(ABC):
    """
    Abstract base class for all plugins.
    
    Subclass this to create custom plugins with specific functionality.
    
    Attributes:
        name: Unique identifier for the plugin
        version: Semantic version string
        author: Plugin author name
        description: What the plugin does
        config_class: Pydantic model for configuration
    """
    
    # Metadata attributes - override in subclass
    name: str = "base_plugin"
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str = "Base plugin class"
    tags: List[str] = []
    dependencies: List[str] = []
    
    # Configuration
    config_class: Type[BasePluginConfig] = BasePluginConfig
    
    def __init__(self, config: Optional[BasePluginConfig] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Optional configuration instance
        """
        self._config = config or self.config_class()
        self._status = PluginStatus.CREATED
        self._error: Optional[str] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Internal initialization hook. Override in subclass."""
        pass
    
    @property
    def config(self) -> BasePluginConfig:
        """Get plugin configuration."""
        return self._config
    
    @property
    def status(self) -> PluginStatus:
        """Get current plugin status."""
        return self._status
    
    @property
    def error(self) -> Optional[str]:
        """Get last error message."""
        return self._error
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            tags=self.tags,
            dependencies=self.dependencies
        )
    
    def validate(self) -> bool:
        """
        Validate plugin can run.
        
        Override in subclass to add validation logic.
        
        Returns:
            True if validation passes
        """
        self._status = PluginStatus.VALIDATED
        return True
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute plugin logic.
        
        This is the main entry point for plugin functionality.
        
        Args:
            **kwargs: Plugin-specific arguments
            
        Returns:
            Dictionary containing the result
        """
        pass
    
    def on_execute(self, **kwargs) -> None:
        """Hook called before execute. Override in subclass."""
        self._status = PluginStatus.EXECUTED
    
    def on_success(self, result: Dict[str, Any]) -> None:
        """Hook called after successful execution. Override in subclass."""
        pass
    
    def on_error(self, error: Exception) -> None:
        """Hook called on execution error. Override in subclass."""
        self._status = PluginStatus.ERROR
        self._error = str(error)
        logger.error(f"Plugin {self.name} error: {error}")
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        Override in subclass to implement cleanup logic.
        Called when plugin is unloaded.
        """
        self._status = PluginStatus.CLEANED
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin metadata and information.
        
        Returns:
            Dictionary containing plugin information
        """
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "config": self.config.model_dump() if self.config else None
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, version={self.version})>"


class AsyncBasePlugin(BasePlugin):
    """
    Async version of BasePlugin for I/O-heavy operations.
    """
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Async execute plugin logic.
        
        Override in subclass.
        """
        raise NotImplementedError("Async plugins must implement execute")
    
    async def validate_async(self) -> bool:
        """Async validation hook. Override in subclass."""
        return self.validate()
    
    async def cleanup_async(self) -> None:
        """Async cleanup hook. Override in subclass."""
        self.cleanup()
