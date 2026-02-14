"""
README generator plugin.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class READMEGeneratorConfig(BasePluginConfig):
    """Configuration for README generator."""
    template: str = Field(default="default", description="README template")


class READMEGenerator(BasePlugin):
    """
    Generate README files for projects.
    """
    
    name = "readme_generator"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Generate README files for projects"
    tags = ["documentation", "readme", "docs"]
    config_class = READMEGeneratorConfig
    
    TEMPLATES = {
        "default": '''# {title}

{description}

## Installation

```bash
{install_command}
```

## Usage

{usage}

## Features

{features}

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
''',
        "python": '''# {title}

{description}

## Installation

```bash
pip install {package_name}
```

## Quick Start

```python
{quick_start}
```

## Features

{features}

## Documentation

For more detailed documentation, see [docs](docs/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
''',
        "javascript": '''# {title}

{description}

## Installation

```bash
npm install {package_name}
```

## Usage

```javascript
{quick_start}
```

## Features

{features}

## Documentation

For more detailed documentation, see [docs](docs/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
''',
    }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate README.
        
        Args:
            title: Project title
            description: Project description
            package_name: Package name for package managers
            install_command: Installation command
            usage: Usage instructions
            features: List of features
            quick_start: Quick start code example
            template: Template to use
            **kwargs: Additional options
            
        Returns:
            Dictionary with generated README
        """
        title = kwargs.get("title", "My Project")
        description = kwargs.get("description", "A project description")
        package_name = kwargs.get("package_name", "my-package")
        install_command = kwargs.get("install_command", f"pip install {package_name}")
        usage = kwargs.get("usage", "See documentation for usage")
        features = kwargs.get("features", [])
        quick_start = kwargs.get("quick_start", "# Add code here")
        template_name = kwargs.get("template", self.config.template)
        
        template = self.TEMPLATES.get(template_name, self.TEMPLATES["default"])
        
        # Format features as bullet points
        features_str = "\n".join([f"- {f}" for f in features]) if features else "- Feature 1\n- Feature 2"
        
        readme = template.format(
            title=title,
            description=description,
            package_name=package_name,
            install_command=install_command,
            usage=usage,
            features=features_str,
            quick_start=quick_start
        )
        
        return {
            "content": readme,
            "filename": "README.md",
            "template": template_name
        }
    
    def generate(self, **kwargs) -> Dict[str, Any]:
        """Generate README."""
        return self.execute(**kwargs)
