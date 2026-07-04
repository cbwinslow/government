#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

import requests

MODELS_URL = "https://openrouter.ai/api/v1/models"
RANKINGS_PAGE_URL = "https://openrouter.ai/rankings"

HEADERS = {
    "User-Agent": "openrouter-free-model-selector/1.0"
}

def fetch_models():
    r = requests.get(MODELS_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("data", [])

def is_free_model(model):
    model_id = (model.get("id") or "").lower()
    model_name = (model.get("name") or "").lower()
    return "free" in model_id or "free" in model_name

def normalize_slug(value):
    value = (value or "").strip().lower()
    value = value.replace(" (free)", "")
    return value

def load_popularity_from_file(path):
    """
    Expected format:
    [
      {"model": "google/gemma-4-31b-it:free", "tokens_used": 123456789},
      {"model": "qwen/qwen3-next-80b-a3b-instruct:free", "tokens_used": 98765432}
    ]
    """
    raw = json.loads(Path(path).read_text())
    popularity = {}
    for row in raw:
        model = normalize_slug(row.get("model") or row.get("id") or row.get("slug"))
        tokens = row.get("tokens_used") or row.get("usage_tokens") or row.get("tokens") or 0
        if model:
            popularity[model] = int(tokens)
    return popularity

def try_extract_popularity_from_rankings_html():
    """
    Best-effort scraper. OpenRouter's rankings page is public, but the usage
    payload may not always be exposed in a stable JSON shape.
    """
    try:
        r = requests.get(RANKINGS_PAGE_URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
    except Exception:
        return {}

    popularity = {}

    patterns = [
        re.compile(r'"model"\s*:\s*"([^"]+)"[^{}]{0,300}?"tokens_used"\s*:\s*(\d+)', re.I),
        re.compile(r'"id"\s*:\s*"([^"]+)"[^{}]{0,300}?"tokens_used"\s*:\s*(\d+)', re.I),
        re.compile(r'"slug"\s*:\s*"([^"]+)"[^{}]{0,300}?"tokens_used"\s*:\s*(\d+)', re.I),
    ]

    for pattern in patterns:
        for match in pattern.finditer(html):
            slug = normalize_slug(match.group(1))
            tokens = int(match.group(2))
            if slug:
                popularity[slug] = max(tokens, popularity.get(slug, 0))

    return popularity

def rank_free_models(models, popularity_map):
    free_models = [m for m in models if is_free_model(m)]

    ranked = []
    for model in free_models:
        model_id = model.get("id", "")
        model_name = model.get("name", "")
        key_candidates = {
            normalize_slug(model_id),
            normalize_slug(model_name),
        }

        tokens_used = 0
        for key in key_candidates:
            if key in popularity_map:
                tokens_used = max(tokens_used, popularity_map[key])

        ranked.append({
            "id": model_id,
            "name": model_name,
            "tokens_used": tokens_used,
            "context_length": model.get("context_length"),
            "pricing": model.get("pricing", {}),
            "top_provider": (model.get("top_provider") or {}),
        })

    ranked.sort(
        key=lambda x: (
            x["tokens_used"],
            x["context_length"] or 0,
            x["id"]
        ),
        reverse=True
    )
    return ranked

def main():
    models = fetch_models()

    popularity = {}
    if len(sys.argv) > 1:
        popularity = load_popularity_from_file(sys.argv[1])

    if not popularity:
        popularity = try_extract_popularity_from_rankings_html()

    ranked = rank_free_models(models, popularity)
    top5 = ranked[:5]

    output = {
        "source_models_endpoint": MODELS_URL,
        "source_rankings_page": RANKINGS_PAGE_URL,
        "free_model_count": len([m for m in models if is_free_model(m)]),
        "used_popularity_data": bool(popularity),
        "top_5_free_models": top5,
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
