from langgraph.graph import StateGraph, END
from opendiscourse.swarm.state import AgentState
from opendiscourse.swarm.agents.supervisor import supervisor_node
from opendiscourse.swarm.agents.congress_agent import congress_node

def build_graph() -> StateGraph:
    """
    Constructs the LangGraph Swarm workflow.
    """
    # 1. Initialize the graph with our custom State
    workflow = StateGraph(AgentState)
    
    # 2. Add Nodes (Agents)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("congress_agent", congress_node)
    
    # 3. Define the Entry Point
    workflow.set_entry_point("supervisor")
    
    # 4. Define Edges (Routing Logic)
    # The supervisor decides who goes next based on state["next_agent"]
    def route_from_supervisor(state: AgentState):
        if state.get("next_agent") == "congress_agent":
            return "congress_agent"
        return END
        
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "congress_agent": "congress_agent",
            END: END
        }
    )
    
    # After a specialist finishes, it returns to the supervisor (or END, depending on architecture)
    # Here, we route congress_agent to END for simplicity, but in a true cyclic swarm, 
    # it would return to supervisor for the next task.
    workflow.add_edge("congress_agent", END)
    
    return workflow.compile()

# Provide a compiled app instance for direct import
app = build_graph()
