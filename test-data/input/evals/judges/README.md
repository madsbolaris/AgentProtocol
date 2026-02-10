# Judge-Based Evaluation Tests

This directory contains evaluation tests that use various judge agents to assess output quality and correctness.

## Subdirectories

### text/
Text-based judges including LLM semantic similarity, regex pattern matching, and case-insensitive matching.

### tool-calls/
Judges that validate tool/function call expectations, including complex sequences and parallel execution.

### semantic/
Semantic analysis judges for sentiment detection, entity recognition, and meaning validation.

## Purpose

These tests demonstrate the judge system's capabilities for:
- Automated quality assessment
- Pattern matching and validation
- Semantic understanding
- Tool interaction verification

## Judge Types

Judges can evaluate outputs using:
- **LLM-based**: Semantic similarity, understanding
- **Regex**: Pattern matching, format validation
- **Tool verification**: Function call validation
- **Semantic analysis**: Sentiment, entities, meaning
