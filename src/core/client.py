"""
Perplexity AI Wrapper - Synchronous Client
File: src/core/client.py
"""
import requests
import json
import time
import uuid
from typing import Dict, List, Optional, Generator, Union
from .models import (
    SearchMode, AIModel, SourceType, SearchConfig, SearchResponse,
    Conversation, validate_model_compatibility,
    PerplexityException, AuthenticationError, RateLimitError,
    InvalidParameterError, NetworkError
)


class PerplexityClient:
    """
    Main synchronous client for Perplexity.ai
    
    Usage:
        client = PerplexityClient(cookies={'session': 'your_token'})
        response = client.search("What is quantum computing?")
        print(response.answer)
    """
    
    def __init__(
        self,
        cookies: Optional[Dict[str, str]] = None,
        base_url: str = "https://www.perplexity.ai",
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: Optional[str] = None
    ):
        """
        Initialize Perplexity client
        
        Args:
            cookies: Authentication cookies
            base_url: Base URL for Perplexity API
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            user_agent: Custom user agent string
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation: Optional[Conversation] = None
        
        # Set realistic headers
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://www.perplexity.ai',
            'Referer': 'https://www.perplexity.ai/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        if cookies:
            self.session.cookies.update(cookies)
    
    def search(
        self,
        query: str,
        mode: Union[SearchMode, str] = SearchMode.AUTO,
        model: Optional[Union[AIModel, str]] = None,
        sources: Optional[List[Union[SourceType, str]]] = None,
        stream: bool = False,
        language: str = 'en-US',
        incognito: bool = False,
        files: Optional[Dict[str, str]] = None,
        use_conversation: bool = False,
        **kwargs
    ) -> Union[SearchResponse, Generator[Dict, None, None]]:
        """
        Execute search query
        
        Args:
            query: Search query string
            mode: Search mode (auto, pro, reasoning, deep_research)
            model: Specific AI model to use
            sources: Source types (web, scholar, social)
            stream: Whether to stream response
            language: Response language code
            incognito: Use incognito mode
            files: Dictionary of files to upload
            use_conversation: Continue current conversation
            **kwargs: Additional parameters
        
        Returns:
            SearchResponse object or Generator for streaming
        
        Raises:
            InvalidParameterError: Invalid parameters
            AuthenticationError: Authentication failed
            RateLimitError: Rate limit exceeded
            NetworkError: Network/connection error
        """
        
        # Convert string enums to proper types
        if isinstance(mode, str):
            mode = SearchMode(mode)
        if isinstance(model, str):
            model = AIModel(model)
        if sources and isinstance(sources[0], str):
            sources = [SourceType(s) for s in sources]
        
        # Validate parameters
        self._validate_search_params(mode, model)
        
        # Build configuration
        config = SearchConfig(
            query=query,
            mode=mode,
            model=model,
            sources=sources or [SourceType.WEB],
            language=language,
            stream=stream,
            incognito=incognito,
            files=files,
            **kwargs
        )
        
        # Add conversation context if enabled
        if use_conversation and self.current_conversation:
            config.follow_up_context = {
                'conversation_id': self.current_conversation.conversation_id,
                'context': self.current_conversation.get_context()
            }
        
        # Execute search
        try:
            if stream:
                return self._stream_search(config)
            else:
                return self._direct_search(config)
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Connection failed")
        except Exception as e:
            raise PerplexityException(f"Search failed: {str(e)}")
    
    def _validate_search_params(
        self,
        mode: SearchMode,
        model: Optional[AIModel]
    ) -> None:
        """Validate search parameters"""
        if not validate_model_compatibility(mode, model):
            raise InvalidParameterError(
                f"Model {model.value if model else 'None'} not compatible with mode {mode.value}"
            )
    
    def _direct_search(self, config: SearchConfig) -> SearchResponse:
        """Execute direct (non-streaming) search"""
        payload = config.to_payload()
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/search",
                    json=payload,
                    timeout=self.timeout
                )
                
                return self._handle_response(response, config.query)
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise NetworkError(f"Max retries exceeded: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _stream_search(self, config: SearchConfig) -> Generator[Dict, None, None]:
        """Execute streaming search"""
        payload = config.to_payload()
        
        response = self.session.post(
            f"{self.base_url}/api/search/stream",
            json=payload,
            stream=True,
            timeout=self.timeout * 2  # Longer timeout for streaming
        )
        
        if response.status_code != 200:
            self._handle_error_response(response)
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    yield data
                except json.JSONDecodeError:
                    continue
    
    def _handle_response(self, response: requests.Response, query: str) -> SearchResponse:
        """Handle API response"""
        if response.status_code == 200:
            data = response.json()
            return self._parse_response(data, query)
        else:
            self._handle_error_response(response)
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses"""
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed - invalid cookies")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded - too many requests")
        elif response.status_code == 400:
            raise InvalidParameterError(f"Invalid request: {response.text}")
        else:
            raise PerplexityException(
                f"Request failed: {response.status_code} - {response.text}"
            )
    
    def _parse_response(self, data: Dict, query: str) -> SearchResponse:
        """Parse API response into SearchResponse object"""
        response = SearchResponse(
            query=query,
            answer=data.get('answer', ''),
            sources=data.get('sources', []),
            related_questions=data.get('related_questions', []),
            mode=data.get('mode', 'auto'),
            model=data.get('model'),
            conversation_id=data.get('conversation_id'),
            tokens_used=data.get('tokens_used'),
            raw_response=data
        )
        
        # Update conversation if exists
        if self.current_conversation and response.conversation_id:
            self.current_conversation.add_message('user', query)
            self.current_conversation.add_message('assistant', response.answer, response.sources)
        
        return response
    
    def start_conversation(self) -> str:
        """Start a new conversation thread"""
        conversation_id = str(uuid.uuid4())
        self.current_conversation = Conversation(conversation_id=conversation_id)
        self.conversations[conversation_id] = self.current_conversation
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def set_conversation(self, conversation_id: str) -> bool:
        """Set active conversation"""
        if conversation_id in self.conversations:
            self.current_conversation = self.conversations[conversation_id]
            return True
        return False
    
    def clear_conversation(self) -> None:
        """Clear current conversation"""
        self.current_conversation = None
    
    def export_conversation(
        self,
        conversation_id: Optional[str] = None,
        format: str = 'json'
    ) -> str:
        """
        Export conversation in specified format
        
        Args:
            conversation_id: ID of conversation to export (current if None)
            format: Export format ('json', 'text', 'markdown')
        
        Returns:
            Formatted conversation string
        """
        conv = self.conversations.get(conversation_id) if conversation_id else self.current_conversation
        
        if not conv:
            return ""
        
        if format == 'json':
            return json.dumps({
                'conversation_id': conv.conversation_id,
                'created_at': conv.created_at.isoformat(),
                'messages': [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat(),
                        'sources': msg.sources
                    }
                    for msg in conv.messages
                ]
            }, indent=2)
        
        elif format == 'text':
            lines = []
            for msg in conv.messages:
                prefix = "Q:" if msg.role == 'user' else "A:"
                lines.append(f"{prefix} {msg.content}\n")
            return '\n'.join(lines)
        
        elif format == 'markdown':
            lines = [f"# Conversation: {conv.conversation_id}\n"]
            for msg in conv.messages:
                if msg.role == 'user':
                    lines.append(f"## Question\n{msg.content}\n")
                else:
                    lines.append(f"## Answer\n{msg.content}\n")
                    if msg.sources:
                        lines.append("### Sources")
                        for idx, src in enumerate(msg.sources, 1):
                            lines.append(f"{idx}. [{src.get('title', 'Source')}]({src.get('url', '#')})")
                        lines.append("")
            return '\n'.join(lines)
        
        return ""
    
    def get_cookies(self) -> Dict[str, str]:
        """Get current session cookies"""
        return dict(self.session.cookies)
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """Update session cookies"""
        self.session.cookies.update(cookies)
    
    def close(self) -> None:
        """Close session and cleanup"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()