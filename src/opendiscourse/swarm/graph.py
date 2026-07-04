from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from src.opendiscourse.swarm.state import AgentState
from src.opendiscourse.swarm.agents.supervisor import supervisor_node
from src.opendiscourse.swarm.agents.scraper_agent import scraper_node

def build_graph() -> StateGraph:
    """Compiles the LangGraph nodes into a state machine."""
    workflow = StateGraph(AgentState)
    
    # 1. Add Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("scraper_agent", scraper_node)
    
    # We will add graph_agent later
    # workflow.add_node("graph_agent", graph_node)
    
    # 2. Add Edges
    # Entry point is always the supervisor
    workflow.set_entry_point("supervisor")
    
    # 3. Add Conditional Edges
    # The supervisor decides where to route next based on state["next_node"]
    def route_from_supervisor(state: AgentState):
        decision = state.get("next_node", "FINISH")
        if decision == "FINISH":
            return END
        return decision
        
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "scraper_agent": "scraper_agent",
            # "graph_agent": "graph_agent",
            END: END
        }
    )
    
    # For now, agents just return back to the supervisor when done
    workflow.add_edge("scraper_agent", "supervisor")
    
    return workflow.compile()
