#!/usr/bin/env python3
"""Background daemon that continuously schedules the LangGraph swarm to poll for updates."""

import sys
import os
import time
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from opendiscourse.swarm.graph import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def trigger_swarm(task_name: str, payload_request: str):
    """Triggers the LangGraph swarm with a specific request."""
    logger.info(f"--- Triggering Swarm Task: {task_name} ---")
    
    initial_state = {
        "user_request": payload_request,
        "messages": [{"role": "user", "content": payload_request}],
        "downloaded_files": [],
        "errors": []
    }
    
    # Optional Langfuse Observability
    config = {}
    if os.environ.get("LANGFUSE_SECRET_KEY"):
        try:
            from langfuse.callback import CallbackHandler
            langfuse_handler = CallbackHandler()
            config["callbacks"] = [langfuse_handler]
            logger.info("Langfuse Observability Active: Tracing execution")
        except ImportError:
            pass
    
    # Stream the state updates as nodes execute
    for s in app.stream(initial_state, config=config):
        if "__end__" not in s:
            node_name = list(s.keys())[0]
            node_state = s[node_name]
            logger.info(f"Node Executed: {node_name}")
            if "status" in node_state:
                logger.info(f"Status: {node_state['status']}")
            if "messages" in node_state and len(node_state["messages"]) > 0:
                logger.info(f"Message: {node_state['messages'][-1]['content']}")
                
    logger.info(f"--- Swarm Task {task_name} Complete ---\n")


def check_congress_updates():
    """Polls congress for delta updates."""
    trigger_swarm("Congress_Delta_Sync", "Please poll GovInfo for any new bills or updates since the last sync.")

def check_courtlistener_updates():
    """Polls CourtListener for docket updates."""
    trigger_swarm("CourtListener_Delta_Sync", "Please poll CourtListener for new dockets involving politicians.")

def main():
    logger.info("Starting LangGraph Swarm Polling Daemon...")
    
    scheduler = BackgroundScheduler()
    
    # Schedule the Congress sync every 6 hours
    scheduler.add_job(check_congress_updates, 'interval', hours=6, id='congress_sync')
    
    # Schedule the CourtListener sync every 12 hours
    scheduler.add_job(check_courtlistener_updates, 'interval', hours=12, id='courtlistener_sync')
    
    scheduler.start()
    
    # For testing purposes, let's trigger a run immediately
    logger.info("Executing initial immediate sync for testing...")
    check_congress_updates()
    
    try:
        # Keep the main thread alive while the background scheduler runs
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Daemon gracefully shut down.")

if __name__ == "__main__":
    main()
