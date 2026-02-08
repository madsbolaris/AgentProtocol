#!/bin/bash

# Script to normalize echom365 → echo-m365 naming
# Only changes folder names and contexts where kebab-case makes sense
# Preserves EchoM365 (PascalCase), echoM365 (camelCase), etc.

set -e

echo "🔄 Normalizing echo naming to kebab-case..."
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FOLDERS_RENAMED=0
FILES_RENAMED=0
FILES_MODIFIED=0

# Function to rename folders
rename_folders() {
    echo -e "${YELLOW}Step 1: Renaming folders from echom365 → echo-m365${NC}"

    # Find all directories named echom365 (deepest first)
    find . -depth -type d -name "echo-m365" \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/dist/*" \
        -not -path "*/bin/*" \
        -not -path "*/obj/*" \
        -not -path "*/__pycache__/*" | while read -r dir; do

        if [ -e "$dir" ]; then
            parent=$(dirname "$dir")
            new_dir="${parent}/echo-m365"

            echo -e "  ${GREEN}Renaming folder:${NC} $dir → $new_dir"
            mv "$dir" "$new_dir"
            FOLDERS_RENAMED=$((FOLDERS_RENAMED + 1))
        fi
    done
}

# Function to rename files that use echom365 in kebab-case contexts
rename_files() {
    echo -e "\n${YELLOW}Step 2: Renaming files with echom365 → echo-m365${NC}"

    # Find files with echom365 in name (only in kebab-case contexts)
    find . -type f -name "*echom365*" \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/dist/*" \
        -not -path "*/bin/*" \
        -not -path "*/obj/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/.pyc" | while read -r file; do

        if [ -e "$file" ]; then
            dir=$(dirname "$file")
            base=$(basename "$file")

            # Only rename if it's in a kebab-case context (has hyphens around it)
            if [[ "$base" == *-echom365-* ]] || [[ "$base" == echom365-* ]] || [[ "$base" == *-echom365.* ]]; then
                new_base=$(echo "$base" | sed "s/echo-m365/echo-m365/g")
                new_file="${dir}/${new_base}"

                echo -e "  ${GREEN}Renaming file:${NC} $file → $new_file"
                mv "$file" "$new_file"
                FILES_RENAMED=$((FILES_RENAMED + 1))
            fi
        fi
    done
}

# Function to update file contents (only in specific contexts)
update_file_contents() {
    echo -e "\n${YELLOW}Step 3: Updating file contents (kebab-case contexts only)${NC}"

    # Patterns to replace (only in kebab-case contexts)
    # - URLs and paths: /echo-m365/ → /echo-m365/
    # - Config keys with hyphens: "echo-m365" where it should be kebab-case

    find . -type f \( \
        -name "*.json" -o \
        -name "*.md" -o \
        -name "*.yaml" -o \
        -name "*.yml" -o \
        -name "*.sh" -o \
        -name "*.html" \
    \) -not -path "*/node_modules/*" \
       -not -path "*/.git/*" \
       -not -path "*/dist/*" \
       -not -path "*/bin/*" \
       -not -path "*/obj/*" \
       -not -path "*/__pycache__/*" | while read -r file; do

        # Check if file contains patterns that should be updated
        if grep -qE "(test_echo_m365|/echo-m365/|echom365\.test|echom365-|echom365_)" "$file" 2>/dev/null; then
            echo -e "  ${GREEN}Updating:${NC} $file"

            # Update various kebab-case contexts
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS sed
                sed -i '' \
                    -e 's|test_echo_m365|test_echo_m365|g' \
                    -e 's|/echo-m365/|/echo-m365/|g' \
                    -e 's|echom365\.test|echo-m365.test|g' \
                    -e 's|"echo-m365"|"echo-m365"|g' \
                    -e 's|echo-m365-snapshots|echo-m365-snapshots|g' \
                    "$file"
            else
                # Linux sed
                sed -i \
                    -e 's|test_echo_m365|test_echo_m365|g' \
                    -e 's|/echo-m365/|/echo-m365/|g' \
                    -e 's|echom365\.test|echo-m365.test|g' \
                    -e 's|"echo-m365"|"echo-m365"|g' \
                    -e 's|echo-m365-snapshots|echo-m365-snapshots|g' \
                    "$file"
            fi

            FILES_MODIFIED=$((FILES_MODIFIED + 1))
        fi
    done
}

# Run the operations
rename_folders
rename_files
update_file_contents

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Folders renamed:${NC} $FOLDERS_RENAMED"
echo -e "${GREEN}✓ Files renamed:${NC} $FILES_RENAMED"
echo -e "${GREEN}✓ Files modified:${NC} $FILES_MODIFIED"
echo ""
echo -e "${GREEN}✅ Normalization complete!${NC}"
echo ""
echo "NOTE: This script preserves:"
echo "  - EchoM365 (PascalCase in code)"
echo "  - echoM365 (camelCase in code)"
echo "  - echo_m365 (snake_case in Python)"
echo ""
echo "⚠️  Review changes before committing:"
echo "   git status"
echo "   git diff"
echo ""
