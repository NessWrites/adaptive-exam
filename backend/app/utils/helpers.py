import pandas as pd
import json
import re
from datetime import datetime, date
from typing import Tuple, Dict, Any, Optional

def format_response(data):
    return {"success": True, "data": data}

def parse_score(score_str: str) -> Tuple[Optional[int], Optional[int]]:
    try:
        obtained, total = score_str.split('/')
        return int(obtained), int(total)
    except Exception:
        return None, None

def parse_marks(marks_str: str) -> Optional[int]:
    try:
        return int(marks_str.split()[0])
    except Exception:
        return None

def parse_datetime(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        cleaned = date_str.replace(" ,", ",").strip()
        return datetime.strptime(cleaned, "%B %d, %Y %I:%M %p")
    except Exception:
        return None

def parse_options_metadata(metadata_str: str) -> Dict[str, Any]:
    """Enhanced to extract n_choices and correct_answer"""
    try:
        opts = json.loads(metadata_str)
        if not isinstance(opts, list):
            return {"all_options": [], "correct_answers": [], "n_choices": 1, "correct_answer": 1}
        
        all_options = [o.get("label") for o in opts if "label" in o]
        correct_answers = [o.get("label") for o in opts if o.get("selected")]
        
        n_choices = len(all_options) if all_options else 1
        correct_answer = 1
        
        if correct_answers and all_options:
            try:
                correct_answer = all_options.index(correct_answers[0]) + 1
            except (ValueError, IndexError):
                correct_answer = 1
                
        return {
            "all_options": all_options, 
            "correct_answers": correct_answers,
            "n_choices": n_choices,
            "correct_answer": correct_answer
        }
    except Exception:
        return {"all_options": [], "correct_answers": [], "n_choices": 1, "correct_answer": 1}

def clean_question_text(text: str) -> str:
    if pd.isna(text):
        return text
    cleaned = re.sub(r'^\d+\.\s*\d+\.\s*', '', text)
    cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
    return cleaned.strip()

def extract_choice_info(question_data: Dict) -> Tuple[int, int]:
    """
    Extract number of choices and correct answer from question data
    Returns: (n_choices, correct_answer)
    """
    selected_options = question_data.get("selected_options", "")
    options_metadata = question_data.get("options_metadata", "")
    
    if options_metadata:
        parsed = parse_options_metadata(options_metadata)
        return parsed["n_choices"], parsed["correct_answer"]
    
    n_choices = 1
    correct_answer = 1
    
    question_type = question_data.get("type", "").lower()
    if "multiple" in question_type or "choice" in question_type:
        n_choices = 4
    
    return n_choices, correct_answer

def extract_chosen_answer(question_data: Dict, n_choices: int, correct_answer: int) -> int:
    """
    Extract what the student actually chose
    Returns: chosen_answer (1-indexed)
    """
    selected_options = question_data.get("selected_options", "")
    is_correct = question_data.get("is_correct", False)
    
    if selected_options:
        try:
            if isinstance(selected_options, str):
                if selected_options.isdigit():
                    return int(selected_options)
                elif len(selected_options) == 1 and selected_options.isalpha():
                    return ord(selected_options.upper()) - ord('A') + 1
            elif isinstance(selected_options, (int, float)):
                return int(selected_options)
        except (ValueError, TypeError):
            pass
    
    if is_correct:
        return correct_answer
    else:
        incorrect_choices = [i for i in range(1, n_choices + 1) if i != correct_answer]
        return incorrect_choices[0] if incorrect_choices else 1
    
    return 1