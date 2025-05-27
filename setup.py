"""
Setup script for the Luxembourg Legal Intelligence MCP server.
"""

import os
from setuptools import setup, find_packages

# Read the long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mcp-luxembourg-legal",
    version="1.0.0",
    description="Luxembourg Legal Intelligence MCP server with AI-ready document processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Temkit Sid-Ali",
    author_email="dev@yet.lu",
    url="https://github.com/yet-market/mcp-luxembourg-legal",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "SPARQLWrapper>=2.0.0",
        "fastmcp>=2.0.0",
        "pydantic>=2.0.0",
        "python-daemon>=2.3.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "beautifulsoup4>=4.12.0",
        "pypdf>=4.0.0",
        "requests>=2.31.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-luxembourg-legal=server:main",
        ],
    },
    data_files=[
        # Include systemd service file
        ('/etc/systemd/system', ['luxembourg-legal-server.service']),
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business :: Legal",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: French",
        "Operating System :: OS Independent",
    ],
    keywords="luxembourg legal mcp sparql ai documents government",
)