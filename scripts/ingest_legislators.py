#!/usr/bin/env python3
"""dlt pipeline to ingest Congress legislators from YAML into Postgres."""

import os
import yaml
import dlt

def load_yaml(file_path: str):
    """Yields records from a YAML file."""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        for record in data:
            yield record

def load_all_yaml():
    base_dir = os.path.join(os.path.dirname(__file__), '../congress/congress-legislators')
    yield from load_yaml(os.path.join(base_dir, 'legislators-current.yaml'))
    yield from load_yaml(os.path.join(base_dir, 'legislators-historical.yaml'))

@dlt.source
def congress_legislators_source():
    """Defines the dlt source for Congress legislators."""
    return [
        dlt.resource(
            load_all_yaml(),
            name="legislators",
            write_disposition="merge",
            primary_key="id__bioguide" # dlt flattens nested dicts with double underscores
        )
    ]

def main():
    print("Initializing dlt pipeline for Congress Legislators...")
    # This automatically picks up the secrets from .dlt/secrets.toml
    pipeline = dlt.pipeline(
        pipeline_name='congress_pipeline',
        destination='postgres',
        dataset_name='congress_data' # Schema name in Postgres
    )
    
    info = pipeline.run(congress_legislators_source())
    print(info)

if __name__ == "__main__":
    main()
