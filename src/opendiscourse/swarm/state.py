from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """The central state object passed between nodes in the LangGraph."""
    
    # The message history, append-only via the operator.add reducer
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # The next node to route to, determined by the Supervisor
    next_node: str
    
    # The original query string for easy access
    query: str
    
    # Any data extracted by the agents
    extracted_data: dict
