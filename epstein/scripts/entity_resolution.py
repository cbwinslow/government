#!/usr/bin/env python3
"""Entity resolution for Epstein email participants using string similarity.

Deduplicates person entities across email datasets using Jaro-Winkler similarity
via difflib (fallback) since rapidfuzz has broken metadata.
"""

from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


def load_all_participants() -> list[str]:
    """Load all participants from processed email datasets.

    Returns
    -------
    list[str]
        List of participant names.
    """
    participants = []
    output_dir = Path("epstein/output/processed_hf/emails")

    # Load from each dataset
    for participant_file in output_dir.glob("*_participants.json"):
        with open(participant_file, encoding="utf-8") as f:
            names = json.load(f)

        for name in names:
            if name and isinstance(name, str):
                participants.append(name.strip())

    # Also load from consolidated email_participants.json
    consolidated_file = Path("epstein/output/processed_hf/email_participants.json")
    if consolidated_file.exists():
        with open(consolidated_file, encoding="utf-8") as f:
            names = json.load(f)
        for name in names:
            if name and isinstance(name, str):
                participants.append(name.strip())

    return participants


def clean_name(name: str) -> str:
    """Clean participant name for matching.

    Parameters
    ----------
    name : str
        Raw participant name/email.

    Returns
    -------
    str
        Cleaned name.
    """
    # Remove email addresses and angle brackets
    cleaned = re.sub(r'<[^>]+>', '', name)
    cleaned = re.sub(r'\s*\[[^\]]+\]', '', cleaned)
    cleaned = re.sub(r'\s*@[^,\s]+', '', cleaned)
    cleaned = cleaned.strip()
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned


def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings.

    Parameters
    ----------
    s1, s2 : str
        Strings to compare.

    Returns
    -------
    float
        Similarity score (0-100).
    """
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio() * 100


def deduplicate_persons(
    names: list[str],
    similarity_threshold: float = 92.0,
) -> tuple[list[list[str]], list[str]]:
    """Deduplicate names using string similarity.

    Parameters
    ----------
    names : list[str]
        Raw participant names.
    similarity_threshold : float
        Threshold for considering names duplicates (0-100).

    Returns
    -------
    tuple[list[list[str]], list[str]]
        Clusters of duplicate names and list of deduplicated names.
    """
    # Deduplicate identical names first
    unique_names = []
    seen_lower = set()
    for name in names:
        cleaned = clean_name(name)
        cleaned_lower = cleaned.lower()
        if cleaned_lower not in seen_lower and len(cleaned) > 2:
            unique_names.append(cleaned)
            seen_lower.add(cleaned_lower)

    print(f"After exact dedup: {len(unique_names)} unique names from {len(names)} raw")

    # Build clusters using similarity
    clusters: list[list[str]] = []
    assigned = set()

    for i, name in enumerate(unique_names):
        if i in assigned:
            continue

        # Find similar names
        cluster = [name]
        for j, other in enumerate(unique_names):
            if j == i or j in assigned:
                continue
            score = similarity_ratio(name, other)
            if score >= similarity_threshold:
                cluster.append(other)
                assigned.add(j)

        # Add to clusters if multiple matches
        if len(cluster) > 1:
            clusters.append(cluster)
            assigned.add(i)

    return clusters, unique_names


def main() -> int:
    """Run entity resolution and save results.

    Returns
    -------
    int
        Number of duplicate clusters found.
    """
    output_dir = Path("epstein/output/processed_hf")

    # Run deduplication
    participants = load_all_participants()
    clusters, unique_names = deduplicate_persons(participants)

    # Save clusters
    results = {
        "clusters": [
            {
                "cluster_id": i,
                "members": cluster,
                "canonical_name": cluster[0],  # Use first as canonical
            }
            for i, cluster in enumerate(clusters)
        ],
        "total_records": len(unique_names),
        "duplicate_pairs": sum(len(c) - 1 for c in clusters),
    }

    clusters_file = output_dir / "entity_clusters.json"
    with open(clusters_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved entity clusters to {clusters_file}")

    # Print summary
    print("\n=== Entity Resolution Summary ===")
    print(f"Raw participants: {len(participants)}")
    print(f"Unique after dedup: {len(unique_names)}")
    print(f"Duplicate clusters found: {len(clusters)}")

    print("\nTop clusters:")
    for cluster in results["clusters"][:10]:
        print(f"  Cluster {cluster['cluster_id']}: {len(cluster['members'])} members")
        for member in cluster['members'][:3]:
            print(f"    - {member}")

    return len(clusters)


if __name__ == "__main__":
    sys.exit(main())