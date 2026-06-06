#!/usr/bin/env python3
import os

ROOT_DIR = "/home/cbwinslow/workspace/government"
IGNORE_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", 
    ".pytest_cache", ".ruff_cache", "epstein/data", "congress/congress-data"
}

GEMINI_TEMPLATE = """# GEMINI.md: Localized Context for AI Assistants

**Directory:** `{dir_name}`

## Architectural Purpose
This directory (`{base_name}`) is part of the overarching `government` intelligence repository. Its primary purpose is determined by the files contained within it.

## Directory Contents
**Subdirectories:** {subdirs}
**Files:** {files}

## AI Coding Protocols
- **Aesthetics:** If modifying UI files in this directory, prioritize rich aesthetics, TailwindCSS (if applicable), and modern micro-animations.
- **Tool Specificity:** Always use the most specific tool available (e.g., `replace_file_content` instead of `sed`).
- **Dependencies:** Do not introduce heavy dependencies unless explicitly authorized.
"""

AGENTS_TEMPLATE = """# AGENTS.md: Swarm & LangGraph Agent Protocol

**Target Directory:** `{dir_name}`

## Permitted Agents
Agents operating in this directory must strictly adhere to the operational limits defined below. Unrecognized agents should escalate to the Supervisor Node.

## Tool Context & MCP Access
- **Database Tools:** Agents should use standard `psql` or `SQLAlchemy` connectors to interact with the Postgres `govdata` database.
- **Vector Operations:** Agents looking for semantic search must route through the `Qdrant` endpoints at `172.25.10.64:6333`.
- **MCP Servers:** If this directory contains MCP configurations, agents must utilize the exposed `mcp_<server_name>_<tool_name>` commands natively.

## System Prompt Directives
```yaml
system_prompt: >
  You are operating within '{base_name}'. Your primary objective is to execute 
  workflows localized to this domain. Do not traverse outside this directory 
  unless explicitly instructed by the LangGraph Orchestrator.
```
"""

def should_ignore(path):
    for ignore in IGNORE_DIRS:
        if ignore in path:
            return True
    return False

def generate_docs():
    for root, dirs, files in os.walk(ROOT_DIR):
        # Filter out ignored directories entirely
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        if should_ignore(root):
            continue
            
        rel_path = os.path.relpath(root, ROOT_DIR)
        if rel_path == ".":
            dir_name = "."
            base_name = "government"
        else:
            dir_name = rel_path
            base_name = os.path.basename(root)
            
        subdirs_str = ", ".join(dirs) if dirs else "None"
        # Don't list GEMINI.md or AGENTS.md in the file list to avoid clutter
        clean_files = [f for f in files if f not in ("GEMINI.md", "AGENTS.MD")]
        files_str = ", ".join(clean_files) if clean_files else "None"

        gemini_path = os.path.join(root, "GEMINI.md")
        agents_path = os.path.join(root, "AGENTS.md")

        # Write GEMINI.md
        if not os.path.exists(gemini_path):
            with open(gemini_path, "w") as f:
                f.write(GEMINI_TEMPLATE.format(
                    dir_name=dir_name, 
                    base_name=base_name,
                    subdirs=subdirs_str,
                    files=files_str
                ))
                
        # Write AGENTS.md
        if not os.path.exists(agents_path):
            with open(agents_path, "w") as f:
                f.write(AGENTS_TEMPLATE.format(
                    dir_name=dir_name,
                    base_name=base_name
                ))

if __name__ == "__main__":
    generate_docs()
    print("Successfully generated GEMINI.md and AGENTS.md across the workspace.")
