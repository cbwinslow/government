"""
OpenStates API Ingestion Pipeline.

This module is responsible for fetching state-level politician data, 
including state legislation and roll-call votes. It bridges the gap 
between federal (Congress.gov) and local political tracking.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional

from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

class OpenStatesClient:
    """
    Client for interacting with the OpenStates API v3.
    Provides methods for pulling state legislators, bills, and votes.
    """
    
    BASE_URL = "https://v3.openstates.org"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENSTATES_API_KEY
        if not self.api_key:
            logger.warning("OPENSTATES_API_KEY is missing. API calls will fail.")

    async def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Base method to execute API calls to OpenStates."""
        if not self.api_key:
            raise ValueError("Cannot make request: OPENSTATES_API_KEY is not configured.")

        headers = {
            "X-API-KEY": self.api_key,
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/{endpoint.strip('/')}"

        async with httpx.AsyncClient() as client:
            try:
                # OpenStates API requires the key in the headers
                response = await client.get(url, headers=headers, params=params or {})
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error fetching {endpoint} from OpenStates: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network Error fetching {endpoint} from OpenStates: {e}")
                raise

    async def get_legislator(self, openstates_id: str) -> Dict[str, Any]:
        """
        Fetch details for a specific state legislator.
        :param openstates_id: e.g. ocd-person/1234abcd-1234-1234-1234-123456abcdef
        """
        data = await self._make_request(f"people", {"id": openstates_id})
        results = data.get("results", [])
        return results[0] if results else {}

    async def get_recent_votes(self, openstates_id: str) -> List[Dict[str, Any]]:
        """
        Fetch recent votes cast by the state legislator.
        OpenStates typically requires you to fetch bills/votes for a jurisdiction,
        then filter by the voter_id.
        """
        # Note: The v3 REST API is somewhat limited for reverse-lookup of votes by person.
        # Often, a GraphQL query is better for this, but as a REST fallback:
        # We query bills sponsored by the person as a proxy for their actions.
        data = await self._make_request("bills", {"sponsor_id": openstates_id, "sort": "updated_desc"})
        return data.get("results", [])

async def sync_openstates_for_politician(openstates_id: str):
    """
    Given a politician's OpenStates OCD ID, fetch their details and sponsored legislation,
    and store them in the database.
    """
    client = OpenStatesClient()
    
    logger.info(f"Syncing OpenStates data for ID: {openstates_id}")
    
    try:
        member_details = await client.get_legislator(openstates_id)
        sponsored_bills = await client.get_recent_votes(openstates_id)
        
        # TODO: Inject SQLAlchemy session here to save to Postgres DB.
        
        return {
            "status": "success",
            "name": member_details.get('name', 'Unknown'),
            "sponsored_bills_count": len(sponsored_bills)
        }
    except Exception as e:
        logger.error(f"Failed to sync OpenStates for {openstates_id}: {e}")
        return {"status": "error", "message": str(e)}
