#!/usr/bin/env bash

OUTPUT_FILE="project_structure.md"

IGNORE_DIRS=".git|node_modules|venv|__pycache__|.mypy_cache|.pytest_cache|.idea|.vscode"

{
  echo "## Project Structure"
  echo '```text'
  tree -a -I "$IGNORE_DIRS"
  echo '```'
} > "$OUTPUT_FILE"

echo "✅ Markdown project tree saved to $OUTPUT_FILE"
chmod +x tree.sh