"""
Congress.gov API Ingestion Pipeline.

This module is responsible for fetching official floor speeches (The 'Words'),
roll-call votes (The 'Actions'), and serving as the Master Identity list 
(Bioguide profiles) for the Honesty Engine.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional

from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

class CongressClient:
    """
    Client for interacting with the official Congress.gov API.
    Provides methods for pulling members, votes, and congressional record speeches.
    """
    
    BASE_URL = "https://api.congress.gov/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CONGRESS_API_KEY
        if not self.api_key:
            logger.warning("CONGRESS_API_KEY is missing. API calls will fail.")

    async def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Base method to execute API calls to Congress.gov."""
        if not self.api_key:
            raise ValueError("Cannot make request: CONGRESS_API_KEY is not configured.")

        payload = {
            "api_key": self.api_key,
            "format": "json"
        }
        if params:
            payload.update(params)

        url = f"{self.BASE_URL}/{endpoint.strip('/')}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error fetching {endpoint} from Congress.gov: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network Error fetching {endpoint} from Congress.gov: {e}")
                raise

    async def get_member(self, bioguide_id: str) -> Dict[str, Any]:
        """
        Fetch details for a specific member of Congress by Bioguide ID.
        """
        data = await self._make_request(f"member/{bioguide_id}")
        return data.get("member", {})

    async def get_member_votes(self, bioguide_id: str) -> List[Dict[str, Any]]:
        """
        Fetch the voting record for a specific member.
        Since the official API might not directly return roll calls by member easily,
        this will likely require fetching roll calls and filtering, or relying on GovTrack.
        For now, this queries the sponsored legislation as a proxy for 'Actions'.
        """
        data = await self._make_request(f"member/{bioguide_id}/sponsored-legislation")
        return data.get("sponsoredLegislation", [])

async def sync_congress_for_politician(bioguide_id: str):
    """
    Given a politician's Bioguide ID, fetch their details and sponsored legislation,
    and store them in the database.
    """
    client = CongressClient()
    
    logger.info(f"Syncing Congress.gov data for Bioguide ID: {bioguide_id}")
    
    try:
        member_details = await client.get_member(bioguide_id)
        sponsored_bills = await client.get_member_votes(bioguide_id)
        
        # TODO: Inject SQLAlchemy session here to save to Postgres DB.
        
        return {
            "status": "success",
            "name": f"{member_details.get('firstName')} {member_details.get('lastName')}",
            "sponsored_bills_count": len(sponsored_bills)
        }
    except Exception as e:
        logger.error(f"Failed to sync Congress.gov for {bioguide_id}: {e}")
        return {"status": "error", "message": str(e)}
