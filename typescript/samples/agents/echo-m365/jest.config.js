/**
 * Jest configuration for echo-m365 agent tests.
 *
 * All tests automatically use LLM recordings instead of real API calls.
 * This ensures fast, deterministic, and free testing.
 */

// Set environment variables for testing
process.env.USE_LLM_RECORDINGS = process.env.USE_LLM_RECORDINGS || 'true';
process.env.RECORD_LLM = process.env.RECORD_LLM || 'false';

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests', '<rootDir>/src'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      tsconfig: {
        types: ['node', 'jest'],
        esModuleInterop: true,
        allowSyntheticDefaultImports: true
      }
    }]
  }
};
