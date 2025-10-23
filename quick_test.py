"""
Perplexity AI Wrapper - Quick Test Script
File: quick_test.py

Run this script to verify your installation and test basic functionality.
"""
import sys
import asyncio
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print colored header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_python_version():
    """Check Python version"""
    print_info("Checking Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print_info("Checking dependencies...")
    
    required = {
        'requests': 'Core HTTP library',
        'aiohttp': 'Async HTTP library',
        'playwright': 'Browser automation',
        'beautifulsoup4': 'HTML parsing',
        'pyyaml': 'Configuration files',
        'rich': 'Terminal UI',
        'click': 'CLI framework'
    }
    
    missing = []
    installed = []
    
    for package, description in required.items():
        try:
            __import__(package.replace('-', '_'))
            installed.append(package)
            print_success(f"{package:20} - {description}")
        except ImportError:
            missing.append(package)
            print_error(f"{package:20} - NOT INSTALLED")
    
    if missing:
        print_warning(f"\nMissing packages: {', '.join(missing)}")
        print_info(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def test_sync_client():
    """Test synchronous client"""
    print_info("Testing synchronous client...")
    
    try:
        from src.core.client import PerplexityClient
        from src.core.models import SearchMode
        
        client = PerplexityClient()
        print_success("Client initialized")
        
        # Note: This will fail without actual API access
        print_warning("Skipping actual API call (needs authentication)")
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_async_client():
    """Test asynchronous client"""
    print_info("Testing asynchronous client...")
    
    try:
        from src.core.async_client import AsyncPerplexityClient
        
        async def test():
            async with AsyncPerplexityClient() as client:
                print_success("Async client initialized")
                return True
        
        result = asyncio.run(test())
        return result
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_models():
    """Test data models"""
    print_info("Testing data models...")
    
    try:
        from src.core.models import (
            SearchMode, AIModel, SourceType, 
            SearchConfig, SearchResponse
        )
        
        # Test enum creation
        mode = SearchMode.PRO
        model = AIModel.GPT_4O
        sources = [SourceType.WEB, SourceType.SCHOLAR]
        
        # Test config creation
        config = SearchConfig(
            query="Test query",
            mode=mode,
            model=model,
            sources=sources
        )
        
        print_success("SearchMode enum works")
        print_success("AIModel enum works")
        print_success("SourceType enum works")
        print_success("SearchConfig creation works")
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_cookie_manager():
    """Test cookie manager"""
    print_info("Testing cookie manager...")
    
    try:
        from src.auth.cookie_manager import CookieManager
        
        manager = CookieManager(storage_path=".test_cookies.json")
        
        # Test save/load
        test_cookies = {'test': 'value'}
        manager.save_cookies(test_cookies, name="test_profile")
        loaded = manager.load_cookies("test_profile")
        
        if loaded == test_cookies:
            print_success("Cookie save/load works")
        else:
            print_error("Cookie save/load mismatch")
            return False
        
        # Cleanup
        manager.delete_profile("test_profile")
        Path(".test_cookies.json").unlink(missing_ok=True)
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_playwright():
    """Test Playwright installation"""
    print_info("Testing Playwright...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Check if chromium is installed
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print_success("Playwright and Chromium installed")
                return True
            except Exception as e:
                print_error(f"Chromium not installed: {str(e)}")
                print_info("Run: playwright install chromium")
                return False
    except ImportError:
        print_error("Playwright not installed")
        print_info("Run: pip install playwright && playwright install chromium")
        return False


def test_file_structure():
    """Test if project structure is correct"""
    print_info("Checking project structure...")
    
    required_paths = [
        'src/core/client.py',
        'src/core/async_client.py',
        'src/core/models.py',
        'src/auth/cookie_manager.py',
        'src/auth/account_generator.py',
        'src/automation/web_driver.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing = []
    for path in required_paths:
        if Path(path).exists():
            print_success(f"{path}")
        else:
            print_error(f"{path} - NOT FOUND")
            missing.append(path)
    
    if missing:
        print_warning(f"\nMissing files: {len(missing)}")
        return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print_header("PERPLEXITY AI WRAPPER - INSTALLATION TEST")
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", test_file_structure),
        ("Data Models", test_models),
        ("Cookie Manager", test_cookie_manager),
        ("Sync Client", test_sync_client),
        ("Async Client", test_async_client),
        ("Playwright", test_playwright),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_header(f"TEST: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name:30} [{status}]")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print(f"{GREEN}All tests passed! ({passed}/{total}){RESET}")
        print(f"{GREEN}✓ Installation is complete and working!{RESET}")
    elif percentage >= 75:
        print(f"{YELLOW}Most tests passed ({passed}/{total}){RESET}")
        print(f"{YELLOW}⚠ Some features may not work correctly{RESET}")
    else:
        print(f"{RED}Many tests failed ({passed}/{total}){RESET}")
        print(f"{RED}✗ Installation needs attention{RESET}")
    
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Next steps
    if percentage < 100:
        print_header("NEXT STEPS")
        
        failed_tests = [name for name, result in results if not result]
        
        if "Dependencies" in failed_tests:
            print_info("Install missing dependencies:")
            print("  pip install -r requirements.txt")
        
        if "Playwright" in failed_tests:
            print_info("Install Playwright browsers:")
            print("  playwright install chromium")
        
        if "Project Structure" in failed_tests:
            print_warning("Some project files are missing")
            print_info("Make sure you have the complete source code")
        
        print()
    else:
        print_header("READY TO USE!")
        print_info("Try these commands:")
        print("  python examples/complete_examples.py 1")
        print("  perplexity search 'What is AI?'")
        print("  python -m src.cli --help")
        print()


def quick_demo():
    """Quick demo if everything is working"""
    print_header("QUICK DEMO")
    
    try:
        from src.core.client import PerplexityClient
        from src.core.models import SearchMode
        
        print_info("Initializing client...")
        client = PerplexityClient()
        
        print_info("Client is ready!")
        print_warning("Note: Actual searches require authentication cookies")
        
        print_info("\nExample usage:")
        print("""
        from src.core.client import PerplexityClient
        
        client = PerplexityClient()
        response = client.search("What is quantum computing?")
        print(response.answer)
        """)
        
    except Exception as e:
        print_error(f"Demo failed: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Perplexity AI Wrapper installation")
    parser.add_argument('--demo', action='store_true', help='Run quick demo')
    parser.add_argument('--minimal', action='store_true', help='Run minimal tests only')
    
    args = parser.parse_args()
    
    if args.demo:
        quick_demo()
    elif args.minimal:
        print_header("MINIMAL TEST")
        check_python_version()
        check_dependencies()
    else:
        run_all_tests()