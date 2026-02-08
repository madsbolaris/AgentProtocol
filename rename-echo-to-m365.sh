#!/bin/bash

# Script to rename all EchoM365 references to EchoM365
# Handles: file names, folder names, and file contents

set -e

echo "🔄 Starting EchoM365 → EchoM365 rename operation..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track changes
FOLDERS_RENAMED=0
FILES_RENAMED=0
FILES_MODIFIED=0

# Function to rename files and folders
rename_items() {
    local search_pattern=$1
    local replace_pattern=$2
    local item_type=$3  # "file" or "directory"

    echo -e "${YELLOW}Searching for ${item_type}s matching: ${search_pattern}${NC}"

    # Find all matching items (deepest first for directories)
    find . -depth -name "*${search_pattern}*" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/bin/*" -not -path "*/obj/*" | while read -r item; do
        if [ -e "$item" ]; then
            # Get the directory and filename
            dir=$(dirname "$item")
            base=$(basename "$item")

            # Replace the pattern in the name
            new_base=$(echo "$base" | sed "s/${search_pattern}/${replace_pattern}/g")
            new_item="${dir}/${new_base}"

            if [ "$item" != "$new_item" ]; then
                echo -e "  ${GREEN}Renaming:${NC} $item"
                echo -e "  ${GREEN}      to:${NC} $new_item"
                mv "$item" "$new_item"

                if [ -d "$new_item" ]; then
                    FOLDERS_RENAMED=$((FOLDERS_RENAMED + 1))
                else
                    FILES_RENAMED=$((FILES_RENAMED + 1))
                fi
            fi
        fi
    done
}

# Function to replace content in files
replace_in_files() {
    local search_text=$1
    local replace_text=$2
    local description=$3

    echo -e "${YELLOW}Replacing content: ${search_text} → ${replace_text}${NC}"

    # Find all text files (excluding binary, node_modules, .git, etc.)
    find . -type f \( \
        -name "*.ts" -o \
        -name "*.tsx" -o \
        -name "*.js" -o \
        -name "*.jsx" -o \
        -name "*.json" -o \
        -name "*.md" -o \
        -name "*.cs" -o \
        -name "*.csproj" -o \
        -name "*.py" -o \
        -name "*.yaml" -o \
        -name "*.yml" -o \
        -name "*.txt" -o \
        -name "*.html" -o \
        -name "*.sh" \
    \) -not -path "*/node_modules/*" \
       -not -path "*/.git/*" \
       -not -path "*/dist/*" \
       -not -path "*/bin/*" \
       -not -path "*/obj/*" \
       -not -path "*/__pycache__/*" \
       -not -path "*/.venv/*" | while read -r file; do

        # Check if file contains the search text
        if grep -q "$search_text" "$file" 2>/dev/null; then
            echo -e "  ${GREEN}Modifying:${NC} $file"

            # Use different sed syntax for macOS vs Linux
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/${search_text}/${replace_text}/g" "$file"
            else
                sed -i "s/${search_text}/${replace_text}/g" "$file"
            fi

            FILES_MODIFIED=$((FILES_MODIFIED + 1))
        fi
    done
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Renaming folders and files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Rename directories and files (process deepest directories first)
# Handle different case variations
rename_items "EchoM365" "EchoM365" "item"
rename_items "echom365" "echom365" "item"
rename_items "echo-m365" "echo-m365" "item"
rename_items "echo_m365" "echo_m365" "item"
rename_items "ECHOM365" "ECHOM365" "item"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Replacing content in files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Replace content in files (all variations)
replace_in_files "EchoM365" "EchoM365" "PascalCase"
replace_in_files "echoM365" "echoM365" "camelCase"
replace_in_files "echom365" "echom365" "lowercase"
replace_in_files "echo-m365" "echo-m365" "kebab-case"
replace_in_files "echo_m365" "echo_m365" "snake_case"
replace_in_files "ECHOM365" "ECHOM365" "UPPERCASE"
replace_in_files "Echo M365" "Echo M365" "Title Case with space"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Folders renamed:${NC} $FOLDERS_RENAMED"
echo -e "${GREEN}✓ Files renamed:${NC} $FILES_RENAMED"
echo -e "${GREEN}✓ Files modified:${NC} $FILES_MODIFIED"
echo ""
echo -e "${GREEN}✅ Rename operation completed!${NC}"
echo ""
echo "⚠️  Please review the changes before committing:"
echo "   git status"
echo "   git diff"
echo ""
