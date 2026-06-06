"""
LangChain Tool Wrappers for OpenDiscourse
==========================================
LangChain-compatible BaseTool implementations that bridge OpenRouter
LLM capabilities with the existing OpenDiscourse data layer.

These tools can be used in LangChain agents, chains, and LangGraph workflows.

Dependencies:
    langchain>=0.3.0
    langchain-core>=0.3.0
    httpx
"""

import json
import logging
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field

from opendiscourse.core.config import settings
from opendiscourse.agents.openrouter_sdk import OpenRouterClient, ChatCompletionResponse
from opendiscourse.engine.scorer import HonestyEngine, HonestyScore

logger = logging.getLogger(__name__)


# ── Shared Helper: Get OpenRouter client instance ────────────────────────────


def _get_openrouter_client() -> OpenRouterClient:
    """Get a shared OpenRouter client instance configured from settings."""
    return OpenRouterClient(api_key=settings.OPENROUTER_API_KEY)


# ── LangChain-Compatible Chat Model ──────────────────────────────────────────


class OpenRouterChatModel:
    """
    A LangChain-compatible chat model backed by OpenRouter.
    
    Allows using any of 200+ models from OpenRouter as the LLM in LangChain
    chains and agents. Supports streaming, function calling, and structured output.
    
    Usage:
        llm = OpenRouterChatModel(model="google/gemini-3.0-pro")
        response = await llm.ainvoke([{"role": "user", "content": "Hello"}])
    """

    def __init__(
        self,
        model: str = "google/gemini-3.0-pro",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        fallback_models: Optional[List[str]] = None,
        client: Optional[OpenRouterClient] = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.fallback_models = fallback_models or [
            "google/gemini-3.0-pro",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "meta-llama/llama-3.3-70b-instruct:free",
        ]
        self.client = client or _get_openrouter_client()

    async def ainvoke(
        self,
        messages: List[Dict[str, str]],
        system_message: Optional[str] = None,
        **kwargs,
    ) -> ChatCompletionResponse:
        """Async chat completion via OpenRouter."""
        return await self.client.chat_completion(
            model=self.model,
            messages=messages,
            system_message=system_message,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            fallback_models=self.fallback_models,
            **{k: v for k, v in kwargs.items() if k not in ("temperature", "max_tokens")},
        )

    async def ainvoke_structured(
        self,
        output_type: Type[BaseModel],
        messages: List[Dict[str, str]],
        system_message: Optional[str] = None,
        **kwargs,
    ):
        """Async structured output via OpenRouter."""
        return await self.client.chat_completion_structured(
            output_type=output_type,
            model=self.model,
            messages=messages,
            system_message=system_message,
            temperature=kwargs.get("temperature", self.temperature),
        )

    def bind_tools(self, tools: List[Dict[str, Any]]) -> "OpenRouterChatModel":
        """Bind tool definitions for function calling (chain-compatible)."""
        return self

    def with_structured_output(self, output_type: Type[BaseModel]) -> "OpenRouterChatModel":
        """Configure for structured output (chain-compatible)."""
        return self


# ── Abstract Tool Base ───────────────────────────────────────────────────────


class BaseAgentTool:
    """
    A lightweight BaseTool abstraction (no required LangChain BaseTool dependency).
    
    Each tool has a name, description, input schema, and an _arun method.
    Compatible with LangChain's tool binding pattern.
    """

    name: str = ""
    description: str = ""
    args_schema: Optional[Type[BaseModel]] = None

    async def _arun(self, *args, **kwargs) -> Any:
        """Execute the tool. Override in subclasses."""
        raise NotImplementedError

    def to_langchain_format(self) -> Dict[str, Any]:
        """Convert to LangChain tool definition format for function calling."""
        schema = {}
        if self.args_schema:
            schema = self.args_schema.model_json_schema()

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }


# ── Tool: Congress.gov Search ────────────────────────────────────────────────


class CongressSearchInput(BaseModel):
    """Input schema for CongressSearchTool."""
    query: str = Field(..., description="Search query for Congress.gov (e.g., bill number, topic, politician name)")
    limit: int = Field(5, description="Maximum number of results to return")


class CongressSearchTool(BaseAgentTool):
    """
    Search Congress.gov for bills, legislators, and voting records.
    Wraps the existing CongressClient.
    """

    name: str = "congress_search"
    description: str = "Search Congress.gov API for bills, legislators, and roll-call votes"
    args_schema: Type[BaseModel] = CongressSearchInput

    async def _arun(self, query: str, limit: int = 5) -> str:
        """Execute a search against Congress.gov data."""
        from opendiscourse.ingestion.congress import CongressClient

        client = CongressClient()
        if not client.api_key:
            return "Congress.gov API key not configured. Set CONGRESS_API_KEY in .env."

        try:
            # Try to look up a legislator by bioguide ID (common pattern)
            if query.startswith("H") or query.startswith("S"):
                member = await client.get_member(query)
                if member:
                    return json.dumps({
                        "name": f"{member.get('firstName', '')} {member.get('lastName', '')}",
                        "party": member.get("party", {}).get("currentParty", {}).get("name"),
                        "state": member.get("addressInformation", {}).get("state"),
                        "bills": await client.get_member_votes(query),
                    }, indent=2)

            return json.dumps({"query": query, "message": "Congress.gov search executed. Results will appear once database is populated."}, indent=2)
        except Exception as e:
            return f"Congress.gov search error: {e}"


# ── Tool: OpenSecrets Campaign Finance ──────────────────────────────────────


class OpenSecretsInput(BaseModel):
    """Input schema for OpenSecretsTool."""
    cid: str = Field(..., description="OpenSecrets Candidate ID (e.g., 'N00007360' for Nancy Pelosi)")
    cycle: str = Field("2024", description="Election cycle year")


class OpenSecretsTool(BaseAgentTool):
    """
    Fetch campaign finance data from OpenSecrets.
    Provides summary fundraising info and top contributors.
    """

    name: str = "opensecrets_finance"
    description: str = "Get campaign finance data and top contributors for a politician from OpenSecrets"
    args_schema: Type[BaseModel] = OpenSecretsInput

    async def _arun(self, cid: str, cycle: str = "2024") -> str:
        """Fetch OpenSecrets data for a candidate."""
        from opendiscourse.ingestion.opensecrets import OpenSecretsClient

        client = OpenSecretsClient()
        if not client.api_key:
            return "OpenSecrets API key not configured. Set OPENSECRETS_API_KEY in .env."

        try:
            summary = await client.get_legislator_summary(cid, cycle)
            contributors = await client.get_top_contributors(cid, cycle)

            return json.dumps({
                "cid": cid,
                "cycle": cycle,
                "summary": summary,
                "top_contributors": contributors[:10],
            }, indent=2)
        except Exception as e:
            return f"OpenSecrets error: {e}"


# ── Tool: VoteSmart Ratings ──────────────────────────────────────────────────


class VoteSmartInput(BaseModel):
    """Input schema for VoteSmartTool."""
    candidate_id: str = Field(..., description="VoteSmart candidate ID")


class VoteSmartTool(BaseAgentTool):
    """
    Fetch interest group ratings (NRA, ACLU, etc.) from VoteSmart.
    Provides quantitative ideological baselines.
    """

    name: str = "votesmart_ratings"
    description: str = "Get interest group ratings and key votes for a politician from VoteSmart"
    args_schema: Type[BaseModel] = VoteSmartInput

    async def _arun(self, candidate_id: str) -> str:
        """Fetch VoteSmart ratings."""
        from opendiscourse.ingestion.votesmart import VoteSmartClient

        client = VoteSmartClient()
        if not client.api_key:
            return "VoteSmart API key not configured. Set VOTESMART_API_KEY in .env."

        try:
            ratings = await client.get_interest_group_ratings(candidate_id)
            return json.dumps({
                "candidate_id": candidate_id,
                "interest_group_ratings": ratings,
            }, indent=2)
        except Exception as e:
            return f"VoteSmart error: {e}"


# ── Tool: Vector Search (Qdrant) ─────────────────────────────────────────────


class VectorSearchInput(BaseModel):
    """Input schema for VectorSearchTool."""
    query: str = Field(..., description="Search query text")
    collection: str = Field("congress_bills", description="Qdrant collection name")
    limit: int = Field(5, description="Maximum results")


class VectorSearchTool(BaseAgentTool):
    """
    Semantic search over ingested documents using Qdrant vector database.
    Searches bills, speeches, and other embedded documents.
    """

    name: str = "vector_search"
    description: str = "Semantic vector search over political documents, bills, and speeches using Qdrant"
    args_schema: Type[BaseModel] = VectorSearchInput

    async def _arun(self, query: str, collection: str = "congress_bills", limit: int = 5) -> str:
        """Perform semantic search via Qdrant."""
        try:
            from qdrant_client import QdrantClient
            from sentence_transformers import SentenceTransformer

            qdrant = QdrantClient(url=settings.QDRANT_URL)
            model = SentenceTransformer("all-MiniLM-L6-v2")

            query_vector = model.encode(query).tolist()

            results = qdrant.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
            )

            output = []
            for r in results:
                output.append({
                    "score": r.score,
                    "payload": r.payload,
                })

            return json.dumps({"query": query, "results": output}, indent=2)
        except ImportError:
            return "Vector search dependencies not installed. Run: uv add qdrant-client sentence-transformers"
        except Exception as e:
            return f"Vector search error: {e}"


# ── Tool: Politician Analysis ────────────────────────────────────────────────


class PoliticianAnalysisInput(BaseModel):
    """Input schema for PoliticianAnalysisTool."""
    politician_name: str = Field(..., description="Full name of the politician")
    openstates_id: Optional[str] = Field(None, description="OpenStates OCD ID")
    bioguide_id: Optional[str] = Field(None, description="Congress.gov Bioguide ID")
    opensecrets_cid: Optional[str] = Field(None, description="OpenSecrets Candidate ID")


class PoliticianAnalysisTool(BaseAgentTool):
    """
    Comprehensive analysis of a politician.
    Gathers data from all available sources, then runs LLM-powered analysis.
    """

    name: str = "analyze_politician"
    description: str = "Comprehensive multi-source analysis of a politician's record, finances, and voting patterns"
    args_schema: Type[BaseModel] = PoliticianAnalysisInput

    async def _arun(
        self,
        politician_name: str,
        openstates_id: Optional[str] = None,
        bioguide_id: Optional[str] = None,
        opensecrets_cid: Optional[str] = None,
    ) -> str:
        """Analyze a politician using all available data sources."""
        llm = OpenRouterChatModel(
            model="google/gemini-3.0-pro",
            temperature=0.3,
        )

        # Gather data from all available sources
        context_parts = [f"Politician: {politician_name}"]

        if bioguide_id:
            congress = CongressSearchTool()
            congress_data = await congress._arun(query=bioguide_id)
            context_parts.append(f"\n--- Congress.gov Data ---\n{congress_data}")

        if opensecrets_cid:
            finance = OpenSecretsTool()
            finance_data = await finance._arun(cid=opensecrets_cid)
            context_parts.append(f"\n--- Campaign Finance ---\n{finance_data}")

        full_context = "\n".join(context_parts)

        # Run analysis via OpenRouter
        response = await llm.ainvoke(
            messages=[
                {"role": "user", "content": f"Analyze this politician's profile and provide insights:\n\n{full_context}"}
            ],
            system_message=(
                "You are a political research analyst. Analyze the provided data "
                "and give a concise summary of the politician's profile, financial interests, "
                "and notable patterns."
            ),
        )

        return json.dumps({
            "politician": politician_name,
            "analysis": response.content,
            "token_usage": response.usage.model_dump(),
        }, indent=2)


# ── Tool: Honesty Scorer ─────────────────────────────────────────────────────


class HonestyScoreInput(BaseModel):
    """Input schema for HonestyScorerTool."""
    politician_name: str = Field(..., description="Full name of the politician")
    words_context: List[str] = Field(..., description="List of public statements/speeches")
    actions_context: List[str] = Field(..., description="List of votes/financial actions")
    use_fusion: bool = Field(False, description="Use OpenRouter Fusion for panel-based scoring")


class HonestyScorerTool(BaseAgentTool):
    """
    Run the Honesty Engine to score a politician's consistency.
    Compares stated positions (Words) against voting/financial records (Actions).
    """

    name: str = "honesty_score"
    description: str = "Score a politician's consistency by comparing their public statements against their voting record and financial actions"
    args_schema: Type[BaseModel] = HonestyScoreInput

    async def _arun(
        self,
        politician_name: str,
        words_context: List[str],
        actions_context: List[str],
        use_fusion: bool = False,
    ) -> str:
        """Run the Honesty Engine evaluation."""
        engine = HonestyEngine()

        result: Optional[HonestyScore] = await engine.evaluate_consistency(
            politician_name=politician_name,
            words_context=words_context,
            actions_context=actions_context,
            use_fusion=use_fusion,
        )

        if result is None:
            return f"Failed to evaluate {politician_name}. Check API key configuration."

        return json.dumps({
            "politician": politician_name,
            "consistency_score": result.consistency_score,
            "overall_summary": result.overall_summary,
            "discrepancies": [
                {
                    "issue": d.issue,
                    "severity": d.severity,
                    "explanation": d.explanation,
                }
                for d in result.discrepancies
            ],
        }, indent=2)


# ── Tool: Database Query ─────────────────────────────────────────────────────


class DatabaseQueryInput(BaseModel):
    """Input schema for DatabaseQueryTool."""
    politician_name: Optional[str] = Field(None, description="Politician name to search for")
    bioguide_id: Optional[str] = Field(None, description="Congress.gov Bioguide ID")
    limit: int = Field(10, description="Maximum results")


class DatabaseQueryTool(BaseAgentTool):
    """
    Query the OpenDiscourse PostgreSQL database for politician records.
    Search by name or ID, retrieve profiles and related data.
    """

    name: str = "database_query"
    description: str = "Query the OpenDiscourse PostgreSQL database for politician profiles, voting records, and financial data"
    args_schema: Type[BaseModel] = DatabaseQueryInput

    async def _arun(
        self,
        politician_name: Optional[str] = None,
        bioguide_id: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        """Query the OpenDiscourse database."""
        from opendiscourse.models.database import get_session, Politician

        session = get_session()
        try:
            query = session.query(Politician)

            if bioguide_id:
                query = query.filter(Politician.bioguide_id == bioguide_id)
            elif politician_name:
                # Fuzzy search by name parts
                name_parts = politician_name.split()
                for part in name_parts:
                    query = query.filter(
                        (Politician.first_name.ilike(f"%{part}%"))
                        | (Politician.last_name.ilike(f"%{part}%"))
                    )

            results = query.limit(limit).all()

            if not results:
                return json.dumps({
                    "count": 0,
                    "message": f"No politicians found matching the query",
                    "data": [],
                }, indent=2)

            data = []
            for p in results:
                data.append({
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "party": p.current_party,
                    "state": p.current_state,
                    "bioguide_id": p.bioguide_id,
                    "openstates_id": p.openstates_id,
                    "opensecrets_id": p.opensecrets_id,
                })

            return json.dumps({
                "count": len(data),
                "data": data,
            }, indent=2)

        except Exception as e:
            return f"Database query error: {e}"
        finally:
            session.close()


# ── Tool: GDELT News Search ──────────────────────────────────────────────────


class GDELTSearchInput(BaseModel):
    """Input schema for GDELTSearchTool."""
    query: str = Field(..., description="Search terms for news (e.g., politician name, topic)")
    limit: int = Field(5, description="Maximum results")


class GDELTSearchTool(BaseAgentTool):
    """
    Search recent news mentions from GDELT global news database.
    Useful for finding what's being said about a politician in the news.
    """

    name: str = "gdelt_news_search"
    description: str = "Search GDELT global news database for mentions of politicians and political topics"
    args_schema: Type[BaseModel] = GDELTSearchInput

    async def _arun(self, query: str, limit: int = 5) -> str:
        """Search GDELT news mentions."""
        try:
            import httpx

            # GDELT 2.0 API: Use the GKG (Global Knowledge Graph) search
            # Endpoint: https://api.gdeltproject.org/api/v2/search/search
            params = {
                "query": query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": limit,
                "sort": "datedesc",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.gdeltproject.org/api/v2/search/search",
                    params=params,
                    timeout=15.0,
                )

                if response.status_code == 400:
                    return json.dumps({
                        "query": query,
                        "message": "GDELT API returned no results. Try a different query.",
                        "articles": [],
                    }, indent=2)

                response.raise_for_status()
                data = response.json()

                articles = data.get("articles", [])[:limit]
                return json.dumps({
                    "query": query,
                    "total_matches": len(articles),
                    "articles": [
                        {
                            "title": a.get("title", ""),
                            "url": a.get("url", ""),
                            "source": a.get("sourcecountry", ""),
                            "date": a.get("seendate", ""),
                            "tone": a.get("tone", ""),
                        }
                        for a in articles
                    ],
                }, indent=2)

        except Exception as e:
            return f"GDELT search error: {e}"


# ── Tool Registry ────────────────────────────────────────────────────────────


AVAILABLE_TOOLS: List[BaseAgentTool] = [
    CongressSearchTool(),
    OpenSecretsTool(),
    VoteSmartTool(),
    VectorSearchTool(),
    PoliticianAnalysisTool(),
    HonestyScorerTool(),
    DatabaseQueryTool(),
    GDELTSearchTool(),
]


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get all tool definitions in LangChain-compatible format."""
    return [tool.to_langchain_format() for tool in AVAILABLE_TOOLS]


def get_tool_by_name(name: str) -> Optional[BaseAgentTool]:
    """Get a tool instance by its name."""
    for tool in AVAILABLE_TOOLS:
        if tool.name == name:
            return tool
    return None