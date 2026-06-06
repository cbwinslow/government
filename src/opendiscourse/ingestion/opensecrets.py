"""
OpenSecrets API Ingestion Pipeline.

This module is responsible for fetching campaign finance data, PAC contributions,
and lobbying records from the OpenSecrets API to track the 'Actions' (Follow The Money)
side of the Honesty Engine.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional

from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

class OpenSecretsClient:
    """
    Client for interacting with the OpenSecrets.org API.
    Provides methods for pulling candidate summaries and top contributors.
    """
    
    BASE_URL = "https://www.opensecrets.org/api/"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENSECRETS_API_KEY
        if not self.api_key:
            logger.warning("OPENSECRETS_API_KEY is missing. API calls will fail.")

    async def _make_request(self, method: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Base method to execute API calls to OpenSecrets."""
        if not self.api_key:
            raise ValueError("Cannot make request: OPENSECRETS_API_KEY is not configured.")

        # OpenSecrets requires 'method' and 'apikey' in every request
        payload = {
            "apikey": self.api_key,
            "output": "json",
            "method": method,
            **params
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error fetching {method} from OpenSecrets: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network Error fetching {method} from OpenSecrets: {e}")
                raise

    async def get_legislator_summary(self, cid: str, cycle: str = "2024") -> Dict[str, Any]:
        """
        Fetch summary fundraising information for a specific politician.
        :param cid: The OpenSecrets Candidate ID (e.g., N00007360 for Nancy Pelosi)
        :param cycle: The election cycle year
        """
        data = await self._make_request("candSummary", {"cid": cid, "cycle": cycle})
        # The OpenSecrets JSON structure is nested: response -> summary -> @attributes
        return data.get("response", {}).get("summary", {}).get("@attributes", {})

    async def get_top_contributors(self, cid: str, cycle: str = "2024") -> List[Dict[str, Any]]:
        """
        Fetch top organizational contributors to a politician.
        Note: These are PACs and individuals associated with the organization, not the org itself.
        """
        data = await self._make_request("candContrib", {"cid": cid, "cycle": cycle})
        contributors = data.get("response", {}).get("contributors", {}).get("contributor", [])
        
        # Extract the attributes from the annoying nested structure
        return [c.get("@attributes", {}) for c in contributors]

async def sync_opensecrets_for_politician(cid: str, cycle: str = "2024"):
    """
    Given a politician's OpenSecrets CID, fetch their financial summary
    and top contributors, and store them in the database.
    """
    client = OpenSecretsClient()
    
    logger.info(f"Syncing OpenSecrets data for CID: {cid} (Cycle: {cycle})")
    
    try:
        summary = await client.get_legislator_summary(cid, cycle)
        contributors = await client.get_top_contributors(cid, cycle)
        
        # TODO: Once the SQLAlchemy session is injected here, save this to the Postgres DB.
        # This will link directly to the Politician table via `fec_id` or `opensecrets_id`.
        
        return {
            "status": "success",
            "summary": summary,
            "contributors_count": len(contributors)
        }
    except Exception as e:
        logger.error(f"Failed to sync OpenSecrets for {cid}: {e}")
        return {"status": "error", "message": str(e)}
