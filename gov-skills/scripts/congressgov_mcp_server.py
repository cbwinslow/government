import json
import os

API_BASE = os.getenv("CONGRESS_API_BASE", "https://api.congress.gov/v3")
API_KEY = os.getenv("CONGRESS_API_KEY", "")

TOOLS = {
    "bill_list": {
        "description": "List bills for a Congress",
        "inputSchema": {"type": "object", "properties": {"congress": {"type": "integer"}, "offset": {"type": "integer"}, "limit": {"type": "integer"}}, "required": ["congress"], "additionalProperties": False}
    },
    "bill_detail": {
        "description": "Fetch bill detail",
        "inputSchema": {"type": "object", "properties": {"congress": {"type": "integer"}, "billType": {"type": "string"}, "billNumber": {"type": "integer"}}, "required": ["congress", "billType", "billNumber"], "additionalProperties": False}
    },
    "member_detail": {
        "description": "Fetch member detail",
        "inputSchema": {"type": "object", "properties": {"bioguideId": {"type": "string"}}, "required": ["bioguideId"], "additionalProperties": False}
    }
}

print(json.dumps({
    "name": "congressgov-mcp-stub",
    "transport": "stdio",
    "tools": TOOLS,
    "examples": {
      "bill_list": f"{API_BASE}/bill/{{congress}}?format=json&limit=250&api_key={API_KEY}",
      "bill_detail": f"{API_BASE}/bill/{{congress}}/{{billType}}/{{billNumber}}?format=json&api_key={API_KEY}",
      "member_detail": f"{API_BASE}/member/{{bioguideId}}?format=json&api_key={API_KEY}"
    }
}, indent=2))
