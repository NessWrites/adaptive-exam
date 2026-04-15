# Cross-Domain Generation Project

The **Cross-Domain Generation** project is designed to evaluate, combine, and generate cross-domain examination questions leveraging a multi-agent system built on top of LangGraph. It processes learning objectives from two different domains, crafts interwoven scenarios, generates candidate questions, simulates a student's attempt to answer them, evaluates pedagogical effectiveness, and saves the final cross-domain question.

## Project Setup

1. **Python Environment:** Make sure you have Python 3.9+ installed and a virtual environment configured.
2. **Install Dependencies:** 
   Navigate to the `generator/cross-domain-generation/` directory and install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables:** 
   Create a `.env` file in the project's directory and provide any required API keys (e.g., `GROQ_API_KEY`).
4. **Data:**
   Ensure `data/topics.json` exists as it is required to validate the inputted domains.

## How to Run End-to-End

To execute the entire cross-domain generation pipeline, you can run the `main.py` script. The pipeline will invoke the graph, pass the initial state, process through all the agents/nodes, and output the generated question and evaluation details.

```bash
python main.py
```
This script initializes the state using predefined topic parameters (e.g., `topic_1`, `topic_2`, `stratum`) and runs the state graph, printing intermediate results at each phase of the generation.

---

## Step-by-Step Explanation

The generation pipeline acts as a state graph where the execution moves from one node to another based on conditional edges corresponding to a multi-agent workflow:

1. **Input Validation:** Retrieves the descriptions / learning objectives for the given two topics from the predefined datasets.
2. **Scenario Generation:** Proposes multiple real-world scenarios combining the two topics effectively.
3. **Scenario Evaluation:** Evaluates the generated scenarios based on interdisciplinary relevance, plausibility, and depth. The best-scoring scenario is selected.
4. **Question Type Classification:** Determines the most suitable mathematical or theoretical question type (e.g., calculation, proof, multiple choice) that best fits the chosen scenario.
5. **Question Generation:** Drafts complete questions following the scenario and recommended question type.
6. **Student Agent Simulation:** A simulated student "attempts" to answer the generated questions to verify their solvability and clarity.
7. **Feedback Handling:** If questions are deemed unsolvable by the simulated student, the feedback is routed back to regenerate the questions. 
8. **Pedagogical Prior Evaluator:** Ranks the successful questions against pedagogical standards (clarity, cognitive depth, cross-domain connection) to pick the final best question.
9. **File Output:** The winning question and relevant metadata are saved to an output storage (e.g., a `.json` file).

---

## Codebase Breakdown (Files, Functions, Edges, Parameters, and Returns)

### `config.py`
Configuration functions handling LLM setup and token usage tracking.
- **Function:** `get_llm`
  - **Parameters:** `temperature: float` (default `1`)
  - **Returns:** Language model instance (`ChatGroq`) needed for prompt execution.
  - **Description:** Instantiates the ChatGroq client using the API key from environment variables.
- **Function:** `update_token_usage`
  - **Parameters:** `node: str`, `response: Any`
  - **Returns:** `None`
  - **Description:** Extracts token counts from the LLM response metadata and cumulatively updates the registry for analytical tracking.
- **Function:** `reset_token_usage`
  - **Parameters:** `None`
  - **Returns:** `None`
  - **Description:** Resets the token usage dictionaries back to zeroes.

### `state.py`
Defines the `GraphState` TypedDict holding the state schemas exchanged across all graph nodes (e.g., learning objectives, retrieved scenarios, retry counts, final outputs).

### `main.py`
The entrypoint script handling graph initialization.
- **Function:** `print_separator`
  - **Parameters:** `title: str`
  - **Returns:** `Any` (prints to stdout)
  - **Description:** Prints formatted textual separators in the command line for better readability.
- **Function:** `run`
  - **Parameters:** `topic_1: str`, `topic_2: str`, `stratum: str`
  - **Returns:** `None`
  - **Description:** Initializes the state dictionary, queries the agent graph, and outputs structured debug summaries per phase.

### `graph.py`
Declares the LangGraph workflow structure (nodes and conditional edges).
- **Function:** `after_validation`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Edge defining target node post validation. Targets `scenario_generator` if no errors.
- **Function:** `after_scenario_evaluator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Targets `question_type_classifier` on success. Routes back to `scenario_generator` on failure.
- **Function:** `after_question_type_classifier`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Transitions graph to `question_generator`.
- **Function:** `after_question_generator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Transitions graph to `student_agent`.
- **Function:** `after_student_agent`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Validates solvability. Transitions to `feedback_handler` for rework if not solvable. Targets `pedagogical_prior_evaluator` if solvable.
- **Function:** `after_pedagogical_prior_evaluator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Moves to `file_output` if pairs are evaluated successfully. Otherwise loops back to `question_generator`.
- **Function:** `after_file_output`
  - **Parameters:** `state: GraphState`
  - **Returns:** `str` (Edge name)
  - **Description:** Ends execution (`__end__`).
- **Function:** `build_graph`
  - **Parameters:** `None`
  - **Returns:** `StateGraph` object
  - **Description:** Links all functional nodes to their string aliases and binds the corresponding conditional edges to execute the workflow sequence.

### Nodes (`nodes/`)
Individual agent modules mapped to graph operations.

#### `nodes/input_validator.py`
- **Function:** `load_topics`
  - **Parameters:** `path: str`
  - **Returns:** `dict` (JSON payload)
  - **Description:** Loads predefined domain topics from a JSON file.
- **Function:** `input_validator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Matches `topic_1` and `topic_2` against the definitions database. Populates their explicit learning objectives.

#### `nodes/scenario_generator.py`
- **Function:** `scenario_generator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Prompts LLM to spawn multiple scenarios combining learning objectives. Sets `generated_scenarios` in state.

#### `nodes/scenario_evaluator.py`
- **Function:** `compute_overall_score`
  - **Parameters:** `scores: dict`
  - **Returns:** `float`
  - **Description:** Averages the graded dimension scores.
- **Function:** `scenario_evaluator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Evaluates scenarios. Populates `top_scenario` based on computed scores, or resets scenario bounds if metrics are not satisfied incrementing `scenario_retry_count`.

#### `nodes/question_type_classifier.py`
- **Function:** `question_type_classifier`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Picks appropriate question paradigm from prompt directives and sets `question_type` in the state corresponding to the top scenario format.

#### `nodes/question_generator.py`
- **Function:** `format_feedback`
  - **Parameters:** `feedback: dict`
  - **Returns:** `str`
  - **Description:** Stringifies critique data from the feedback handler for inclusion into prompt text.
- **Function:** `question_generator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Crafts questions bound to the categorized `question_type` inside the specific `top_scenario`. Appends questions to `generated_questions`.

#### `nodes/student_agent.py`
- **Function:** `student_agent`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Triggers model instances acting as distinct learners. Submits solution attempts assessing if conditions explicitly yield an unambiguous answer. Stores `student_attempts`.

#### `nodes/feedback_handler.py`
- **Function:** `feedback_handler`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Collates unsolvability insights identified by `student_agent` and modifies `question_feedback` state prior to looping back into generator. 

#### `nodes/pedagogical_prior_evaluator.py`
- **Function:** `compute_overall_score`
  - **Parameters:** `scores: dict`
  - **Returns:** `float`
  - **Description:** Standard metric averager for evaluation grades. 
- **Function:** `format_questions_and_attempts`
  - **Parameters:** `questions: list`, `attempts: list`
  - **Returns:** `str`
  - **Description:** Normalizes dicts to formatted string texts for evaluation prompting. 
- **Function:** `pedagogical_prior_evaluator`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Reviews question clarity, target depth, and mapping to objectives. Extracts best cross-domain question into `evaluated_pairs` list.

#### `nodes/file_output.py`
- **Function:** `file_output`
  - **Parameters:** `state: GraphState`
  - **Returns:** `GraphState`
  - **Description:** Aggregates top scenario, pair combinations, and topics to write final data into target JSON file at `outputs/{topic_1}__{topic_2}.json` format.

