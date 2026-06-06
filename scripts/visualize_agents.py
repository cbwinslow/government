#!/usr/bin/env -S uv run python
"""
OpenDiscourse Agent System Visualization
=========================================
Generates an interactive HTML network graph of the agent system architecture.

This script reads the actual code to discover:
  - All agent tools and their class hierarchy
  - Import dependencies between modules
  - API endpoints and their connections
  - Data source connections

Output: scripts/agent_architecture.html (open in browser)

Usage:
    uv run python scripts/visualize_agents.py
    # Opens the interactive graph in your browser
"""

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# ── Code Analysis ─────────────────────────────────────────────────────────────


def extract_classes_and_imports(filepath: str) -> Tuple[List[str], List[str], List[str]]:
    """Extract class names, import statements, and methods from a Python file."""
    classes: List[str] = []
    imports: List[str] = []
    methods: List[str] = []
    
    with open(filepath, "r") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return classes, imports, methods
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(f"{node.name}.{item.name}()")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
    
    return classes, imports, methods


def analyze_project() -> Dict[str, Any]:
    """Analyze the entire agents/ and api/ directories."""
    project_root = Path(__file__).parent.parent
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    # ── Layer 1: Agent Module ──────────────────────────────────────────────
    agents_dir = project_root / "src" / "opendiscourse" / "agents"
    for pyfile in sorted(agents_dir.glob("*.py")):
        if pyfile.name == "__pycache__":
            continue
        classes, imports, methods = extract_classes_and_imports(str(pyfile))
        
        # Add file as a node
        file_node = {
            "id": f"file:{pyfile.name}",
            "label": pyfile.name.replace(".py", ""),
            "group": "agent_module",
            "title": f"<b>{pyfile.name}</b><br/>Classes: {', '.join(classes) if classes else '—'}<br/>Methods: {len(methods)}",
            "shape": "box",
        }
        nodes.append(file_node)
        
        # Add classes as sub-nodes
        for cls in classes:
            cls_node = {
                "id": cls,
                "label": cls,
                "group": "agent_class",
                "title": f"<b>{cls}</b><br/>File: {pyfile.name}",
                "shape": "ellipse",
            }
            nodes.append(cls_node)
            edges.append({
                "from": f"file:{pyfile.name}",
                "to": cls,
                "label": "defines",
                "dashes": True,
            })
        
        # Add import edges
        for imp in imports:
            for other_file in agents_dir.glob("*.py"):
                other_classes, _, _ = extract_classes_and_imports(str(other_file))
                for cls in other_classes:
                    if cls in imp:
                        edges.append({
                            "from": f"file:{pyfile.name}",
                            "to": cls,
                            "label": "imports",
                            "dashes": False,
                        })
    
    # ── Layer 2: API Module ────────────────────────────────────────────────
    api_dir = project_root / "src" / "opendiscourse" / "api"
    for pyfile in sorted(api_dir.glob("*.py")):
        if pyfile.name == "__pycache__":
            continue
        classes, imports, methods = extract_classes_and_imports(str(pyfile))
        
        file_node = {
            "id": f"api:{pyfile.name}",
            "label": pyfile.name.replace(".py", ""),
            "group": "api_module",
            "title": f"<b>{pyfile.name}</b><br/>Classes: {', '.join(classes) if classes else '—'}<br/>Imports: {len(imports)}",
            "shape": "box",
        }
        nodes.append(file_node)
        
        # Connect to imported modules from agents
        for imp in imports:
            if "agents" in imp:
                for agent_file in agents_dir.glob("*.py"):
                    if agent_file.name.replace(".py", "") in imp or agent_file.stem in imp:
                        edges.append({
                            "from": f"api:{pyfile.name}",
                            "to": f"file:{agent_file.name}",
                            "label": "imports",
                            "dashes": False,
                        })
    
    # ── Layer 3: Existing Engine ───────────────────────────────────────────
    engine_dir = project_root / "src" / "opendiscourse" / "engine"
    for pyfile in sorted(engine_dir.glob("*.py")):
        if pyfile.name == "__pycache__":
            continue
        file_node = {
            "id": f"engine:{pyfile.name}",
            "label": pyfile.name.replace(".py", ""),
            "group": "existing_module",
            "title": f"<b>{pyfile.name}</b> (Existing Engine)",
            "shape": "box",
        }
        nodes.append(file_node)

    # ── Layer 4: Data Sources (external) ──────────────────────────────────
    data_sources = [
        {"id": "ds:congress", "label": "Congress.gov", "group": "datasource"},
        {"id": "ds:opensecrets", "label": "OpenSecrets.org", "group": "datasource"},
        {"id": "ds:votesmart", "label": "Vote Smart", "group": "datasource"},
        {"id": "ds:qdrant", "label": "Qdrant Vector DB", "group": "datasource"},
        {"id": "ds:postgres", "label": "PostgreSQL", "group": "datasource"},
        {"id": "ds:gdelt", "label": "GDELT News", "group": "datasource"},
        {"id": "ds:openrouter", "label": "OpenRouter (200+ LLMs)", "group": "openrouter"},
    ]
    for ds in data_sources:
        ds_node = {
            "id": ds["id"],
            "label": ds["label"],
            "group": ds["group"],
            "shape": "diamond",
            "title": f"<b>{ds['label']}</b>",
            "size": 30,
        }
        nodes.append(ds_node)
    
    # ── Layer 5: API Endpoints ─────────────────────────────────────────────
    endpoints = [
        {"id": "ep:research", "label": "POST /research", "group": "endpoint"},
        {"id": "ep:score", "label": "POST /score-consistency", "group": "endpoint"},
        {"id": "ep:runtool", "label": "POST /run-tool", "group": "endpoint"},
        {"id": "ep:tools", "label": "GET /tools", "group": "endpoint"},
        {"id": "ep:chat", "label": "POST /chat", "group": "endpoint"},
        {"id": "ep:models", "label": "POST /discover-models", "group": "endpoint"},
        {"id": "ep:compare", "label": "POST /compare-models", "group": "endpoint"},
        {"id": "ep:alerts", "label": "GET /alerts", "group": "endpoint"},
    ]
    for ep in endpoints:
        ep_node = {
            "id": ep["id"],
            "label": ep["label"],
            "group": ep["group"],
            "shape": "hexagon",
        }
        nodes.append(ep_node)
    
    # ── Manual edges: Tools → Data Sources ─────────────────────────────────
    tool_to_datasource = [
        ("file:langchain_tools.py", "ds:congress", "CongressSearchTool"),
        ("file:langchain_tools.py", "ds:opensecrets", "OpenSecretsTool"),
        ("file:langchain_tools.py", "ds:votesmart", "VoteSmartTool"),
        ("file:langchain_tools.py", "ds:qdrant", "VectorSearchTool"),
        ("file:langchain_tools.py", "ds:postgres", "DatabaseQueryTool"),
        ("file:langchain_tools.py", "ds:gdelt", "GDELTSearchTool"),
        ("file:langchain_tools.py", "ds:openrouter", "OpenRouterChatModel"),
        ("file:openrouter_sdk.py", "ds:openrouter", "OpenRouterClient"),
        ("file:scorer.py", "ds:openrouter", "HonestyEngine"),
    ]
    for src, tgt, label in tool_to_datasource:
        edges.append({"from": src, "to": tgt, "label": label, "dashes": False})
    
    # ── Manual edges: API → Agents ─────────────────────────────────────────
    edges.append({"from": "api:agents_endpoints.py", "to": "file:orchestrator.py", "label": "calls", "dashes": False})
    edges.append({"from": "api:agents_endpoints.py", "to": "file:openrouter_sdk.py", "label": "calls", "dashes": False})
    
    # ── Manual edges: Endpoints → API module ───────────────────────────────
    for ep in endpoints:
        edges.append({"from": "api:agents_endpoints.py", "to": ep["id"], "label": "defines", "dashes": True})
    
    # ── Manual edges: Orchestrator → Agents ────────────────────────────────
    edges.append({"from": "file:orchestrator.py", "to": "ResearchAgent", "label": "wraps", "dashes": True})
    edges.append({"from": "file:orchestrator.py", "to": "ConsistencyAnalyzer", "label": "wraps", "dashes": True})
    edges.append({"from": "file:orchestrator.py", "to": "AlertGenerator", "label": "wraps", "dashes": True})
    edges.append({"from": "file:orchestrator.py", "to": "OpenDiscourseAgentSystem", "label": "is", "dashes": True})
    
    return {"nodes": nodes, "edges": edges}


def generate_html(graph_data: Dict[str, Any]) -> str:
    """Generate an interactive HTML visualization using vis-network."""
    
    nodes_json = json.dumps(graph_data["nodes"])
    edges_json = json.dumps(graph_data["edges"])
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenDiscourse Agent Architecture</title>
    <script src="https://unpkg.com/vis-network@9.1.6/dist/vis-network.min.js"></script>
    <script src="https://unpkg.com/vis-data@7.1.9/peer/umd/vis-data.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0c; color: #e0e0e0; overflow: hidden;
        }}
        #mynetwork {{ 
            width: 100vw; height: 100vh;
            background: radial-gradient(ellipse at 50% 50%, #121316 0%, #0a0a0c 100%);
        }}
        #legend {{
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 20px; padding: 12px 24px;
            background: rgba(18, 19, 22, 0.9);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            backdrop-filter: blur(16px);
            font-size: 12px;
            z-index: 100;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .legend-color {{ width: 14px; height: 14px; border-radius: 50%; }}
        #title {{
            position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
            font-family: 'Outfit', -apple-system, sans-serif;
            font-weight: 800; font-size: 20px;
            letter-spacing: -0.02em;
            background: rgba(18, 19, 22, 0.8);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 12px 24px;
            backdrop-filter: blur(16px);
            z-index: 100;
            text-align: center;
        }}
        #title small {{ display: block; font-weight: 400; font-size: 12px; color: #a0a0ab; margin-top: 4px; }}
    </style>
</head>
<body>
    <div id="title">
        🧠 OpenDiscourse Agent System
        <small>Drag nodes · Scroll to zoom · Click for details</small>
    </div>
    <div id="mynetwork"></div>
    <div id="legend">
        <span class="legend-item"><span class="legend-color" style="background:#4a1942;border:2px solid #a855f7"></span> Agent Modules</span>
        <span class="legend-item"><span class="legend-color" style="background:#1a4731;border:2px solid #10b981"></span> API Modules</span>
        <span class="legend-item"><span class="legend-color" style="background:#3b1f3b;border:2px solid #ec4899"></span> Agent Classes</span>
        <span class="legend-item"><span class="legend-color" style="background:#1e3a5f;border:2px solid #3b82f6"></span> API Endpoints</span>
        <span class="legend-item"><span class="legend-color" style="background:#1e2a4a;border:2px solid #60a5fa"></span> OpenRouter</span>
        <span class="legend-item"><span class="legend-color" style="background:#1a3a3a;border:2px solid #14b8a6"></span> Data Sources</span>
        <span class="legend-item"><span class="legend-color" style="background:#3a2a1a;border:2px solid #f59e0b"></span> Existing Engine</span>
    </div>
    <script>
        (function() {{
            const nodes = new vis.DataSet({nodes_json});
            const edges = new vis.DataSet({edges_json});

            const container = document.getElementById('mynetwork');
            
            const data = {{ nodes, edges }};
            const options = {{
                nodes: {{
                    font: {{ color: '#e0e0e0', size: 14, face: 'Inter, -apple-system, sans-serif' }},
                    borderWidth: 2,
                    shadow: {{ enabled: true, size: 6 }}
                }},
                edges: {{
                    font: {{ color: '#a0a0ab', size: 10, align: 'middle', strokeWidth: 0 }},
                    width: 1.5,
                    arrows: {{ to: {{ enabled: true, scaleFactor: 0.8 }} }},
                    color: {{ color: '#6b7280', highlight: '#a855f7', hover: '#a855f7' }},
                    smooth: {{ type: 'continuous' }}
                }},
                physics: {{
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -40,
                        centralGravity: 0.005,
                        springLength: 200,
                        springConstant: 0.02,
                        damping: 0.4,
                    }},
                    stabilization: {{ iterations: 200 }}
                }},
                groups: {{
                    agent_module: {{ color: {{ background: '#4a1942', border: '#a855f7' }} }},
                    api_module: {{ color: {{ background: '#1a4731', border: '#10b981' }} }},
                    agent_class: {{ color: {{ background: '#3b1f3b', border: '#ec4899' }} }},
                    endpoint: {{ color: {{ background: '#1e3a5f', border: '#3b82f6' }} }},
                    openrouter: {{ color: {{ background: '#1e2a4a', border: '#60a5fa' }} }},
                    datasource: {{ color: {{ background: '#1a3a3a', border: '#14b8a6' }} }},
                    existing_module: {{ color: {{ background: '#3a2a1a', border: '#f59e0b' }} }},
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200,
                    navigationButtons: true,
                    keyboard: true,
                }},
            }};

            const network = new vis.Network(container, data, options);

            // Open URLs on double-click
            network.on('doubleClick', function(params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    const node = nodes.get(nodeId);
                    if (node.title) {{
                        // Show in console
                        console.log(node.title);
                    }}
                }}
            }});

            // Fit to viewport after stabilization
            network.on('stabilizationIterationsDone', function() {{
                network.fit({{ animation: true }});
            }});

            // Handle window resize
            window.addEventListener('resize', function() {{
                network.fit({{ animation: true }});
            }});
        }})();
    </script>
</body>
</html>"""


def main():
    print("🔍 Analyzing OpenDiscourse Agent System...")
    
    graph_data = analyze_project()
    
    print(f"   Found {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
    
    html = generate_html(graph_data)
    
    output_path = Path(__file__).parent / "agent_architecture.html"
    output_path.write_text(html)
    
    print(f"   Written to: {output_path}")
    print()
    print("📊 Visualization generated! Open it in your browser:")
    print(f"   file://{output_path.resolve()}")
    print()
    print(" Or run: open scripts/agent_architecture.html")


if __name__ == "__main__":
    main()