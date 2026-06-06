# GEMINI.md: Localized Context for AI Assistants

**Directory:** `src/opendiscourse/agents`

## Architectural Purpose
This directory (`agents`) is part of the overarching `government` intelligence repository. Its primary purpose is determined by the files contained within it.

## Directory Contents
**Subdirectories:** None
**Files:** langchain_tools.py, orchestrator.py, openrouter_sdk.py, __init__.py

## AI Coding Protocols
- **Aesthetics:** If modifying UI files in this directory, prioritize rich aesthetics, TailwindCSS (if applicable), and modern micro-animations.
- **Tool Specificity:** Always use the most specific tool available (e.g., `replace_file_content` instead of `sed`).
- **Dependencies:** Do not introduce heavy dependencies unless explicitly authorized.
