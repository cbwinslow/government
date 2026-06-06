#!/usr/bin/env python3
"""
Financial Disclosures dlt Pipeline
Parses zip files from financial-disclosures/ and loads them into Postgres.
"""

import os
import zipfile
import csv
import dlt
from typing import Iterator, Dict, Any

FD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../financial-disclosures/'))

@dlt.source
def financial_disclosures_source():
    """Generates a dlt source reading from the ZIP archives."""
    
    @dlt.resource(name="house_financial_disclosures", write_disposition="append")
    def read_disclosures() -> Iterator[Dict[str, Any]]:
        # Iterate over 2008FD.zip to 2026FD.zip
        for year in range(2008, 2027):
            zip_name = f"{year}FD.zip"
            zip_path = os.path.join(FD_DIR, zip_name)
            
            if not os.path.exists(zip_path):
                continue
                
            print(f"Processing {zip_name}...")
            
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Inside the zip, the file is typically named {year}FD.txt
                txt_name = f"{year}FD.txt"
                if txt_name in z.namelist():
                    with z.open(txt_name) as f:
                        # Decode bytes to string
                        content = f.read().decode('utf-8', errors='replace').splitlines()
                        # Usually tab delimited: Prefix, Last, First, DocType, Year, DocID
                        reader = csv.DictReader(content, delimiter='\t')
                        for row in reader:
                            if not row:
                                continue
                            
                            # Clean up keys and yield
                            clean_row = {k.strip().lower() if k else 'unknown': v.strip() for k, v in row.items()}
                            # Assign the year explicitly since it might be missing
                            clean_row['filing_year'] = year
                            yield clean_row

    return [read_disclosures()]

def main():
    print("Initializing Financial Disclosures Pipeline...")
    pipeline = dlt.pipeline(
        pipeline_name='financials_pipeline',
        destination='postgres',
        dataset_name='financial_data'
    )
    
    info = pipeline.run(financial_disclosures_source())
    print(info)

if __name__ == "__main__":
    main()
