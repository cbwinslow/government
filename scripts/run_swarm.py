import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from opendiscourse.swarm.graph import app

def main():
    print("Starting LangGraph Swarm...")
    
    # Define the initial state (the user's request)
    initial_state = {
        "user_request": "Please ingest the latest bulk data from congress",
        "messages": [{"role": "user", "content": "Please ingest the latest bulk data from congress"}],
        "downloaded_files": [],
        "errors": []
    }
    
    # Run the graph
    print(f"\n[USER INPUT]: {initial_state['user_request']}\n")
    
    # Stream the state updates as nodes execute
    for s in app.stream(initial_state):
        if "__end__" not in s:
            node_name = list(s.keys())[0]
            print(f"--- Node Executed: {node_name} ---")
            node_state = s[node_name]
            if "status" in node_state:
                print(f"Status: {node_state['status']}")
            if "messages" in node_state and len(node_state["messages"]) > 0:
                print(f"Last Message: {node_state['messages'][-1]['content']}")
            print("-" * 40 + "\n")
            
    print("Swarm Execution Complete.")

if __name__ == "__main__":
    main()
