"""
Tests for Multi-Agent Plugins system.
"""

import pytest
from plugins import PluginManager, BasePlugin, PluginMetadata
from plugins.base import BasePluginConfig, PluginStatus


# Test plugin for testing
class TestPlugin(BasePlugin):
    """A test plugin for testing."""
    
    name = "test_plugin"
    version = "1.0.0"
    author = "Test"
    description = "A test plugin"
    
    def execute(self, **kwargs):
        return {"status": "success", "args": kwargs}


class TestBasePlugin:
    """Tests for BasePlugin class."""
    
    def test_plugin_creation(self):
        """Test creating a plugin instance."""
        plugin = TestPlugin()
        
        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.status == PluginStatus.CREATED
    
    def test_plugin_validation(self):
        """Test plugin validation."""
        plugin = TestPlugin()
        assert plugin.validate() is True
        assert plugin.status == PluginStatus.VALIDATED
    
    def test_plugin_execution(self):
        """Test plugin execution."""
        plugin = TestPlugin()
        
        result = plugin.execute(action="test", value=123)
        
        assert result["status"] == "success"
        assert result["args"]["action"] == "test"
        assert result["args"]["value"] == 123
    
    def test_plugin_info(self):
        """Test getting plugin info."""
        plugin = TestPlugin()
        info = plugin.get_info()
        
        assert info["name"] == "test_plugin"
        assert info["version"] == "1.0.0"
        assert info["author"] == "Test"
    
    def test_plugin_cleanup(self):
        """Test plugin cleanup."""
        plugin = TestPlugin()
        plugin.cleanup()
        
        assert plugin.status == PluginStatus.CLEANED


class TestPluginManager:
    """Tests for PluginManager class."""
    
    def test_manager_creation(self):
        """Test creating a plugin manager."""
        manager = PluginManager(auto_discover=False)
        
        assert len(manager) == 0
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        manager = PluginManager(auto_discover=False)
        plugin = TestPlugin()
        
        registered = manager.register(plugin)
        
        assert registered.name == "test_plugin"
        assert len(manager) == 1
        assert "test_plugin" in manager
    
    def test_get_plugin(self):
        """Test getting a plugin by name."""
        manager = PluginManager(auto_discover=False)
        plugin = TestPlugin()
        manager.register(plugin)
        
        retrieved = manager.get("test_plugin")
        
        assert retrieved is not None
        assert retrieved.name == "test_plugin"
    
    def test_unload_plugin(self):
        """Test unloading a plugin."""
        manager = PluginManager(auto_discover=False)
        plugin = TestPlugin()
        manager.register(plugin)
        
        manager.unload("test_plugin")
        
        assert len(manager) == 0
    
    def test_list_plugins(self):
        """Test listing plugins."""
        manager = PluginManager(auto_discover=False)
        plugin = TestPlugin()
        manager.register(plugin)
        
        plugins = manager.list_plugins()
        
        assert len(plugins) == 1
        assert plugins[0]["name"] == "test_plugin"
    
    def test_enable_disable_plugin(self):
        """Test enabling and disabling plugins."""
        manager = PluginManager(auto_discover=False)
        plugin = TestPlugin()
        manager.register(plugin)
        
        manager.disable("test_plugin")
        # Check the entry's enabled status via the manager
        entry = manager._plugins["test_plugin"]
        assert entry.enabled is False
        
        manager.enable("test_plugin")
        entry = manager._plugins["test_plugin"]
        assert entry.enabled is True


class TestGenerators:
    """Tests for generator plugins."""
    
    def test_python_generator(self):
        """Test Python code generator."""
        from plugins.generators.python_generator import PythonGenerator
        
        plugin = PythonGenerator()
        result = plugin.execute(type="class", class_name="User", description="User class")
        
        assert "code" in result
        assert result["language"] == "python"
    
    def test_javascript_generator(self):
        """Test JavaScript code generator."""
        from plugins.generators.javascript_generator import JavaScriptGenerator
        
        plugin = JavaScriptGenerator()
        result = plugin.execute(type="express", endpoints=[])
        
        assert "code" in result
    
    def test_rust_generator(self):
        """Test Rust code generator."""
        from plugins.generators.rust_generator import RustGenerator
        
        plugin = RustGenerator()
        result = plugin.execute(type="cli", name="myapp")
        
        assert "code" in result
    
    def test_go_generator(self):
        """Test Go code generator."""
        from plugins.generators.go_generator import GoGenerator
        
        plugin = GoGenerator()
        result = plugin.execute(type="cli", name="myapp")
        
        assert "code" in result


class TestProcessors:
    """Tests for processor plugins."""
    
    def test_csv_processor(self):
        """Test CSV processor."""
        from plugins.processors.csv_processor import CSVProcessor
        
        plugin = CSVProcessor()
        result = plugin.execute(
            operation="read",
            data="name,age\nJohn,30\nJane,25"
        )
        
        assert result["count"] == 2
        assert len(result["data"]) == 2
    
    def test_json_transformer(self):
        """Test JSON transformer."""
        from plugins.processors.json_transformer import JSONTransformer
        
        plugin = JSONTransformer()
        result = plugin.execute(
            operation="parse",
            data='{"key": "value"}'
        )
        
        assert result["success"] is True
        assert result["data"]["key"] == "value"
    
    def test_yaml_handler(self):
        """Test YAML handler."""
        from plugins.processors.yaml_handler import YAMLHandler
        
        plugin = YAMLHandler()
        result = plugin.execute(
            operation="dump",
            data={"key": "value"}
        )
        
        assert result["success"] is True
        assert "key" in result["data"]


class TestTesting:
    """Tests for testing plugins."""
    
    def test_unit_test_generator(self):
        """Test unit test generator."""
        from plugins.testing.unit_test_generator import UnitTestGenerator
        
        plugin = UnitTestGenerator()
        result = plugin.execute(
            source_code="""
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, a, b):
        return a * b
""",
            framework="pytest"
        )
        
        assert "code" in result
        assert result["functions_tested"] == 1
    
    def test_code_linter(self):
        """Test code linter."""
        from plugins.testing.code_linter import CodeLinter
        
        plugin = CodeLinter()
        result = plugin.execute(
            source_code="""
# TODO: fix this
eval("print('hello')")
""",
            language="python"
        )
        
        assert "issues" in result
        assert result["summary"]["warnings"] > 0
    
    def test_security_scanner(self):
        """Test security scanner."""
        from plugins.testing.security_scanner import SecurityScanner
        
        plugin = SecurityScanner()
        result = plugin.execute(
            source_code="""
password = "hardcoded123"
eval("print('dangerous')")
""",
            language="python"
        )
        
        assert "vulnerabilities" in result
        assert result["summary"]["high"] > 0


class TestDocumentation:
    """Tests for documentation plugins."""
    
    def test_readme_generator(self):
        """Test README generator."""
        from plugins.docs.readme_generator import READMEGenerator
        
        plugin = READMEGenerator()
        result = plugin.execute(
            title="My Project",
            description="A test project",
            features=["Feature 1", "Feature 2"]
        )
        
        assert "content" in result
        assert "My Project" in result["content"]
    
    def test_docstring_writer(self):
        """Test docstring writer."""
        from plugins.docs.docstring_writer import DocstringWriter
        
        plugin = DocstringWriter()
        result = plugin.execute(
            source_code="""
def greet(name):
    return f"Hello, {name}!"
""",
            style="google"
        )
        
        assert "code" in result
        assert '"""' in result["code"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
