import openai
import google.generativeai as genai
from typing import Dict, Any, List
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.tracing import get_tracer, trace_function
from .ai_constants import (
    MODEL_OPENAI_GPT4,
    MODEL_OPENAI_GPT35_TURBO,
    MODEL_GOOGLE_GEMINI_PRO,
    ERROR_API_KEY_MISSING,
    ERROR_MODEL_NOT_SUPPORTED,
    ERROR_REQUEST_FAILED
)
from .ai_models import AIPrompt, AIResponse, AIChatRequest, AIChatResponse, AIMessage

logger = setup_logging()
tracer = get_tracer()

@trace_function
def get_openai_client():
    """
    Get OpenAI client
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_API_KEY_MISSING
        )
    
    return openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@trace_function
def get_google_ai_client():
    """
    Get Google AI client
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_API_KEY_MISSING
        )
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    return genai

@trace_function
async def generate_completion(prompt: AIPrompt) -> AIResponse:
    """
    Generate text completion using AI models
    
    Args:
        prompt: AI prompt
        
    Returns:
        AIResponse: AI response
    """
    with tracer.start_as_current_span(
        "generate_completion",
        attributes={
            "ai.model": prompt.model,
            "ai.max_tokens": prompt.max_tokens,
            "ai.temperature": prompt.temperature
        }
    ):
        try:
            if prompt.model in [MODEL_OPENAI_GPT4, MODEL_OPENAI_GPT35_TURBO]:
                return await generate_openai_completion(prompt)
            elif prompt.model == MODEL_GOOGLE_GEMINI_PRO:
                return await generate_google_completion(prompt)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MODEL_NOT_SUPPORTED
                )
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{ERROR_REQUEST_FAILED}: {str(e)}"
            )

@trace_function
async def generate_openai_completion(prompt: AIPrompt) -> AIResponse:
    """
    Generate text completion using OpenAI models
    
    Args:
        prompt: AI prompt
        
    Returns:
        AIResponse: AI response
    """
    with tracer.start_as_current_span("generate_openai_completion"):
        client = get_openai_client()
        
        try:
            response = client.completions.create(
                model=prompt.model,
                prompt=prompt.text,
                max_tokens=prompt.max_tokens,
                temperature=prompt.temperature,
                top_p=prompt.top_p,
                frequency_penalty=prompt.frequency_penalty,
                presence_penalty=prompt.presence_penalty
            )
            
            return AIResponse(
                text=response.choices[0].text.strip(),
                model=prompt.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                raw_response=response.model_dump()
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

@trace_function
async def generate_google_completion(prompt: AIPrompt) -> AIResponse:
    """
    Generate text completion using Google AI models
    
    Args:
        prompt: AI prompt
        
    Returns:
        AIResponse: AI response
    """
    with tracer.start_as_current_span("generate_google_completion"):
        client = get_google_ai_client()
        
        try:
            model = client.GenerativeModel(MODEL_GOOGLE_GEMINI_PRO)
            response = model.generate_content(prompt.text)
            
            # Google AI doesn't provide token usage in the same way as OpenAI
            # This is an approximation
            estimated_prompt_tokens = len(prompt.text.split()) * 1.3
            estimated_completion_tokens = len(response.text.split()) * 1.3
            
            return AIResponse(
                text=response.text,
                model=prompt.model,
                usage={
                    "prompt_tokens": int(estimated_prompt_tokens),
                    "completion_tokens": int(estimated_completion_tokens),
                    "total_tokens": int(estimated_prompt_tokens + estimated_completion_tokens)
                },
                raw_response={"text": response.text}
            )
        except Exception as e:
            logger.error(f"Google AI API error: {e}")
            raise

@trace_function
async def generate_chat_completion(request: AIChatRequest) -> AIChatResponse:
    """
    Generate chat completion using AI models
    
    Args:
        request: AI chat request
        
    Returns:
        AIChatResponse: AI chat response
    """
    with tracer.start_as_current_span(
        "generate_chat_completion",
        attributes={
            "ai.model": request.model,
            "ai.max_tokens": request.max_tokens,
            "ai.temperature": request.temperature,
            "ai.messages_count": len(request.messages)
        }
    ):
        try:
            if request.model in [MODEL_OPENAI_GPT4, MODEL_OPENAI_GPT35_TURBO]:
                return await generate_openai_chat_completion(request)
            elif request.model == MODEL_GOOGLE_GEMINI_PRO:
                return await generate_google_chat_completion(request)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MODEL_NOT_SUPPORTED
                )
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{ERROR_REQUEST_FAILED}: {str(e)}"
            )

@trace_function
async def generate_openai_chat_completion(request: AIChatRequest) -> AIChatResponse:
    """
    Generate chat completion using OpenAI models
    
    Args:
        request: AI chat request
        
    Returns:
        AIChatResponse: AI chat response
    """
    with tracer.start_as_current_span("generate_openai_chat_completion"):
        client = get_openai_client()
        
        try:
            # Convert messages to OpenAI format
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            response = client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty
            )
            
            return AIChatResponse(
                message=AIMessage(
                    role="assistant",
                    content=response.choices[0].message.content
                ),
                model=request.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                raw_response=response.model_dump()
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

@trace_function
async def generate_google_chat_completion(request: AIChatRequest) -> AIChatResponse:
    """
    Generate chat completion using Google AI models
    
    Args:
        request: AI chat request
        
    Returns:
        AIChatResponse: AI chat response
    """
    with tracer.start_as_current_span("generate_google_chat_completion"):
        client = get_google_ai_client()
        
        try:
            model = client.GenerativeModel(MODEL_GOOGLE_GEMINI_PRO)
            
            # Convert messages to Google AI format
            chat = model.start_chat()
            
            for msg in request.messages:
                if msg.role == "user":
                    chat.send_message(msg.content)
            
            # Send the last user message to get a response
            last_user_msg = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), "")
            response = chat.send_message(last_user_msg)
            
            # Google AI doesn't provide token usage in the same way as OpenAI
            # This is an approximation
            estimated_prompt_tokens = sum(len(msg.content.split()) for msg in request.messages) * 1.3
            estimated_completion_tokens = len(response.text.split()) * 1.3
            
            return AIChatResponse(
                message=AIMessage(
                    role="assistant",
                    content=response.text
                ),
                model=request.model,
                usage={
                    "prompt_tokens": int(estimated_prompt_tokens),
                    "completion_tokens": int(estimated_completion_tokens),
                    "total_tokens": int(estimated_prompt_tokens + estimated_completion_tokens)
                },
                raw_response={"text": response.text}
            )
        except Exception as e:
            logger.error(f"Google AI API error: {e}")
            raise

