import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

API_BASE = os.getenv("GOVINFO_BASE_URL", "https://api.govinfo.gov")
API_KEY = os.getenv("GOVINFO_API_KEY", "")
BULK_BASE = os.getenv("GOVINFO_BULKDATA_BASE", "https://www.govinfo.gov/bulkdata")

TOOLS = {
    "list_collections": {
        "description": "List GovInfo collections",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
    },
    "package_summary": {
        "description": "Fetch a GovInfo package summary",
        "inputSchema": {"type": "object", "properties": {"packageId": {"type": "string"}}, "required": ["packageId"], "additionalProperties": False}
    },
    "granules": {
        "description": "List granules for a GovInfo package",
        "inputSchema": {"type": "object", "properties": {"packageId": {"type": "string"}}, "required": ["packageId"], "additionalProperties": False}
    },
    "bulkdata_listing": {
        "description": "Return a GovInfo bulkdata JSON listing URL",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}
    }
}

print(json.dumps({
    "name": "govinfo-mcp-stub",
    "transport": "stdio",
    "tools": TOOLS,
    "examples": {
      "list_collections": f"{API_BASE}/collections?api_key={API_KEY}",
      "package_summary": f"{API_BASE}/packages/{{packageId}}/summary?api_key={API_KEY}",
      "granules": f"{API_BASE}/packages/{{packageId}}/granules?api_key={API_KEY}",
      "bulkdata_listing": f"{BULK_BASE}/json/{{path}}"
    }
}, indent=2))
