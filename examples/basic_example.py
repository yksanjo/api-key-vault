"""
Example: Basic Plugin Usage

This example demonstrates how to use the Multi-Agent Plugins system.
"""

from plugins import PluginManager
from plugins.base import BasePlugin, BasePluginConfig
from pydantic import Field


# Define a custom plugin
class MyPluginConfig(BasePluginConfig):
    """Configuration for my custom plugin."""
    custom_setting: str = Field(default="default_value", description="A custom setting")


class MyPlugin(BasePlugin):
    """A custom plugin that demonstrates the plugin API."""
    
    name = "my_plugin"
    version = "1.0.0"
    author = "Example Author"
    description = "A custom plugin for demonstration"
    tags = ["example", "custom"]
    config_class = MyPluginConfig
    
    def execute(self, **kwargs):
        """Execute the plugin."""
        action = kwargs.get("action", "greet")
        
        if action == "greet":
            return {"message": f"Hello, {kwargs.get('name', 'World')}!"}
        elif action == "echo":
            return {"echo": kwargs.get("message", "")}
        else:
            return {"error": f"Unknown action: {action}"}


def main():
    # Initialize the plugin manager
    manager = PluginManager()
    
    # Register our custom plugin
    my_plugin = manager.register(MyPlugin())
    print(f"Registered plugin: {my_plugin.name}")
    
    # Execute plugin
    result = my_plugin.execute(action="greet", name="Multi-Agent")
    print(f"Result: {result}")
    
    # Use built-in plugins
    # Python generator
    from plugins.generators.python_generator import PythonGenerator
    python_gen = manager.register(PythonGenerator())
    
    result = python_gen.execute(
        type="flask_api",
        endpoints=[
            {"path": "/users", "method": "GET"},
            {"path": "/users", "method": "POST"},
        ]
    )
    print(f"\nGenerated Python code:\n{result.get('code', 'N/A')[:200]}...")
    
    # CSV processor
    from plugins.processors.csv_processor import CSVProcessor
    csv_processor = manager.register(CSVProcessor())
    
    # Process CSV data
    csv_data = """name,age,city
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago"""
    
    result = csv_processor.execute(
        operation="read",
        data=csv_data
    )
    print(f"\nCSV Data: {result.get('count', 0)} rows read")
    
    # List all registered plugins
    plugins = manager.list_plugins()
    print(f"\nRegistered plugins: {len(plugins)}")
    for plugin in plugins:
        print(f"  - {plugin['name']}: {plugin['status']}")


if __name__ == "__main__":
    main()
