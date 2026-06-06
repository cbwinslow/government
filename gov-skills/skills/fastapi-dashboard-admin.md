# Skill: fastapi-dashboard-admin

## Purpose
Use this skill when developing, extending, or debugging the OpenDiscourse FastAPI backend and the React/TypeScript dashboard frontend. The API serves politician profiles, Honesty Engine scores, network graphs, and semantic search results to the dashboard UI.

## Architecture facts to honor
- Backend: FastAPI lives in `src/opendiscourse/api/` (uvicorn server).
- Frontend: React/TypeScript dashboard lives in `src/dashboard/`.
- The API connects to PostgreSQL (politician data, scores) and Qdrant (semantic search).
- CORS is enabled for the dashboard origin.
- Settings are managed through `src/opendiscourse/core/config.py` (pydantic-settings).

## API endpoints to maintain

### Politician endpoints
```python
GET /api/politicians          # List all politicians (paginated, filterable by party/state)
GET /api/politicians/{id}     # Single politician profile with linked data
GET /api/politicians/search   # Full-text search by name (uses pg_trgm or ILIKE)
```

### Analysis endpoints
```python
GET /api/honesty/{politician_id}       # Latest Honesty Engine score for a politician
GET /api/honesty/{politician_id}/history  # Score history over time
GET /api/discrepancies/{politician_id}    # Detailed discrepancy list
```

### Finance endpoints
```python
GET /api/finance/transactions/{politician_id}  # Stock/asset transactions from disclosures
GET /api/finance/contributors/{politician_id}   # Top campaign contributors
```

### Search endpoints
```python
POST /api/search/semantic        # Qdrant vector search over bills/profiles
GET /api/search/bills            # Metadata-filtered bill search
```

### Network endpoints
```python
GET /api/network/politician/{id}         # Connections: committees, donors, co-sponsors
GET /api/network/overview                # Full network graph for the dashboard
```

## Frontend components (src/dashboard/src/components/)
The React dashboard has these key components that must be kept in sync with the API:

- `PoliticianProfile.tsx` — Full profile view with score, bio, finance data, discrepancies
- `NetworkGraph.tsx` — Force-directed graph of politician connections
- (Add) `SearchResults.tsx` — Semantic search result display
- (Add) `ScoreHistory.tsx` — Time-series chart of Honesty scores

## Data serving patterns

### Pagination
All list endpoints should support `limit` and `offset` query params. Return:
```json
{
  "data": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

### Profile assembly
The politician profile endpoint should join data from multiple tables:
1. `politicians` — core identity
2. `disclosure.transaction` — stock trades
3. `finance.contribution` — campaign contributors
4. `leg.bill` — sponsored legislation
5. Honesty scores — latest + history

### Error handling
- Return structured error responses: `{"detail": "message", "code": "ERROR_CODE"}`
- Log all 500s with full traceback to stderr.
- Rate limit at 100 req/min per IP.

## Dashboard styling
- Tailwind CSS with a dark theme (see `src/dashboard/src/index.css`).
- Network graph uses a force-directed layout (D3.js or vis.js).
- Politician cards show party color-coded borders (blue/red/gray).

## Prompting template
- "Add a new API endpoint that returns the top 10 most-discrepant politicians (highest severity × frequency)."
- "Create a React component that displays the Honesty Score history as a line chart over time."
- "Wire up the semantic search input on the dashboard to the Qdrant-backed API endpoint."
- "Add pagination to the politician list endpoint and update the dashboard table component."
- "Build a network graph endpoint that returns committee co-memberships and donor overlaps."