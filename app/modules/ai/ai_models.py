from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class AIPrompt(BaseModel):
    """
    AI prompt model
    """
    text: str
    model: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0

class AIResponse(BaseModel):
    """
    AI response model
    """
    text: str
    model: str
    usage: Dict[str, int]
    raw_response: Optional[Dict[str, Any]] = None

class AICompletionHistory(BaseModel):
    """
    AI completion history model
    """
    id: int
    prompt: str
    response: str
    model: str
    created_at: str

class AIMessage(BaseModel):
    """
    AI chat message model
    """
    role: str
    content: str

class AIChatRequest(BaseModel):
    """
    AI chat request model
    """
    messages: List[AIMessage]
    model: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0

class AIChatResponse(BaseModel):
    """
    AI chat response model
    """
    message: AIMessage
    model: str
    usage: Dict[str, int]
    raw_response: Optional[Dict[str, Any]] = None

