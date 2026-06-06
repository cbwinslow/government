import json
import pandas as pd
from sqlalchemy import create_engine
import os

DATABASE_URL = "postgresql://govadmin:govpassword@172.25.10.64:5433/govdata"
DATA_DIR = "/home/cbwinslow/workspace/government/financial-disclosures/congress-trading-monitor/public/data"

def ingest_prices():
    print("=================================================")
    print("Starting Prices JSON Normalization & Ingestion")
    print("=================================================")
    
    engine = create_engine(DATABASE_URL)
    prices_file = os.path.join(DATA_DIR, "prices.json")
    
    print(f"--> Reading {prices_file}")
    with open(prices_file, 'r') as f:
        raw_data = json.load(f)
        
    normalized_records = []
    
    # Parse the nested JSON structure
    # Format: {"AAPL": {"latest": {"date": "...", "close": ...}, "previous": {...}, "month": {...}}}
    print("--> Normalizing data...")
    for ticker, periods in raw_data.items():
        for period_name, data in periods.items():
            if isinstance(data, dict) and "date" in data and "close" in data:
                normalized_records.append({
                    "ticker": ticker,
                    "period": period_name,
                    "date": data["date"],
                    "close": data["close"]
                })
                
    df_prices = pd.DataFrame(normalized_records)
    print(f"--> Extracted {len(df_prices)} price records.")
    
    print("--> Pushing to Postgres 'historical_prices' table...")
    df_prices.to_sql("historical_prices", engine, schema="financial_data", if_exists="replace", index=False, chunksize=10000)
    
    print("=================================================")
    print("Prices Ingestion Complete.")
    print("=================================================")

if __name__ == "__main__":
    ingest_prices()
