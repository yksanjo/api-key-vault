# Multi-Agent Plugins

Plugin system for extending Multi-Agent Orchestrator

![Plugins](https://img.shields.io/badge/Plugins-Extensible-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)

## Features

- 🔌 **Plugin Architecture**: Easy to add new capabilities
- 📦 **Pre-built Plugins**: 20+ ready-to-use plugins
- 🎯 **Type-safe**: Strong typing with Pydantic
- 🔄 **Hot Reload**: Load plugins without restart
- 📝 **Auto-discovery**: Plugins discovered automatically
- 🛠️ **Developer-friendly**: Simple plugin API

## Available Plugins

### Code Generation
- `python_generator` - Generate Python code
- `javascript_generator` - Generate JavaScript/TypeScript
- `rust_generator` - Generate Rust code
- `go_generator` - Generate Go code

### Data Processing
- `csv_processor` - Process CSV files
- `json_transformer` - Transform JSON data
- `xml_parser` - Parse and manipulate XML
- `yaml_handler` - Work with YAML files

### External Services
- `github_integration` - GitHub API integration
- `slack_notifier` - Send Slack notifications
- `email_sender` - Send emails
- `webhook_caller` - Call webhooks

### Testing
- `unit_test_generator` - Generate unit tests
- `code_linter` - Lint code
- `security_scanner` - Scan for vulnerabilities

### Documentation
- `readme_generator` - Generate README files
- `api_docs` - Generate API documentation
- `docstring_writer` - Add docstrings to code

### Utilities
- `file_watcher` - Watch file changes
- `git_helper` - Git operations
- `docker_manager` - Manage Docker containers

## Install

```bash
pip install -r requirements.txt
```

## Quick Start

### Use a Plugin

```python
from plugins import PluginManager

# Initialize plugin manager
manager = PluginManager()

# Load a plugin
python_gen = manager.register(
    'plugins.generators.python_generator.PythonGenerator'
)

# Use the plugin
result = python_gen.execute(
    type="flask_api",
    endpoints=[
        {"path": "/users", "method": "GET"},
        {"path": "/users", "method": "POST"},
    ]
)

print(result['code'])
```

### Create Custom Plugin

```python
from plugins.base import BasePlugin, BasePluginConfig
from pydantic import Field

class MyPluginConfig(BasePluginConfig):
    """Plugin configuration"""
    api_key: str = Field(..., description="API key")

class MyPlugin(BasePlugin):
    """My custom plugin"""
    
    name = "my_plugin"
    version = "1.0.0"
    description = "What this plugin does"
    config_class = MyPluginConfig
    
    def execute(self, **kwargs):
        """Execute plugin logic"""
        return {"status": "success"}

# Register plugin
manager.register(MyPlugin())
```

## Plugin Development

### Plugin Structure

```python
from plugins.base import BasePlugin
from pydantic import BaseModel, Field

class MyPluginConfig(BaseModel):
    """Plugin configuration"""
    api_key: str = Field(..., description="API key")

class MyPlugin(BasePlugin):
    """Description of what the plugin does"""
    
    # Metadata
    name = "my_plugin"
    version = "1.0.0"
    author = "Your Name"
    description = "What this plugin does"
    
    # Configuration
    config_class = MyPluginConfig
    
    def __init__(self, config: MyPluginConfig = None):
        super().__init__(config)
    
    def execute(self, **kwargs):
        """Main plugin logic"""
        return {"result": "success"}
    
    def validate(self):
        """Validate plugin can run"""
        return True
```

### Plugin Lifecycle

```
┌─────────────┐
│   Created   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validated  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Registered │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Executed   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Cleaned   │
└─────────────┘
```

## Examples

See the `examples/` directory for more examples.

## Testing

```bash
pytest tests/test_plugins.py -v
```

## Configuration

Edit `plugins.yaml` to enable/disable plugins and configure their settings.

## License

MIT

## Links

- [Parent Project](https://github.com/yksanjo/multi-agent-orchestrator)
