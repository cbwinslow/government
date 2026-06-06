from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="OpenDiscourse API Bridge")

# Allow React dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = "postgresql://govadmin:govpassword@172.25.10.64:5433/govdata"

def get_db_connection():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "OpenDiscourse API Bridge is running."}

@app.get("/api/network/epstein")
def get_epstein_network():
    """Returns the correlated Epstein financial overlap view."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # We query the dbt-generated view
            cur.execute("""
                SELECT 
                    filing_year, 
                    first_name, 
                    last_name, 
                    epstein_associate_name, 
                    associate_role
                FROM public_network_mapping.epstein_overlap
                LIMIT 1000;
            """)
            rows = cur.fetchall()
            return {"data": rows}
    finally:
        conn.close()

@app.get("/api/finance/stats")
def get_finance_stats():
    """Returns aggregate financial disclosure stats."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT filing_year, COUNT(*) as disclosure_count
                FROM financial_data.house_financial_disclosures
                WHERE filing_year IS NOT NULL
                GROUP BY filing_year
                ORDER BY filing_year DESC;
            """)
            rows = cur.fetchall()
            return {"data": rows}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
