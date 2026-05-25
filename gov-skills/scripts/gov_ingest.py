import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

TIMEOUT = int(os.getenv("HTTP_TIMEOUT_SECONDS", "60"))

@dataclass
class Settings:
    govinfo_api_key: str = os.getenv("GOVINFO_API_KEY", "")
    govinfo_base: str = os.getenv("GOVINFO_BASE_URL", "https://api.govinfo.gov")
    govinfo_bulk: str = os.getenv("GOVINFO_BULKDATA_BASE", "https://www.govinfo.gov/bulkdata")
    congress_api_key: str = os.getenv("CONGRESS_API_KEY", "")
    congress_base: str = os.getenv("CONGRESS_API_BASE", "https://api.congress.gov/v3")

S = Settings()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_json(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    r = requests.get(url, headers=headers or {}, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def govinfo_collection(collection: str):
    url = f"{S.govinfo_base}/collections/{collection}"
    params = {"api_key": S.govinfo_api_key}
    return get_json(url, params=params)


def govinfo_bulk_listing(path: str):
    url = f"{S.govinfo_bulk}/json/{path.lstrip('/')}"
    return get_json(url, headers={"Accept": "application/json"})


def congress_bill_list(congress: int, offset: int = 0, limit: int = 250):
    url = f"{S.congress_base}/bill/{congress}"
    params = {"api_key": S.congress_api_key, "format": "json", "offset": offset, "limit": min(limit, 250)}
    return get_json(url, params=params)


def cmd_govinfo_backfill(args):
    data = govinfo_bulk_listing(f"{args.collection}/{args.congress}")
    print(json.dumps({"mode": "govinfo-backfill", "keys": list(data)[:10], "sha256": sha256_text(json.dumps(data)[:5000])}))


def cmd_govinfo_incremental(args):
    data = govinfo_collection(args.collection)
    print(json.dumps({"mode": "govinfo-incremental", "keys": list(data)[:10]}))


def cmd_congress_sync(args):
    data = congress_bill_list(args.congress)
    print(json.dumps({"mode": "congress-sync", "keys": list(data)[:10]}))


def cmd_dq(args):
    print(json.dumps({"mode": "dq", "status": "stub", "checks": ["duplicates", "null_rates", "lag", "orphans"]}))


def build_parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)

    p1 = sp.add_parser("govinfo-backfill")
    p1.add_argument("--collection", required=True)
    p1.add_argument("--congress", required=True)
    p1.set_defaults(func=cmd_govinfo_backfill)

    p2 = sp.add_parser("govinfo-incremental")
    p2.add_argument("--collection", required=True)
    p2.set_defaults(func=cmd_govinfo_incremental)

    p3 = sp.add_parser("congress-sync")
    p3.add_argument("--entity", required=True)
    p3.add_argument("--congress", type=int, required=True)
    p3.set_defaults(func=cmd_congress_sync)

    p4 = sp.add_parser("dq")
    p4.set_defaults(func=cmd_dq)
    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
