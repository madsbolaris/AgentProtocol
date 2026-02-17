// Simple Calculator - Intentionally flawed for testing
// NO type annotations, NO validation, NO error handling

export function add(a, b) {
  return a + b;  // Will silently coerce types!
}

export function subtract(a, b) {
  return a - b;
}

export function multiply(a, b) {
  return a * b;
}

export function divide(a, b) {
  return a / b;  // No zero check! Will return Infinity
}

export function modulo(a, b) {
  return a % b;
}
