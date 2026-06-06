from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add StockInsightsTracker to path to reuse some nancy.py logic if needed, 
# or we'll just mock the periodic loop for the demo.
sys.path.append("/home/cbwinslow/workspace/government/financial-disclosures/StockInsightsTracker")
import nancy
from market_data_server import get_market_data

load_dotenv("/home/cbwinslow/workspace/government/financial-disclosures/StockInsightsTracker/.env")

app = FastAPI(title="Trade Monitor WebSocket Server")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

async def poll_house_clerk_loop():
    """Background task that runs the nancy.py logic periodically and broadcasts over WS."""
    # We will poll every 60 seconds
    while True:
        try:
            # We mock the nancy.py check_for_new_trades() call.
            # In a real environment, we'd call nancy.check_for_new_trades()
            # For demonstration of the pipeline, we'll fetch the live market data for a known stock
            
            # Let's say nancy.py detected Pelosi bought AAPL today:
            mock_trade = {
                "member_name": "Pelosi, Nancy",
                "ticker": "AAPL",
                "transaction_date": datetime.now().strftime("%Y-%m-%d"),
                "amount_range": "$1,000,001 - $5,000,000",
                "transaction_type": "Purchase",
                "doc_id": "20024567"
            }
            
            # 1. Agent intercepts trade.
            # 2. Agent asks MarketDataAgent for context.
            print(f"Trade Monitor Agent detected trade for {mock_trade['ticker']}. Requesting Market Context...")
            market_context = get_market_data(mock_trade["ticker"])
            
            # 3. Enrich payload
            enriched_payload = {
                "trade": mock_trade,
                "market_context": market_context,
                "timestamp": datetime.now().isoformat()
            }
            
            # 4. Broadcast to LangGraph Orchestrator / Dashboard
            if manager.active_connections:
                print("Broadcasting enriched trade to WebSockets...")
                await manager.broadcast(enriched_payload)
            
        except Exception as e:
            print(f"Error in polling loop: {e}")
            
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    # Start the polling background task
    asyncio.create_task(poll_house_clerk_loop())

@app.websocket("/ws/trades")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We just keep the connection open, waiting for client messages if any
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("trade_monitor_ws:app", host="0.0.0.0", port=8081, reload=True)
