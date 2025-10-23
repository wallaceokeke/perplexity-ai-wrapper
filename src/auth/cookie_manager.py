"""
Perplexity AI Wrapper - Cookie Management
File: src/auth/cookie_manager.py
"""
import json
import os
import sqlite3
import base64
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime


class CookieManager:
    """
    Manage cookies for Perplexity authentication
    Supports extraction from various browsers
    """
    
    def __init__(self, storage_path: str = "cookies.json"):
        """
        Initialize cookie manager
        
        Args:
            storage_path: Path to store cookies
        """
        self.storage_path = storage_path
    
    def save_cookies(self, cookies: Dict[str, str], name: str = "default") -> None:
        """
        Save cookies to storage
        
        Args:
            cookies: Cookie dictionary
            name: Profile name
        """
        storage = self._load_storage()
        storage[name] = {
            'cookies': cookies,
            'timestamp': datetime.now().isoformat(),
            'active': True
        }
        self._save_storage(storage)
    
    def load_cookies(self, name: str = "default") -> Optional[Dict[str, str]]:
        """
        Load cookies from storage
        
        Args:
            name: Profile name
        
        Returns:
            Cookie dictionary or None
        """
        storage = self._load_storage()
        profile = storage.get(name)
        return profile['cookies'] if profile else None
    
    def list_profiles(self) -> List[str]:
        """List all saved cookie profiles"""
        storage = self._load_storage()
        return list(storage.keys())
    
    def delete_profile(self, name: str) -> bool:
        """Delete a cookie profile"""
        storage = self._load_storage()
        if name in storage:
            del storage[name]
            self._save_storage(storage)
            return True
        return False
    
    def _load_storage(self) -> Dict:
        """Load storage file"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_storage(self, storage: Dict) -> None:
        """Save storage file"""
        with open(self.storage_path, 'w') as f:
            json.dump(storage, f, indent=2)
    
    @staticmethod
    def extract_from_chrome(profile_path: Optional[str] = None) -> Dict[str, str]:
        """
        Extract Perplexity cookies from Chrome
        
        Args:
            profile_path: Custom Chrome profile path
        
        Returns:
            Cookie dictionary
        """
        try:
            import browser_cookie3
            
            # Get Chrome cookies for perplexity.ai
            cookies = browser_cookie3.chrome(domain_name='perplexity.ai')
            
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie.name] = cookie.value
            
            return cookie_dict
        except ImportError:
            raise ImportError("browser_cookie3 not installed. Run: pip install browser-cookie3")
        except Exception as e:
            raise Exception(f"Failed to extract Chrome cookies: {str(e)}")
    
    @staticmethod
    def extract_from_firefox(profile_path: Optional[str] = None) -> Dict[str, str]:
        """
        Extract Perplexity cookies from Firefox
        
        Args:
            profile_path: Custom Firefox profile path
        
        Returns:
            Cookie dictionary
        """
        try:
            import browser_cookie3
            
            cookies = browser_cookie3.firefox(domain_name='perplexity.ai')
            
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie.name] = cookie.value
            
            return cookie_dict
        except ImportError:
            raise ImportError("browser_cookie3 not installed. Run: pip install browser-cookie3")
        except Exception as e:
            raise Exception(f"Failed to extract Firefox cookies: {str(e)}")
    
    @staticmethod
    def extract_from_edge(profile_path: Optional[str] = None) -> Dict[str, str]:
        """
        Extract Perplexity cookies from Edge
        
        Args:
            profile_path: Custom Edge profile path
        
        Returns:
            Cookie dictionary
        """
        try:
            import browser_cookie3
            
            cookies = browser_cookie3.edge(domain_name='perplexity.ai')
            
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie.name] = cookie.value
            
            return cookie_dict
        except ImportError:
            raise ImportError("browser_cookie3 not installed. Run: pip install browser-cookie3")
        except Exception as e:
            raise Exception(f"Failed to extract Edge cookies: {str(e)}")
    
    @staticmethod
    def extract_from_json(file_path: str) -> Dict[str, str]:
        """
        Extract cookies from JSON file (from browser extensions)
        
        Args:
            file_path: Path to JSON cookie file
        
        Returns:
            Cookie dictionary
        """
        with open(file_path, 'r') as f:
            cookies_list = json.load(f)
        
        cookie_dict = {}
        for cookie in cookies_list:
            if 'perplexity.ai' in cookie.get('domain', ''):
                cookie_dict[cookie['name']] = cookie['value']
        
        return cookie_dict
    
    @staticmethod
    def validate_cookies(cookies: Dict[str, str]) -> bool:
        """
        Validate if cookies are valid for Perplexity
        
        Args:
            cookies: Cookie dictionary
        
        Returns:
            True if valid, False otherwise
        """
        # Check for essential cookies (adjust based on actual Perplexity requirements)
        essential_cookies = ['__Secure-next-auth.session-token']  # Example
        
        for cookie_name in essential_cookies:
            if cookie_name not in cookies:
                return False
        
        return True
    
    def auto_extract(self, browser: str = "chrome") -> Dict[str, str]:
        """
        Automatically extract cookies from specified browser
        
        Args:
            browser: Browser name (chrome, firefox, edge)
        
        Returns:
            Cookie dictionary
        """
        browser_methods = {
            'chrome': self.extract_from_chrome,
            'firefox': self.extract_from_firefox,
            'edge': self.extract_from_edge
        }
        
        if browser.lower() not in browser_methods:
            raise ValueError(f"Unsupported browser: {browser}")
        
        return browser_methods[browser.lower()]()


class SessionManager:
    """
    Manage multiple Perplexity sessions
    """
    
    def __init__(self, cookie_manager: CookieManager):
        """
        Initialize session manager
        
        Args:
            cookie_manager: CookieManager instance
        """
        self.cookie_manager = cookie_manager
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(
        self,
        name: str,
        cookies: Optional[Dict[str, str]] = None,
        profile: Optional[str] = None
    ) -> str:
        """
        Create a new session
        
        Args:
            name: Session name
            cookies: Cookie dictionary
            profile: Load cookies from profile
        
        Returns:
            Session ID
        """
        if not cookies and profile:
            cookies = self.cookie_manager.load_cookies(profile)
        
        if not cookies:
            raise ValueError("No cookies provided")
        
        session_id = f"session_{name}_{datetime.now().timestamp()}"
        self.sessions[session_id] = {
            'name': name,
            'cookies': cookies,
            'created_at': datetime.now(),
            'active': True
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[str]:
        """List all active sessions"""
        return [sid for sid, sess in self.sessions.items() if sess['active']]
    
    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['active'] = False
            return True
        return False
    
    def refresh_session(self, session_id: str, cookies: Dict[str, str]) -> bool:
        """Refresh session cookies"""
        if session_id in self.sessions:
            self.sessions[session_id]['cookies'] = cookies
            self.sessions[session_id]['updated_at'] = datetime.now()
            return True
        return False