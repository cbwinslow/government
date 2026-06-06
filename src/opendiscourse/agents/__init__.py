"""OpenDiscourse agent tools: OpenRouter SDK, LangChain tools, and agent orchestration."""

from opendiscourse.agents.openrouter_sdk import (
    OpenRouterClient,
    ModelInfo,
    ChatCompletionRequest,
    ChatCompletionResponse,
    TokenUsage,
    ModelCapability,
)

from opendiscourse.agents.langchain_tools import (
    OpenRouterChatModel,
    CongressSearchTool,
    OpenSecretsTool,
    VoteSmartTool,
    VectorSearchTool,
    PoliticianAnalysisTool,
    HonestyScorerTool,
    DatabaseQueryTool,
    GDELTSearchTool,
)

from opendiscourse.agents.orchestrator import (
    ResearchAgent,
    ConsistencyAnalyzer,
    AlertGenerator,
    OpenDiscourseAgentSystem,
)

__all__ = [
    # OpenRouter SDK
    "OpenRouterClient",
    "ModelInfo",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "TokenUsage",
    "ModelCapability",
    # LangChain Tools
    "OpenRouterChatModel",
    "CongressSearchTool",
    "OpenSecretsTool",
    "VoteSmartTool",
    "VectorSearchTool",
    "PoliticianAnalysisTool",
    "HonestyScorerTool",
    "DatabaseQueryTool",
    "GDELTSearchTool",
    # Orchestrator
    "ResearchAgent",
    "ConsistencyAnalyzer",
    "AlertGenerator",
    "OpenDiscourseAgentSystem",
]