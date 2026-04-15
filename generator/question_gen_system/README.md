# Question Generation System

## Overview
The Question Generation System is an automated pipeline designed to dynamically generate assessment questions aligned with the curriculum of the Fusemachines AI Fellowship program. Focusing on foundational domains like AI, Machine Learning, Linear Algebra, Calculus, and Probability, it crafts questions adhering to the first three cognitive levels of Bloom’s Taxonomy (Remember, Understand, Apply). 

The system utilizes structured question "skeletons" (incorporating the base question, Bloom level, context, and constraints) and offloads them to a Large Language Model (LLM) for expansion. Once generated, questions undergo an automated LLM-as-Judge validation to ensure pedagogical relevance and Bloom level alignment. Validated questions are saved into a PostgreSQL database, ready to be utilized by downstream assessment workflows (such as Mark Scheme Generation).

## Project Setup

This codebase runs isolated as a microservice using Docker, fitting seamlessly into the overarching Adaptive Exam ecosystem.

1. **Docker Setup**: Ensure you have [Docker](https://docs.docker.com/get-docker/) installed and running on your machine.
2. **Environment Variables**: 
   Create a `.env` file within the system and specify necessary API Keys (like `GEMINI_API_KEY` for the `HydrationAgent`) and the `DATABASE_URL` routing to the main database cluster instance.

## How to Run

1. **Start the API Server via Docker**:
   Build and start the container instances defined in your project's `docker-compose.yml` to spin up both the Question Gen backend server and its necessary dependencies.
   ```bash
   docker-compose up --build
   ```
2. **Generate Questions**:
   Trigger the endpoint specifying domain parameters. Ensure you check `taxonomy/schema.py` for valid values for domain, unit, topic, and Bloom level.
   
   **Endpoint Example**:
   ```http
   GET /questions/generator?domain=math&unit=Linear%20Algebra&topic=Transformations&level=2&num_questions=5
   ```
   This triggers background tasks to generate the specified amount of questions, validate them, and store them directly in the database.

## Codebase Breakdown

### `routes/`
- **`routes.py`**
  - **Function:** `generator(background_tasks: BackgroundTasks, domain: str, unit: str, topic: str, level: int, num_questions: int, db: Session)`
  - **Returns:** API response indicating the background task has started.
  - **Task:** Endpoint to trigger the question generation pipeline. Dispatches validation and saving logic as background tasks.

### `src/agents/`
- **`question_agent.py`**
  - **Class:** `HydrationAgent`
  - **Task:** Integrates with the LLM (Gemini) to expand question 'skeletons' into robust, full-text questions.
  - **Function:** `__init__(self, api_key: str, model_name: str)`
    - **Returns:** `Any` (Initialized instance)
    - **Task:** Initializes the Google GenAI interface configurations.
  - **Function:** `hydrate(self, domain: str, concept: str, level: int, skeleton: str, num_questions: int)`
    - **Returns:** `Dict`
    - **Task:** Calls Gemini to turn a basic skeleton prompt into multiple well-structured, solvable questions returned as a JSON dictionary.
- **`prompt_registry.py`**
  - **Task:** Holds system prompts and templates for LLM instruction mapping.

### `src/core/`
- **`generator.py`**
  - **Class:** `SkeletonGenerator`
  - **Task:** Assembles the initial prompt scaffolding using Bloom's Taxonomy contexts.
  - **Function:** `__init__(self, schema: list)`
    - **Returns:** `Any` (Initialized instance).
  - **Function:** `_get_topic_node(self, domain_name: str, unit_name: str, topic_name: str)`
    - **Returns:** `Dict`
    - **Task:** Helper function locating specific taxonomic criteria descending through domain, unit, and topic levels.
  - **Function:** `generate_skeleton(self, domain_name: str, unit_name: str, topic_name: str, level: int)`
    - **Returns:** `Tuple[str, str, Optional[str]]`
    - **Task:** Selects randomized axes based on the request's Bloom level and constructs the foundational "skeleton" string.
- **`taxonomy_loader.py`**
  - **Task:** Interacts with or parses taxonomic structures.

### `src/crud.py`
- **Function:** `save_subjective_question(db: Session, domain: str, unit: str, topic: str, level: int, question: str, total_marks: int)`
  - **Returns:** `SubjectiveQuestion` (SQLAlchemy model instance)
  - **Task:** Parses passed LLM outputs and commits the corresponding evaluated questions directly into the PostgreSQL `subjective_questions` table.

### `src/ingestion/`
- **`schema_loader.py`**
  - **Function:** `get_schema()`
    - **Returns:** Schema payload (Dict/List).
    - **Task:** Loads the structural definitions imported from the taxonomy schema directory.

### `src/pipeline/`
- **`batch_buffer.py`**
  - **Function:** `add_to_buffer(rows: Any)`
    - **Returns:** `Any`
    - **Task:** Appends generated question pipelines into an accumulated processing buffer.
  - **Function:** `current_buffer_size()`
    - **Returns:** `int`
    - **Task:** Returns the count of items waiting in the validation queue.

### `src/schemas/`
- **`items_schema.py`**
  - **Classes:** `LLMQuestionResponse`, `QuestionRow`
  - **Task:** Pydantic data models enforcing strict output typing and runtime type checking for the parsed LLM JSONs.

### `src/services/`
- **`validator.py`**
  - **Function:** `system_prompt(batch: List[Dict])`
    - **Returns:** Prompt `Str` or messages object.
    - **Task:** Formulates the rigorous LLM-as-Judge instructions necessary for evaluating the alignment of the batch.
  - **Function:** `validate_batch(batch: Any)`
    - **Returns:** Evaluated object batch.
    - **Task:** Acts as the LLM judge checking Bloom constraints, context alignment scoring, and yielding binary acceptance criteria.
- **`processer.py`**
  - **Function:** `split_question(llm_response: Any, domain: Any, unit: Any, topic: Any, context: Any, level: Any)`
    - **Returns:** Transformed components.
    - **Task:** Extracts and formats raw text into categorized properties.
  - **Function:** `create_batches(rows: Any, batch_size: Any)`
    - **Returns:** Chunked `List` arrays.
    - **Task:** Segments larger result lists into batched subsets for parallel chunked validation.

### `taxonomy/`
- **`schema.py`**
  - **Task:** Dictionary/Lists defining the static ontology holding subjects, concepts. Only domains, topics, and Bloom levels existing here are accepted by the generator.
