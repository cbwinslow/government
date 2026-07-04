import os
from langchain_core.messages import HumanMessage
from src.opendiscourse.swarm.graph import build_graph

# Ensure API keys are loaded
if not os.getenv("OPENROUTER_API_KEY"):
    print("WARNING: OPENROUTER_API_KEY not set. Using mock key for testing routing logic.")
    os.environ["OPENROUTER_API_KEY"] = "mock_key"

def main():
    print("Compiling LangGraph Engine...")
    graph = build_graph()
    
    # Initialize the starting state
    initial_state = {
        "messages": [HumanMessage(content="Find the latest court filings for United States v. Epstein.")],
        "query": "Find the latest court filings for United States v. Epstein.",
        "extracted_data": {},
        "next_node": ""
    }
    
    print("\nTriggering Supervisor Node with query: 'Find the latest court filings for United States v. Epstein.'")
    
    try:
        # We will stream the graph execution to see the node transitions
        for output in graph.stream(initial_state, config={"recursion_limit": 5}):
            for node_name, state_update in output.items():
                print(f"\n--- Node [{node_name}] Executed ---")
                
                if "next_node" in state_update:
                    print(f"Routing Decision: -> {state_update['next_node']}")
                    
                if "messages" in state_update and state_update["messages"]:
                    last_msg = state_update["messages"][-1]
                    print(f"Message Output: {last_msg.content[:200]}")
                    
    except Exception as e:
        print(f"\nGraph execution stopped: {e}")

if __name__ == "__main__":
    main()
