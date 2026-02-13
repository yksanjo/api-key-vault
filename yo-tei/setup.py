"""Setup script for Yo-tei."""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="yotei",
    version="0.1.0",
    description="Yo-tei (予定) - Agent-to-Agent Social Planning CLI",
    author="Yoshi Kondo",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "yotei=yotei.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
