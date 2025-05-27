"""
Setup script for the SPARQL-enabled MCP server.
"""

import os
from setuptools import setup, find_packages

# Read the long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mcp-server-sparql",
    version="1.0.0",
    description="SPARQL-enabled MCP server with caching and result formatting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Temkit Sid-Ali",
    author_email="dev@yet.lu",
    url="https://github.com/yet-market/yet-sparql-mcp-server",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "SPARQLWrapper>=2.0.0",
        "fastmcp>=2.0.0",
        "pydantic>=2.0.0",
        "python-daemon>=2.3.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-server-sparql=server:main",
        ],
    },
    data_files=[
        # Include systemd service file
        ('/etc/systemd/system', ['sparql-server.service']),
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
    ],
)