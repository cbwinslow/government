import pandas as pd
from sqlalchemy import create_engine
import os
import time

DATABASE_URL = "postgresql://govadmin:govpassword@172.25.10.64:5433/govdata"
DATA_DIR = "/home/cbwinslow/workspace/government/financial-disclosures/congress-trading-monitor/public/data"

def ingest_trades():
    print("=================================================")
    print("Starting Historical Insider Trades Ingestion")
    print("=================================================")
    
    engine = create_engine(DATABASE_URL)
    
    trades_file = os.path.join(DATA_DIR, "trades.json")
    print(f"--> Reading {trades_file}")
    df_trades = pd.read_json(trades_file)
    
    print(f"--> Loaded {len(df_trades)} trades. Pushing to Postgres 'insider_trades' table...")
    df_trades.to_sql("insider_trades", engine, schema="financial_data", if_exists="replace", index=False)
    
    print("--> Trades ingested successfully.")
    
    prices_file = os.path.join(DATA_DIR, "prices.json")
    if os.path.exists(prices_file):
        print(f"--> Reading {prices_file}")
        # prices.json might be a dict of tickers to prices, let's load it appropriately
        # If it's complex, we'll just push the raw json or flatten it
        try:
            df_prices = pd.read_json(prices_file)
            df_prices.to_sql("historical_prices", engine, schema="financial_data", if_exists="replace", index=False)
            print("--> Prices ingested successfully.")
        except Exception as e:
            print(f"--> Skipping prices due to complex JSON structure: {e}")
            
    print("=================================================")
    print("Ingestion Complete.")
    print("=================================================")

if __name__ == "__main__":
    ingest_trades()
