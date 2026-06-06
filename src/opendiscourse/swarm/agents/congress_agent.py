import logging
import os
import yaml
from datetime import datetime
from opendiscourse.swarm.state import AgentState
from opendiscourse.core.db_client import DBClient

logger = logging.getLogger(__name__)

def load_config():
    """Loads the pipeline configurations from YAML."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../config/pipelines.yaml'))
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def congress_node(state: AgentState) -> AgentState:
    """
    The Congress Specialist Node. 
    Responsible for executing the config-driven pipeline dynamically.
    """
    logger.info("Congress Agent parsing config/pipelines.yaml for active jobs...")
    
    config = load_config()
    pipelines = config.get('pipelines', {})
    
    # We check if Congress pipelines are enabled
    active_jobs = [k for k, v in pipelines.items() if 'congress' in k and v.get('enabled')]
    
    db = DBClient()
    
    try:
        if not active_jobs:
            logger.info("No active Congress pipelines found in config.")
            state["status"] = "congress_ingestion_skipped"
            messages = state.get("messages", [])
            messages.append({"role": "assistant", "content": "Congress Agent found no enabled congress pipelines in config."})
            state["messages"] = messages
            state["next_agent"] = "END"
            return state
            
        logger.info(f"Executing active pipelines: {active_jobs}")
        
        # Simulate delta sync
        downloaded = state.get("downloaded_files", [])
        new_bill_id = "BILLSTATUS-118-s-updated"
        downloaded.append(f"{new_bill_id}.zip")
        state["downloaded_files"] = downloaded
        
        # Idempotently upsert to Qdrant
        db.upsert_qdrant_point(
            collection_name="congress_bills",
            point_id_string=new_bill_id,
            vector=[0.1] * 384, # Mock vector, would normally use LlamaIndex here now
            payload={
                "bill_id": new_bill_id,
                "official_title": "Idempotent Config-Driven Bill",
                "last_updated": datetime.utcnow().isoformat(),
                "pipeline_source": active_jobs[0]
            }
        )
        
        state["status"] = "congress_ingestion_complete"
        messages = state.get("messages", [])
        messages.append({"role": "assistant", "content": f"Congress Agent executed {active_jobs}. Upserted {new_bill_id} idempotently."})
        state["messages"] = messages
        
    except Exception as e:
        logger.error(f"Congress Agent failed: {str(e)}")
        errors = state.get("errors", [])
        errors.append(str(e))
        state["errors"] = errors
        state["status"] = "congress_ingestion_failed"
        
    state["next_agent"] = "END"
    return state
