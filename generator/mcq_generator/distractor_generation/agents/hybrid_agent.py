# agents/hybrid_agent.py
import os
from typing import List, Dict
from ..config import Config
from .llm_agent import LLMAgent
from ..utils import text_similarity, load_json
import logging

logging.basicConfig(level=logging.INFO)

class HybridAgent:
    """Hybrid agent: Database first, then LLM fallback (reuses LLMAgent)."""
    
    def __init__(self, config: Config, llm_agent: LLMAgent):
        self.config = config
        self.llm_agent = llm_agent  # Reuse existing LLM agent
        self.misconceptions_db = self._load_misconceptions_db()
    
    def _load_misconceptions_db(self) -> Dict:
        """Load misconceptions database."""
        if not self.config.USE_DATABASE:
            return {}
        
        db_path = self.config.MISCONCEPTIONS_DB_PATH
        if not os.path.exists(db_path):
            print(f"⚠️  Misconceptions DB not found at {db_path}")
            logging.warning(f"Misconceptions DB not found at {db_path}")
            return {}
        logging.info(f"Loaded misconceptions DB from {db_path}")
        return load_json(db_path) or {}
    
    def generate(self, stem: str, answer: str, q_type: str, concept_tag: str = "") -> List[Dict]:
        """
        Hybrid generation:
        1. First try to get from database
        2. If insufficient, use LLM agent as fallback
        """
        distractors = []
        
        # Step 1: Get from database (if enabled)
        if self.config.USE_DATABASE and concept_tag:
            db_distractors = self._get_from_database(concept_tag, answer)
            distractors.extend(db_distractors)
            print(f"Database: Found {len(db_distractors)} distractors")
            logging.info(f"Database: Found {len(db_distractors)} distractors for concept_tag '{concept_tag}'")
        
        # Step 2: If not enough, use LLM agent
        needed = self.config.MAX_DISTRACTORS_PER_QUESTION - len(distractors)
        if needed > 0 and self.llm_agent:
            print(f"   LLM: Generating {needed} more distractors")
            llm_distractors = self.llm_agent.generate(stem, answer, q_type, concept_tag)
            logging.info(f"LLM: Generated {len(llm_distractors)} distractors")
            
            # Take only as many as needed
            for d in llm_distractors:
                if len(distractors) >= self.config.MAX_DISTRACTORS_PER_QUESTION:
                    break
                distractors.append(d)
                logging.info(f"Added LLM distractor: {d['text']}")
        
        return distractors[:self.config.MAX_DISTRACTORS_PER_QUESTION]
    
    def _get_from_database(self, concept_tag: str, correct_answer: str) -> List[Dict]:
        """Get distractors from misconceptions database."""
        if not concept_tag or not self.misconceptions_db:
            return []
        
        # Look for exact concept tag match
        if concept_tag in self.misconceptions_db:
            misconceptions = self.misconceptions_db[concept_tag]
            distractors = []
            
            for mc in misconceptions:
                if isinstance(mc, dict):
                    text = mc.get("text", "")
                    if not text:
                        continue
                    logging.info(f"Database distractor found: {text}")
                    
                    distractors.append({
                        "text": text.strip(),
                        "type": mc.get("type", "misconception"),
                        "source": "database",
                        "rationale": mc.get("rationale", f"Common misconception about {concept_tag}"),
                        "_sim": text_similarity(text, correct_answer)
                    })
                elif isinstance(mc, str):
                    distractors.append({
                        "text": mc.strip(),
                        "type": "misconception",
                        "source": "database",
                        "rationale": f"Common misconception about {concept_tag}",
                        "_sim": text_similarity(mc, correct_answer)
                    })
                    
                
                # Take max 2 from DB to leave room for LLM
                if len(distractors) >= 2:
                    break
            
            return distractors
        
        # Try partial matches (if concept_tag is "ml_fundamentals", also check "ml_")
        for key in self.misconceptions_db.keys():
            if concept_tag.startswith(key) or key.startswith(concept_tag):
                # Return 1-2 from related concept
                misconceptions = self.misconceptions_db[key]
                distractors = []
                
                for mc in misconceptions[:1]:  # Just take 1 from related
                    if isinstance(mc, dict):
                        text = mc.get("text", "")
                    else:
                        text = mc
                    
                    if text:
                        distractors.append({
                            "text": text.strip(),
                            "type": "misconception",
                            "source": "database",
                            "rationale": f"Related misconception from {key}",
                            "_sim": text_similarity(text, correct_answer)
                        })
                
                return distractors
        
        return []