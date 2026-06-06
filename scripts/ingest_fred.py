#!/usr/bin/env python3
"""
Config-Driven dlt pipeline to ingest Federal Reserve Economic Data (FRED).
"""

import os
import yaml
import dlt
import requests
from typing import Iterator, Dict, Any

def load_config() -> Dict[str, Any]:
    """Loads the pipeline configurations from YAML."""
    config_path = os.path.join(os.path.dirname(__file__), '../config/pipelines.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@dlt.source
def fred_source(api_key: str = dlt.secrets.value):
    """
    Dynamically generates dlt resources for FRED endpoints based on pipelines.yaml
    """
    config = load_config()
    fred_config = config['pipelines']['fred_economic']
    
    if not fred_config.get('enabled', False):
        print("FRED pipeline is disabled in config.")
        return []

    base_url = fred_config['base_url']
    endpoints = fred_config['endpoints']
    
    resources = []
    
    for series_id in endpoints:
        
        @dlt.resource(name=f"fred_{series_id.lower()}", write_disposition="merge", primary_key="date")
        def fetch_series(series=series_id):
            """Generator that fetches the FRED observations for a series."""
            print(f"Fetching {series} from FRED...")
            
            # If no API key is provided via secrets.toml, yield mock data for demonstration
            if not api_key or api_key == "mock":
                print(f"No API key provided for FRED. Yielding mock data for {series}.")
                yield {"date": "2026-05-01", "value": "100.5", "realtime_start": "2026-05-01"}
                yield {"date": "2026-06-01", "value": "101.2", "realtime_start": "2026-06-01"}
                return
                
            params = {
                "series_id": series,
                "api_key": api_key,
                "file_type": "json"
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            # Yield each observation as a separate row
            for obs in data.get('observations', []):
                yield {
                    "date": obs["date"],
                    "value": obs["value"],
                    "realtime_start": obs["realtime_start"],
                    "realtime_end": obs["realtime_end"]
                }
                
        resources.append(fetch_series)
        
    return resources

def main():
    print("Initializing FRED Economic Data Pipeline...")
    config = load_config()['pipelines']['fred_economic']
    
    # We dynamically load the schema/destination from the yaml
    pipeline = dlt.pipeline(
        pipeline_name='fred_pipeline',
        destination=config['destination'],
        dataset_name=config['schema']
    )
    
    # Note: dlt automatically injects the API key from .dlt/secrets.toml if available
    # We'll pass 'mock' to demonstrate the flow without requiring the user to sign up immediately.
    info = pipeline.run(fred_source(api_key="mock"))
    print(info)

if __name__ == "__main__":
    main()
