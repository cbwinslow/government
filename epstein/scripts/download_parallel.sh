#!/bin/bash
# Parallel download script for Epstein datasets
# Uses multiple background processes to maximize server throughput

set -e

SCRIPT_DIR="/home/cbwinslow/workspace/government/epstein"
VENV="$SCRIPT_DIR/.venv/bin/python"

echo "Starting parallel downloads at $(date)"

# Download 1: notesbymuneeb full (5,082 emails)
$VENV $SCRIPT_DIR/download_hf_epstein.py --dataset "notesbymuneeb/epstein-emails" --max-samples 5082 > /tmp/notesbymuneeb_download.log 2>&1 &
PID1=$!
echo "Started notesbymuneeb download (PID: $PID1)"

# Download 2: 567-labs DOJ data
$VENV $SCRIPT_DIR/download_hf_epstein.py --dataset "567-labs/epstein-doj" --max-samples 5000 > /tmp/epstein-doj_download.log 2>&1 &
PID2=$!
echo "Started epstein-doj download (PID: $PID2)"

# Download 3: 567-labs House Oversight
$VENV $SCRIPT_DIR/download_hf_epstein.py --dataset "567-labs/epstein-house-oversight" --max-samples 5000 > /tmp/epstein-house_download.log 2>&1 &
PID3=$!
echo "Started epstein-house-oversight download (PID: $PID3)"

# Download 4: 567-labs Email
$VENV $SCRIPT_DIR/download_hf_epstein.py --dataset "567-labs/epstein-email" --max-samples 5000 > /tmp/epstein-email_download.log 2>&1 &
PID4=$!
echo "Started epstein-email download (PID: $PID4)"

# Download 5: kabasshouse text (1.42M, get 50K for now)
$VENV $SCRIPT_DIR/download_hf_epstein.py --dataset "kabasshouse/epstein-data" --max-samples 50000 > /tmp/kabasshouse_download.log 2>&1 &
PID5=$!
echo "Started kabasshouse download (PID: $PID5)"

# Download 6: Nikity text (5.4M, get 50K for now)
$VENV $SCRIPT_DIR/download_hf_epstein.py --dataset "Nikity/Epstein-Files" --max-samples 50000 > /tmp/nikity_download.log 2>&1 &
PID6=$!
echo "Started Nikity download (PID: $PID6)"

echo ""
echo "Waiting for downloads to complete..."
wait $PID1 || echo "notesbymuneeb: check /tmp/notesbymuneeb_download.log"
wait $PID2 || echo "epstein-doj: check /tmp/epstein-doj_download.log"
wait $PID3 || echo "epstein-house-oversight: check /tmp/epstein-house_download.log"
wait $PID4 || echo "epstein-email: check /tmp/epstein-email_download.log"
wait $PID5 || echo "kabasshouse: check /tmp/kabasshouse_download.log"
wait $PID6 || echo "Nikity: check /tmp/nikity_download.log"

echo ""
echo "All downloads completed at $(date)"
echo "Check logs in /tmp/ for any errors"