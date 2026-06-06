import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from opendiscourse.engine.scorer import HonestyEngine

logger = logging.getLogger(__name__)

class ExtractedEntity(BaseModel):
    name: str = Field(..., description="The name of the politician or entity mentioned.")
    context: str = Field(..., description="A short summary of what the entity is doing or what is being said about them in the text.")
    sentiment_score: int = Field(..., description="Sentiment of the mention towards this entity from -10 (very negative) to 10 (very positive).")

class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity] = Field(..., description="List of all politicians and major political entities mentioned.")


class GDELTEntityExtractor:
    """
    Extracts politicians and political entities from GDELT news snippets
    using the LLM engine to map unstructured text into structured mentions.
    """
    def __init__(self, engine: Optional[HonestyEngine] = None):
        # We reuse the HonestyEngine's client and primary model for consistency
        self.engine = engine or HonestyEngine()
        self.client = self.engine.client
        self.model = self.engine.primary_model.value

    async def extract_entities(self, article_text: str) -> List[ExtractedEntity]:
        """
        Extracts political entities and their contexts from a given news article snippet.
        """
        system_prompt = (
            "You are an advanced Named Entity Recognition (NER) system for a political database. "
            "Your task is to extract the names of all US politicians or major political organizations "
            "mentioned in the provided text, along with a brief summary of their context and the sentiment "
            "of the article towards them."
        )

        user_prompt = f"Please extract entities from the following news text:\n\n{article_text}"

        try:
            logger.info(f"Running Entity Extraction using model: {self.model}")
            
            # Using OpenRouter/OpenAI SDK with Structured Outputs
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=ExtractionResult,
                temperature=0.1
            )
            
            result = response.choices[0].message.parsed
            logger.info(f"Extracted {len(result.entities)} entities.")
            return result.entities

        except Exception as e:
            logger.error(f"Error during entity extraction: {e}")
            return []

    async def map_to_database(self, entities: List[ExtractedEntity], db_store) -> List[Dict]:
        """
        Maps extracted text entities to Master Identity UUIDs using the RelationalStore.
        `db_store` should be an instance of RelationalStore.
        """
        mapped_results = []
        for entity in entities:
            # Note: A real implementation would parse the name and use fuzzy matching 
            # or vector similarity (pgvector) to find the correct `politicians` record.
            # Here we demonstrate the structural integration:
            
            # 1. Attempt exact/fuzzy match on names
            # politician_record = db_store.find_politician_by_name(entity.name)
            
            # 2. If matched, append to results
            # if politician_record:
            #     mapped_results.append({
            #         "politician_id": politician_record["id"],
            #         "context": entity.context,
            #         "sentiment": entity.sentiment_score
            #     })
            pass
            
        return mapped_results
