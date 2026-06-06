import yfinance as yf
import json
import argparse
import sys

def get_market_data(ticker):
    """Fetch current price, volume, and 50-day moving average for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        # Get historical data for the last 50 days to calculate the moving average
        hist = stock.history(period="50d")
        
        if hist.empty:
            return {"ticker": ticker, "error": "No data found for ticker"}
            
        current_price = float(hist['Close'].iloc[-1])
        daily_volume = int(hist['Volume'].iloc[-1])
        fifty_day_ma = float(hist['Close'].mean())
        
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "daily_volume": daily_volume,
            "fifty_day_ma": round(fifty_day_ma, 2)
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Market Data Tool")
    parser.add_argument("--ticker", type=str, help="Stock Ticker (e.g., AAPL)")
    args = parser.parse_args()
    
    if args.ticker:
        result = get_market_data(args.ticker)
        print(json.dumps(result))
    else:
        # Read from stdin if no arg provided (useful for MCP/Langchain integration)
        input_data = sys.stdin.read().strip()
        if input_data:
            result = get_market_data(input_data)
            print(json.dumps(result))
        else:
            print(json.dumps({"error": "No ticker provided"}))
