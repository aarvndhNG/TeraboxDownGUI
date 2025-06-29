#!/usr/bin/env python3
"""
Setup script for Terabox Downloader GUI
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    with open("requirements-github.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="terabox-downloader-gui",
    version="1.0.0",
    author="Terabox Downloader GUI Contributors",
    description="A comprehensive GUI application for downloading files from Terabox cloud storage",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/terabox-downloader-gui",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "terabox-downloader=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="terabox downloader gui cloud storage file download",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/terabox-downloader-gui/issues",
        "Source": "https://github.com/yourusername/terabox-downloader-gui",
        "Documentation": "https://github.com/yourusername/terabox-downloader-gui/blob/main/README.md",
    },
)
