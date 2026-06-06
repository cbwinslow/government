import logging
from opendiscourse.swarm.state import AgentState
from opendiscourse.engine.llm_factory import get_llm, get_callbacks

logger = logging.getLogger(__name__)

def supervisor_node(state: AgentState) -> AgentState:
    """
    The Master Orchestrator. Analyzes the user request and routes
    to the correct specialized agent.
    """
    logger.info("Supervisor Node active. Routing request...")
    
    llm = get_llm() # Callbacks are typically bound at the graph level in LangGraph, but available here
    
    request = state.get("user_request", "").lower()
    
    # Basic Routing Logic (in production, use LLM structured output / tool calling)
    if "congress" in request or "bill" in request or "vote" in request:
        next_agent = "congress_agent"
    else:
        next_agent = "END"
        
    state["next_agent"] = next_agent
    state["status"] = f"delegated_to_{next_agent}"
    
    # Append to messages array
    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": f"Supervisor routed task to: {next_agent}"})
    state["messages"] = messages
    
    return state
