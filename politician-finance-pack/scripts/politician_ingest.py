import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

TIMEOUT = int(os.getenv("HTTP_TIMEOUT_SECONDS", "60"))

@dataclass
class Settings:
    congress_api_key: str = os.getenv("CONGRESS_API_KEY", "")
    congress_base: str = os.getenv("CONGRESS_API_BASE", "https://api.congress.gov/v3")
    fec_api_key: str = os.getenv("FEC_API_KEY", "")
    fec_base: str = os.getenv("FEC_API_BASE", "https://api.open.fec.gov/v1")

S = Settings()


def get_json(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    r = requests.get(url, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def ingest_members(args):
    url = f"{S.congress_base}/member"
    data = get_json(url, {"api_key": S.congress_api_key, "format": "json", "limit": 250})
    print(json.dumps({"cmd": "ingest-members", "top_keys": list(data)[:10], "congress": args.congress}))


def ingest_openfec(args):
    url = f"{S.fec_base}/candidates/search/"
    data = get_json(url, {"api_key": S.fec_api_key, "cycle": args.cycle, "per_page": 20})
    print(json.dumps({"cmd": "ingest-openfec", "top_keys": list(data)[:10], "cycle": args.cycle}))


def ingest_disclosures(args):
    print(json.dumps({"cmd": "ingest-disclosures", "year": args.year, "status": "scaffold"}))


def index_embeddings(args):
    print(json.dumps({"cmd": "index-embeddings", "limit": args.limit, "status": "scaffold"}))


def build_parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)

    a = sp.add_parser("ingest-members")
    a.add_argument("--congress", type=int, required=True)
    a.set_defaults(func=ingest_members)

    b = sp.add_parser("ingest-openfec")
    b.add_argument("--cycle", type=int, required=True)
    b.set_defaults(func=ingest_openfec)

    c = sp.add_parser("ingest-disclosures")
    c.add_argument("--year", type=int, required=True)
    c.set_defaults(func=ingest_disclosures)

    d = sp.add_parser("index-embeddings")
    d.add_argument("--limit", type=int, default=1000)
    d.set_defaults(func=index_embeddings)
    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
