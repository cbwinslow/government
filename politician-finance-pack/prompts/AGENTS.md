# AGENTS.md: Swarm & LangGraph Agent Protocol

**Target Directory:** `politician-finance-pack/prompts`

## Permitted Agents
Agents operating in this directory must strictly adhere to the operational limits defined below. Unrecognized agents should escalate to the Supervisor Node.

## Tool Context & MCP Access
- **Database Tools:** Agents should use standard `psql` or `SQLAlchemy` connectors to interact with the Postgres `govdata` database.
- **Vector Operations:** Agents looking for semantic search must route through the `Qdrant` endpoints at `172.25.10.64:6333`.
- **MCP Servers:** If this directory contains MCP configurations, agents must utilize the exposed `mcp_<server_name>_<tool_name>` commands natively.

## System Prompt Directives
```yaml
system_prompt: >
  You are operating within 'prompts'. Your primary objective is to execute 
  workflows localized to this domain. Do not traverse outside this directory 
  unless explicitly instructed by the LangGraph Orchestrator.
```
