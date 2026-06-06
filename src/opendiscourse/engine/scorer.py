import logging
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

class LLMModel(str, Enum):
    """
    Structured Enum of the absolute best free and premium models available via OpenRouter.
    Prioritizes massive parameter models (405B, 70B) over smaller 8B models.
    """
    # Free Tier (Massive Parameters)
    LAGUNA_M1_FREE = "poolside/laguna-m.1:free"
    HERMES_405B_FREE = "nousresearch/hermes-3-llama-3.1-405b:free"
    LLAMA_70B_FREE = "meta-llama/llama-3.3-70b-instruct:free"
    
    # Premium Tier
    GEMINI_3_PRO = "google/gemini-3.0-pro"
    
    # Special Routing Mode
    FUSION = "openrouter/fusion"


# Pydantic models for structured output from the LLM
class Discrepancy(BaseModel):
    issue: str = Field(..., description="The specific issue or topic (e.g., 'Gun Control', 'Corporate Tax').")
    words_summary: str = Field(..., description="Summary of what the politician said about this issue.")
    actions_summary: str = Field(..., description="Summary of how the politician voted or acted financially regarding this issue.")
    severity: int = Field(..., description="Severity of the contradiction on a scale of 1-10 (10 being outright lying).")
    explanation: str = Field(..., description="Detailed explanation of why this is a discrepancy.")

class HonestyScore(BaseModel):
    consistency_score: int = Field(..., description="Overall consistency/honesty score from 0-100. 100 means actions perfectly match words.")
    discrepancies: List[Discrepancy] = Field(..., description="List of identified contradictions between words and actions.")
    overall_summary: str = Field(..., description="A 2-3 paragraph summary of the politician's overall consistency.")


class HonestyEngine:
    """
    The core LLM engine responsible for evaluating a politician's stated positions ('Words')
    against their actual record ('Actions') using OpenRouter's advanced routing.
    """

    def __init__(self, primary_model: LLMModel = LLMModel.LAGUNA_M1_FREE):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.primary_model = primary_model
        
        # Define the fallback chain: start with the massive 405B, fallback to 70B if rate limited
        self.fallback_chain = [
            self.primary_model.value,
            LLMModel.LLAMA_70B_FREE.value
        ]

    async def evaluate_consistency(
        self, 
        politician_name: str, 
        words_context: List[str], 
        actions_context: List[str],
        use_fusion: bool = False
    ) -> Optional[HonestyScore]:
        """
        Evaluate a politician based on their words vs actions.
        
        :param use_fusion: If True, uses openrouter/fusion to panel multiple models and synthesize a judge response.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.error("OPENROUTER_API_KEY is not set. Cannot run Honesty Engine.")
            return None

        words_text = "\n- ".join(words_context)
        actions_text = "\n- ".join(actions_context)

        system_prompt = (
            "You are an impartial, highly analytical political auditor for the 'OpenDiscourse' platform. "
            "Your job is to generate an 'Honesty/Consistency Score' for politicians by strictly comparing "
            "their stated public positions ('Words') against their legislative and financial records ('Actions'). "
            "Identify any hypocrisies, lies, or discrepancies. Be objective and cite the provided evidence. "
            "You must output valid JSON matching the requested schema."
        )

        user_prompt = f"""
        Please evaluate the following record for: {politician_name}

        === THE WORDS (Speeches, Quotes, Social Media) ===
        - {words_text}

        === THE ACTIONS (Votes, Campaign Finance, Legislation) ===
        - {actions_text}
        
        Analyze the data and provide your assessment.
        """

        # Determine target model based on fusion toggle
        target_model = LLMModel.FUSION.value if use_fusion else self.primary_model.value
        
        # extra_body is used for fallback routing in OpenRouter
        extra_body = {}
        if not use_fusion:
            extra_body["models"] = self.fallback_chain

        try:
            logger.info(f"Running Honesty Engine evaluation for {politician_name} (Model: {target_model})...")
            
            # Using Structured Outputs (JSON Schema) via OpenRouter/OpenAI SDK
            response = await self.client.beta.chat.completions.parse(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=HonestyScore,
                temperature=0.2,
                extra_body=extra_body
            )
            
            result = response.choices[0].message.parsed
            logger.info(f"Successfully evaluated {politician_name}. Score: {result.consistency_score}/100")
            return result

        except Exception as e:
            logger.error(f"Error evaluating consistency for {politician_name}: {e}")
            return None
