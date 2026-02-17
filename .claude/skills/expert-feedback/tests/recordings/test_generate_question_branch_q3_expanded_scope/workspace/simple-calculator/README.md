# Simple Calculator API

A basic calculator API for testing purposes. This is an intentionally flawed implementation designed to trigger expert analysis and questions.

## Features

- Basic arithmetic operations (add, multiply, divide)
- REST API endpoints
- Available in both TypeScript and Python

## Known Issues (Intentional)

This code has several intentional issues for experts to identify:

1. **No input validation** - accepts any input type
2. **No error handling** - crashes on invalid input
3. **Missing tests** - 0% test coverage
4. **No type safety** - TypeScript uses `any` types
5. **No documentation** - functions lack docstrings
6. **Security issue** - Python version uses eval() for calculations

## Purpose

This project is a fixture for integration testing of the expert-feedback system. The intentionally simple code (100 total lines) allows experts to:

- Quickly scan and understand the entire codebase (<20 seconds)
- Identify obvious issues rapidly
- Raise clarifying questions about requirements
- Generate recommendations for improvements
