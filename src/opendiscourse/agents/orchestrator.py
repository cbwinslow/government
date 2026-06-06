"""
Agent Orchestrator
==================
High-level agent workflows that combine OpenRouter LLM capabilities
with LangChain-compatible tools to create autonomous research agents.

Provides:
    - ResearchAgent: Multi-source politician research
    - ConsistencyAnalyzer: Words-vs-actions discrepancy analysis
    - AlertGenerator: Monitor for new events and generate alerts
    - OpenDiscourseAgentSystem: Top-level system that orchestrates all agents
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from opendiscourse.agents.openrouter_sdk import OpenRouterClient, ModelCapability
from opendiscourse.agents.langchain_tools import (
    OpenRouterChatModel,
    CongressSearchTool,
    OpenSecretsTool,
    VoteSmartTool,
    VectorSearchTool,
    DatabaseQueryTool,
    GDELTSearchTool,
    HonestyScorerTool,
    PoliticianAnalysisTool,
    get_tool_definitions,
    get_tool_by_name,
)
from opendiscourse.core.config import settings
from opendiscourse.engine.scorer import HonestyScore

logger = logging.getLogger(__name__)


# ── Data Models ──────────────────────────────────────────────────────────────


class AgentTaskStatus(str, Enum):
    """Status of an agent task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ResearchReport(BaseModel):
    """A comprehensive research report on a politician."""
    politician_name: str = Field(..., description="Full name of the politician")
    profile: Dict[str, Any] = Field(default_factory=dict, description="Basic profile info")
    campaign_finance: Dict[str, Any] = Field(default_factory=dict, description="Campaign finance data")
    interest_group_ratings: List[Dict[str, Any]] = Field(default_factory=list, description="Ratings from interest groups")
    news_mentions: List[Dict[str, Any]] = Field(default_factory=list, description="Recent news mentions")
    llm_analysis: str = Field("", description="LLM-generated analysis and insights")
    sources_used: List[str] = Field(default_factory=list, description="Which data sources were queried")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: AgentTaskStatus = AgentTaskStatus.COMPLETED


class DiscrepancyReport(BaseModel):
    """Report on discrepancies between words and actions."""
    politician_name: str = Field(...)
    consistency_score: int = Field(0, ge=0, le=100)
    discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    overall_summary: str = Field("")
    status: AgentTaskStatus = AgentTaskStatus.COMPLETED


class Alert(BaseModel):
    """A generated alert about a significant event."""
    id: str = Field(default_factory=lambda: f"alert-{datetime.utcnow().timestamp()}")
    type: str = Field(..., description="Alert type: 'new_trade', 'vote_contradiction', 'news_mention', 'score_change'")
    politician_name: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    severity: int = Field(5, ge=1, le=10)
    source_url: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    dismissed: bool = False


class AgentRunResult(BaseModel):
    """Result of an agent execution."""
    task_id: str = Field(default_factory=lambda: f"task-{datetime.utcnow().timestamp()}")
    agent_name: str = Field(...)
    status: AgentTaskStatus = AgentTaskStatus.COMPLETED
    output: Any = None
    error: Optional[str] = None
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


# ── Research Agent ───────────────────────────────────────────────────────────


class ResearchAgent:
    """
    Multi-source politician research agent.
    
    Gathers data from Congress.gov, OpenSecrets, VoteSmart, GDELT, and the
    local database, then synthesizes everything with an LLM analysis.
    """

    def __init__(self, llm_model: str = "google/gemini-3.0-pro"):
        self.llm = OpenRouterChatModel(model=llm_model, temperature=0.3)
        self.openrouter = OpenRouterClient()
        self.tools = {
            "congress": CongressSearchTool(),
            "opensecrets": OpenSecretsTool(),
            "votesmart": VoteSmartTool(),
            "database": DatabaseQueryTool(),
            "gdelt": GDELTSearchTool(),
        }

    async def research(
        self,
        politician_name: str,
        bioguide_id: Optional[str] = None,
        opensecrets_cid: Optional[str] = None,
        votesmart_cid: Optional[str] = None,
        openstates_id: Optional[str] = None,
        search_news: bool = True,
    ) -> ResearchReport:
        """
        Run a comprehensive research sweep on a politician.
        
        Gathers data from all configured sources, then runs LLM synthesis.
        Each data source is attempted independently - failures in one source
        don't block the rest.
        """
        logger.info(f"ResearchAgent: Starting research on {politician_name}")

        report = ResearchReport(politician_name=politician_name)
        sources_used: List[str] = []

        # Phase 1: Database lookup
        try:
            db_result = await self.tools["database"]._arun(
                politician_name=politician_name,
                bioguide_id=bioguide_id,
            )
            db_data = json.loads(db_result)
            if db_data.get("data"):
                report.profile = db_data["data"][0]
                sources_used.append("opendiscourse_database")
        except Exception as e:
            logger.warning(f"Database lookup failed: {e}")

        # Phase 2: Campaign finance (OpenSecrets)
        if opensecrets_cid:
            try:
                finance_result = await self.tools["opensecrets"]._arun(cid=opensecrets_cid)
                report.campaign_finance = json.loads(finance_result)
                sources_used.append("opensecrets")
            except Exception as e:
                logger.warning(f"OpenSecrets query failed: {e}")

        # Phase 3: Interest group ratings (VoteSmart)
        if votesmart_cid:
            try:
                ratings_result = await self.tools["votesmart"]._arun(candidate_id=votesmart_cid)
                ratings_data = json.loads(ratings_result)
                report.interest_group_ratings = ratings_data.get("interest_group_ratings", [])
                sources_used.append("votesmart")
            except Exception as e:
                logger.warning(f"VoteSmart query failed: {e}")

        # Phase 4: News mentions
        if search_news:
            try:
                news_result = await self.tools["gdelt"]._arun(query=politician_name, limit=5)
                news_data = json.loads(news_result)
                report.news_mentions = news_data.get("articles", [])
                sources_used.append("gdelt")
            except Exception as e:
                logger.warning(f"GDELT search failed: {e}")

        report.sources_used = sources_used

        # Phase 5: LLM analysis
        try:
            analysis_context = self._build_analysis_context(report)
            response = await self.llm.ainvoke(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Provide a comprehensive analysis of {politician_name} "
                            f"based on the following data:\n\n{analysis_context}"
                        ),
                    }
                ],
                system_message=(
                    "You are a political research analyst. Provide a clear, data-driven "
                    "analysis of this politician's profile. Include: key financial backers, "
                    "ideological alignment based on interest group ratings, notable patterns, "
                    "and any potential conflicts of interest."
                ),
            )
            report.llm_analysis = response.content
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            report.status = AgentTaskStatus.PARTIAL

        return report

    def _build_analysis_context(self, report: ResearchReport) -> str:
        """Build a structured context string for LLM analysis."""
        parts = [f"# Research Report: {report.politician_name}\n"]

        if report.profile:
            parts.append(f"## Profile\n{json.dumps(report.profile, indent=2)}\n")

        if report.campaign_finance:
            parts.append(f"## Campaign Finance\n{json.dumps(report.campaign_finance, indent=2)}\n")

        if report.interest_group_ratings:
            parts.append(f"## Interest Group Ratings\n{json.dumps(report.interest_group_ratings, indent=2)}\n")

        if report.news_mentions:
            parts.append(f"## Recent News\n{json.dumps(report.news_mentions, indent=2)}\n")

        return "\n".join(parts)


# ── Consistency Analyzer ─────────────────────────────────────────────────────


class ConsistencyAnalyzer:
    """
    Analyzes discrepancies between a politician's stated positions (Words)
    and their actual voting record / financial actions (Actions).
    
    Uses the Honesty Engine for scoring and can also gather context
    from additional sources.
    """

    def __init__(self, llm_model: str = "google/gemini-3.0-pro"):
        self.honesty_tool = HonestyScorerTool()
        self.research_agent = ResearchAgent(llm_model=llm_model)

    async def analyze(
        self,
        politician_name: str,
        words_context: List[str],
        actions_context: List[str],
        use_fusion: bool = False,
        gather_context: bool = True,
    ) -> DiscrepancyReport:
        """
        Analyze a politician's consistency between words and actions.
        
        Args:
            politician_name: Full name of the politician
            words_context: List of their public statements / positions
            actions_context: List of their votes / financial actions
            use_fusion: Use OpenRouter Fusion for multi-model panel scoring
            gather_context: If True, also gather news context from GDELT
        
        Returns:
            Structured discrepancy report with score and explanations
        """
        logger.info(f"ConsistencyAnalyzer: Analyzing {politician_name}")

        # Build the context
        all_words = list(words_context)
        all_actions = list(actions_context)

        # Optionally gather additional news context
        if gather_context:
            try:
                gdelt = GDELTSearchTool()
                news = await gdelt._arun(query=politician_name, limit=3)
                news_data = json.loads(news)
                for article in news_data.get("articles", []):
                    if article.get("title"):
                        all_words.append(f"[News] {article['title']}: {article.get('tone', '')}")
            except Exception as e:
                logger.warning(f"News context gathering failed: {e}")

        # Run the Honesty Engine
        result_str = await self.honesty_tool._arun(
            politician_name=politician_name,
            words_context=all_words,
            actions_context=all_actions,
            use_fusion=use_fusion,
        )

        try:
            result = json.loads(result_str)
            return DiscrepancyReport(
                politician_name=politician_name,
                consistency_score=result.get("consistency_score", 0),
                discrepancies=result.get("discrepancies", []),
                overall_summary=result.get("overall_summary", ""),
            )
        except json.JSONDecodeError:
            return DiscrepancyReport(
                politician_name=politician_name,
                status=AgentTaskStatus.FAILED,
                overall_summary=result_str,
            )


# ── Alert Generator ──────────────────────────────────────────────────────────


class AlertGenerator:
    """
    Monitors for new events (trades, votes, news) and generates
    structured alerts that can be surfaced in the dashboard.
    """

    def __init__(self):
        self.llm = OpenRouterChatModel(temperature=0.3)
        self.active_alerts: List[Alert] = []

    async def check_new_trades(
        self,
        politician_name: str,
        recent_trades: List[Dict[str, Any]],
    ) -> List[Alert]:
        """Check recent stock trades for noteworthy patterns."""
        alerts: List[Alert] = []

        for trade in recent_trades:
            ticker = trade.get("ticker", "")
            amount = trade.get("amount", "")
            transaction_type = trade.get("type", "")

            # Generate alert for large trades
            if "50,000" in str(amount) or "100,000" in str(amount):
                alert = Alert(
                    type="new_trade",
                    politician_name=politician_name,
                    title=f"Large {transaction_type}: ${amount} in {ticker}",
                    description=f"{politician_name} reported a {transaction_type} of {ticker} in the range ${amount}.",
                    severity=7,
                )
                alerts.append(alert)

        self.active_alerts.extend(alerts)
        return alerts

    async def check_vote_contradiction(
        self,
        politician_name: str,
        public_statement: str,
        vote_cast: str,
    ) -> Optional[Alert]:
        """Check if a vote contradicts a recent public statement."""
        response = await self.llm.ainvoke(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Politician: {politician_name}\n"
                        f"Public Statement: \"{public_statement}\"\n"
                        f"Vote Cast: \"{vote_cast}\"\n\n"
                        "Does this vote contradict the public statement? "
                        "Answer with YES/NO and a brief explanation."
                    ),
                }
            ],
            system_message="You are a political fact-checking assistant.",
        )

        if "YES" in response.content.upper():
            alert = Alert(
                type="vote_contradiction",
                politician_name=politician_name,
                title=f"Vote contradicts stated position",
                description=response.content,
                severity=8,
            )
            self.active_alerts.append(alert)
            return alert

        return None

    def get_active_alerts(self, min_severity: int = 1) -> List[Alert]:
        """Get all non-dismissed alerts with minimum severity."""
        return [
            a for a in self.active_alerts
            if not a.dismissed and a.severity >= min_severity
        ]

    def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss an alert by ID."""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.dismissed = True
                return True
        return False


# ── Top-Level Orchestrator ───────────────────────────────────────────────────


class OpenDiscourseAgentSystem:
    """
    Top-level orchestrator that coordinates all agents.
    
    Provides a unified interface for:
        - Researching politicians across all data sources
        - Running the Honesty Engine for consistency scoring
        - Generating alerts for significant events
        - Executing custom tool calls
        - Model discovery and selection
    """

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.consistency_analyzer = ConsistencyAnalyzer()
        self.alert_generator = AlertGenerator()
        self.openrouter = OpenRouterClient()
        self.llm = OpenRouterChatModel()

    async def research_politician(
        self,
        name: str,
        bioguide_id: Optional[str] = None,
        opensecrets_cid: Optional[str] = None,
    ) -> AgentRunResult:
        """Research a politician across all data sources."""
        result = AgentRunResult(agent_name="research_politician")
        try:
            report = await self.research_agent.research(
                politician_name=name,
                bioguide_id=bioguide_id,
                opensecrets_cid=opensecrets_cid,
            )
            result.output = report.model_dump()
            result.completed_at = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            result.status = AgentTaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow().isoformat()
            return result

    async def score_consistency(
        self,
        name: str,
        words: List[str],
        actions: List[str],
        use_fusion: bool = False,
    ) -> AgentRunResult:
        """Score a politician's consistency between words and actions."""
        result = AgentRunResult(agent_name="score_consistency")
        try:
            report = await self.consistency_analyzer.analyze(
                politician_name=name,
                words_context=words,
                actions_context=actions,
                use_fusion=use_fusion,
            )
            result.output = report.model_dump()
            result.completed_at = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            result.status = AgentTaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow().isoformat()
            return result

    async def run_tool(
        self,
        tool_name: str,
        **kwargs,
    ) -> AgentRunResult:
        """
        Execute a specific tool by name.
        
        Args:
            tool_name: Name of the tool (e.g., "congress_search", "opensecrets_finance")
            **kwargs: Tool-specific parameters
        
        Returns:
            AgentRunResult with the tool's output
        """
        result = AgentRunResult(agent_name=f"tool:{tool_name}")
        try:
            tool = get_tool_by_name(tool_name)
            if not tool:
                raise ValueError(f"Unknown tool: {tool_name}. Available: {[t.name for t in get_tool_definitions()]}")

            output = await tool._arun(**kwargs)
            result.output = {"tool": tool_name, "result": output}
            result.completed_at = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            result.status = AgentTaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow().isoformat()
            return result

    async def discover_models(
        self,
        task_type: Optional[str] = None,
        free_only: bool = False,
    ) -> AgentRunResult:
        """
        Discover available models on OpenRouter.
        
        Args:
            task_type: Type of task - "reasoning", "code", "vision", "chat", "structured"
            free_only: Only list free models
        
        Returns:
            AgentRunResult with filtered model list
        """
        result = AgentRunResult(agent_name="discover_models")
        try:
            # Map task types to capabilities
            capability_map = {
                "reasoning": ModelCapability.REASONING,
                "code": ModelCapability.CODE,
                "vision": ModelCapability.VISION,
                "structured": ModelCapability.STRUCTURED_OUTPUT,
                "chat": ModelCapability.CHAT,
            }

            capability = capability_map.get(task_type) if task_type else None

            models = await self.openrouter.list_models(
                capability=capability,
                free_only=free_only,
                min_context=8000,
            )

            result.output = {
                "task_type": task_type or "all",
                "free_only": free_only,
                "total_models": len(models),
                "models": [
                    {
                        "id": m.id,
                        "context_length": m.context_length,
                        "pricing": m.pricing.model_dump(),
                        "capabilities": [c.value for c in m.capabilities],
                    }
                    for m in models[:20]  # Top 20 by context length
                ],
            }
            result.completed_at = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            result.status = AgentTaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow().isoformat()
            return result

    async def compare_models_on_prompt(
        self,
        prompt: str,
        model_a: str = "google/gemini-3.0-pro",
        model_b: str = "nousresearch/hermes-3-llama-3.1-405b:free",
    ) -> AgentRunResult:
        """Compare two models on the same prompt."""
        result = AgentRunResult(agent_name="compare_models")
        try:
            comparison = await self.openrouter.compare_models(
                prompt=prompt,
                model_a=model_a,
                model_b=model_b,
            )
            result.output = comparison.model_dump()
            result.completed_at = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            result.status = AgentTaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow().isoformat()
            return result

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get all available tools in LangChain-compatible format."""
        return get_tool_definitions()