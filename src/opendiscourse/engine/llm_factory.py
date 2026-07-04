import os
import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

# Cache to prevent fetching models on every instantiation
_TOP_FREE_MODELS_CACHE = []

def get_top_free_models() -> list[str]:
    """Reads the top free models from the yaml configuration file."""
    global _TOP_FREE_MODELS_CACHE
    if _TOP_FREE_MODELS_CACHE:
        return _TOP_FREE_MODELS_CACHE

    try:
        config_path = Path("/home/cbwinslow/workspace/government/config/models.yaml")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                _TOP_FREE_MODELS_CACHE = data.get("free_models", [])
                
        if not _TOP_FREE_MODELS_CACHE:
            raise ValueError("No free_models found in yaml config.")
            
    except Exception as e:
        print(f"Warning: Failed to read models.yaml. Falling back to defaults. Error: {e}")
        _TOP_FREE_MODELS_CACHE = [
            "poolside/laguna-m.1:free",
            "openai/gpt-oss-120b:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "z-ai/glm-4.5-air:free"
        ]
        
    return _TOP_FREE_MODELS_CACHE

class LLMFactory:
    """Factory for instantiating LangChain LLMs via OpenRouter with Fallbacks."""
    
    @staticmethod
    def get_model(temperature: float = 0.0) -> BaseChatModel:
        """Returns a LangChain ChatOpenAI instance pointed at OpenRouter.
        Uses the models from config/models.yaml as a fallback sequence.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")
            
        top_models = get_top_free_models()
        
        # Primary model is the #1 ranked free model from yaml
        primary_model = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name=top_models[0],
            temperature=temperature,
            max_tokens=4000,
            model_kwargs={"extra_headers": {"HTTP-Referer": "https://opendiscourse.ai"}}
        )
        
        # Create fallbacks for the remaining models in yaml
        fallbacks = []
        for model_id in top_models[1:]:
            fallbacks.append(
                ChatOpenAI(
                    openai_api_key=api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    model_name=model_id,
                    temperature=temperature,
                    max_tokens=4000,
                    model_kwargs={"extra_headers": {"HTTP-Referer": "https://opendiscourse.ai"}}
                )
            )
            
        # Return the primary model configured to fall back to the others if one fails
        return primary_model.with_fallbacks(fallbacks)

# Convenience singletons
def get_supervisor_llm() -> BaseChatModel:
    return LLMFactory.get_model(temperature=0.0)

def get_agent_llm() -> BaseChatModel:
    return LLMFactory.get_model(temperature=0.0)
