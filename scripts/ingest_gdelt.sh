#!/bin/bash
set -e

# GDELT V2 Master Ingestion Script
# This script downloads the GDELT 2.0 master file list and begins processing events

DATA_DIR="./data/gdelt"
mkdir -p "$DATA_DIR"

echo "================================================="
echo "Starting GDELT Master Ingestion Pipeline"
echo "================================================="

# Download the master file list
echo "--> Downloading GDELT 2.0 Master File List..."
curl -s -o "$DATA_DIR/masterfilelist.txt" http://data.gdeltproject.org/gdeltv2/masterfilelist.txt

echo "--> Master file list downloaded. Total files:"
wc -l "$DATA_DIR/masterfilelist.txt"

# For now, let's grab the latest 5 updates (every 15 mins)
echo "--> Extracting the latest 5 export zips..."
tail -n 15 "$DATA_DIR/masterfilelist.txt" | grep "export.CSV.zip" | tail -n 5 > "$DATA_DIR/latest_exports.txt"

while IFS= read -r line; do
    # format: <size> <hash> <url>
    url=$(echo "$line" | awk '{print $3}')
    filename=$(basename "$url")
    
    echo "    Downloading $filename..."
    curl -s -o "$DATA_DIR/$filename" "$url"
    unzip -o -q "$DATA_DIR/$filename" -d "$DATA_DIR/raw"
done < "$DATA_DIR/latest_exports.txt"

echo "================================================="
echo "GDELT Ingestion Complete."
echo "Raw events extracted to $DATA_DIR/raw"
echo "Next step: Connect to Postgres / Qdrant."
echo "================================================="
