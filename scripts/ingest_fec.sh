#!/bin/bash
# FEC Bulk Data Ingestion Pipeline (2000 to Present)
# Downloads all individual, corporate, PAC, and expenditure data

set -e

STORAGE_DIR="/home/cbwinslow/workspace/government/fec_bulk_data"
mkdir -p "$STORAGE_DIR"
cd "$STORAGE_DIR"

echo "================================================="
echo "Starting FEC Bulk Data Mass Ingestion (2000-2024)"
echo "================================================="

# FEC cycles run every 2 years (2000, 2002, 2004...)
for YEAR in {2000..2024..2}; do
    # Get the last two digits of the year (e.g., 2000 -> 00)
    YY=$(printf "%02d" $((YEAR % 100)))
    
    echo "Downloading Cycle $YEAR ($YY)..."
    
    # 1. Individual Contributions (indiv)
    wget -nc -q --show-progress "https://www.fec.gov/files/bulk-downloads/${YEAR}/indiv${YY}.zip" || echo "Failed to download indiv${YY}"
    
    # 2. PAC to Candidate Contributions (pas2)
    wget -nc -q --show-progress "https://www.fec.gov/files/bulk-downloads/${YEAR}/pas2${YY}.zip" || echo "Failed to download pas2${YY}"
    
    # 3. PAC to PAC / Other Committee Contributions (oth)
    wget -nc -q --show-progress "https://www.fec.gov/files/bulk-downloads/${YEAR}/oth${YY}.zip" || echo "Failed to download oth${YY}"
    
    # 4. Operating Expenditures (oppexp)
    wget -nc -q --show-progress "https://www.fec.gov/files/bulk-downloads/${YEAR}/oppexp${YY}.zip" || echo "Failed to download oppexp${YY}"
done

echo "================================================="
echo "FEC Bulk Data Ingestion Complete."
echo "Data is stored in $STORAGE_DIR."
echo "================================================="
