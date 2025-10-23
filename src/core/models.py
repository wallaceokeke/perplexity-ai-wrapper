"""
Perplexity AI Wrapper - Data Models and Enums
File: src/core/models.py
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


class SearchMode(Enum):
    """Available search modes in Perplexity"""
    AUTO = "auto"
    PRO = "pro"
    REASONING = "reasoning"
    DEEP_RESEARCH = "deep_research"


class AIModel(Enum):
    """Available AI models"""
    # Pro models
    SONAR = "sonar"
    GPT_4_5 = "gpt-4.5"
    GPT_4O = "gpt-4o"
    CLAUDE_3_7_SONNET = "claude-3.7-sonnet"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GROK_2 = "grok-2"
    
    # Reasoning models
    R1 = "r1"
    O3_MINI = "o3-mini"
    CLAUDE_REASONING = "claude-3.7-sonnet"


class SourceType(Enum):
    """Available source types"""
    WEB = "web"
    SCHOLAR = "scholar"
    SOCIAL = "social"
    REDDIT = "reddit"
    YOUTUBE = "youtube"


class ResponseFormat(Enum):
    """Response format types"""
    JSON = "json"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class SearchConfig:
    """Configuration for a search request"""
    query: str
    mode: SearchMode = SearchMode.AUTO
    model: Optional[AIModel] = None
    sources: List[SourceType] = field(default_factory=lambda: [SourceType.WEB])
    language: str = "en-US"
    stream: bool = False
    incognito: bool = False
    follow_up_context: Optional[Dict[str, Any]] = None
    files: Optional[Dict[str, str]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    
    def to_payload(self) -> Dict[str, Any]:
        """Convert to API payload"""
        payload = {
            "query": self.query,
            "mode": self.mode.value,
            "language": self.language,
            "incognito": self.incognito,
            "sources": [s.value for s in self.sources]
        }
        
        if self.model:
            payload["model"] = self.model.value
        
        if self.files:
            payload["files"] = self.files
        
        if self.follow_up_context:
            payload["follow_up"] = self.follow_up_context
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        
        return payload


@dataclass
class SearchResponse:
    """Structured search response"""
    query: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    related_questions: List[str] = field(default_factory=list)
    mode: str = "auto"
    model: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: Optional[str] = None
    tokens_used: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query,
            "answer": self.answer,
            "sources": self.sources,
            "related_questions": self.related_questions,
            "mode": self.mode,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "tokens_used": self.tokens_used
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"# Query: {self.query}\n\n"
        md += f"## Answer\n{self.answer}\n\n"
        
        if self.sources:
            md += "## Sources\n"
            for idx, source in enumerate(self.sources, 1):
                md += f"{idx}. [{source.get('title', 'Source')}]({source.get('url', '#')})\n"
            md += "\n"
        
        if self.related_questions:
            md += "## Related Questions\n"
            for q in self.related_questions:
                md += f"- {q}\n"
        
        return md


@dataclass
class AccountCredentials:
    """Account credentials"""
    email: str
    cookies: Dict[str, str]
    session_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "email": self.email,
            "cookies": self.cookies,
            "session_token": self.session_token,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }


@dataclass
class ConversationMessage:
    """Single conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Conversation thread"""
    conversation_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, sources: List[Dict] = None):
        """Add message to conversation"""
        message = ConversationMessage(
            role=role,
            content=content,
            sources=sources or []
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context"""
        recent = self.messages[-max_messages:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent
        ]


# Model validation mappings
MODEL_COMPATIBILITY = {
    SearchMode.AUTO: [None],
    SearchMode.PRO: [
        None,
        AIModel.SONAR,
        AIModel.GPT_4_5,
        AIModel.GPT_4O,
        AIModel.CLAUDE_3_7_SONNET,
        AIModel.GEMINI_2_0_FLASH,
        AIModel.GROK_2
    ],
    SearchMode.REASONING: [
        None,
        AIModel.R1,
        AIModel.O3_MINI,
        AIModel.CLAUDE_REASONING
    ],
    SearchMode.DEEP_RESEARCH: [None]
}


def validate_model_compatibility(mode: SearchMode, model: Optional[AIModel]) -> bool:
    """Validate if model is compatible with search mode"""
    if model is None:
        return True
    return model in MODEL_COMPATIBILITY.get(mode, [])


class PerplexityException(Exception):
    """Base exception for Perplexity wrapper"""
    pass


class AuthenticationError(PerplexityException):
    """Authentication related errors"""
    pass


class RateLimitError(PerplexityException):
    """Rate limiting errors"""
    pass


class InvalidParameterError(PerplexityException):
    """Invalid parameter errors"""
    pass


class NetworkError(PerplexityException):
    """Network related errors"""
    pass