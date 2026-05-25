import json

TOOLS = {
  "get_politician_profile": {
    "description": "Fetch politician profile and linked metrics",
    "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False}
  },
  "find_transactions": {
    "description": "Find disclosure transactions by person, ticker, or date range",
    "inputSchema": {"type": "object", "properties": {"person": {"type": "string"}, "ticker": {"type": "string"}}, "additionalProperties": False}
  }
}

print(json.dumps({"name": "politician-db-mcp-stub", "transport": "stdio", "tools": TOOLS}, indent=2))
