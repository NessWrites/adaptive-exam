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
        opts = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        if not isinstance(opts, list):
            return {"all_options": [], "correct_answers": [],"selected_options":[], "n_choices": 1, "correct_answer": []}
        
        all_options = [o.get("label") for o in opts if "label" in o]
        selected_options = [o.get("label", "") for o in opts if o.get("selected", False)]
        correct_answers = [o.get("label", "") for o in opts if o.get("selected", False) and o.get("is_correct", False)]
        if not correct_answers:
            correct_answers = selected_options  # Fallback to selected if is_correct not provided

        
        n_choices = len(all_options) if all_options else 1
        correct_answer_indices = [all_options.index(ca) + 1 for ca in correct_answers if ca in all_options] or [1]
        
                
        return {
            "all_options": all_options, 
            "correct_answers": correct_answers,
            "selected_options": selected_options,
            "n_choices": n_choices,
            "correct_answer": correct_answer_indices
        }
    except Exception:
        print(f"Error parsing options_metadata: {e}")
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

    options_metadata = question_data.get("options_metadata", "")
    
    if options_metadata:
        parsed = parse_options_metadata(options_metadata)
        return parsed["n_choices"], parsed["correct_answer"]
    
    n_choices = 1
    correct_answer = [1]
    
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
                # Handle comma-separated or list-like strings
                if ',' in selected_options:
                    selected = [s.strip() for s in selected_options.split(',')]
                else:
                    selected = [selected_options]
            elif isinstance(selected_options, list):
                selected = selected_options
            else:
                selected = [str(selected_options)]
            
            # Convert to indices
            parsed = parse_options_metadata(question_data.get("options_metadata", ""))
            all_options = parsed["all_options"]
            chosen_indices = []
            for sel in selected:
                if sel.isdigit():
                    chosen_indices.append(int(sel))
                elif sel in all_options:
                    chosen_indices.append(all_options.index(sel) + 1)
                elif len(sel) == 1 and sel.isalpha():
                    chosen_indices.append(ord(sel.upper()) - ord('A') + 1)
            return sorted(list(set(chosen_indices))) or [1]
        except Exception as e:
            print(f"Error extracting chosen answer: {e}")
    
    # Fallback: if is_correct, return correct_answer; else, return first incorrect choice
    if is_correct:
        return correct_answer
    else:
        incorrect_choices = [i for i in range(1, n_choices + 1) if i not in correct_answer]
        return [incorrect_choices[0]] if incorrect_choices else [1]
    
    return [1]