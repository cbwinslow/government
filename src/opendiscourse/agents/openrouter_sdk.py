"""
OpenRouter SDK Wrapper Tools
============================
A structured SDK wrapper around OpenRouter's API for accessing 200+ models.
Provides chat completions, model discovery, streaming, comparison, and structured output.

Usage:
    client = OpenRouterClient()
    response = await client.chat_completion(
        model="google/gemini-3.0-pro",
        messages=[{"role": "user", "content": "Hello"}],
    )
"""

import json
import logging
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field

from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# ── Data Models ──────────────────────────────────────────────────────────────


class ModelCapability(str, Enum):
    """Capability flags for OpenRouter models."""

    CHAT = "chat"
    COMPLETIONS = "completions"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    STREAMING = "streaming"
    VISION = "vision"
    TOOL_USE = "tool_use"
    CODE = "code"
    REASONING = "reasoning"


class ModelPricing(BaseModel):
    """Pricing info for a model in USD per token."""

    prompt: float = 0.0
    completion: float = 0.0


class ModelInfo(BaseModel):
    """Information about an OpenRouter model."""

    id: str = Field(..., description="Full model ID, e.g. 'openai/gpt-4o'")
    name: str = Field("", description="Human-readable name")
    created: int = Field(0, description="Model creation timestamp")
    description: str = Field("", description="Model description")
    context_length: int = Field(0, description="Max context tokens")
    pricing: ModelPricing = Field(default_factory=ModelPricing)
    capabilities: List[ModelCapability] = Field(default_factory=list)
    architecture: str = Field("", description="e.g. 'Llama-3.1-405B'")
    top_provider: Dict[str, Any] = Field(default_factory=dict)


class ChatCompletionMessage(BaseModel):
    """A single message in a chat completion request/response."""

    role: str = Field(..., description="'user', 'assistant', 'system', or 'tool'")
    content: str = Field("", description="Message content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls made by the assistant")
    tool_call_id: Optional[str] = Field(None, description="ID for tool call responses")


class TokenUsage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionRequest(BaseModel):
    """Request parameters for a chat completion."""

    model: str = "google/gemini-3.0-pro"
    messages: List[ChatCompletionMessage]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    response_format: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    seed: Optional[int] = None
    # OpenRouter-specific
    models: Optional[List[str]] = Field(None, description="Fallback model order")
    route: Optional[str] = Field(None, description="OpenRouter route: 'fallback' or 'fusion'")
    provider: Optional[Dict[str, Any]] = Field(None, description="Provider routing preferences")


class ChatCompletionResponse(BaseModel):
    """Parsed response from a chat completion."""

    id: str = ""
    model: str = ""
    choices: List[Dict[str, Any]] = Field(default_factory=list)
    usage: TokenUsage = Field(default_factory=TokenUsage)
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw API response")

    @property
    def content(self) -> str:
        """Get the text content from the first choice."""
        if not self.choices:
            return ""
        return self.choices[0].get("message", {}).get("content", "")

    @property
    def finish_reason(self) -> Optional[str]:
        """Get the finish reason from the first choice."""
        if not self.choices:
            return None
        return self.choices[0].get("finish_reason")

    def parse_structured(self, output_type: Type[T]) -> Optional[T]:
        """Parse the response content into a Pydantic model."""
        if not self.content:
            return None
        try:
            # Handle both JSON string response and parsed response
            data = json.loads(self.content) if isinstance(self.content, str) else self.content
            return output_type.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse structured output: {e}")
            return None

    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """Extract tool calls from the response."""
        if not self.choices:
            return []
        message = self.choices[0].get("message", {})
        return message.get("tool_calls", [])

    def cost_usd(self) -> float:
        """Estimate cost in USD."""
        prompt_cost = self.usage.prompt_tokens * 1e-6  # rough estimate
        completion_cost = self.usage.completion_tokens * 2e-6
        return round(prompt_cost + completion_cost, 6)


class ModelComparisonResult(BaseModel):
    """Result of comparing two models on the same prompt."""

    prompt: str = ""
    model_a: str = ""
    model_b: str = ""
    response_a: str = ""
    response_b: str = ""
    usage_a: TokenUsage = Field(default_factory=TokenUsage)
    usage_b: TokenUsage = Field(default_factory=TokenUsage)
    verdict: str = Field("", description="Which model performed better, or 'tie'")


# ── OpenRouter Client ────────────────────────────────────────────────────────


class OpenRouterClient:
    """
    Core client for OpenRouter API operations.
    
    Provides structured access to chat completions, model discovery,
    streaming, model comparison, and structured output generation
    across 200+ models.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None, http_client: Any = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self._http_client = http_client
        self._session: Any = None

    async def _ensure_session(self) -> Any:
        """Get or create an HTTP client session."""
        if self._http_client:
            return self._http_client
        if not self._session:
            import httpx
            self._session = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=self._default_headers,
                timeout=60.0,
            )
        return self._session

    @property
    def _default_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat_completion(
        self,
        model: str = "google/gemini-3.0-pro",
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
        use_fusion: bool = False,
        **kwargs,
    ) -> ChatCompletionResponse:
        """
        Call any OpenRouter model with structured input/output.
        
        Args:
            model: The primary model to use (e.g. "google/gemini-3.0-pro")
            messages: Chat messages as a list of {"role": ..., "content": ...}
            system_message: Optional system prompt (prepended as system message)
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens in response
            response_format: JSON schema for structured output, e.g. {"type": "json_object"}
            tools: Tool definitions for function calling
            tool_choice: "auto", "any", "none", or {"type": "function", "function": {"name": ...}}
            fallback_models: Ordered list of fallback models if primary fails
            use_fusion: If True, use OpenRouter Fusion (panel multiple models)
            **kwargs: Additional OpenRouter parameters
        
        Returns:
            Parsed ChatCompletionResponse with content, usage, and tool calls
        """
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured. "
                "Set it in your .env file or pass it to the constructor."
            )

        # Prepare messages
        all_messages: List[Dict[str, str]] = []
        if system_message:
            all_messages.append({"role": "system", "content": system_message})
        if messages:
            all_messages.extend(messages)

        # Build the request body
        body: Dict[str, Any] = {
            "model": model,
            "messages": all_messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if response_format is not None:
            body["response_format"] = response_format
        if tools is not None:
            body["tools"] = tools
        if tool_choice is not None:
            body["tool_choice"] = tool_choice

        # OpenRouter-specific routing
        extra_body: Dict[str, Any] = kwargs.pop("extra_body", {})
        if use_fusion:
            body["model"] = "openrouter/fusion"
        elif fallback_models:
            extra_body["models"] = fallback_models

        # Provider routing
        provider = kwargs.pop("provider", None)
        if provider:
            extra_body["provider"] = provider

        if extra_body:
            body["extra_body"] = extra_body

        # Add any remaining kwargs
        body.update(kwargs)

        session = await self._ensure_session()

        try:
            logger.info(f"OpenRouter chat completion - model: {model}")
            response = await session.post(
                f"{self.BASE_URL}/chat/completions",
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            return ChatCompletionResponse(
                id=data.get("id", ""),
                model=data.get("model", model),
                choices=data.get("choices", []),
                usage=TokenUsage(
                    prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                    completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                    total_tokens=data.get("usage", {}).get("total_tokens", 0),
                ),
                raw=data,
            )

        except Exception as e:
            logger.error(f"OpenRouter chat completion failed: {e}")
            raise

    async def chat_completion_structured(
        self,
        output_type: Type[T],
        model: str = "google/gemini-3.0-pro",
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        **kwargs,
    ) -> Optional[T]:
        """
        Get a structured (JSON schema-constrained) response from any model.
        
        Uses OpenRouter's response_format support to enforce JSON Schema output.
        
        Args:
            output_type: A Pydantic BaseModel subclass defining the output schema
            model: The model to use (must support structured output)
            messages: Chat messages
            system_message: Optional system prompt
            temperature: Lower temperature for more precise structured output
            **kwargs: Additional parameters
        
        Returns:
            Parsed instance of output_type, or None if parsing fails
        """
        schema = output_type.model_json_schema()

        response = await self.chat_completion(
            model=model,
            messages=messages,
            system_message=system_message,
            temperature=temperature,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": output_type.__name__,
                    "schema": schema,
                },
            },
            **kwargs,
        )

        return response.parse_structured(output_type)

    async def stream_completion(
        self,
        model: str = "google/gemini-3.0-pro",
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion token by token.
        
        Args:
            model: The model to use
            messages: Chat messages
            system_message: Optional system prompt
            temperature: Sampling temperature
            on_token: Optional callback for each token
            **kwargs: Additional parameters
        
        Yields:
            Content tokens as they arrive
        """
        all_messages: List[Dict[str, str]] = []
        if system_message:
            all_messages.append({"role": "system", "content": system_message})
        if messages:
            all_messages.extend(messages)

        body: Dict[str, Any] = {
            "model": model,
            "messages": all_messages,
            "temperature": temperature,
            "stream": True,
        }
        body.update(kwargs)

        session = await self._ensure_session()

        async with session.stream(
            "POST",
            f"{self.BASE_URL}/chat/completions",
            json=body,
        ) as stream:
            async for line in stream.aiter_lines():
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            if on_token:
                                on_token(content)
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def list_models(
        self,
        capability: Optional[ModelCapability] = None,
        min_context: Optional[int] = None,
        max_cost_per_token: Optional[float] = None,
        free_only: bool = False,
    ) -> List[ModelInfo]:
        """
        Discover available models on OpenRouter with optional filters.
        
        Args:
            capability: Filter by capability (e.g., STRUCTURED_OUTPUT, VISION)
            min_context: Minimum context window size
            max_cost_per_token: Maximum cost per token
            free_only: Only show free models
        
        Returns:
            List of filtered ModelInfo objects
        """
        session = await self._ensure_session()

        try:
            response = await session.get(f"{self.BASE_URL}/models")
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

        models: List[ModelInfo] = []
        for m in data.get("data", []):
            model_id = m.get("id", "")

            # Determine capabilities based on model properties
            caps: List[ModelCapability] = [ModelCapability.CHAT, ModelCapability.COMPLETIONS]
            if m.get("features", {}).get("function_calling"):
                caps.append(ModelCapability.FUNCTION_CALLING)
                caps.append(ModelCapability.TOOL_USE)
            if m.get("features", {}).get("vision"):
                caps.append(ModelCapability.VISION)
            if m.get("features", {}).get("structured_output"):
                caps.append(ModelCapability.STRUCTURED_OUTPUT)

            pricing = ModelPricing(
                prompt=float(m.get("pricing", {}).get("prompt", 0)),
                completion=float(m.get("pricing", {}).get("completion", 0)),
            )

            # Apply filters
            if free_only and (pricing.prompt > 0 or pricing.completion > 0):
                continue
            if max_cost_per_token is not None and (
                pricing.prompt > max_cost_per_token or pricing.completion > max_cost_per_token
            ):
                continue
            if min_context is not None:
                ctx = m.get("context_length", 0)
                if ctx > 0 and ctx < min_context:
                    continue

            model_info = ModelInfo(
                id=model_id,
                name=m.get("name", model_id),
                created=m.get("created", 0),
                description=m.get("description", ""),
                context_length=m.get("context_length", 0),
                pricing=pricing,
                capabilities=caps,
                architecture=m.get("architecture", ""),
                top_provider=m.get("top_provider", {}),
            )

            if capability and capability not in caps:
                continue

            models.append(model_info)

        # Sort by context length descending
        models.sort(key=lambda m: (-m.context_length, m.id))
        return models

    async def compare_models(
        self,
        prompt: str,
        model_a: str = "google/gemini-3.0-pro",
        model_b: str = "nousresearch/hermes-3-llama-3.1-405b:free",
        system_message: Optional[str] = None,
        temperature: float = 0.7,
    ) -> ModelComparisonResult:
        """
        Compare two models on the same prompt.
        
        Sends the same prompt to both models and returns both responses
        for comparison.
        """
        messages = [{"role": "user", "content": prompt}]

        response_a = await self.chat_completion(
            model=model_a,
            messages=messages,
            system_message=system_message,
            temperature=temperature,
        )

        response_b = await self.chat_completion(
            model=model_b,
            messages=messages,
            system_message=system_message,
            temperature=temperature,
        )

        # Generate a simple verdict
        verdict = "tie"
        if not response_a.content and response_b.content:
            verdict = model_b
        elif response_a.content and not response_b.content:
            verdict = model_a
        elif response_a.content and response_b.content:
            len_a = len(response_a.content)
            len_b = len(response_b.content)
            if abs(len_a - len_b) / max(len_a, len_b) > 0.3:
                verdict = model_a if len_a > len_b else model_b

        return ModelComparisonResult(
            prompt=prompt,
            model_a=model_a,
            model_b=model_b,
            response_a=response_a.content,
            response_b=response_b.content,
            usage_a=response_a.usage,
            usage_b=response_b.usage,
            verdict=verdict,
        )

    async def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate the cost of a request for a given model.
        
        Args:
            model: Model ID
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
        
        Returns:
            Estimated cost in USD
        """
        models = await self.list_models()
        for m in models:
            if m.id == model:
                return round(
                    (prompt_tokens * m.pricing.prompt + completion_tokens * m.pricing.completion) / 1000,
                    6,
                )
        return 0.0

    async def close(self):
        """Close the underlying HTTP client session."""
        if self._session:
            await self._session.aclose()
            self._session = None