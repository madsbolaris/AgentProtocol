#!/bin/bash

# Watch CSS files and trigger MkDocs rebuild
CSS_DIR="docs/assets/css"
TRIGGER_FILE="docs/index.md"

echo "Watching $CSS_DIR for changes..."

fswatch -o "$CSS_DIR" | while read f; do
  echo "CSS changed, triggering rebuild..."
  touch "$TRIGGER_FILE"
done
