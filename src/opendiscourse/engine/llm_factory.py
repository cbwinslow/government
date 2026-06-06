import os
import logging
from langchain_openai import ChatOpenAI
from opendiscourse.engine.scorer import LLMModel
from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Langfuse callback, but fail gracefully if not configured
try:
    from langfuse.callback import CallbackHandler
    # We expect these to be set in .env if the user is using Langfuse Cloud,
    # or left as default if connecting to the local docker-compose instance.
    langfuse_handler = CallbackHandler(
        secret_key=os.environ.get("LANGFUSE_SECRET_KEY", "sk-lf-..."),
        public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", "pk-lf-..."),
        host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000")
    )
    HAS_LANGFUSE = True
except ImportError:
    logger.warning("Langfuse not installed. Tracing disabled.")
    HAS_LANGFUSE = False
except Exception as e:
    logger.error(f"Failed to initialize Langfuse handler: {e}")
    HAS_LANGFUSE = False

def get_llm(model: str = LLMModel.LAGUNA_M1_FREE.value, temperature: float = 0.2) -> ChatOpenAI:
    """
    Returns a configured LangChain ChatOpenAI instance pointing to OpenRouter.
    """
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is missing. LLM calls will fail.")
        
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/cbwinslow/government", 
            "X-Title": "OpenDiscourse Honesty Engine",
        }
    )
    
    return llm

def get_callbacks():
    """Returns the list of callbacks (e.g., Langfuse) to pass to LangGraph."""
    callbacks = []
    if HAS_LANGFUSE:
        callbacks.append(langfuse_handler)
    return callbacks
