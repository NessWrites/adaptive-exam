import os
import sys
import json

# Add project root to path so we can import backend models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')))

from backend.app.models.database_models import MCQQuestion, SubjectiveQuestion, CodeQuestion, Question

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    sys.exit(1)

# Sometimes docker-compose DB_URL says localhost but from inside container it should be 'db'
# We handle both by allowing override or just trying to connect depending on execution environment.
if os.getenv("IS_DOCKER"):
    DATABASE_URL = DATABASE_URL.replace("localhost", "db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def generate_report():
    session = SessionLocal()
    mcqs = session.query(MCQQuestion).all()
    
    output_lines = ["# 🧠 MCQ Generation Quality Review Report\n"]
    output_lines.append(f"**Total MCQs Generated:** {len(mcqs)}\n")
    output_lines.append("---\n")
    
    if len(mcqs) == 0:
        output_lines.append("> No MCQ questions found in the database. Run the generator API first!")
    
    for i, mcq in enumerate(mcqs, 1):
        mcq_category = getattr(mcq, 'mcq_category', 'text')
        output_lines.append(f"## {i}. MCQ ID: `{mcq.id}` (Bloom: {mcq.bloom_level}, Category: `{mcq_category}`)")
        
        # Get parent details
        parent = mcq.source_subjective_question or mcq.source_code_question
        parent_type = parent.question_type if parent else "Unknown"
        output_lines.append(f"**Source Question Type:** `{parent_type}`")
        
        if parent:
            output_lines.append(f"**Domain/Concept:** `{parent.domain}` / `{parent.concept_tag}`")
            output_lines.append("\n### Original Source Text:")
            if parent_type == "code":
                output_lines.append("```python\n" + str(parent.question_text) + "\n```")
                if getattr(parent, 'markscheme', None):
                    output_lines.append("**Test Cases:**\n```json\n" + json.dumps(parent.markscheme, indent=2) + "\n```")
            else:
                output_lines.append("> " + str(parent.question_text).replace("\n", "\n> "))
                if getattr(parent, 'mark_schema', None):
                    output_lines.append("**Marking Schema:**\n```json\n" + json.dumps(parent.mark_schema, indent=2) + "\n```")
        
        output_lines.append("\n### Generated MCQ:")
        output_lines.append(f"**Stem:**\n{mcq.question_text}\n")
        
        if getattr(mcq, 'stem_code', None):
            output_lines.append("**Stem Code Context:**\n```python\n" + str(mcq.stem_code) + "\n```\n")
            
        output_lines.append("**Options:**")
        if isinstance(mcq.options, dict):
            for k, v in mcq.options.items():
                if mcq_category and mcq_category.startswith('code'):
                    output_lines.append(f"- **{k}:**\n  ```python\n  {v}\n  ```")
                else:
                    output_lines.append(f"- **{k}:** {v}")
        else:
            output_lines.append(str(mcq.options))
            
        output_lines.append("\n**Correct Answer:**")
        if isinstance(mcq.correct_answer, dict):
            ans = mcq.correct_answer.get("text", "")
            key = mcq.correct_answer.get("key", "?")
            if mcq_category and mcq_category.startswith('code'):
                output_lines.append(f"Option **{key}**:\n```python\n{ans}\n```")
            else:
                output_lines.append(f"Option **{key}**: {ans}")
        else:
             output_lines.append(str(mcq.correct_answer))
        
        output_lines.append(f"\n**Explanation:**\n> {mcq.explanation}")
        
        output_lines.append("\n### LLM Validation Score:")
        if mcq.validation_score:
            output_lines.append("```json\n" + json.dumps(mcq.validation_score, indent=2) + "\n```")
        else:
            output_lines.append("*Not evaluated yet.*")
            
        output_lines.append("\n<br>\n\n---\n")
        
    report_path = os.path.join(os.path.dirname(__file__), "review_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"✅ Successfully wrote {len(mcqs)} questions to {report_path}")

if __name__ == "__main__":
    generate_report()
