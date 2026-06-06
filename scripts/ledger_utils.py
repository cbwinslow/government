import json
import os
from datetime import datetime

LEDGER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/ingestion_ledger.json"))

def _load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return {"datasets": {}, "files": [], "last_updated": ""}
    with open(LEDGER_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"datasets": {}, "files": [], "last_updated": ""}

def _save_ledger(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(LEDGER_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def log_file_ingestion(filepath, dataset_name, status, details=None):
    """
    Log a specific file ingestion event.
    status: e.g. 'DOWNLOADED', 'EXTRACTED', 'VECTORIZED', 'FAILED'
    """
    ledger = _load_ledger()
    
    # Check if file exists in ledger
    file_entry = next((item for item in ledger["files"] if item["filepath"] == filepath), None)
    
    if file_entry:
        file_entry["status"] = status
        file_entry["updated_at"] = datetime.now().isoformat()
        if details:
            file_entry["details"] = details
    else:
        ledger["files"].append({
            "filepath": filepath,
            "dataset": dataset_name,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "details": details or {}
        })
        
    # Update dataset aggregate stats
    if dataset_name not in ledger["datasets"]:
        ledger["datasets"][dataset_name] = {"total_files": 0, "status": "IN_PROGRESS"}
        
    ledger["datasets"][dataset_name]["updated_at"] = datetime.now().isoformat()
    
    _save_ledger(ledger)

if __name__ == "__main__":
    # Test logging
    log_file_ingestion("/test/dummy.xml", "test_dataset", "VECTORIZED", {"collection": "test_collection"})
    print("Ledger updated.")
