from typing import TypedDict, Annotated, List, Optional
import operator

class AgentState(TypedDict):
    """
    The state structure passed between all nodes in the LangGraph swarm.
    """
    user_request: str
    messages: Annotated[List[dict], operator.add]
    
    # Routing
    next_agent: Optional[str]
    
    # Execution Tracking
    downloaded_files: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    status: str
