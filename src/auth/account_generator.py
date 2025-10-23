"""
Perplexity AI Wrapper - Account Generator
File: src/auth/account_generator.py
"""
import requests
import json
import time
import random
import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from .cookie_manager import CookieManager
from ..core.models import AccountCredentials


class EmailnatorClient:
    """
    Client for Emailnator temporary email service
    """
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        Initialize Emailnator client
        
        Args:
            cookies: Emailnator session cookies
        """
        self.base_url = "https://www.emailnator.com"
        self.session = requests.Session()
        
        if cookies:
            self.session.cookies.update(cookies)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Origin': 'https://www.emailnator.com',
            'Referer': 'https://www.emailnator.com/'
        })
    
    def generate_email(self, domains: List[str] = None) -> str:
        """
        Generate temporary email address
        
        Args:
            domains: List of domain options
        
        Returns:
            Generated email address
        """
        if domains is None:
            domains = ["plusGmail", "dotGmail", "googleEmail"]
        
        payload = {"email": domains}
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate-email",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                emails = data.get('email', [])
                
                if emails:
                    email = emails[0]
                    print(f"✓ Generated email: {email}")
                    return email
                else:
                    raise Exception("No email generated")
            else:
                raise Exception(f"Email generation failed: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Failed to generate email: {str(e)}")
    
    def get_messages(self, email: str) -> List[Dict]:
        """
        Retrieve messages for email address
        
        Args:
            email: Email address
        
        Returns:
            List of message dictionaries
        """
        try:
            response = self.session.post(
                f"{self.base_url}/message-list",
                json={"email": email}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('messageData', [])
            
            return []
            
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            return []
    
    def get_message_content(self, message_id: str) -> Optional[str]:
        """
        Get full message content
        
        Args:
            message_id: Message ID
        
        Returns:
            Message content HTML/text
        """
        try:
            response = self.session.post(
                f"{self.base_url}/message-content",
                json={"messageID": message_id}
            )
            
            if response.status_code == 200:
                return response.text
            
            return None
            
        except Exception as e:
            print(f"Error fetching message content: {str(e)}")
            return None
    
    def wait_for_email(
        self,
        email: str,
        subject_contains: str,
        timeout: int = 120,
        check_interval: int = 5
    ) -> Optional[Dict]:
        """
        Wait for specific email to arrive
        
        Args:
            email: Email address
            subject_contains: String to search in subject
            timeout: Maximum wait time in seconds
            check_interval: Time between checks
        
        Returns:
            Message dictionary or None
        """
        print(f"Waiting for email with subject containing: {subject_contains}")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages(email)
            
            for message in messages:
                subject = message.get('subject', '').lower()
                if subject_contains.lower() in subject:
                    print(f"✓ Email received: {message.get('subject')}")
                    return message
            
            time.sleep(check_interval)
            print(".", end="", flush=True)
        
        print("\n✗ Timeout waiting for email")
        return None


class AccountGenerator:
    """
    Generate Perplexity accounts automatically
    """
    
    def __init__(
        self,
        emailnator_cookies: Optional[Dict[str, str]] = None,
        cookie_manager: Optional[CookieManager] = None
    ):
        """
        Initialize account generator
        
        Args:
            emailnator_cookies: Emailnator session cookies
            cookie_manager: CookieManager for storing accounts
        """
        self.emailnator = EmailnatorClient(emailnator_cookies)
        self.cookie_manager = cookie_manager or CookieManager()
        self.perplexity_session = requests.Session()
        
        self.perplexity_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://www.perplexity.ai',
            'Referer': 'https://www.perplexity.ai/'
        })
    
    def create_account(
        self,
        save_profile: bool = True,
        profile_name: Optional[str] = None
    ) -> AccountCredentials:
        """
        Create complete Perplexity account
        
        Args:
            save_profile: Save account to cookie manager
            profile_name: Custom profile name
        
        Returns:
            AccountCredentials object
        """
        print("\n=== Starting Account Creation ===")
        
        # Step 1: Generate email
        print("\n[1/4] Generating temporary email...")
        email = self.emailnator.generate_email()
        
        # Step 2: Sign up on Perplexity
        print("\n[2/4] Signing up on Perplexity...")
        signup_result = self._signup_perplexity(email)
        
        if not signup_result:
            raise Exception("Signup failed")
        
        # Step 3: Wait for verification email
        print("\n[3/4] Waiting for verification email...")
        verification_email = self.emailnator.wait_for_email(
            email=email,
            subject_contains="verify",
            timeout=120
        )
        
        if not verification_email:
            raise Exception("Verification email not received")
        
        # Step 4: Extract and verify
        print("\n[4/4] Completing verification...")
        verification_link = self._extract_verification_link(verification_email)
        
        if not verification_link:
            raise Exception("Could not extract verification link")
        
        account_cookies = self._complete_verification(verification_link)
        
        # Create credentials
        credentials = AccountCredentials(
            email=email,
            cookies=account_cookies,
            status='active',
            metadata={'signup_method': 'emailnator'}
        )
        
        # Save if requested
        if save_profile:
            profile = profile_name or f"auto_{email.split('@')[0]}"
            self.cookie_manager.save_cookies(account_cookies, profile)
            print(f"\n✓ Account saved as profile: {profile}")
        
        print("\n=== Account Creation Complete ===")
        return credentials
    
    def _signup_perplexity(self, email: str) -> bool:
        """
        Initiate Perplexity signup
        
        Args:
            email: Email address
        
        Returns:
            True if successful
        """
        try:
            # This is a placeholder - actual implementation needs real API endpoint
            payload = {
                "email": email,
                "action": "signup"
            }
            
            response = self.perplexity_session.post(
                "https://www.perplexity.ai/api/auth/signup",
                json=payload,
                timeout=30
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Signup error: {str(e)}")
            return False
    
    def _extract_verification_link(self, message: Dict) -> Optional[str]:
        """
        Extract verification link from email
        
        Args:
            message: Message dictionary
        
        Returns:
            Verification URL or None
        """
        message_id = message.get('messageID')
        if not message_id:
            return None
        
        content = self.emailnator.get_message_content(message_id)
        if not content:
            return None
        
        # Parse HTML to find verification link
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for links containing verification patterns
        patterns = [
            r'https://www\.perplexity\.ai/verify\?token=',
            r'https://www\.perplexity\.ai/api/auth/verify',
            r'https://www\.perplexity\.ai/.*verify.*'
        ]
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            for pattern in patterns:
                if re.search(pattern, href):
                    print(f"✓ Found verification link")
                    return href
        
        # Fallback: regex search in raw content
        for pattern in patterns:
            match = re.search(pattern + r'[^\s<>"]+', content)
            if match:
                return match.group(0)
        
        return None
    
    def _complete_verification(self, verification_link: str) -> Dict[str, str]:
        """
        Complete email verification
        
        Args:
            verification_link: Verification URL
        
        Returns:
            Account cookies
        """
        try:
            response = self.perplexity_session.get(
                verification_link,
                allow_redirects=True,
                timeout=30
            )
            
            if response.status_code == 200:
                cookies = dict(self.perplexity_session.cookies)
                print(f"✓ Verification complete - {len(cookies)} cookies obtained")
                return cookies
            else:
                raise Exception(f"Verification failed: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Verification error: {str(e)}")
    
    def create_multiple_accounts(
        self,
        count: int,
        delay: int = 30
    ) -> List[AccountCredentials]:
        """
        Create multiple accounts
        
        Args:
            count: Number of accounts to create
            delay: Delay between creations in seconds
        
        Returns:
            List of AccountCredentials
        """
        accounts = []
        
        for i in range(count):
            print(f"\n\n{'='*60}")
            print(f"Creating account {i+1}/{count}")
            print('='*60)
            
            try:
                account = self.create_account(
                    save_profile=True,
                    profile_name=f"batch_{i+1}"
                )
                accounts.append(account)
                
                if i < count - 1:
                    print(f"\nWaiting {delay} seconds before next account...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"✗ Failed to create account {i+1}: {str(e)}")
                continue
        
        print(f"\n\n✓ Successfully created {len(accounts)}/{count} accounts")
        return accounts