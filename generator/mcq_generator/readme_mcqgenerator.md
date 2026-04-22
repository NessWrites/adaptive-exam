# MCQ Generator Module

The **MCQ Generator** is an advanced AI-powered pipeline responsible for transforming base questions (Subjective/Conceptual or Coding Problems) into rigorously validated Multiple Choice Questions (MCQs). These MCQs are designed to probe different Bloom's Taxonomy levels (Remember, Understand, Apply, Analyze). 

This module leverages Google's Gemini LLM along with Groq/Llama models in a hybrid architecture to ensure pedagogical quality, avoid hallucinated distractors, and accurately format specific question types (e.g., Code-based "Find the Bug" questions).

---

## 🏗️ Project Structure

The module is situated at `generator/mcq_generator/` and is structured as follows:

```text
mcq_generator/
├── api/
│   └── routes.py             # FastAPI endpoints handling MCQ generation requests
├── core/
│   ├── ai_engine.py          # Primary LLM prompts/chains for stem & correct answer generation
│   └── mcq_evaluator.py      # LLM-as-a-judge system validating generated MCQs
├── db/
│   └── repository.py         # SQLAlchemy repository for polymorphic fetch/save logic
├── schemas/
│   ├── mcq_schema.py         # Pydantic models for structured LLM outputs
│   └── evaluator_schema.py   # Schemas for the LLM evaluation scores
├── services/
│   ├── mcq_service.py        # Orchestration layer tying engines, evaluators, and DB together
│   ├── distractor_bridge.py  # Connects the core system to the Distractor Manager
│   └── distractor_config_adapter.py # Bridges Pydantic settings to the Distractor sub-module
├── distractor_generation/    # Specialized sub-module for agentic distractor generation
│   ├── distractor_manager.py # Orchestrates agents generating plausible wrong options
│   └── agents/               # Numeric and Conceptual distractor agents
└──  readme_mcqgenerator.md   # This documentation file!
```

---

## ⚙️ How It Works (Data Flow)

The pipeline dynamically alters its strategy based on the **Source Question Type**: Subjective vs. Code.

### 1. Subjective to MCQ Flow
For text-based conceptual questions:
1. **API Call:** A request is hit via `POST /generator/mcq/convert/{question_id}`.
2. **Fetch Source:** `MCQRepository` fetches the polymorphic `SubjectiveQuestion`.
3. **Core Generation:** `MCQEngine` uses the subjective prompt to generate the *Question Stem*, *Correct Answer*, and *Explanation* for distinct Bloom's levels.
4. **Distractor Bridge:** The `DistractorBridge` and `DistractorManager` analyze the stem and use numeric/conceptual sub-agents to generate 3 highly plausible wrong options.
5. **Evaluation:** The `MCQEvaluator` scores the assembled MCQ on Hallucination, Trickiness, and Bloom Alignment.
6. **Storage:** The MCQ is persisted to the database, linked to the `SubjectiveQuestion` parent.

### 2. Code to MCQ Flow
For coding problems (leveraging actual code, test cases, and configurations):
1. **API Call:** Same endpoint `POST /generator/mcq/convert/{question_id}`.
2. **Fetch Source:** `MCQRepository` fetches the polymorphic `CodeQuestion`.
3. **Unified Code Generation:** `MCQEngine` uses the **code-specific prompt** to generate the *entire* MCQ at once (Correct Answer + 3 Buggy/Flawed Distractors). 
    - *Why bypass the Distractor Bridge?* Generating buggy code requires full context of the algorithm, which standard distractor agents cannot handle.
4. **Formatting Options:** Returns a specific `mcq_category` (e.g., `code_fill_blank`, `code_find_bug`, `code_implementation`) and an optional `stem_code` body.
5. **Evaluation & Storage:** Evaluated by the `MCQEvaluator` and persisted with `mcq_category` and `stem_code`, linked directly to the `CodeQuestion` parent via `derived_from_code_id`.

---

## 🧩 Essential Components

### `MCQEngine` (Core Engine)
Transforms the raw DB question into a pedagogical MCQ. It contains carefully tuned Prompts utilizing `gemini-2.5-flash` to extract core concepts without creating overly obvious answers.

### `DistractorBridge` & `DistractorManager`
An agentic sub-system (relying internally on LLaMA-based models via Groq) that decides if a conceptual/hybrid question needs Numeric (math) distractors or Conceptual distractors. Ensures distractors are plausible student misconceptions.

### `MCQEvaluator` (LLM-as-a-Judge)
A secondary LLM validation pass ensuring that the output MCQ:
- **Does not hallucinate** outside the provided marking scheme or test cases.
- **Is effectively tricky**, forcing the student to reason.
- **Matches** the target Bloom's Taxonomy level.

---

## 🗄️ Database Schemas Mapping

We use SQLAlchemy's **Polymorphic Inheritance** alongside Foreign Keys to cleanly track the origin of generated MCQs.

- **`Question` (Base Table):** Contains `unique_id`, `domain`, `concept_tag`, `question_text`, etc.
- **`SubjectiveQuestion` (Child):** Inherits from `Question`. Adds fields like `mark_schema`.
- **`CodeQuestion` (Child):** Inherits from `Question`. Adds fields like `configurations`, `markscheme` (test cases), `function_name`.
- **`MCQQuestion` (Child):** Inherits from `Question`. Saved in the `mcq_questions_converted` table. Contains fields:
  - `derived_from_subjective_id`: FK to subjective question (Nullable).
  - `derived_from_code_id`: FK to code question (Nullable).
  - `mcq_category`: Defines frontend render logic (e.g., `text`, `code_fill_blank`).
  - `stem_code`: Nullable code snippet used alongside the question text.

A check constraint ensures that **exactly one** of `derived_from_...` is populated.

---

## 💻 Frontend Integration Guide

The frontend can blindly fetch the newly generated MCQs, but it **MUST** parse the `mcq_category` parameter to determine how to render the question UI:

```javascript
const mcq = fetchMCQ();

if (mcq.mcq_category === "text") {
    // 🎨 Standard Rendering
    // Render question_text simply as text.
    // Render options (A,B,C,D) as text.
} else if (mcq.mcq_category.startsWith("code_")) {
    // 🎨 Code Rendering Logic
    
    // 1. Render the main `question_text`
    renderText(mcq.question_text);
    
    // 2. Render the Code Stem (if available)
    if (mcq.stem_code) {
        // Render inside a <pre><code class="language-python"> Highlighting Block
        // code_fill_blank will show ??? where students need to guess
        // code_find_bug will show flawed logic
        // code_implementation will show the problem statement (stem_code is null)
        renderSyntaxHighlightedBlock(mcq.stem_code);
    }
    
    // 3. Render the Options
    // Since this is a code MCQ, options A, B, C, D are CODE STRINGS.
    // Render EACH option button as a mini <pre><code> block
    mcq.options.forEach(option => renderOptionAsCode(option.value));
}
```

---

## 🐳 Docker Execution & Environment

This module is designed to run seamlessly as part of the broader backend Docker network defined in the root `docker-compose.yml`.

### Prerequisites
In your root `.env` file, ensure the following API keys are present:
```env
# Required for core MCQ generation and Evaluation
GEMINI_API_KEY=your_gemini_key_here

# Optional: Separate key for validation (defaults to GEMINI_API_KEY if not used)
GEMINI_API_KEY_FOR_VALIDATION=your_gemini_key_here

# Required for the Distractor Engine
GROQ_API_KEY=your_groq_key_here
```

### Running the Services
Start the entire stack (Database, Backend API) from the project root:
```bash
docker compose up --build -d
```

### Applying Migrations
Since `mcq_category` and `stem_code` were recently added, you **must** apply Alembic migrations against the Dockerized PostgreSQL database:
```bash
# Execute Alembic migrations inside the running backend container
docker compose exec backend alembic upgrade head
```

### Triggering via API
You can test the generation locally on an existing question by hitting the exposed endpoint:
```bash
# Example: Generate 2 Bloom variants for a specific Code Question
curl -X POST "http://localhost:8000/generator/mcq/convert/12?num_variants=2"
```
