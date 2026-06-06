#!/usr/bin/env python3
"""
GDELT GKG Ingestion Pipeline for Epstein Research

Downloads Global Knowledge Graph (GKG) data from GDELT Project,
extracts Epstein-related news articles, and ingests into PostgreSQL.

Source: http://data.gdeltproject.org/gdeltv2/
Data Type: GKG 2.0 (15-minute slices)
Coverage: February 2015 - Present

Usage:
    python3 gdelt_ingestion_pipeline.py --start-date 2019-07-06 --end-date 2019-08-31

Author: Research Team
Date: 2025-04-10
"""

import os
import re
import csv
import json
import asyncio
import asyncpg
import zipfile
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DOWNLOAD_DIR = Path("/home/cbwinslow/workspace/epstein-data/gdelt/raw")
EXTRACT_DIR = Path("/home/cbwinslow/workspace/epstein-data/gdelt/extracted")
GDELT_V2_BASE = "http://data.gdeltproject.org/gdeltv2"

# Database connection
DB_URL = os.getenv("DATABASE_URL", "postgresql://cbwinslow:123qweasd@localhost:5432/epstein")

# Epstein-related search terms (case-insensitive)
EPSTEIN_TERMS = [
    'epstein',
    'maxwell',
    'ghislaine',
    'giuffre',
    'virginia roberts',
    'les wexner',
    'alan dershowitz',
    'prince andrew',
    'little st. james',
    'zorro ranch',
    'lolita express',
    'jeffrey e.',
    'j. epstein',
    'epstein island'
]

# Ensure directories exist
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class GKGRecord:
    """Represents a GDELT GKG record."""
    gkg_record_id: str
    date: datetime
    source_collection_identifier: str
    source_common_name: str
    document_identifier: str  # URL
    counts: str
    enhanced_theme: str
    enhanced_location: str
    enhanced_person: str
    enhanced_organization: str
    tone: str
    
    @property
    def url(self) -> str:
        return self.document_identifier
    
    def extract_entities(self) -> Dict:
        """Extract named entities from GKG record."""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'themes': []
        }
        
        # Parse persons (semicolon-separated, format: name,count)
        if self.enhanced_person:
            for person_entry in self.enhanced_person.split(';'):
                if ',' in person_entry:
                    person = person_entry.split(',')[0].strip()
                    if person:
                        entities['persons'].append(person)
        
        # Parse organizations
        if self.enhanced_organization:
            for org_entry in self.enhanced_organization.split(';'):
                if ',' in org_entry:
                    org = org_entry.split(',')[0].strip()
                    if org:
                        entities['organizations'].append(org)
        
        # Parse locations
        if self.enhanced_location:
            for loc_entry in self.enhanced_location.split(';'):
                if '#' in loc_entry:
                    loc_parts = loc_entry.split('#')
                    if len(loc_parts) >= 2:
                        entities['locations'].append(loc_parts[1])
        
        # Parse themes
        if self.enhanced_theme:
            entities['themes'] = [t.strip() for t in self.enhanced_theme.split(',') if t.strip()]
        
        return entities
    
    def has_epstein_terms(self) -> bool:
        """Check if record contains Epstein-related terms."""
        search_text = ' '.join([
            self.enhanced_person or '',
            self.enhanced_organization or '',
            self.document_identifier or ''
        ]).lower()
        
        return any(term.lower() in search_text for term in EPSTEIN_TERMS)


class DatabaseLoader:
    """Handles database connections and article insertion."""
    
    def __init__(self, db_url: str = DB_URL):
        self.db_url = db_url
        self.conn: Optional[asyncpg.Connection] = None
    
    async def connect(self):
        """Establish database connection."""
        self.conn = await asyncpg.connect(self.db_url)
        logger.info("Connected to database")
    
    async def disconnect(self):
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            logger.info("Disconnected from database")
    
    async def article_exists(self, url: str) -> bool:
        """Check if article URL already exists."""
        if not self.conn:
            return False
        
        result = await self.conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM media_news_articles WHERE article_url = $1)",
            url
        )
        return result
    
    async def insert_gkg_article(self, record: GKGRecord) -> bool:
        """Insert GKG record as news article."""
        if not self.conn:
            return False
        
        try:
            entities = record.extract_entities()
            
            # Parse tone
            tone_value = None
            if record.tone:
                try:
                    tone_parts = record.tone.split(',')
                    if tone_parts:
                        tone_value = float(tone_parts[0])
                except (ValueError, IndexError):
                    pass
            
            await self.conn.execute(
                """INSERT INTO media_news_articles 
                    (article_url, source_domain, publish_date, all_topics, 
                     discovery_source, collected_at, title)
                   VALUES ($1, $2, $3, $4, 'gdelt', NOW(), $5)
                   ON CONFLICT (article_url) DO UPDATE SET
                       all_topics = EXCLUDED.all_topics,
                       collected_at = NOW()""",
                record.url,
                record.source_common_name or 'unknown',
                record.date.date(),
                json.dumps({
                    'gkg_persons': entities['persons'],
                    'gkg_organizations': entities['organizations'],
                    'gkg_locations': entities['locations'],
                    'gkg_themes': entities['themes'],
                    'gkg_tone': tone_value,
                    'gkg_record_id': record.gkg_record_id
                }),
                record.source_common_name or 'Untitled'
            )
            return True
            
        except Exception as e:
            logger.error(f"Insert failed for {record.url}: {e}")
            return False


class GKGDownloader:
    """Downloads GKG data files from GDELT."""
    
    def __init__(self, download_dir: Path = DOWNLOAD_DIR):
        self.download_dir = download_dir
        self.session = requests.Session()
    
    def get_gkg_url(self, timestamp: datetime) -> str:
        """Get GKG URL for specific timestamp."""
        time_str = timestamp.strftime("%Y%m%d%H%M%S")
        return f"{GDELT_V2_BASE}/{time_str}.gkg.csv.zip"
    
    def download_file(self, url: str, local_path: Path, timeout: int = 60) -> bool:
        """Download a single GKG file with retry logic."""
        if local_path.exists():
            return True
        
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=timeout)
                
                if response.status_code == 404:
                    logger.debug(f"File not found: {url}")
                    return False
                
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    return False
        
        return False
    
    def download_date_gkg(self, date: datetime, max_slices: int = 96) -> List[Path]:
        """Download all GKG slices for a date (96 slices = 15-min intervals)."""
        downloaded = []
        count = 0
        
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                if max_slices and count >= max_slices:
                    break
                
                timestamp = date.replace(hour=hour, minute=minute, second=0)
                url = self.get_gkg_url(timestamp)
                filename = f"{timestamp.strftime('%Y%m%d%H%M%S')}.gkg.csv.zip"
                local_path = self.download_dir / filename
                
                if self.download_file(url, local_path):
                    downloaded.append(local_path)
                
                count += 1
        
        return downloaded


class GKGParser:
    """Parses GKG CSV files and extracts records."""
    
    def __init__(self, extract_dir: Path = EXTRACT_DIR):
        self.extract_dir = extract_dir
    
    def extract_zip(self, zip_path: Path) -> Optional[Path]:
        """Extract GKG zip file."""
        csv_name = zip_path.stem
        extract_path = self.extract_dir / f"{csv_name}.csv"
        
        if extract_path.exists():
            return extract_path
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(self.extract_dir)
            return extract_path
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return None
    
    def parse_gkg_file(self, csv_path: Path) -> List[GKGRecord]:
        """Parse GKG CSV and return records."""
        records = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f, delimiter='\t')
                
                for row in reader:
                    if len(row) < 19:
                        continue
                    
                    try:
                        # Parse date from GKG record ID (YYYYMMDD HHMMSS)
                        date_str = row[0][:8]
                        time_str = row[0][8:14] if len(row[0]) >= 14 else "000000"
                        record_date = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
                        
                        record = GKGRecord(
                            gkg_record_id=row[0],
                            date=record_date,
                            source_collection_identifier=row[1] if len(row) > 1 else '',
                            source_common_name=row[2] if len(row) > 2 else '',
                            document_identifier=row[3] if len(row) > 3 else '',
                            counts=row[4] if len(row) > 4 else '',
                            enhanced_theme=row[12] if len(row) > 12 else '',
                            enhanced_location=row[10] if len(row) > 10 else '',
                            enhanced_person=row[14] if len(row) > 14 else '',
                            enhanced_organization=row[16] if len(row) > 16 else '',
                            tone=row[18] if len(row) > 18 else ''
                        )
                        records.append(record)
                        
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logger.error(f"Parse failed {csv_path}: {e}")
        
        return records


class GDELTPipeline:
    """Main pipeline coordinating download, parse, filter, ingest."""
    
    def __init__(self):
        self.downloader = GKGDownloader()
        self.parser = GKGParser()
        self.db = DatabaseLoader()
        self.stats = {
            'files_downloaded': 0,
            'files_processed': 0,
            'records_parsed': 0,
            'epstein_matches': 0,
            'articles_inserted': 0
        }
    
    async def process_date(self, date: datetime) -> Dict:
        """Process all GKG slices for a single date."""
        logger.info(f"Processing {date.date()}")
        
        await self.db.connect()
        
        try:
            # Download
            zip_files = self.downloader.download_date_gkg(date)
            self.stats['files_downloaded'] += len(zip_files)
            
            for zip_path in zip_files:
                # Extract
                csv_path = self.parser.extract_zip(zip_path)
                if not csv_path:
                    continue
                
                self.stats['files_processed'] += 1
                
                # Parse
                records = self.parser.parse_gkg_file(csv_path)
                self.stats['records_parsed'] += len(records)
                
                # Filter and insert
                epstein_records = [r for r in records if r.has_epstein_terms()]
                self.stats['epstein_matches'] += len(epstein_records)
                
                if epstein_records:
                    logger.info(f"Found {len(epstein_records)} Epstein matches in {zip_path.name}")
                    
                    for record in epstein_records:
                        if await self.db.insert_gkg_article(record):
                            self.stats['articles_inserted'] += 1
                
                # Cleanup
                try:
                    csv_path.unlink()
                except:
                    pass
        
        finally:
            await self.db.disconnect()
        
        return self.stats
    
    async def process_date_range(self, start_date: datetime, end_date: datetime):
        """Process date range day by day."""
        current = start_date
        
        while current <= end_date:
            await self.process_date(current)
            current += timedelta(days=1)
        
        logger.info(f"Pipeline complete: {self.stats}")
        return self.stats


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='GDELT GKG Pipeline for Epstein Research'
    )
    parser.add_argument('--start-date', type=str, required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True,
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Download and parse without DB insertion')
    
    args = parser.parse_args()
    
    start = datetime.strptime(args.start_date, '%Y-%m-%d')
    end = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    logger.info(f"GDELT GKG Pipeline: {start.date()} to {end.date()}")
    
    if start.year < 2015 or (start.year == 2015 and start.month < 2):
        logger.warning("GKG data only available from February 2015")
    
    pipeline = GDELTPipeline()
    asyncio.run(pipeline.process_date_range(start, end))


if __name__ == "__main__":
    main()
