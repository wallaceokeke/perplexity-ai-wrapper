"""Setup script for Perplexity AI Wrapper"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="perplexity-ai-wrapper",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Unofficial API Wrapper for Perplexity.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "perplexity=src.interfaces.cli:main",
        ],
    },
)
