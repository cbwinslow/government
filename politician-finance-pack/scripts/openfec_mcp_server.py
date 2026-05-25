import json
import os

API_KEY = os.getenv("FEC_API_KEY", "")
BASE = os.getenv("FEC_API_BASE", "https://api.open.fec.gov/v1")

TOOLS = {
  "candidate_search": {
    "description": "Search OpenFEC candidates",
    "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"], "additionalProperties": False}
  },
  "committee_search": {
    "description": "Search OpenFEC committees",
    "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"], "additionalProperties": False}
  }
}

print(json.dumps({
  "name": "openfec-mcp-stub",
  "transport": "stdio",
  "base": BASE,
  "api_key_present": bool(API_KEY),
  "tools": TOOLS
}, indent=2))
