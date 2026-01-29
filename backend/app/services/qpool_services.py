"""
QPool API Client Service
Handles communication with the question paraphrasing and distractor generation API
"""
import httpx
from typing import Dict, List, Optional, Any
from backend.app.core.config import get_settings

settings = get_settings()


class QPoolService:
    """Service for interacting with QPool API"""
    
    def __init__(self):
        # TODO: Add to your config file
        self.base_url = "http://127.0.0.1:8000"  # Adjust to your qpool API URL
        self.timeout = 30.0  # Timeout for API calls
    
    async def paraphrase_question(
        self,
        question_id: str,
        base_stem: str,
        base_answer: str,
        difficulty: str,
        concept_tags: List[str],
        is_template: bool = False,
        template_config: Optional[Dict] = None,
        transformations: List[str] = None,
        variants: int = 1,
        scenario_domains: Optional[List[str]] = None,
        generate_distractors: bool = True
    ) -> Dict[str, Any]:
        """
        Call QPool API to paraphrase question and generate distractors
        
        Args:
            question_id: Unique identifier for the question
            base_stem: Original question text
            base_answer: Correct answer
            difficulty: Question difficulty level
            concept_tags: List of concept tags
            is_template: Whether this is a template question
            template_config: Template configuration if applicable
            transformations: List of transformations to apply (default: ["paraphrase"])
            variants: Number of variants to generate (default: 1)
            scenario_domains: Domains for scenario generation
            generate_distractors: Whether to generate distractors
        
        Returns:
            Dict containing paraphrased question and distractors
        """
        
        if transformations is None:
            transformations = ["paraphrase"]
        
        payload = {
            "question_id": question_id,
            "base_stem": base_stem,
            "base_answer": base_answer,
            "difficulty": difficulty,
            "concept_tags": concept_tags,
            "questions_metadata": {
                "is_template": is_template,
                "template_config": template_config
            },
            "generation_config": {
                "transformations": transformations,
                "variants": variants,
                "scenario_domains": scenario_domains,
                "generate_distractors": generate_distractors
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/qpool/paraphrase",  # Adjust endpoint as needed
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.TimeoutException:
            raise Exception(f"QPool API timeout after {self.timeout}s")
        except httpx.HTTPError as e:
            raise Exception(f"QPool API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to paraphrase question: {str(e)}")
    
    def paraphrase_question_sync(
        self,
        question_id: str,
        base_stem: str,
        base_answer: str,
        difficulty: str,
        concept_tags: List[str],
        is_template: bool = False,
        template_config: Optional[Dict] = None,
        transformations: List[str] = None,
        variants: int = 1,
        scenario_domains: Optional[List[str]] = None,
        generate_distractors: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronous version of paraphrase_question for use in non-async contexts
        """
        
        if transformations is None:
            transformations = ["paraphrase"]
        
        payload = {
            "question_id": question_id,
            "base_stem": base_stem,
            "base_answer": base_answer,
            "difficulty": difficulty,
            "concept_tags": concept_tags,
            "questions_metadata": {
                "is_template": is_template,
                "template_config": template_config
            },
            "generation_config": {
                "transformations": transformations,
                "variants": variants,
                "scenario_domains": scenario_domains,
                "generate_distractors": generate_distractors
            }
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/qpool/generatevuc",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.TimeoutException:
            raise Exception(f"QPool API timeout after {self.timeout}s")
        except httpx.HTTPError as e:
            raise Exception(f"QPool API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to paraphrase question: {str(e)}")