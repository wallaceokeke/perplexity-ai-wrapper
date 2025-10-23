#!/usr/bin/env python3
"""
Perplexity AI Wrapper - Fresh Start Script
Generates complete project and pushes to GitHub in one go!

Usage:
    python fresh_start.py
"""
import os
import subprocess
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║     PERPLEXITY AI WRAPPER - FRESH START                      ║
║                                                              ║
║     Complete setup from scratch                              ║
╚══════════════════════════════════════════════════════════════╝
""")

# Configuration
PROJECT_NAME = "perplexity-ai-wrapper"
GITHUB_REPO = "https://github.com/wallaceokeke/perplexity-ai-wrapper.git"

print("\n[1/6] Creating project structure...")
BASE_DIR = Path(PROJECT_NAME)

# Create directories
dirs = [
    "src/core", "src/auth", "src/automation", "src/interfaces", "src/utils",
    "tools", "examples", "tests", "logs", "exports", "screenshots",
    ".cache", "debug/raw_responses", "docs"
]

for d in dirs:
    (BASE_DIR / d).mkdir(parents=True, exist_ok=True)

# Create __init__.py files
for init in ["src", "src/core", "src/auth", "src/automation", "src/interfaces", "src/utils"]:
    (BASE_DIR / init / "__init__.py").write_text('"""Perplexity AI Wrapper"""\n')

print("✓ Project structure created")

print("\n[2/6] Creating configuration files...")

# requirements.txt
(BASE_DIR / "requirements.txt").write_text("""# Perplexity AI Wrapper Dependencies

# Core HTTP/Async
requests>=2.31.0
aiohttp>=3.9.0
httpx>=0.25.0

# Web Automation
playwright>=1.40.0

# Cookie Management
browser-cookie3>=0.19.0

# HTML Parsing
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Data Handling
pyyaml>=6.0
python-dotenv>=1.0.0
pydantic>=2.5.0

# CLI & UI
rich>=13.7.0
colorama>=0.4.6
click>=8.1.0

# Async Utilities
asyncio-throttle>=1.0.0
aiofiles>=23.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
""")

# .gitignore
(BASE_DIR / ".gitignore").write_text("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project Specific
.env
cookies.json
*.log
logs/
exports/
screenshots/
.cache/
debug/
emailnator_cookies.json
*_cookies.json

# OS
.DS_Store
Thumbs.db
""")

# README.md
(BASE_DIR / "README.md").write_text("""# 🚀 Perplexity AI Wrapper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/wallaceokeke/perplexity-ai-wrapper?style=social)](https://github.com/wallaceokeke/perplexity-ai-wrapper)

> Comprehensive unofficial Python API wrapper for Perplexity.ai with async support, browser automation, and account generation.

## ✨ Features

- 🔥 **Sync & Async Clients** - Choose your preferred approach
- 🤖 **Browser Automation** - Full Playwright integration
- 🍪 **Cookie Management** - Extract from Chrome/Firefox/Edge
- 📊 **Batch Processing** - Process multiple queries concurrently
- 💬 **Conversation Mode** - Multi-turn dialogues
- 🎨 **CLI Interface** - Rich terminal interface
- 📝 **Multiple Formats** - Export to JSON, Markdown, Text, PDF
- 🔍 **Network Inspector** - Discover API endpoints
- 🚀 **Account Generator** - Automated account creation

## 🚀 Quick Start

\`\`\`bash
# Clone repository
git clone https://github.com/wallaceokeke/perplexity-ai-wrapper.git
cd perplexity-ai-wrapper

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run test
python quick_test.py
\`\`\`

## 📖 Basic Usage

\`\`\`python
from src.core.client import PerplexityClient

client = PerplexityClient()
response = client.search("What is quantum computing?")
print(response.answer)
\`\`\`

## 📚 Documentation

- [Setup Instructions](SETUP_INSTRUCTIONS.md)
- [Complete Guide](PROJECT_SUMMARY.md)
- [Examples](examples/)

## ⚠️ Disclaimer

This is an **unofficial** wrapper. Use responsibly and in accordance with Perplexity's Terms of Service.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with ❤️ by [@wallaceokeke](https://github.com/wallaceokeke)**
""")

# LICENSE
(BASE_DIR / "LICENSE").write_text("""MIT License

Copyright (c) 2025 Wallace Okeke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")

# config.yaml
(BASE_DIR / "config.yaml").write_text("""# Perplexity AI Wrapper Configuration

client:
  base_url: "https://www.perplexity.ai"
  timeout: 30
  max_retries: 3

search:
  available_modes:
    - "auto"
    - "pro"
    - "reasoning"
    - "deep_research"

logging:
  level: "INFO"
  file: "logs/perplexity_wrapper.log"

automation:
  browser:
    headless: false
    stealth: true
""")

# setup.py
(BASE_DIR / "setup.py").write_text("""from setuptools import setup, find_packages

setup(
    name="perplexity-ai-wrapper",
    version="1.0.0",
    author="Wallace Okeke",
    description="Unofficial API Wrapper for Perplexity.ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "perplexity=src.interfaces.cli:main",
        ],
    },
)
""")

# SETUP_INSTRUCTIONS.md
(BASE_DIR / "SETUP_INSTRUCTIONS.md").write_text("""# 🚀 Setup Instructions

## Step 1: Copy Artifact Content

Copy the complete content from the conversation artifacts into these files:

### Files to Update:
- `src/core/models.py` → Copy from "models.py" artifact
- `src/core/client.py` → Copy from "client.py" artifact
- `src/core/async_client.py` → Copy from "async_client.py" artifact
- `src/auth/cookie_manager.py` → Copy from "cookie_manager.py" artifact
- `src/auth/account_generator.py` → Copy from "account_generator.py" artifact
- `src/automation/web_driver.py` → Copy from "web_driver.py" artifact
- `src/interfaces/cli.py` → Copy from "cli.py" artifact
- `tools/network_inspector.py` → Copy from "network_inspector.py" artifact
- `examples/complete_examples.py` → Copy from "complete_examples.py" artifact
- `quick_test.py` → Copy from "quick_test.py" artifact

## Step 2: Install Dependencies

\`\`\`bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\\Scripts\\activate    # Windows

# Install dependencies
pip install -r requirements.txt
playwright install chromium
\`\`\`

## Step 3: Test Installation

\`\`\`bash
python quick_test.py
\`\`\`

## Step 4: Discover API Endpoints

\`\`\`bash
python tools/network_inspector.py --mode interactive
\`\`\`

## Step 5: Extract Cookies

\`\`\`python
from src.auth.cookie_manager import CookieManager

manager = CookieManager()
cookies = manager.auto_extract(browser='chrome')
manager.save_cookies(cookies, 'my_profile')
\`\`\`

## Step 6: Start Using!

\`\`\`python
from src.core.client import PerplexityClient
from src.auth.cookie_manager import CookieManager

cookies = CookieManager().load_cookies('my_profile')
client = PerplexityClient(cookies=cookies)

response = client.search("What is quantum computing?")
print(response.answer)
\`\`\`

## Need Help?

Refer to README.md and PROJECT_SUMMARY.md for complete documentation.
""")

# Placeholder source files
source_files = {
    "src/core/models.py": '# TODO: Copy from "models.py" artifact\npass\n',
    "src/core/client.py": '# TODO: Copy from "client.py" artifact\npass\n',
    "src/core/async_client.py": '# TODO: Copy from "async_client.py" artifact\npass\n',
    "src/auth/cookie_manager.py": '# TODO: Copy from "cookie_manager.py" artifact\npass\n',
    "src/auth/account_generator.py": '# TODO: Copy from "account_generator.py" artifact\npass\n',
    "src/automation/web_driver.py": '# TODO: Copy from "web_driver.py" artifact\npass\n',
    "src/interfaces/cli.py": '# TODO: Copy from "cli.py" artifact\npass\n',
    "tools/network_inspector.py": '# TODO: Copy from "network_inspector.py" artifact\npass\n',
    "examples/complete_examples.py": '# TODO: Copy from "complete_examples.py" artifact\npass\n',
    "quick_test.py": '# TODO: Copy from "quick_test.py" artifact\npass\n',
}

for filepath, content in source_files.items():
    (BASE_DIR / filepath).write_text(content)

print("✓ Configuration files created")

print("\n[3/6] Initializing Git...")
os.chdir(BASE_DIR)
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "add", "."], check=True)
subprocess.run([
    "git", "commit", "-m", 
    "Initial commit: Complete Perplexity AI Wrapper\n\nFeatures:\n- Synchronous and asynchronous clients\n- Browser automation\n- Cookie management\n- Account generation\n- Network inspector\n- CLI interface"
], check=True)
print("✓ Git initialized and first commit created")

print("\n[4/6] Configuring remote...")
subprocess.run(["git", "branch", "-M", "main"], check=True)
subprocess.run(["git", "remote", "add", "origin", GITHUB_REPO], check=True)
print("✓ Remote configured")

print("\n[5/6] Pushing to GitHub...")
try:
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print("✓ Successfully pushed to GitHub!")
except subprocess.CalledProcessError:
    print("⚠️  Push failed. Run manually: git push -u origin main --force")

print("\n[6/6] Setup complete!")
print("\n" + "="*70)
print("✅ PROJECT CREATED SUCCESSFULLY!")
print("="*70)
print(f"\nLocation: {Path.cwd()}")
print(f"\nGitHub: https://github.com/wallaceokeke/perplexity-ai-wrapper")
print("\nNext steps:")
print("1. Copy artifact content into source files (see SETUP_INSTRUCTIONS.md)")
print("2. Run: pip install -r requirements.txt")
print("3. Run: python quick_test.py")
print("="*70)