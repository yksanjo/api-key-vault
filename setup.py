from setuptools import setup, find_packages

setup(
    name="multi-agent-plugins",
    version="1.0.0",
    description="Plugin system for extending Multi-Agent Orchestrator",
    author="Multi-Agent Plugins",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ]
    },
)
