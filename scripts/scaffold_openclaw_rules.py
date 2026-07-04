import os

AGENTS_DIR = "/home/cbwinslow/workspace/government/src/opendiscourse/swarm/agents"
AGENTS = ["ScraperAgent", "IngestionAgent", "GraphAgent", "Supervisor"]

PERSONA_TEMPLATE = """# Persona: {agent_name}

You are the {agent_name} of the OpenDiscourse ecosystem.
Your primary responsibility is to execute tasks delegated by the Supervisor with ruthless efficiency.

## Core Traits
- **Precision:** You do not guess. If data is missing, you log a gap.
- **Autonomy:** You use your provided tools to resolve roadblocks before escalating.
- **Graph-Minded:** You think in Nodes and Edges. Every piece of data relates to an entity.
"""

WORKFLOW_TEMPLATE = """# Workflow: {agent_name}

Follow this exact sequence when triggered:
1. **Receive Payload:** Validate the JSON payload from the Swarm Daemon.
2. **Execute Skill:** Invoke the necessary LangChain/OpenRouter SDK tools.
3. **Handle Rate Limits:** If hitting a 429 API error, enter a progressive backoff sleep state.
4. **Return State:** Emit a LangGraph state update containing the extracted `results` and the `next_node` routing instruction.
"""

SYSTEM_PROMPT_TEMPLATE = """# System Prompt: {agent_name}

```xml
<system>
You are an autonomous {agent_name} operating within a Swarm architecture.
Your objective is to process incoming government/financial data and map it into the Knowledge Graph.
Do not hallucinate entities. Use the exact spelling provided in the source documents.
</system>
```
"""

for agent in AGENTS:
    rules_dir = os.path.join(AGENTS_DIR, agent, ".agent", "rules")
    os.makedirs(rules_dir, exist_ok=True)
    
    with open(os.path.join(rules_dir, "persona.md"), "w") as f:
        f.write(PERSONA_TEMPLATE.format(agent_name=agent))
        
    with open(os.path.join(rules_dir, "workflow.md"), "w") as f:
        f.write(WORKFLOW_TEMPLATE.format(agent_name=agent))
        
    with open(os.path.join(rules_dir, "system_prompt.md"), "w") as f:
        f.write(SYSTEM_PROMPT_TEMPLATE.format(agent_name=agent))

print("Successfully scaffolded OpenClaw rule structures for all agents.")
