# utils.py
import json
import difflib
import random
import re
from typing import List, Dict, Any, Optional
# from jinja2 import Template

def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error: {filepath} is not valid JSON")
        return {}

def save_json(data: Dict, filepath: str) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



def text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity (0 to 1)."""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def token_similarity(a: str, b: str) -> float:
    a_tokens = set(re.findall(r'\w+', a.lower()))
    b_tokens = set(re.findall(r'\w+', b.lower()))
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)




def remove_duplicates(items: List[Dict]) -> List[Dict]:
    """Remove duplicate items while preserving order."""
    seen = set()
    result = []
    for item in items:
        text = item.get('text', '').lower().strip()
        if text and text not in seen:
            seen.add(text)
            result.append(item)
    return result








