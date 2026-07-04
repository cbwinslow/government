import os
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from src.opendiscourse.swarm.state import AgentState
from src.opendiscourse.engine.llm_factory import get_agent_llm

# --- Mock Tools ---
@tool
def search_courtlistener(query: str) -> str:
    """Searches the CourtListener API for legal dockets matching the query."""
    print(f"    [Tool Executing] search_courtlistener({query})")
    return json.dumps([{"docket_id": "12345", "title": "United States v. Epstein", "court": "SDNY"}])

@tool
def fetch_fec_filings(candidate_name: str) -> str:
    """Fetches campaign finance filings from the FEC for a given candidate."""
    print(f"    [Tool Executing] fetch_fec_filings({candidate_name})")
    return json.dumps([{"receipt_id": "FEC-9876", "amount": 5000, "donor": "PAC"}])

tools = [search_courtlistener, fetch_fec_filings]

def get_scraper_prompt() -> str:
    """Loads the system prompt from the OpenClaw rules directory."""
    prompt_path = "/home/cbwinslow/workspace/government/src/opendiscourse/swarm/agents/ScraperAgent/.agent/rules/system_prompt.md"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are the Scraper Agent. Use your tools to find data."

def scraper_node(state: AgentState) -> dict:
    """The LangGraph node for the ScraperAgent."""
    print("--- [ScraperAgent Node] Executing ---")
    
    llm = get_agent_llm()
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = get_scraper_prompt()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm_with_tools
    
    # Invoke the LLM
    response = chain.invoke({"messages": state["messages"]})
    
    messages_to_return = [response]
    
    # If the LLM decided to use a tool, we execute it immediately (simple synchronous flow for now)
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute the matched tool function
            tool_func = next((t for t in tools if t.name == tool_name), None)
            if tool_func:
                tool_result = tool_func.invoke(tool_args)
                
                # Append the ToolMessage so the LLM knows the result
                messages_to_return.append(
                    ToolMessage(content=tool_result, tool_call_id=tool_call["id"])
                )
    
    return {"messages": messages_to_return}
