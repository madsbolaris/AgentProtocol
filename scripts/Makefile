# AgentProtocol Documentation Consistency Tools
# Run validation checks and generate reports

.PHONY: all validate enums links line-refs api-ref misplaced api-docs-complete generate merge docs clean help install

# Default target
all: validate

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt

# Run all validation checks
validate:
	@echo "Running complete validation suite..."
	python3 validation/validate-consistency.py

# Individual checks
enums:
	@echo "Checking enum synchronization..."
	python3 validation/validate-enums.py

links:
	@echo "Validating internal links..."
	python3 validation/validate-links.py

line-refs:
	@echo "Checking line number references..."
	python3 validation/check-line-references.py

api-ref:
	@echo "Validating API reference quality..."
	python3 validation/validate-api-reference.py

misplaced:
	@echo "Detecting misplaced content in API reference..."
	python3 validation/detect-misplaced-content.py ../api-reference

api-docs-complete:
	@echo "Validating API documentation completeness..."
	python3 validation/validate-api-docs-completeness.py ../api-reference

# Generation tasks
generate:
	@echo "Generating API reference from TypeSpec..."
	python3 generation/generate-api-reference.py

merge:
	@echo "Merging generated and manual documentation..."
	python3 generation/merge-api-docs.py

# Complete doc generation workflow
docs: generate merge
	@echo "✅ Documentation generated and merged"

# Clean generated reports
clean:
	@echo "Cleaning reports..."
	rm -rf reports/*.txt

# Show help
help:
	@echo "AgentProtocol Scripts"
	@echo ""
	@echo "Documentation Generation:"
	@echo "  make generate    - Generate API reference from TypeSpec"
	@echo "  make merge       - Merge generated + manual documentation"
	@echo "  make docs        - Complete workflow (generate + merge)"
	@echo ""
	@echo "Validation:"
	@echo "  make validate    - Run all validation checks"
	@echo "  make enums       - Check enum synchronization"
	@echo "  make links       - Validate internal links"
	@echo "  make line-refs       - Check line number references"
	@echo "  make api-ref         - Validate API reference quality"
	@echo "  make misplaced       - Detect misplaced content in API docs"
	@echo "  make api-docs-complete - Check for missing overview/examples"
	@echo ""
	@echo "Utilities:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make clean       - Remove generated reports"
	@echo "  make help        - Show this help message"
