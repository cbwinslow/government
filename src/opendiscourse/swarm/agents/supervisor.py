import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from typing import Literal
from pydantic import BaseModel, Field

from src.opendiscourse.swarm.state import AgentState
from src.opendiscourse.engine.llm_factory import get_supervisor_llm

class RouteDecision(BaseModel):
    """The decision made by the Supervisor."""
    next_node: Literal['scraper_agent', 'graph_agent', 'FINISH'] = Field(
        description="The next agent to route to. Return 'FINISH' if the task is complete."
    )

def get_supervisor_prompt() -> str:
    """Loads the system prompt from the OpenClaw rules directory."""
    prompt_path = "/home/cbwinslow/workspace/government/src/opendiscourse/swarm/agents/Supervisor/.agent/rules/system_prompt.md"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are the Supervisor. Route the user's request."

def supervisor_node(state: AgentState) -> dict:
    """The LangGraph node for the Supervisor."""
    print("--- [Supervisor Node] Analyzing Request ---")
    
    llm = get_supervisor_llm()
    structured_llm = llm.with_structured_output(RouteDecision)
    
    system_prompt = get_supervisor_prompt()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the conversation above, who should act next? "
                   "If the required data has been successfully retrieved by the agents, "
                   "you MUST respond with 'FINISH'. Otherwise, respond with 'scraper_agent' or 'graph_agent'.")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({"messages": state["messages"]})
    
    print(f"--- [Supervisor Node] Decision: Route to {result.next_node} ---")
    
    return {"next_node": result.next_node}
