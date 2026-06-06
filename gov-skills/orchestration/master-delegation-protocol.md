# Master Swarm Delegation Protocol

## Overview
This document outlines the standard operating procedure for any AI agent in this workspace to safely and efficiently delegate work to a sub-agent. This leverages the `.autoclaw/mateam/scratch/` state framework.

## When to Delegate
You should spawn a sub-agent when:
1. A task requires massive context gathering (e.g., searching across hundreds of files).
2. You need to run a completely isolated task (e.g., executing a python script to scrape data) while you continue working on something else.
3. You need a dedicated "Reviewer" or "Verifier" to test your code.

## How to Delegate (The MAteam Paradigm)

1. **Create the Scratchpad:**
   Using your file-writing tools, create a new directory inside `.autoclaw/mateam/scratch/` named `<YYYY-MM-DD>-<task-slug>/`.

2. **Define the Scope:**
   Create a `plan.md` in that scratchpad outlining exactly what the sub-agent is supposed to do.

3. **Spawn the Agent:**
   Use the `MAteam` or equivalent CLI tools (or your native `Agent` subagent tool if available) to spawn the agent. Point them to the reusable `.txt` prompts located in `gov-skills/orchestration/prompts/`.

## Reusable Prompts Library
Always look in `gov-skills/orchestration/prompts/` to see if a prompt already exists for the task you want to delegate.
- If it does, use it.
- If it doesn't, create a new `.txt` prompt and save it there for future agents to reuse!
