"""
Perplexity AI Wrapper - Web Automation Driver
File: src/automation/web_driver.py
"""
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from playwright.async_api import async_playwright
import json
import time
from typing import Optional, Dict, List, Callable
from pathlib import Path


class PerplexityWebDriver:
    """
    Browser automation for Perplexity using Playwright
    """
    
    def __init__(
        self,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        stealth_mode: bool = True
    ):
        """
        Initialize web driver
        
        Args:
            headless: Run browser in headless mode
            user_data_dir: Chrome user data directory
            stealth_mode: Enable stealth features
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.stealth_mode = stealth_mode
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def start(self, port: Optional[int] = None) -> None:
        """
        Start browser session
        
        Args:
            port: Remote debugging port (connects to existing Chrome)
        """
        self.playwright = sync_playwright().start()
        
        if port:
            # Connect to existing Chrome instance
            self.browser = self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{port}"
            )
            self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
        else:
            # Launch new browser
            launch_options = {
                'headless': self.headless,
                'args': [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            }
            
            if self.user_data_dir:
                launch_options['user_data_dir'] = self.user_data_dir
            
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir or '',
                **launch_options
            ) if self.user_data_dir else self.playwright.chromium.launch(**launch_options)
            
            if not self.user_data_dir:
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
        
        self.page = self.context.new_page() if self.context else self.browser.new_page()
        
        if self.stealth_mode:
            self._apply_stealth()
        
        print("✓ Browser started")
    
    def _apply_stealth(self) -> None:
        """Apply stealth techniques to avoid detection"""
        if not self.page:
            return
        
        # Remove webdriver property
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Chrome runtime
            window.chrome = {
                runtime: {},
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    def navigate_to_perplexity(self) -> None:
        """Navigate to Perplexity homepage"""
        if not self.page:
            raise Exception("Browser not started")
        
        print("Navigating to Perplexity...")
        self.page.goto("https://www.perplexity.ai", wait_until="domcontentloaded")
        time.sleep(2)  # Let page settle
        print("✓ Loaded Perplexity")
    
    def search(
        self,
        query: str,
        wait_for_response: bool = True,
        timeout: int = 60000
    ) -> str:
        """
        Execute search via UI
        
        Args:
            query: Search query
            wait_for_response: Wait for AI response
            timeout: Timeout in milliseconds
        
        Returns:
            Response text
        """
        if not self.page:
            raise Exception("Browser not started")
        
        print(f"Searching: {query}")
        
        # Find and fill search box
        search_selectors = [
            'textarea[placeholder*="Ask"]',
            'textarea[placeholder*="Search"]',
            'input[type="text"]',
            'textarea'
        ]
        
        search_box = None
        for selector in search_selectors:
            try:
                search_box = self.page.wait_for_selector(selector, timeout=5000)
                if search_box:
                    break
            except:
                continue
        
        if not search_box:
            raise Exception("Could not find search input")
        
        # Enter query
        search_box.fill(query)
        search_box.press('Enter')
        
        if wait_for_response:
            # Wait for response to appear
            print("Waiting for response...")
            try:
                # Wait for response container
                self.page.wait_for_selector(
                    '[class*="answer"], [class*="response"], .prose',
                    timeout=timeout
                )
                time.sleep(2)  # Let response complete
                
                response_text = self.get_response_text()
                print(f"✓ Response received ({len(response_text)} chars)")
                return response_text
                
            except Exception as e:
                print(f"Timeout or error waiting for response: {e}")
                return ""