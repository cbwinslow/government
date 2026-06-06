#!/usr/bin/env python3
"""
GDELT Parallel Swarm Coordinator

Manages multiple concurrent GDELT pipeline workers for large-scale ingestion.
Each worker processes a 30-day date range independently.

Usage:
    python3 gdelt_parallel_swarm.py \
        --start-date 2019-07-01 \
        --end-date 2025-04-10 \
        --max-workers 5

Features:
- Automatic worker lifecycle management
- State persistence (resume on crash)
- Progress tracking
- Worker log aggregation

Author: Research Team
Date: 2025-04-10
"""

import os
import sys
import json
import time
import signal
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/tmp/gdelt_swarm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
STATE_FILE = Path('/tmp/gdelt_swarm_state.json')
BASE_DIR = Path("/home/cbwinslow/workspace/epstein-pipeline")
PIPELINE_SCRIPT = BASE_DIR / "gdelt_ingestion_pipeline.py"
CHUNK_SIZE_DAYS = 30
MAX_WORKERS_DEFAULT = 5


@dataclass
class WorkerJob:
    """Represents a single worker job."""
    worker_id: int
    start_date: str
    end_date: str
    log_file: str
    pid: Optional[int] = None
    status: str = "pending"  # pending, running, completed, failed
    articles_found: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class GDELTSwarmCoordinator:
    """Coordinates parallel GDELT ingestion workers."""
    
    def __init__(self, max_workers: int = MAX_WORKERS_DEFAULT):
        self.max_workers = max_workers
        self.jobs: List[WorkerJob] = []
        self.running = False
    
    def generate_chunks(self, start_date: datetime, end_date: datetime) -> List[Tuple[datetime, datetime]]:
        """Split date range into 30-day chunks."""
        chunks = []
        current = start_date
        
        while current <= end_date:
            chunk_end = min(current + timedelta(days=CHUNK_SIZE_DAYS - 1), end_date)
            chunks.append((current, chunk_end))
            current = chunk_end + timedelta(days=1)
        
        return chunks
    
    def create_jobs(self, chunks: List[Tuple[datetime, datetime]]) -> List[WorkerJob]:
        """Create worker jobs from chunks."""
        jobs = []
        for i, (start, end) in enumerate(chunks):
            job = WorkerJob(
                worker_id=i,
                start_date=start.strftime('%Y-%m-%d'),
                end_date=end.strftime('%Y-%m-%d'),
                log_file=f"/tmp/gdelt_worker_{i:03d}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.log",
                status="pending"
            )
            jobs.append(job)
        return jobs
    
    def save_state(self):
        """Save job state to disk."""
        state = {
            'jobs': [asdict(job) for job in self.jobs],
            'max_workers': self.max_workers,
            'updated_at': datetime.now().isoformat()
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> bool:
        """Load job state from disk."""
        if not STATE_FILE.exists():
            return False
        
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            
            self.jobs = []
            for job_data in state.get('jobs', []):
                # Filter out running status on resume (they may have died)
                if job_data.get('status') == 'running':
                    job_data['status'] = 'pending'
                    job_data['pid'] = None
                self.jobs.append(WorkerJob(**job_data))
            
            self.max_workers = state.get('max_workers', MAX_WORKERS_DEFAULT)
            logger.info(f"Resumed {len(self.jobs)} jobs from state file")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False
    
    def start_worker(self, job: WorkerJob) -> bool:
        """Start a single worker process."""
        try:
            cmd = [
                sys.executable,
                str(PIPELINE_SCRIPT),
                '--start-date', job.start_date,
                '--end-date', job.end_date
            ]
            
            with open(job.log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=BASE_DIR,
                    start_new_session=True
                )
            
            job.pid = process.pid
            job.status = "running"
            job.started_at = datetime.now().isoformat()
            
            logger.info(f"Started worker {job.worker_id}: {job.start_date} to {job.end_date} (PID: {job.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start worker {job.worker_id}: {e}")
            job.status = "failed"
            return False
    
    def check_worker_status(self, job: WorkerJob):
        """Check if worker is still running."""
        if job.status != "running" or not job.pid:
            return
        
        try:
            process = psutil.Process(job.pid)
            if not process.is_running():
                job.status = "completed"
                job.completed_at = datetime.now().isoformat()
                job.articles_found = self._count_articles(job.log_file)
                logger.info(f"Worker {job.worker_id} completed: {job.articles_found} articles")
        except psutil.NoSuchProcess:
            job.status = "completed"
            job.completed_at = datetime.now().isoformat()
    
    def _count_articles(self, log_file: str) -> int:
        """Count articles from worker log."""
        try:
            if not Path(log_file).exists():
                return 0
            
            count = 0
            with open(log_file, 'r') as f:
                for line in f:
                    if 'Epstein matches' in line:
                        try:
                            count += int(line.split('Found')[1].split()[0])
                        except:
                            pass
            return count
        except:
            return 0
    
    def get_stats(self) -> Dict:
        """Get swarm statistics."""
        stats = {
            'total': len(self.jobs),
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'articles': 0
        }
        
        for job in self.jobs:
            stats[job.status] += 1
            stats['articles'] += job.articles_found
        
        return stats
    
    def print_status(self):
        """Print status table."""
        stats = self.get_stats()
        
        print(f"\n{'='*70}")
        print(f"GDELT SWARM STATUS  [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'='*70}")
        print(f"Workers: {stats['running']} running | {stats['pending']} pending | "
              f"{stats['completed']} completed | {stats['failed']} failed")
        print(f"Total jobs: {stats['total']} | Articles: {stats['articles']:,}")
        print(f"{'-'*70}")
        
        for job in self.jobs:
            if job.status == "running":
                runtime = ""
                if job.started_at:
                    mins = (datetime.now() - datetime.fromisoformat(job.started_at)).seconds // 60
                    runtime = f"({mins}m)"
                print(f"  Worker {job.worker_id:03d}: {job.start_date} → {job.end_date} PID={job.pid} {runtime}")
        
        print(f"{'='*70}\n")
    
    def run_swarm(self, start_date: datetime, end_date: datetime, resume: bool = False):
        """Run swarm coordination loop."""
        logger.info(f"GDELT Swarm: {start_date.date()} to {end_date.date()}")
        
        # Load or create jobs
        if resume and self.load_state():
            pass
        else:
            chunks = self.generate_chunks(start_date, end_date)
            self.jobs = self.create_jobs(chunks)
            logger.info(f"Created {len(self.jobs)} jobs")
        
        self.save_state()
        self.running = True
        
        try:
            while self.running:
                # Update statuses
                for job in self.jobs:
                    self.check_worker_status(job)
                
                # Start new workers
                running = sum(1 for j in self.jobs if j.status == 'running')
                pending = sum(1 for j in self.jobs if j.status == 'pending')
                
                if running < self.max_workers and pending > 0:
                    slots = self.max_workers - running
                    for job in self.jobs:
                        if job.status == 'pending' and slots > 0:
                            if self.start_worker(job):
                                slots -= 1
                                time.sleep(2)
                
                self.save_state()
                self.print_status()
                
                # Check completion
                if pending == 0 and running == 0:
                    logger.info("All workers completed!")
                    break
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.shutdown()
        
        self.print_final_stats()
    
    def shutdown(self):
        """Shutdown all workers."""
        for job in self.jobs:
            if job.status == "running" and job.pid:
                try:
                    os.kill(job.pid, signal.SIGTERM)
                    job.status = "failed"
                except:
                    pass
        self.save_state()
    
    def print_final_stats(self):
        """Print final summary."""
        stats = self.get_stats()
        
        print(f"\n{'='*70}")
        print(f"GDELT SWARM COMPLETE")
        print(f"{'='*70}")
        print(f"Total jobs:    {stats['total']}")
        print(f"Completed:     {stats['completed']}")
        print(f"Failed:        {stats['failed']}")
        print(f"Total articles: {stats['articles']:,}")
        print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description='GDELT Parallel Swarm')
    parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-workers', type=int, default=MAX_WORKERS_DEFAULT, help='Max parallel workers')
    parser.add_argument('--resume', action='store_true', help='Resume from previous run')
    
    args = parser.parse_args()
    
    start = datetime.strptime(args.start_date, '%Y-%m-%d')
    end = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    swarm = GDELTSwarmCoordinator(max_workers=args.max_workers)
    swarm.run_swarm(start, end, resume=args.resume)


if __name__ == "__main__":
    main()
