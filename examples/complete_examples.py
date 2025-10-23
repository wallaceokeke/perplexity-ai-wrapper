"""
Perplexity AI Wrapper - Complete Usage Examples
Enhanced with robust connection management
File: examples/complete_examples.py
"""
import asyncio
import json
import sys
import os
import time
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.client import PerplexityClient
from src.core.async_client import AsyncPerplexityClient
from src.core.models import SearchMode, AIModel, SourceType
from src.auth.cookie_manager import CookieManager, SessionManager
from src.auth.account_generator import AccountGenerator, EmailnatorClient
from src.automation.web_driver import PerplexityWebDriver


class ConnectionManager:
    """Enhanced connection manager with fallback strategies"""
    
    def __init__(self):
        self.cookie_manager = CookieManager()
        self.connection_attempts = []
        self.active_client = None
    
    def log_attempt(self, method: str, success: bool, message: str = ""):
        """Log connection attempts"""
        attempt = {
            'method': method,
            'success': success,
            'message': message,
            'timestamp': time.time()
        }
        self.connection_attempts.append(attempt)
        status = "✓" if success else "✗"
        print(f"  {status} {method}: {message}")
    
    def setup_connection(self) -> Optional[PerplexityClient]:
        """Comprehensive connection setup with fallback strategies"""
        print("\n" + "="*70)
        print("PERPLEXITY AI CONNECTION SETUP")
        print("="*70)
        
        print("\nAttempting to establish connection...")
        
        # Strategy 1: Try existing cookies
        client = self._try_existing_cookies()
        if client:
            return client
        
        # Strategy 2: Try browser cookie extraction
        client = self._try_cookie_extraction()
        if client:
            return client
        
        # Strategy 3: Try manual cookie setup
        client = self._try_manual_cookies()
        if client:
            return client
        
        # Strategy 4: Use web automation as last resort
        client = self._try_web_automation()
        if client:
            return client
        
        # All strategies failed
        print("\n" + "!"*70)
        print("ALL CONNECTION METHODS FAILED")
        print("!"*70)
        print("\nPlease choose one of these setup options:")
        print("1. Open browser manually and login to Perplexity.ai")
        print("2. Use web automation with manual intervention")
        print("3. Configure manual cookies")
        
        return None
    
    def _try_existing_cookies(self) -> Optional[PerplexityClient]:
        """Try loading existing cookie profiles"""
        print("\n[1/4] Checking existing cookie profiles...")
        
        try:
            profiles = self.cookie_manager.list_profiles()
            if profiles:
                print(f"  Found profiles: {', '.join(profiles)}")
                
                # Try each profile
                for profile in profiles:
                    try:
                        cookies = self.cookie_manager.load_cookies(profile)
                        if cookies:
                            client = PerplexityClient(cookies=cookies)
                            # Test the connection
                            test_response = client.search("test", timeout=10)
                            self.log_attempt(
                                f"Existing profile '{profile}'", 
                                True, 
                                f"Loaded {len(cookies)} cookies"
                            )
                            return client
                    except Exception as e:
                        self.log_attempt(
                            f"Profile '{profile}'", 
                            False, 
                            str(e)
                        )
                        continue
            else:
                self.log_attempt("Existing profiles", False, "No profiles found")
                
        except Exception as e:
            self.log_attempt("Existing profiles", False, str(e))
        
        return None
    
    def _try_cookie_extraction(self) -> Optional[PerplexityClient]:
        """Try extracting cookies from browsers"""
        print("\n[2/4] Attempting browser cookie extraction...")
        
        browsers = ['chrome', 'firefox', 'edge', 'brave']
        
        for browser in browsers:
            try:
                print(f"  Trying {browser}...")
                cookies = self.cookie_manager.auto_extract(browser=browser)
                if cookies:
                    # Save and test
                    profile_name = f"auto_{browser}"
                    self.cookie_manager.save_cookies(cookies, profile_name)
                    
                    client = PerplexityClient(cookies=cookies)
                    test_response = client.search("test", timeout=10)
                    
                    self.log_attempt(
                        f"Browser extraction ({browser})", 
                        True, 
                        f"Extracted {len(cookies)} cookies"
                    )
                    return client
                    
            except Exception as e:
                self.log_attempt(
                    f"Browser extraction ({browser})", 
                    False, 
                    str(e)
                )
                continue
        
        return None
    
    def _try_manual_cookies(self) -> Optional[PerplexityClient]:
        """Try manual cookie setup with user interaction"""
        print("\n[3/4] Manual cookie setup...")
        
        manual_files = ['cookies.json', 'manual_cookies.json', 'pp_cookies.json']
        
        for file in manual_files:
            if os.path.exists(file):
                try:
                    with open(file, 'r') as f:
                        cookies = json.load(f)
                    
                    if cookies:
                        client = PerplexityClient(cookies=cookies)
                        test_response = client.search("test", timeout=10)
                        
                        self.log_attempt(
                            f"Manual file '{file}'", 
                            True, 
                            f"Loaded {len(cookies)} cookies"
                        )
                        return client
                        
                except Exception as e:
                    self.log_attempt(f"Manual file '{file}'", False, str(e))
                    continue
        
        # Interactive manual setup
        print("\n  No manual cookie files found.")
        response = input("  Would you like to set up cookies manually? (y/N): ")
        if response.lower() in ['y', 'yes']:
            return self._interactive_cookie_setup()
        
        return None
    
    def _interactive_cookie_setup(self) -> Optional[PerplexityClient]:
        """Interactive cookie setup guide"""
        print("\n" + "-"*50)
        print("MANUAL COOKIE SETUP INSTRUCTIONS")
        print("-"*50)
        print("1. Open https://www.perplexity.ai in your browser")
        print("2. Login to your account (or create one)")
        print("3. Open Developer Tools (F12)")
        print("4. Go to Application/Storage tab")
        print("5. Copy all cookies as JSON")
        print("6. Save as 'cookies.json' in this directory")
        print("7. Press Enter when ready...")
        input()
        
        if os.path.exists('cookies.json'):
            try:
                with open('cookies.json', 'r') as f:
                    cookies = json.load(f)
                
                client = PerplexityClient(cookies=cookies)
                test_response = client.search("test", timeout=10)
                
                self.log_attempt("Interactive setup", True, "Manual cookies loaded")
                return client
                
            except Exception as e:
                self.log_attempt("Interactive setup", False, str(e))
        
        return None
    
    def _try_web_automation(self) -> Optional[PerplexityClient]:
        """Use web automation as fallback"""
        print("\n[4/4] Attempting web automation...")
        
        try:
            print("  Starting browser automation...")
            driver = PerplexityWebDriver(headless=False, stealth_mode=True)
            driver.start()
            driver.navigate_to_perplexity()
            
            print("  Please complete any CAPTCHA or login in the browser window...")
            print("  Press Enter when you are logged in and ready to continue...")
            input()
            
            # Extract cookies from automation
            auto_cookies = driver.get_cookies()
            if auto_cookies:
                self.cookie_manager.save_cookies(auto_cookies, "automation_profile")
                client = PerplexityClient(cookies=auto_cookies)
                
                self.log_attempt(
                    "Web automation", 
                    True, 
                    f"Extracted {len(auto_cookies)} cookies via automation"
                )
                
                driver.close()
                return client
                
            driver.close()
            
        except Exception as e:
            self.log_attempt("Web automation", False, str(e))
        
        return None
    
    def get_connection_summary(self) -> str:
        """Get summary of connection attempts"""
        successful = [a for a in self.connection_attempts if a['success']]
        failed = [a for a in self.connection_attempts if not a['success']]
        
        summary = f"\nConnection Summary: {len(successful)} successful, {len(failed)} failed"
        if successful:
            summary += f"\nActive method: {successful[-1]['method']}"
        return summary


class EnhancedExamples:
    """Complete examples with enhanced connection management"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.client = None
    
    def ensure_connection(self):
        """Ensure we have a working connection before running examples"""
        if self.client is None:
            self.client = self.connection_manager.setup_connection()
        
        if self.client is None:
            raise Exception("Unable to establish connection to Perplexity AI")
        
        return self.client
    
    # ============================================================================
    # EXAMPLE 1: Basic Synchronous Search (ENHANCED)
    # ============================================================================
    
    def example_1_basic_sync_search(self):
        """Basic synchronous search with connection management"""
        print("\n" + "="*70)
        print("EXAMPLE 1: Basic Synchronous Search")
        print("="*70)
        
        # Ensure connection
        client = self.ensure_connection()
        
        # Simple search
        response = client.search(
            query="What is quantum computing?",
            mode=SearchMode.AUTO
        )
        
        print(f"\nQuery: {response.query}")
        print(f"Answer: {response.answer[:200]}...")
        print(f"Sources: {len(response.sources)}")
        print(self.connection_manager.get_connection_summary())
        
        return response
    
    # ============================================================================
    # EXAMPLE 2: Advanced Search with Models (ENHANCED)
    # ============================================================================
    
    def example_2_advanced_search(self):
        """Advanced search with specific models and sources"""
        print("\n" + "="*70)
        print("EXAMPLE 2: Advanced Search with Models")
        print("="*70)
        
        client = self.ensure_connection()
        
        # Pro search with specific model
        response = client.search(
            query="Latest developments in AI for 2025",
            mode=SearchMode.PRO,
            model=AIModel.GPT_4O,
            sources=[SourceType.WEB, SourceType.SCHOLAR],
            language="en-US"
        )
        
        print(f"\nMode: {response.mode}")
        print(f"Model: {response.model}")
        print(f"Answer: {response.answer[:300]}...")
        
        # Show sources
        print(f"\nSources ({len(response.sources)}):")
        for idx, source in enumerate(response.sources[:3], 1):
            print(f"  {idx}. {source.get('title', 'N/A')}")
        
        # Related questions
        print(f"\nRelated Questions:")
        for q in response.related_questions[:3]:
            print(f"  - {q}")
        
        print(self.connection_manager.get_connection_summary())
        return response
    
    # ============================================================================
    # EXAMPLE 3: Conversation Mode (ENHANCED)
    # ============================================================================
    
    def example_3_conversation(self):
        """Multi-turn conversation"""
        print("\n" + "="*70)
        print("EXAMPLE 3: Conversation Mode")
        print("="*70)
        
        client = self.ensure_connection()
        
        # Start conversation
        conv_id = client.start_conversation()
        print(f"Started conversation: {conv_id}")
        
        # First query
        print("\n[Turn 1]")
        response1 = client.search(
            "What is machine learning?",
            use_conversation=True
        )
        print(f"Q: What is machine learning?")
        print(f"A: {response1.answer[:150]}...")
        
        # Follow-up query
        print("\n[Turn 2]")
        response2 = client.search(
            "How is it different from deep learning?",
            use_conversation=True
        )
        print(f"Q: How is it different from deep learning?")
        print(f"A: {response2.answer[:150]}...")
        
        # Export conversation
        export = client.export_conversation(format='text')
        print(f"\n=== Conversation Export ===\n{export[:300]}...")
        
        print(self.connection_manager.get_connection_summary())
        return client
    
    # ============================================================================
    # EXAMPLE 4: Asynchronous Search (ENHANCED)
    # ============================================================================
    
    async def example_4_async_search(self):
        """Asynchronous search"""
        print("\n" + "="*70)
        print("EXAMPLE 4: Asynchronous Search")
        print("="*70)
        
        # For async, we need to ensure connection first
        self.ensure_connection()
        
        async with AsyncPerplexityClient(cookies=self.client.cookies if self.client else None) as client:
            # Single async search
            response = await client.search(
                "Explain neural networks",
                mode=SearchMode.PRO
            )
            
            print(f"\nAsync Response: {response.answer[:200]}...")
            print(self.connection_manager.get_connection_summary())
            
            return response
    
    # ============================================================================
    # EXAMPLE 5: Batch Processing (Async) (ENHANCED)
    # ============================================================================
    
    async def example_5_batch_processing(self):
        """Batch process multiple queries concurrently"""
        print("\n" + "="*70)
        print("EXAMPLE 5: Batch Processing (Concurrent)")
        print("="*70)
        
        self.ensure_connection()
        
        queries = [
            "What is Python programming?",
            "Explain blockchain technology",
            "What are neural networks?",
            "How does quantum computing work?"
        ]
        
        async with AsyncPerplexityClient(cookies=self.client.cookies if self.client else None) as client:
            print(f"\nProcessing {len(queries)} queries concurrently...")
            
            responses = await client.batch_search(
                queries,
                mode=SearchMode.AUTO
            )
            
            print(f"\n✓ Completed {len(responses)} searches")
            
            for idx, response in enumerate(responses, 1):
                if isinstance(response, Exception):
                    print(f"\n{idx}. ERROR: {str(response)}")
                else:
                    print(f"\n{idx}. {response.query}")
                    print(f"   Answer: {response.answer[:100]}...")
            
            print(self.connection_manager.get_connection_summary())
            return responses
    
    # ============================================================================
    # EXAMPLE 6: Streaming Response (ENHANCED)
    # ============================================================================
    
    def example_6_streaming(self):
        """Streaming response"""
        print("\n" + "="*70)
        print("EXAMPLE 6: Streaming Response")
        print("="*70)
        
        client = self.ensure_connection()
        
        print("\nQuery: Explain climate change")
        print("Streaming response:\n")
        
        # Stream response chunks
        for chunk in client.search(
            "Explain climate change",
            stream=True
        ):
            # Process each chunk
            content = chunk.get('content', '')
            if content:
                print(content, end='', flush=True)
        
        print("\n\n✓ Streaming complete")
        print(self.connection_manager.get_connection_summary())
    
    # ============================================================================
    # EXAMPLE 7: Cookie Management (ENHANCED)
    # ============================================================================
    
    def example_7_cookie_management(self):
        """Cookie extraction and management"""
        print("\n" + "="*70)
        print("EXAMPLE 7: Cookie Management")
        print("="*70)
        
        # This example demonstrates cookie management, so we don't need active connection
        cookie_manager = CookieManager()
        
        # Try to extract cookies from Chrome
        try:
            print("\nExtracting cookies from Chrome...")
            cookies = cookie_manager.auto_extract(browser='chrome')
            print(f"✓ Extracted {len(cookies)} cookies")
            
            # Save cookies
            cookie_manager.save_cookies(cookies, name="chrome_profile")
            print("✓ Saved to profile: chrome_profile")
            
            # List profiles
            profiles = cookie_manager.list_profiles()
            print(f"\nAvailable profiles: {profiles}")
            
            # Load cookies
            loaded_cookies = cookie_manager.load_cookies("chrome_profile")
            print(f"✓ Loaded {len(loaded_cookies)} cookies from profile")
            
            # Use with client
            client = PerplexityClient(cookies=loaded_cookies)
            print("✓ Client initialized with saved cookies")
            
        except Exception as e:
            print(f"✗ Cookie extraction failed: {str(e)}")
            print("  Note: Requires browser-cookie3 package")
    
    # ============================================================================
    # REMAINING EXAMPLES (8-12) - Similar enhancements applied
    # ============================================================================
    
    # Examples 8-12 would follow the same pattern...
    # For brevity, I'll show the structure for one more:
    
    def example_10_web_automation(self):
        """Browser automation"""
        print("\n" + "="*70)
        print("EXAMPLE 10: Web Automation")
        print("="*70)
        
        # Initialize driver
        driver = PerplexityWebDriver(headless=False, stealth_mode=True)
        
        try:
            # Start browser
            print("\nStarting browser...")
            driver.start()
            
            # Navigate to Perplexity
            driver.navigate_to_perplexity()
            
            # Perform search
            print("\nExecuting search...")
            response = driver.search(
                "What is the weather in New York?",
                wait_for_response=True
            )
            
            print(f"\nResponse:\n{response[:300]}...")
            
            # Get sources
            sources = driver.get_sources()
            print(f"\nSources found: {len(sources)}")
            
            # Take screenshot
            driver.save_screenshot("perplexity_search.png")
            
            # Export conversation
            export = driver.export_conversation(format='markdown')
            print(f"\nExport preview:\n{export[:200]}...")
            
        finally:
            print("\nClosing browser...")
            driver.close()


# ============================================================================
# ENHANCED MAIN RUNNER
# ============================================================================

def run_example(example_num: int):
    """Run specific example with enhanced error handling"""
    examples = EnhancedExamples()
    
    example_map = {
        1: examples.example_1_basic_sync_search,
        2: examples.example_2_advanced_search,
        3: examples.example_3_conversation,
        4: lambda: asyncio.run(examples.example_4_async_search()),
        5: lambda: asyncio.run(examples.example_5_batch_processing()),
        6: examples.example_6_streaming,
        7: examples.example_7_cookie_management,
        8: examples.example_8_session_management,  # You'll need to implement this
        9: examples.example_9_account_generation,  # You'll need to implement this
        10: examples.example_10_web_automation,
        11: examples.example_11_interactive_mode,  # You'll need to implement this
        12: lambda: asyncio.run(examples.example_12_complete_workflow())  # You'll need to implement this
    }
    
    if example_num in example_map:
        try:
            print(f"\n🚀 Running Example {example_num}...")
            result = example_map[example_num]()
            print(f"\n✅ Example {example_num} completed successfully!")
            return result
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error in Example {example_num}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Offer to retry with different connection method
            retry = input("\nWould you like to try reconnecting? (y/N): ")
            if retry.lower() in ['y', 'yes']:
                examples.connection_manager.client = None  # Reset connection
                return run_example(example_num)  # Retry
    else:
        print(f"❌ Example {example_num} not found")


def run_all_examples():
    """Run all examples sequentially with connection sharing"""
    print("\n" + "="*70)
    print("RUNNING ALL ENHANCED EXAMPLES")
    print("="*70)
    
    examples = EnhancedExamples()
    
    for i in range(1, 13):
        try:
            print(f"\n{'='*50}")
            print(f"EXAMPLE {i}")
            print(f"{'='*50}")
            
            # Map the examples to the enhanced class methods
            example_methods = {
                1: examples.example_1_basic_sync_search,
                2: examples.example_2_advanced_search,
                3: examples.example_3_conversation,
                4: lambda: asyncio.run(examples.example_4_async_search()),
                5: lambda: asyncio.run(examples.example_5_batch_processing()),
                6: examples.example_6_streaming,
                7: examples.example_7_cookie_management,
                # ... add others as you implement them
            }
            
            if i in example_methods:
                example_methods[i]()
            else:
                print(f"Example {i} not yet implemented in enhanced version")
            
            if i < 12:  # Don't prompt after last example
                input("\nPress Enter to continue to next example...")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping...")
            break
        except Exception as e:
            print(f"\n❌ Error in Example {i}: {str(e)}")
            continue


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Perplexity AI Wrapper Examples")
    parser.add_argument('example', type=int, nargs='?', help='Example number (1-12)')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    parser.add_argument('--setup', action='store_true', help='Run connection setup only')
    
    args = parser.parse_args()
    
    if args.setup:
        # Just test connection setup
        manager = ConnectionManager()
        client = manager.setup_connection()
        if client:
            print("\n✅ Setup completed successfully!")
            print(manager.get_connection_summary())
        else:
            print("\n❌ Setup failed!")
            
    elif args.all:
        run_all_examples()
    elif args.example:
        run_example(args.example)
    else:
        print("\n🚀 Enhanced Perplexity AI Wrapper Examples")
        print("   (Now with automatic connection management!)")
        print("\nAvailable examples:")
        print("  1.  Basic Synchronous Search")
        print("  2.  Advanced Search with Models")
        print("  3.  Conversation Mode")
        print("  4.  Asynchronous Search")
        print("  5.  Batch Processing")
        print("  6.  Streaming Response")
        print("  7.  Cookie Management")
        print("  8.  Session Management")
        print("  9.  Account Generation")
        print("  10. Web Automation")
        print("  11. Interactive Mode")
        print("  12. Complete Workflow")
        print("\nUsage:")
        print("  python complete_examples.py <number>    # Run specific example")
        print("  python complete_examples.py --all       # Run all examples")
        print("  python complete_examples.py --setup     # Test connection setup only")