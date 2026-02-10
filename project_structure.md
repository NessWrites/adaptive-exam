## Project Structure
```text
.
├── .env
├── .gitignore
├── README.md
├── ai_models
│   ├── README.md
│   └── model.py
├── backend
│   ├── alembic
│   │   ├── 001_add_indexes.py
│   │   ├── README
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions
│   ├── alembic.ini
│   ├── app
│   │   ├── __init__.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── exception.py
│   │   ├── database
│   │   │   ├── mongodb
│   │   │   │   └── connection.py
│   │   │   └── postgresql
│   │   │       └── connection.py
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── .gitkeep
│   │   │   └── database_models.py
│   │   ├── routes
│   │   │   ├── __init__.py
│   │   │   ├── exam_route.py
│   │   │   ├── health.py
│   │   │   └── question_routes.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── exam_schema.py
│   │   │   ├── performance_schema.py
│   │   │   └── question_schema.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── exam_service.py
│   │   │   ├── irt_engine.py
│   │   │   ├── qpool_services.py
│   │   │   └── question_service.py
│   │   └── utils
│   │       └── helpers.py
│   └── requirements.txt
├── backend.log
├── data
│   ├── 2pl_mirt_qbank.csv
│   └── mirt_base_questions.json
├── docker-compose.yml
├── docs
│   ├── architecture.md
│   └── setup.md
├── frontend
│   ├── examinee_results.csv
│   └── streamlit_app.py
├── generator
│   └── question_generator.py
├── locustfile.py
├── project_structure.md
├── requirements.txt
├── results
│   └── generated_questions
│       └── generated_questions_mirt.json
├── scripts
│   ├── 2pl_mirt_5.R
│   └── 2pl_mirt_7.R
├── tests
│   ├── .gitkeep
│   ├── conftest.py
│   ├── test_exam_flow.py
│   └── test_irt_logic.py
└── tree.sh

23 directories, 54 files
```
