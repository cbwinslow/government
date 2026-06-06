#!/bin/bash
# Mass Sync Script for GovInfo/Congress Data (Year 2000 to Present)
# Congresses 106 to 119

set -e

CONGRESS_DIR="/home/cbwinslow/workspace/government/congress/congress"
cd "$CONGRESS_DIR"
uv pip install -r requirements.txt || uv pip install .

echo "============================================="
echo "Starting Mass Sync of GovInfo Bulk Data"
echo "============================================="
uv run ./run govinfo --bulkdata=BILLSTATUS,CREC,COMMITTEEPUB,CHRG,CPROT,TREATIES,PLAW,CDIR

echo "============================================="
echo "Starting Mass Sync of Bills (106 to 119)"
echo "============================================="

for c in {106..119}; do
    echo "Processing Congress $c..."
    uv run ./run bills --congress=$c
    echo "Congress $c complete."
done

echo "============================================="
echo "Starting Mass Sync of Roll Call Votes (106 to 119)"
echo "============================================="

for c in {106..119}; do
    echo "Processing Votes for Congress $c..."
    uv run ./run votes --congress=$c
    echo "Votes for Congress $c complete."
done

echo "Mass Sync Complete!"
