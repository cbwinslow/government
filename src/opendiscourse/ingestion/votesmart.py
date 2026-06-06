"""
Project Vote Smart API Ingestion Pipeline.

This module is responsible for fetching interest group ratings (e.g. NRA, ACLU)
and issue positions for politicians to help quantify their ideological leaning.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional

from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

class VoteSmartClient:
    """
    Client for interacting with the Project Vote Smart API.
    Provides methods for pulling candidate ratings from special interest groups and key votes.
    """
    
    BASE_URL = "http://api.votesmart.org/"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.VOTESMART_API_KEY
        if not self.api_key:
            logger.warning("VOTESMART_API_KEY is missing. API calls will fail.")

    async def _make_request(self, method: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Base method to execute API calls to VoteSmart."""
        if not self.api_key:
            raise ValueError("Cannot make request: VOTESMART_API_KEY is not configured.")

        payload = {
            "key": self.api_key,
            "o": "JSON",  # Output format
            **params
        }
        
        # VoteSmart API paths are structured as ClassName.methodName
        url = f"{self.BASE_URL}{method}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error fetching {method} from VoteSmart: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network Error fetching {method} from VoteSmart: {e}")
                raise

    async def get_interest_group_ratings(self, candidate_id: str) -> List[Dict[str, Any]]:
        """
        Fetch ratings from various interest groups for a politician.
        :param candidate_id: The VoteSmart candidate ID
        """
        data = await self._make_request("Rating.getCandidateRating", {"candidateId": candidate_id})
        # VoteSmart JSON structure
        ratings = data.get("candidateRating", {}).get("rating", [])
        
        # If there's only one rating, the API sometimes returns a dict instead of a list
        if isinstance(ratings, dict):
            ratings = [ratings]
            
        return ratings

    async def get_votes(self, candidate_id: str) -> List[Dict[str, Any]]:
        """
        Fetch key votes cast by the politician.
        :param candidate_id: The VoteSmart candidate ID
        """
        data = await self._make_request("Votes.getByOfficial", {"candidateId": candidate_id})
        
        votes = data.get("votes", {}).get("vote", [])
        if isinstance(votes, dict):
            votes = [votes]
            
        return votes

async def sync_votesmart_for_politician(candidate_id: str):
    """
    Given a politician's VoteSmart candidate ID, fetch their ratings and key votes,
    and store them in the database.
    """
    client = VoteSmartClient()
    
    logger.info(f"Syncing VoteSmart data for Candidate ID: {candidate_id}")
    
    try:
        ratings = await client.get_interest_group_ratings(candidate_id)
        votes = await client.get_votes(candidate_id)
        
        # TODO: Inject SQLAlchemy session here to save to Postgres DB.
        
        return {
            "status": "success",
            "ratings_count": len(ratings),
            "votes_count": len(votes)
        }
    except Exception as e:
        logger.error(f"Failed to sync VoteSmart for {candidate_id}: {e}")
        return {"status": "error", "message": str(e)}
