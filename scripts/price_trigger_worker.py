import json
import time
import logging
import psycopg
import yfinance as yf
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = "postgresql://govadmin:govpassword@172.25.10.64:5433/govdata"

def fetch_and_insert_price(ticker, trade_date_str, conn):
    if not ticker:
        return
        
    try:
        # yfinance expects YYYY-MM-DD strings
        # We need end date to be the day after to get the range
        trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d").date()
        logger.info(f"Fetching {ticker} price for {trade_date}...")
        
        stock = yf.Ticker(ticker)
        # We just grab a small 5-day window around the trade date just in case it falls on a weekend
        hist = stock.history(start=trade_date.isoformat(), periods=5)
        
        if hist.empty:
            logger.warning(f"No price data found for {ticker} around {trade_date}")
            return
            
        # Get the first available trading day price on or after the trade date
        row = hist.iloc[0]
        close_price = float(row['Close'])
        volume = int(row['Volume'])
        
        # Insert into historical_prices
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO financial_data.historical_prices 
                (ticker, trade_date, close_price, volume, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ticker, trade_date) DO NOTHING;
            """, (ticker, trade_date.isoformat(), close_price, volume, 'yfinance_trigger'))
            conn.commit()
            
        logger.info(f"Successfully inserted {ticker} price: ${close_price:.2f}")
        
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")

def listen_loop():
    logger.info("Connecting to Postgres (government database)...")
    try:
        # We use autocommit=True so LISTEN doesn't block the transaction
        conn = psycopg.connect(DB_URL, autocommit=True)
        cur = conn.cursor()
        
        logger.info("Setting up Postgres trigger on insider_trades...")
        # 1. Create the trigger function
        cur.execute("""
            CREATE OR REPLACE FUNCTION notify_new_trade() RETURNS trigger AS $$
            DECLARE
                payload json;
            BEGIN
                payload = json_build_object(
                    'ticker', NEW.ticker,
                    'transaction_date', NEW.transaction_date
                );
                PERFORM pg_notify('new_trade_channel', payload::text);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # 2. Attach it to the table
        cur.execute("""
            DROP TRIGGER IF EXISTS trg_notify_new_trade ON financial_data.insider_trades;
            CREATE TRIGGER trg_notify_new_trade
            AFTER INSERT ON financial_data.insider_trades
            FOR EACH ROW EXECUTE FUNCTION notify_new_trade();
        """)
        
        logger.info("Trigger setup complete. Listening on 'new_trade_channel'...")
        cur.execute("LISTEN new_trade_channel;")
        
        # Use generator to block and wait for notifications
        gen = conn.notifies()
        for notify in gen:
            payload = json.loads(notify.payload)
            ticker = payload.get("ticker")
            t_date = payload.get("transaction_date")
            
            if ticker and t_date:
                # We need a separate connection/transaction to insert the data since this one is autocommit for LISTEN
                with psycopg.connect(DB_URL) as insert_conn:
                    fetch_and_insert_price(ticker, t_date, insert_conn)
                    
    except Exception as e:
        logger.error(f"Listener error: {e}")
        time.sleep(5)
        listen_loop() # Reconnect on crash

if __name__ == "__main__":
    listen_loop()
