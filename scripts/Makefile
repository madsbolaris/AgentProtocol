# AgentProtocol Documentation Consistency Tools
# Run validation checks and generate reports

.PHONY: all validate enums links line-refs api-ref misplaced api-docs-complete generate merge docs clean help install
.PHONY: test test-record test-playback test-csharp test-python test-typescript verify-recordings clean-recordings

# Default target
all: validate

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt

# Run all validation checks
validate:
	@echo "Running complete validation suite..."
	python3 validation/validate_consistency.py

# Individual checks
enums:
	@echo "Checking enum synchronization..."
	python3 validation/validate_enums.py

links:
	@echo "Validating internal links..."
	python3 validation/validate_links.py

line-refs:
	@echo "Checking line number references..."
	python3 validation/check_line_references.py

api-ref:
	@echo "Validating API reference quality..."
	python3 validation/validate_api_reference.py

misplaced:
	@echo "Detecting misplaced content in API reference..."
	python3 validation/detect_misplaced_content.py ../api-reference

api-docs-complete:
	@echo "Validating API documentation completeness..."
	python3 validation/validate_api_docs_completeness.py ../api-reference

# Generation tasks
generate:
	@echo "Generating API reference from TypeSpec..."
	python3 codegen/generate_api_reference.py

merge:
	@echo "Merging generated and manual documentation..."
	python3 codegen/merge_api_docs.py

# Complete doc generation workflow
docs: generate merge
	@echo "✅ Documentation generated and merged"

# Clean generated reports
clean:
	@echo "Cleaning reports..."
	rm -rf reports/*.txt

# ============================================================================
# Testing & Recording Management
# ============================================================================

# Run all tests (playback mode - uses existing recordings)
test: test-csharp test-python test-typescript
	@echo "✅ All tests completed"

# Generate new recordings (requires real API server)
test-record:
	@echo "📹 Recording mode: Generating new test recordings..."
	@echo "⚠️  Requires real Agent Protocol API server running on localhost:5000"
	@echo ""
	@echo "Starting C# recording..."
	cd ../dotnet/tests/Microsoft.Agents.Client.Tests && RECORD_HTTP=true dotnet test --filter "FullyQualifiedName~Docs.QuickstartTests"
	@echo ""
	@echo "Note: Python and TypeScript recording not yet implemented"
	@echo "See .workspace/python-http-recording-implementation.md"
	@echo "See .workspace/typescript-http-recording-implementation.md"
	@echo ""
	@echo "✅ Recordings saved to: ../test-data/llm-recordings/docs/"

# Run tests with existing recordings (fast, no API required)
test-playback:
	@echo "▶️  Playback mode: Using existing recordings..."
	@$(MAKE) test

# Run C# tests
test-csharp:
	@echo "Testing C# Client SDK..."
	cd ../dotnet/tests/Microsoft.Agents.Client.Tests && dotnet test --filter "FullyQualifiedName~Docs.QuickstartTests"

# Run Python tests (when implemented)
test-python:
	@echo "Testing Python Client SDK..."
	@if [ -f "../python/microsoft-agents-protocol-client/tests/docs/test_quickstart.py" ]; then \
		cd ../python/microsoft-agents-protocol-client && pytest tests/docs/test_quickstart.py -v; \
	else \
		echo "⚠️  Python tests not yet implemented"; \
		echo "See .workspace/python-http-recording-implementation.md"; \
	fi

# Run TypeScript tests (when implemented)
test-typescript:
	@echo "Testing TypeScript Client SDK..."
	@if [ -f "../typescript/packages/agents-protocol-client/tests/docs/quickstart.test.ts" ]; then \
		cd ../typescript/packages/agents-protocol-client && npm test -- tests/docs/quickstart.test.ts; \
	else \
		echo "⚠️  TypeScript tests not yet implemented"; \
		echo "See .workspace/typescript-http-recording-implementation.md"; \
	fi

# Verify cross-language recording compatibility
verify-recordings:
	@echo "🔍 Verifying cross-language recording compatibility..."
	@echo ""
	@echo "Checking if recordings exist..."
	@if [ -d "../test-data/llm-recordings/docs/simple-completion" ]; then \
		echo "✅ Found recordings in: ../test-data/llm-recordings/docs/simple-completion/"; \
		ls -lh ../test-data/llm-recordings/docs/simple-completion/ | head -10; \
		echo ""; \
		echo "Running cross-language verification..."; \
		echo "⚠️  Hash compatibility tests not yet implemented"; \
		echo "See .workspace/cross-language-recording-verification.md"; \
	else \
		echo "❌ No recordings found!"; \
		echo "Run 'make test-record' to generate recordings first"; \
		exit 1; \
	fi

# Clean all test recordings
clean-recordings:
	@echo "🧹 Cleaning all test recordings..."
	@read -p "This will delete all recordings in test-data/llm-recordings/docs/. Continue? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf ../test-data/llm-recordings/docs/*/; \
		echo "✅ Recordings cleaned"; \
	else \
		echo "Cancelled"; \
	fi

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
	@echo "Testing & Recordings:"
	@echo "  make test             - Run all tests (playback mode)"
	@echo "  make test-record      - Generate recordings (requires real API)"
	@echo "  make test-playback    - Run tests with recordings (fast, no API)"
	@echo "  make test-csharp      - Run C# tests only"
	@echo "  make test-python      - Run Python tests only"
	@echo "  make test-typescript  - Run TypeScript tests only"
	@echo "  make verify-recordings - Verify cross-language hash compatibility"
	@echo "  make clean-recordings  - Remove all test recordings"
	@echo ""
	@echo "Utilities:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make clean       - Remove generated reports"
	@echo "  make help        - Show this help message"
