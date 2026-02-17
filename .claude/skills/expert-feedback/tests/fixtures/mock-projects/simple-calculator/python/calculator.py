# Simple Calculator - Intentionally flawed for testing
# NO validation, NO error handling, NO docstrings

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b  # No zero check!

def modulo(a, b):
    return a % b

def evaluate(expression):
    # SECURITY ISSUE: Using eval() is dangerous!
    return eval(expression)
