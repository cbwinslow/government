import os
import json
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text

# Initialize FastMCP Server
mcp = FastMCP(
    "OpenDiscourse Database",
    dependencies=["sqlalchemy", "psycopg2-binary"],
    description="Provides tools to query the 1.5TB OpenDiscourse Postgres database for political and financial intelligence."
)

# Database Connection
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://govadmin:govpassword@172.25.10.64:5433/govdata"
)
engine = create_engine(DATABASE_URL)

@mcp.tool()
def query_epstein_overlap(limit: int = 50) -> str:
    """
    Query the direct financial and networking overlaps between sitting politicians 
    and known associates from the Jeffrey Epstein flight logs.
    
    Args:
        limit: The maximum number of records to return.
    """
    query = f"""
        SELECT filing_year, first_name, last_name, epstein_associate_name, associate_role
        FROM public_network_mapping.epstein_overlap
        LIMIT {limit};
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            if not result:
                return "No overlaps found."
            
            # Format as JSON string
            data = [dict(row._mapping) for row in result]
            return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return f"Database error: {str(e)}"

@mcp.tool()
def query_financial_disclosures(last_name: str, limit: int = 10) -> str:
    """
    Search for all financial disclosures, stock trades, and donations made by a 
    specific politician or entity. Use this to track insider trading.
    
    Args:
        last_name: The last name of the politician or entity to search.
        limit: The maximum number of records to return.
    """
    query = f"""
        SELECT docid, filing_year, first, last, filingtype, statenumber, district
        FROM financial_data.house_financial_disclosures
        WHERE last ILIKE '%{last_name}%'
        LIMIT {limit};
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            if not result:
                return f"No financial disclosures found for {last_name}."
            
            data = [dict(row._mapping) for row in result]
            return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return f"Database error: {str(e)}"

@mcp.tool()
def query_openstates_bills(state_abbr: str, limit: int = 10) -> str:
    """
    Query recent bills ingested from the OpenStates state-level API.
    
    Args:
        state_abbr: The two-letter state abbreviation (e.g., 'nc', 'va', 'ny').
        limit: The maximum number of records to return.
    """
    # OpenStates schema uses the jurisdiction ID, but for simplicity we will query 
    # the opencivicdata_bill table.
    query = f"""
        SELECT identifier, title, classification, created_at
        FROM opencivicdata_bill
        WHERE extras->>'state' = '{state_abbr.lower()}' OR identifier IS NOT NULL
        ORDER BY created_at DESC
        LIMIT {limit};
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            if not result:
                return f"No bills found for state {state_abbr}."
            
            data = [dict(row._mapping) for row in result]
            return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return f"Database error: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server over standard I/O for Claude Desktop integration
    print("OpenDiscourse MCP Server initialized.", flush=True)
    mcp.run(transport='stdio')
