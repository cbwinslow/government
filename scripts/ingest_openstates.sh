#!/bin/bash
# OpenStates Scraper Orchestration Wrapper
# Automatically injects ZeroTier Postgres credentials

if [[ $# -lt 1 ]]; then
    echo "Usage: ./ingest_openstates.sh [state_abbreviation] [data_type]"
    echo "Example: ./ingest_openstates.sh nc bills"
    echo "Example: ./ingest_openstates.sh ca votes"
    exit 1
fi

STATE=$1
DATA_TYPE=${2:-bills}

# Inject API Keys and Database URLs
export OPENSTATES_API_KEY="a4cffebb-1787-481f-be4c-762638ed0a7f"
export DATABASE_URL="postgresql://cbwinslow:123qweasd@172.25.10.64:5432/govdata"

SCRAPER_DIR="/home/cbwinslow/workspace/government/openstates-monorepo/openstates-scrapers"
cd "$SCRAPER_DIR"

echo "================================================="
echo "Initializing OpenStates Database Schema in govdata"
echo "================================================="
# This safely creates the schema if it doesn't exist
poetry run os-initdb

# The core openstates CLI requires PYTHONPATH to include the scrapers directory

ALL_STATES="al ak az ar ca co ct de fl ga hi id il in ia ks ky la me md ma mi mn ms mo mt ne nv nh nj nm ny nc nd oh ok or pa ri sc sd tn tx ut vt va wa wv wi wy"

if [ "$STATE" = "ALL" ]; then
    STATES_TO_RUN=$ALL_STATES
else
    # Replace commas with spaces
    STATES_TO_RUN=${STATE//,/ }
fi

TYPES_TO_RUN="bills votes people organizations events"

for s in $STATES_TO_RUN; do
    echo "================================================="
    echo "Starting OpenStates Master Scrape: State=$s"
    echo "================================================="
    for t in $TYPES_TO_RUN; do
        echo "--> Scraping $t for $s"
        PYTHONPATH=scrapers/ poetry run os-update $s $t
    done
    echo "================================================="
    echo "OpenStates Scrape Complete for $s"
    echo "================================================="
done
