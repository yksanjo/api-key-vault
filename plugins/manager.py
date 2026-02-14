"""
Plugin Manager - Handles plugin loading, registration, and lifecycle management.
"""

import os
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field

from plugins.base import BasePlugin, BasePluginConfig, PluginStatus

logger = logging.getLogger(__name__)


@dataclass
class PluginEntry:
    """Internal plugin registry entry."""
    plugin: BasePlugin
    instance: Optional[BasePlugin] = None
    enabled: bool = True
    loaded_at: Optional[str] = None


class PluginManager:
    """
    Manages plugin lifecycle: loading, registration, execution, and cleanup.
    
    Example:
        manager = PluginManager()
        github = manager.load('github_integration', config={'token': 'xxx'})
        result = github.create_repo(name="my-repo")
    """
    
    def __init__(self, config_path: Optional[str] = None, auto_discover: bool = True):
        """
        Initialize the plugin manager.
        
        Args:
            config_path: Path to plugins.yaml configuration file
            auto_discover: Whether to auto-discover built-in plugins
        """
        self._plugins: Dict[str, PluginEntry] = {}
        self._config_path = config_path
        self._global_config: Dict[str, Any] = {}
        
        if config_path and os.path.exists(config_path):
            self._load_global_config(config_path)
        
        if auto_discover:
            self._discover_plugins()
    
    def _load_global_config(self, config_path: str) -> None:
        """Load global plugin configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'plugins' in config:
                    self._global_config = config['plugins']
            logger.info(f"Loaded plugin config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    
    def _discover_plugins(self) -> None:
        """Auto-discover built-in plugins."""
        built_in_plugins = [
            'plugins.generators.python_generator',
            'plugins.generators.javascript_generator',
            'plugins.generators.rust_generator',
            'plugins.generators.go_generator',
            'plugins.processors.csv_processor',
            'plugins.processors.json_transformer',
            'plugins.processors.xml_parser',
            'plugins.processors.yaml_handler',
            'plugins.services.github_integration',
            'plugins.services.slack_notifier',
            'plugins.services.email_sender',
            'plugins.services.webhook_caller',
            'plugins.testing.unit_test_generator',
            'plugins.testing.code_linter',
            'plugins.testing.security_scanner',
            'plugins.docs.readme_generator',
            'plugins.docs.api_docs',
            'plugins.docs.docstring_writer',
            'plugins.utils.file_watcher',
            'plugins.utils.git_helper',
            'plugins.utils.docker_manager',
        ]
        
        for plugin_path in built_in_plugins:
            try:
                importlib.import_module(plugin_path)
            except ImportError:
                pass  # Plugin not available
    
    def register(
        self, 
        plugin: Union[BasePlugin, Type[BasePlugin]], 
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        enabled: bool = True
    ) -> BasePlugin:
        """
        Register a plugin with the manager.
        
        Args:
            plugin: Plugin instance or class
            name: Optional custom name (defaults to plugin.name)
            config: Optional configuration dictionary
            enabled: Whether plugin is enabled
            
        Returns:
            Registered plugin instance
        """
        # Instantiate if class
        if isinstance(plugin, type):
            plugin_instance = plugin()
        else:
            plugin_instance = plugin
        
        # Use custom name or plugin's default
        plugin_name = name or plugin_instance.name
        
        # Apply configuration if provided
        if config and hasattr(plugin_instance, 'config_class'):
            try:
                plugin_instance._config = plugin_instance.config_class(**config)
            except Exception as e:
                logger.warning(f"Failed to apply config for {plugin_name}: {e}")
        
        # Validate plugin
        if not plugin_instance.validate():
            raise ValueError(f"Plugin {plugin_name} validation failed")
        
        # Create registry entry
        entry = PluginEntry(
            plugin=plugin_instance,
            instance=plugin_instance,
            enabled=enabled
        )
        
        self._plugins[plugin_name] = entry
        logger.info(f"Registered plugin: {plugin_name}")
        
        return plugin_instance
    
    def load(
        self, 
        name: str, 
        config: Optional[Dict[str, Any]] = None,
        auto_register: bool = True
    ) -> BasePlugin:
        """
        Load a plugin by name.
        
        Args:
            name: Plugin name
            config: Optional configuration
            auto_register: Auto-register if not found
            
        Returns:
            Loaded plugin instance
        """
        # Check if already loaded
        if name in self._plugins:
            entry = self._plugins[name]
            if not entry.enabled:
                raise ValueError(f"Plugin {name} is disabled")
            return entry.instance
        
        # Check global config for enabled status
        if name in self._global_config:
            global_cfg = self._global_config[name]
            if not global_cfg.get('enabled', True):
                raise ValueError(f"Plugin {name} is disabled in config")
            if 'config' in global_cfg and config is None:
                config = global_cfg['config']
        
        # Try to auto-load from built-in plugins
        plugin_class = self._get_plugin_class(name)
        
        if plugin_class:
            return self.register(plugin_class, name=name, config=config)
        
        if auto_register:
            raise ValueError(f"Plugin '{name}' not found")
        
        raise ValueError(f"Plugin '{name}' not registered")
    
    def _get_plugin_class(self, name: str) -> Optional[Type[BasePlugin]]:
        """Get plugin class by name from discovered modules."""
        # Map of plugin names to their classes
        plugin_registry = {
            'python_generator': ('plugins.generators', 'PythonGenerator'),
            'javascript_generator': ('plugins.generators', 'JavaScriptGenerator'),
            'rust_generator': ('plugins.generators', 'RustGenerator'),
            'go_generator': ('plugins.generators', 'GoGenerator'),
            'csv_processor': ('plugins.processors', 'CSVProcessor'),
            'json_transformer': ('plugins.processors', 'JSONTransformer'),
            'xml_parser': ('plugins.processors', 'XMLParser'),
            'yaml_handler': ('plugins.processors', 'YAMLHandler'),
            'github_integration': ('plugins.services', 'GitHubIntegration'),
            'slack_notifier': ('plugins.services', 'SlackNotifier'),
            'email_sender': ('plugins.services', 'EmailSender'),
            'webhook_caller': ('plugins.services', 'WebhookCaller'),
            'unit_test_generator': ('plugins.testing', 'UnitTestGenerator'),
            'code_linter': ('plugins.testing', 'CodeLinter'),
            'security_scanner': ('plugins.testing', 'SecurityScanner'),
            'readme_generator': ('plugins.docs', 'READMEGenerator'),
            'api_docs': ('plugins.docs', 'APIDocs'),
            'docstring_writer': ('plugins.docs', 'DocstringWriter'),
            'file_watcher': ('plugins.utils', 'FileWatcher'),
            'git_helper': ('plugins.utils', 'GitHelper'),
            'docker_manager': ('plugins.utils', 'DockerManager'),
        }
        
        if name not in plugin_registry:
            return None
        
        module_name, class_name = plugin_registry[name]
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name, None)
        except ImportError:
            return None
    
    def unload(self, name: str) -> None:
        """
        Unload a plugin.
        
        Args:
            name: Plugin name
        """
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not loaded")
        
        entry = self._plugins[name]
        if entry.instance:
            entry.instance.cleanup()
        
        del self._plugins[name]
        logger.info(f"Unloaded plugin: {name}")
    
    def reload(self, name: str) -> BasePlugin:
        """
        Reload a plugin (unload and load again).
        
        Args:
            name: Plugin name
            
        Returns:
            Reloaded plugin instance
        """
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not loaded")
        
        entry = self._plugins[name]
        config = entry.instance.config.model_dump() if entry.instance.config else None
        
        self.unload(name)
        return self.load(name, config=config)
    
    def enable(self, name: str) -> None:
        """Enable a plugin."""
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not loaded")
        self._plugins[name].enabled = True
    
    def disable(self, name: str) -> None:
        """Disable a plugin."""
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not loaded")
        self._plugins[name].enabled = False
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        result = []
        for name, entry in self._plugins.items():
            if entry.instance:
                result.append({
                    "name": name,
                    "enabled": entry.enabled,
                    "status": entry.instance.status.value,
                    "info": entry.instance.get_info()
                })
        return result
    
    def get(self, name: str) -> BasePlugin:
        """Get a plugin by name."""
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not loaded")
        return self._plugins[name].instance
    
    def __contains__(self, name: str) -> bool:
        """Check if plugin is registered."""
        return name in self._plugins
    
    def __len__(self) -> int:
        """Get number of registered plugins."""
        return len(self._plugins)
    
    def __getitem__(self, name: str) -> BasePlugin:
        """Get plugin by name using bracket notation."""
        return self.get(name)
    
    def cleanup_all(self) -> None:
        """Clean up all registered plugins."""
        for name in list(self._plugins.keys()):
            try:
                self.unload(name)
            except Exception as e:
                logger.error(f"Error unloading plugin {name}: {e}")
