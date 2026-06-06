import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from opendiscourse.swarm.graph import app

def main():
    print("Generating Mermaid diagram...")
    mermaid_code = app.get_graph().draw_mermaid()
    
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../swarm_architecture.md'))
    
    with open(output_path, "w") as f:
        f.write("# LangGraph Swarm Architecture\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")
        
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
