#!/usr/bin/env bash

# start_backend.sh
# Quickly spins up all background ingestion and monitoring agents

# Start PostgREST
nohup ./postgrest postgrest.conf > .system_generated/tasks/postgrest.log 2>&1 &

# Start Swarm Daemon
nohup uv run python scripts/swarm_daemon.py > .system_generated/tasks/swarm_daemon.log 2>&1 &

# Start Trade Monitor WebSocket
nohup uv run python scripts/trade_monitor_ws.py > .system_generated/tasks/trade_monitor.log 2>&1 &

# Start Postgres Price Trigger Worker
nohup uv run python scripts/price_trigger_worker.py > .system_generated/tasks/price_trigger.log 2>&1 &

# Start OpenStates Scraper
nohup ./scripts/ingest_openstates.sh ALL > .system_generated/tasks/openstates.log 2>&1 &

echo "Backend services started successfully!"
