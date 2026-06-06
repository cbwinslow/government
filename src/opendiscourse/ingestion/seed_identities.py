"""
Identity Seeding Script.

This script traverses the `openstates-monorepo/people/data` directory, parses
every YAML file representing a politician, and upserts them into the Master
Identity table in PostgreSQL.

This completely automates the process of mapping OpenStates IDs to Bioguide,
FEC, OpenSecrets, and VoteSmart IDs without relying on fragile web scraping.
"""

import os
import glob
import yaml
import logging
from sqlalchemy.orm import Session
from opendiscourse.models.database import get_engine, Politician, Base

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_identifier(identifiers: list, scheme: str) -> str:
    """Helper to extract a specific ID scheme from the other_identifiers list."""
    for ident in identifiers:
        if ident.get("scheme") == scheme:
            return str(ident.get("identifier"))
    return None

def seed_identities(people_data_dir: str):
    """Parse all YAML files in the given directory and seed the database."""
    engine = get_engine()
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    yaml_files = glob.glob(os.path.join(people_data_dir, "**", "*.yml"), recursive=True)
    logger.info(f"Found {len(yaml_files)} politician YAML files. Commencing ingestion...")
    
    upsert_count = 0
    
    with Session(engine) as session:
        for file_path in yaml_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    
                if not data:
                    continue
                    
                openstates_id = data.get("id")
                if not openstates_id:
                    continue
                    
                # Extract basic info
                first_name = data.get("given_name", "")
                last_name = data.get("family_name", "")
                
                if not first_name or not last_name:
                    # Fallback to splitting 'name' if given/family missing
                    name_parts = data.get("name", "Unknown").split()
                    if name_parts:
                        first_name = first_name or name_parts[0]
                        last_name = last_name or (" ".join(name_parts[1:]) if len(name_parts) > 1 else "")
                
                # Extract party
                party = None
                parties = data.get("party", [])
                if parties:
                    party = parties[0].get("name")
                    
                # Extract external IDs
                other_ids = data.get("other_identifiers", [])
                bioguide_id = get_identifier(other_ids, "bioguide")
                fec_id = get_identifier(other_ids, "fec")
                opensecrets_id = get_identifier(other_ids, "opensecrets")
                votesmart_id = get_identifier(other_ids, "votesmart")
                
                # Check if politician already exists by openstates_id
                politician = session.query(Politician).filter(Politician.openstates_id == openstates_id).first()
                
                if politician:
                    # Update existing
                    politician.first_name = first_name
                    politician.last_name = last_name
                    politician.party = party
                    politician.bioguide_id = bioguide_id or politician.bioguide_id
                    politician.fec_id = fec_id or politician.fec_id
                    politician.opensecrets_id = opensecrets_id or politician.opensecrets_id
                    politician.votesmart_id = votesmart_id or politician.votesmart_id
                else:
                    # Insert new
                    politician = Politician(
                        first_name=first_name,
                        last_name=last_name,
                        party=party,
                        openstates_id=openstates_id,
                        bioguide_id=bioguide_id,
                        fec_id=fec_id,
                        opensecrets_id=opensecrets_id,
                        votesmart_id=votesmart_id
                    )
                    session.add(politician)
                
                upsert_count += 1
                
                # Commit in batches of 500
                if upsert_count % 500 == 0:
                    session.commit()
                    logger.info(f"Processed {upsert_count} politicians...")
                    
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                
        # Final commit
        session.commit()
        logger.info(f"Ingestion complete! Successfully upserted {upsert_count} politicians into the Master Identity table.")

if __name__ == "__main__":
    # Assuming script is run from the workspace root or handles relative paths
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../openstates-monorepo/people/data"))
    seed_identities(data_dir)
