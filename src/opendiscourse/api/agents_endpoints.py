"""
FastAPI Agent Endpoints
=======================
REST API endpoints for the OpenDiscourse agent system.
Exposes OpenRouter SDK tools, LangChain tools, and orchestration
agents as HTTP endpoints consumable by the dashboard.

Endpoints:
    POST /api/agents/research          - Research a politician
    POST /api/agents/score-consistency - Score words-vs-actions consistency
    POST /api/agents/run-tool          - Execute a specific tool
    GET  /api/agents/tools             - List all available tools
    POST /api/agents/chat              - Chat with an OpenRouter model
    POST /api/agents/discover-models   - Discover available models
    POST /api/agents/compare-models    - Compare two models
    GET  /api/agents/alerts            - Get active alerts
    POST /api/agents/alerts/dismiss    - Dismiss an alert
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from opendiscourse.agents.orchestrator import OpenDiscourseAgentSystem, AgentRunResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Singleton agent system
_agent_system: Optional[OpenDiscourseAgentSystem] = None


def get_agent_system() -> OpenDiscourseAgentSystem:
    """Get or create the shared agent system instance."""
    global _agent_system
    if _agent_system is None:
        _agent_system = OpenDiscourseAgentSystem()
    return _agent_system


# ── Request/Response Models ──────────────────────────────────────────────────


class ResearchRequest(BaseModel):
    name: str = Field(..., description="Politician's full name")
    bioguide_id: Optional[str] = Field(None, description="Congress.gov Bioguide ID")
    opensecrets_cid: Optional[str] = Field(None, description="OpenSecrets Candidate ID")


class ConsistencyRequest(BaseModel):
    name: str = Field(..., description="Politician's full name")
    words: List[str] = Field(..., description="List of public statements / positions")
    actions: List[str] = Field(..., description="List of votes / financial actions")
    use_fusion: bool = Field(False, description="Use OpenRouter Fusion for panel scoring")


class RunToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    system_message: Optional[str] = Field(None, description="System prompt")
    model: str = Field("google/gemini-3.0-pro", description="OpenRouter model ID")
    temperature: float = Field(0.7, ge=0.0, le=2.0)


class DiscoverModelsRequest(BaseModel):
    task_type: Optional[str] = Field(None, description="Filter by task type: reasoning, code, vision, chat, structured")
    free_only: bool = Field(False, description="Only show free models")


class CompareModelsRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to send to both models")
    model_a: str = Field("google/gemini-3.0-pro", description="First model")
    model_b: str = Field("nousresearch/hermes-3-llama-3.1-405b:free", description="Second model")


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/research", response_model=AgentRunResult)
async def research_politician(request: ResearchRequest):
    """Research a politician across all available data sources."""
    system = get_agent_system()
    result = await system.research_politician(
        name=request.name,
        bioguide_id=request.bioguide_id,
        opensecrets_cid=request.opensecrets_cid,
    )
    return result


@router.post("/score-consistency", response_model=AgentRunResult)
async def score_consistency(request: ConsistencyRequest):
    """Score a politician's consistency between words and actions."""
    system = get_agent_system()
    result = await system.score_consistency(
        name=request.name,
        words=request.words,
        actions=request.actions,
        use_fusion=request.use_fusion,
    )
    return result


@router.post("/run-tool", response_model=AgentRunResult)
async def run_tool(request: RunToolRequest):
    """Execute a specific agent tool by name."""
    system = get_agent_system()
    result = await system.run_tool(
        tool_name=request.tool_name,
        **request.params,
    )
    return result


@router.get("/tools")
async def list_tools():
    """List all available agent tools with their descriptions and schemas."""
    system = get_agent_system()
    return {"tools": system.get_tool_list()}


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with any OpenRouter model. 
    
    Supports 200+ models including free options.
    """
    from opendiscourse.agents.openrouter_sdk import OpenRouterClient

    client = OpenRouterClient()

    if not client.api_key:
        raise HTTPException(
            status_code=401,
            detail="OPENROUTER_API_KEY not configured. Set it in your .env file."
        )

    response = await client.chat_completion(
        model=request.model,
        messages=[{"role": "user", "content": request.message}],
        system_message=request.system_message,
        temperature=request.temperature,
    )

    return {
        "content": response.content,
        "model": response.model,
        "usage": response.usage.model_dump(),
        "cost_usd": response.cost_usd(),
    }


@router.post("/discover-models")
async def discover_models(request: DiscoverModelsRequest):
    """Discover available models on OpenRouter with optional filters."""
    system = get_agent_system()
    result = await system.discover_models(
        task_type=request.task_type,
        free_only=request.free_only,
    )
    return result


@router.post("/compare-models")
async def compare_models(request: CompareModelsRequest):
    """Compare two models on the same prompt."""
    system = get_agent_system()
    result = await system.compare_models_on_prompt(
        prompt=request.prompt,
        model_a=request.model_a,
        model_b=request.model_b,
    )
    return result


@router.get("/alerts")
async def get_alerts(min_severity: int = 1):
    """Get active alerts with optional minimum severity filter."""
    system = get_agent_system()
    alerts = system.alert_generator.get_active_alerts(min_severity=min_severity)
    return {
        "alerts": [a.model_dump() for a in alerts],
        "count": len(alerts),
    }


@router.post("/alerts/dismiss")
async def dismiss_alert(alert_id: str):
    """Dismiss an alert by ID."""
    system = get_agent_system()
    success = system.alert_generator.dismiss_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")
    return {"status": "dismissed", "alert_id": alert_id}