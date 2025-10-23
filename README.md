# 🚀 Perplexity AI Wrapper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Comprehensive unofficial API wrapper for Perplexity.ai with automated account generation, browser automation, and full async support.**

## ✨ Features

- 🔥 **Synchronous & Asynchronous Clients** - Choose your preferred approach
- 🤖 **Automated Account Generation** - Create accounts using Emailnator
- 🌐 **Browser Automation** - Full Playwright integration for UI interaction
- 🍪 **Cookie Management** - Extract from Chrome, Firefox, Edge
- 💬 **Conversation Mode** - Multi-turn conversations with context
- 📊 **Batch Processing** - Process multiple queries concurrently
- 🎨 **CLI Interface** - Rich terminal interface with colors
- 📡 **Streaming Support** - Real-time response streaming
- 🔍 **Network Inspector** - Tool to discover API endpoints
- 📝 **Multiple Export Formats** - JSON, Markdown, Text, PDF

## 🎯 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/perplexity-ai-wrapper.git
cd perplexity-ai-wrapper

# Run installation script
bash install.sh  # Linux/Mac
# OR
install.bat      # Windows

# Manual installation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### Basic Usage

```python
from src.core.client import PerplexityClient

# Simple search
client = PerplexityClient()
response = client.search("What is quantum computing?")
print(response.answer)
```

## 📚 Complete Examples

### 1. Basic Synchronous Search

```python
from src.core.client import PerplexityClient
from src.core.models import SearchMode, AIModel, SourceType

client = PerplexityClient()

response = client.search(
    query="Explain artificial intelligence",
    mode=SearchMode.PRO,
    model=AIModel.GPT_4O,
    sources=[SourceType.WEB, SourceType.SCHOLAR]
)

print(f"Answer: {response.answer}")
print(f"Sources: {len(response.sources)}")
```

### 2. Asynchronous Batch Processing

```python
import asyncio
from src.core.async_client import AsyncPerplexityClient

async def main():
    queries = [
        "What is machine learning?",
        "Explain blockchain",
        "How do neural networks work?"
    ]
    
    async with AsyncPerplexityClient() as client:
        responses = await client.batch_search(queries)
        
        for response in responses:
            print(f"Q: {response.query}")
            print(f"A: {response.answer[:100]}...\n")

asyncio.run(main())
```

### 3. Conversation Mode

```python
from src.core.client import PerplexityClient

client = PerplexityClient()

# Start conversation
conv_id = client.start_conversation()

# Multi-turn dialogue
response1 = client.search("What is Python?", use_conversation=True)
response2 = client.search("What are its main features?", use_conversation=True)
response3 = client.search("Show me a code example", use_conversation=True)

# Export conversation
export = client.export_conversation(format='markdown')
print(export)
```

### 4. Streaming Responses

```python
from src.core.client import PerplexityClient

client = PerplexityClient()

print("Streaming response:")
for chunk in client.search("Explain climate change", stream=True):
    content = chunk.get('content', '')
    if content:
        print(content, end='', flush=True)
```

### 5. Cookie Extraction & Management

```python
from src.auth.cookie_manager import CookieManager

# Initialize manager
cookie_manager = CookieManager()

# Extract from Chrome
cookies = cookie_manager.auto_extract(browser='chrome')
print(f"Extracted {len(cookies)} cookies")

# Save to profile
cookie_manager.save_cookies(cookies, name="my_profile")

# Load and use
loaded_cookies = cookie_manager.load_cookies("my_profile")
client = PerplexityClient(cookies=loaded_cookies)
```

### 6. Automated Account Generation

```python
import json
from src.auth.account_generator import AccountGenerator
from src.auth.cookie_manager import CookieManager

# Load Emailnator cookies
with open('emailnator_cookies.json', 'r') as f:
    emailnator_cookies = json.load(f)

# Generate account
generator = AccountGenerator(
    emailnator_cookies=emailnator_cookies,
    cookie_manager=CookieManager()
)

account = generator.create_account(
    save_profile=True,
    profile_name="auto_account_1"
)

print(f"Created: {account.email}")

# Use new account
client = PerplexityClient(cookies=account.cookies)
```

### 7. Browser Automation

```python
from src.automation.web_driver import PerplexityWebDriver

# Initialize driver
driver = PerplexityWebDriver(headless=False, stealth_mode=True)

driver.start()
driver.navigate_to_perplexity()

# Perform search
response = driver.search("What is the weather today?", wait_for_response=True)
print(response)

# Take screenshot
driver.save_screenshot("search_result.png")

# Export conversation
export = driver.export_conversation(format='markdown')

# Interactive mode
driver.interactive_mode()

driver.close()
```

### 8. Network Inspector (API Discovery)

```python
import asyncio
from tools.network_inspector import NetworkInspector

async def discover_api():
    inspector = NetworkInspector(output_dir="api_discovery")
    
    await inspector.start(headless=False)
    
    # Automated capture
    queries = [
        "What is AI?",
        "Explain quantum physics",
        "Latest tech news"
    ]
    await inspector.automated_capture(queries)
    
    # Save results
    inspector.save_results()
    
    await inspector.close()

asyncio.run(discover_api())
```

## 🖥️ CLI Usage

### Installation as CLI Tool

```bash
pip install -e .
```

### Commands

```bash
# Basic search
perplexity search "What is quantum computing?"

# Advanced search
perplexity search "AI developments" --mode pro --model gpt-4o --format json

# Interactive conversation
perplexity conversation --profile my_account

# Batch processing
perplexity batch "Query 1" "Query 2" "Query 3" --output results.json

# Cookie management
perplexity cookies extract --browser chrome --profile my_profile
perplexity cookies list
perplexity cookies delete old_profile

# Account generation
perplexity account generate --count 3 --emailnator-cookies cookies.json

# Browser automation
perplexity browser --user-data-dir "C:\Users\User\AppData\Local\Google\Chrome\User Data"
```

## 📖 API Documentation

### Search Modes

| Mode | Description | Models Available |
|------|-------------|------------------|
| `auto` | Automatic mode selection | Default |
| `pro` | Advanced search with citations | sonar, gpt-4.5, gpt-4o, claude-3.7-sonnet, gemini-2.0-flash, grok-2 |
| `reasoning` | Deep reasoning mode | r1, o3-mini, claude-3.7-sonnet |
| `deep_research` | Comprehensive research | Default |

### Source Types

- `web` - Web search results
- `scholar` - Academic papers
- `social` - Social media content
- `reddit` - Reddit discussions
- `youtube` - YouTube videos

### Search Parameters

```python
client.search(
    query: str,                    # Search query (required)
    mode: SearchMode,              # Search mode (default: auto)
    model: AIModel,                # Specific AI model (optional)
    sources: List[SourceType],     # Source types (default: [web])
    stream: bool,                  # Stream response (default: False)
    language: str,                 # Language code (default: en-US)
    incognito: bool,               # Incognito mode (default: False)
    files: Dict[str, str],         # File uploads (optional)
    use_conversation: bool,        # Continue conversation (default: False)
)
```

## 🔧 Configuration

### config.yaml

```yaml
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

automation:
  browser:
    headless: false
    stealth: true

logging:
  level: "INFO"
  file: "perplexity_wrapper.log"
```

### Environment Variables (.env)

```bash
PERPLEXITY_BASE_URL=https://www.perplexity.ai
PERPLEXITY_SESSION_TOKEN=your_token
CHROME_USER_DATA_DIR=/path/to/chrome/profile
LOG_LEVEL=INFO
```

## 🛠️ Project Structure

```
perplexity-ai-wrapper/
├── src/
│   ├── core/
│   │   ├── client.py              # Sync client
│   │   ├── async_client.py        # Async client
│   │   └── models.py              # Data models
│   ├── auth/
│   │   ├── cookie_manager.py      # Cookie handling
│   │   ├── account_generator.py   # Account creation
│   │   └── session_manager.py     # Session management
│   ├── automation/
│   │   └── web_driver.py          # Browser automation
│   ├── interfaces/
│   │   └── cli.py                 # CLI interface
│   └── utils/
│       ├── config_loader.py       # Configuration
│       └── logger.py              # Logging
├── tools/
│   └── network_inspector.py       # API discovery
├── examples/
│   └── complete_examples.py       # Usage examples
├── tests/
├── config.yaml
├── requirements.txt
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_client.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This is an **unofficial** wrapper for Perplexity.ai. Use responsibly and in accordance with Perplexity's Terms of Service. The authors are not responsible for any misuse or violations.

## 📋 Requirements

- Python 3.8+
- Chrome/Firefox/Edge (for cookie extraction)
- Playwright (for browser automation)
- Emailnator account (for account generation)

## 🐛 Troubleshooting

### Cookie Extraction Issues

```bash
# Install browser-cookie3
pip install browser-cookie3

# For Linux, may need additional packages
sudo apt-get install python3-dev libsqlite3-dev
```

### Playwright Issues

```bash
# Reinstall Playwright browsers
playwright install --force chromium

# Check installation
playwright --version
```

### Rate Limiting

If you encounter rate limiting:
- Add delays between requests
- Use multiple accounts
- Enable incognito mode

```python
import time
client = PerplexityClient()

for query in queries:
    response = client.search(query)
    time.sleep(5)  # 5 second delay
```

## 🔐 Security Best Practices

1. **Never commit cookies or tokens** - Use `.env` files and add to `.gitignore`
2. **Rotate accounts regularly** - Generate new accounts periodically
3. **Use environment variables** - Store sensitive data securely
4. **Limit API calls** - Respect rate limits

```python
# Good practice
from dotenv import load_dotenv
import os

load_dotenv()
cookies = json.loads(os.getenv('PERPLEXITY_COOKIES'))
```

## 📊 Performance Tips

### Async for Speed

```python
import asyncio
from src.core.async_client import AsyncPerplexityClient

async def fast_processing():
    async with AsyncPerplexityClient() as client:
        # 10 concurrent requests
        tasks = [client.search(f"Query {i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        return results
```

### Connection Pooling

```python
import aiohttp

connector = aiohttp.TCPConnector(
    limit=100,
    limit_per_host=30
)

client = AsyncPerplexityClient(connector=connector)
```

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query):
    client = PerplexityClient()
    return client.search(query)
```

## 📚 Advanced Usage

### Custom Retry Logic

```python
from src.core.client import PerplexityClient
import time

def search_with_retry(query, max_retries=3):
    client = PerplexityClient()
    
    for attempt in range(max_retries):
        try:
            return client.search(query)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Retry {attempt + 1} after {wait_time}s...")
            time.sleep(wait_time)
```

### Proxy Support

```python
import aiohttp

proxy = "http://proxy.example.com:8080"
connector = aiohttp.TCPConnector()

client = AsyncPerplexityClient(
    connector=connector
)

# Set proxy in session
client.session._connector = aiohttp.TCPConnector(
    limit=100,
    proxy=proxy
)
```

### File Upload Support

```python
from src.core.client import PerplexityClient

client = PerplexityClient()

# Upload file with query
response = client.search(
    query="Analyze this document",
    files={
        'document': 'path/to/file.pdf'
    }
)
```

### Custom Headers

```python
from src.core.client import PerplexityClient

client = PerplexityClient()

# Add custom headers
client.session.headers.update({
    'X-Custom-Header': 'value',
    'Accept-Language': 'es-ES'
})
```

## 🎓 Tutorial: Building a Research Assistant

Complete example of building a research assistant:

```python
import asyncio
from src.core.async_client import AsyncPerplexityClient
from src.core.models import SearchMode, SourceType
import json

class ResearchAssistant:
    def __init__(self):
        self.client = None
        self.research_data = []
    
    async def research_topic(self, topic: str, depth: int = 3):
        """Research a topic with follow-up questions"""
        async with AsyncPerplexityClient() as client:
            self.client = client
            
            # Initial query
            print(f"Researching: {topic}")
            response = await client.search(
                query=topic,
                mode=SearchMode.PRO,
                sources=[SourceType.WEB, SourceType.SCHOLAR]
            )
            
            self.research_data.append(response.to_dict())
            
            # Follow-up with related questions
            for i, related_q in enumerate(response.related_questions[:depth], 1):
                print(f"  Follow-up {i}: {related_q}")
                follow_up = await client.search(related_q)
                self.research_data.append(follow_up.to_dict())
            
            return self.generate_report()
    
    def generate_report(self) -> str:
        """Generate markdown report"""
        report = "# Research Report\n\n"
        
        for idx, data in enumerate(self.research_data, 1):
            report += f"## Query {idx}: {data['query']}\n\n"
            report += f"{data['answer']}\n\n"
            
            if data['sources']:
                report += "### Sources\n"
                for source in data['sources']:
                    report += f"- [{source['title']}]({source['url']})\n"
                report += "\n"
        
        return report
    
    def save_report(self, filename: str):
        """Save report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved: {filename}")

# Usage
async def main():
    assistant = ResearchAssistant()
    await assistant.research_topic("Quantum Computing Applications", depth=3)
    assistant.save_report("quantum_computing_research.md")

asyncio.run(main())
```

## 🌟 Real-World Use Cases

### 1. News Aggregator

```python
from src.core.async_client import AsyncPerplexityClient
from datetime import datetime

async def daily_news_digest(topics):
    async with AsyncPerplexityClient() as client:
        news = []
        for topic in topics:
            query = f"Latest news about {topic} today"
            response = await client.search(query)
            news.append({
                'topic': topic,
                'summary': response.answer,
                'sources': response.sources
            })
        return news

topics = ["AI", "Technology", "Science"]
digest = asyncio.run(daily_news_digest(topics))
```

### 2. Study Assistant

```python
class StudyAssistant:
    def __init__(self):
        self.client = PerplexityClient()
    
    def explain_concept(self, concept: str, level: str = "beginner"):
        """Explain concept at different levels"""
        query = f"Explain {concept} for a {level} level student"
        response = self.client.search(query)
        return response.answer
    
    def generate_quiz(self, topic: str, num_questions: int = 5):
        """Generate practice questions"""
        query = f"Generate {num_questions} quiz questions about {topic}"
        response = self.client.search(query)
        return response.answer

assistant = StudyAssistant()
print(assistant.explain_concept("Neural Networks", "intermediate"))
```

### 3. Market Research Tool

```python
async def market_research(company: str):
    async with AsyncPerplexityClient() as client:
        queries = [
            f"Latest news about {company}",
            f"{company} competitors analysis",
            f"{company} market position 2025",
            f"{company} financial performance"
        ]
        
        results = await client.batch_search(queries)
        
        report = {
            'company': company,
            'timestamp': datetime.now().isoformat(),
            'analysis': [r.to_dict() for r in results]
        }
        
        return report

research = asyncio.run(market_research("Tesla"))
```

## 📝 Changelog

### v1.0.0 (2025-01-15)
- Initial release
- Sync and async clients
- Cookie management
- Account generation
- Browser automation
- CLI interface
- Network inspector tool

## 🗺️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Image upload and analysis
- [ ] Voice input/output
- [ ] Integration with LangChain
- [ ] Docker container
- [ ] Web dashboard
- [ ] Plugin system
- [ ] Multi-language support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/perplexity-ai-wrapper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/perplexity-ai-wrapper/discussions)
- **Email**: your.email@example.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Perplexity.ai](https://www.perplexity.ai) for the amazing search engine
- [Playwright](https://playwright.dev/) for browser automation
- [Emailnator](https://www.emailnator.com) for temporary email service
- All contributors and users

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ by the community**

*Last updated: 2025-01-15*