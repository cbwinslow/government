---
name: honesty-engine-scorer
description: Configure, extend, or operate the Honesty Engine — the core LLM-based consistency scorer that evaluates politicians by cross-referencing their stated positions (Words) against their actual record (Actions). Use for scoring politician consistency, generating discrepancy reports, and tracking score deltas over time.
category: integration-documentation
risk: low
source: community
tags: [honesty-engine, consistency-scoring, llm, openrouter, politician, discrepancy, words-actions]
tools: [python, openrouter, gemini, pydantic, postgresql, sqlalchemy]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

# Skill: honesty-engine-scorer

## Purpose
Use this skill when configuring, extending, or operating the Honesty Engine — the core LLM-based consistency scorer that evaluates politicians by cross-referencing their stated positions ("Words") against their actual record ("Actions").

## Architecture facts to honor
- The engine lives in `src/opendiscourse/engine/scorer.py`.
- It uses OpenRouter's API with a fallback chain: Hermes 405B (free) → Llama 70B (free) → optional Fusion mode.
- Structured output is enforced via Pydantic `response_format` (OpenAI SDK beta parse).
- `Discrepancy` model has: `issue`, `words_summary`, `actions_summary`, `severity` (1-10), `explanation`.
- `HonestyScore` model has: `consistency_score` (0-100), `discrepancies` list, `overall_summary`.
- Fusion mode uses `openrouter/fusion` to panel multiple models into a synthesized judge response.

## Scoring workflow

### 1. Scorer initialization
```python
from opendiscourse.engine.scorer import HonestyEngine, LLMModel

# Default: free massive 405B model
engine = HonestyEngine()

# For deeper analysis (uses credits):
engine = HonestyEngine(primary_model=LLMModel.GEMINI_3_PRO)

# For multi-model paneling (uses credits):
score = await engine.evaluate_consistency(name, words, actions, use_fusion=True)
```

### 2. Context assembly
Before calling the engine, gather:
- **Words**: floor speeches, social media, quotes, town hall statements
- **Actions**: votes, sponsored legislation, campaign contributions, financial disclosures, lawsuit involvement, interest group ratings

Each list item should be a concise, evidence-backed string.

### 3. Handling results
```python
result = await engine.evaluate_consistency(politician_name, words, actions)
if result:
    print(f"{politician_name}: {result.consistency_score}/100")
    for d in result.discrepancies:
        print(f"  [{d.severity}/10] {d.issue}: {d.explanation}")
```

### 4. Persistent storage
Engine results should be stored so they can be tracked over time:
- Store each `HonestyScore` record with a timestamp and source data fingerprint.
- Track score deltas over time (a dropping score is more significant than a static low score).
- Persist `Discrepancy` records with a foreign key to the politician.

## Configuration concerns
- `OPENROUTER_API_KEY` must be set, or the engine returns `None`.
- `GEMINI_API_KEY` is available but not used by the default engine (OpenRouter routes Gemini).
- `temperature=0.2` is the default — use lower for stricter factuality, higher for more creative synthesis.
- Ensemble/fusion mode costs tokens across multiple models; use only for high-stakes evaluations.

## Extending
To add a new model to the fallback chain:
1. Add the model string to `LLMModel` enum in `scorer.py`.
2. Insert it into `self.fallback_chain` with the desired priority order.

To add new evidence types:
1. Add a new ingestion module in `src/opendiscourse/ingestion/`.
2. Feed its output into the `words_context` or `actions_context` list.
3. The engine handles arbitrary text — no schema changes needed on the scorer side.

## Prompting template
- "Run the Honesty Engine on Representative X using their last 20 floor speeches and their voting record in the current Congress."
- "Score all members of the House Banking Committee against their campaign finance disclosures."
- "Compare a politician's consistency score over the last 3 Congresses — has it improved or worsened, and on which issues?"
- "Generate a discrepancy report for Senator Y showing the highest-severity contradictions between their public statements and their committee votes."

## When to Use
- Scoring politician consistency between words and actions
- Generating discrepancy reports for specific politicians
- Tracking consistency score changes over time
- Configuring LLM model fallback chains
- Adding new evidence types to scoring context

## Limitations
- Requires OPENROUTER_API_KEY (free tier available)
- Fusion mode consumes significant tokens across multiple models
- Default temperature=0.2; adjust for factuality vs creativity tradeoff
- Results depend on quality/completeness of Words/Actions context
- Does not directly ingest data; requires pre-assembled context