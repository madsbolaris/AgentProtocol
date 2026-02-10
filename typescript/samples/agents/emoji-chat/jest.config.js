/**
 * Jest configuration for emoji-chat agent tests.
 *
 * All tests automatically use LLM recordings instead of real API calls.
 * This ensures fast, deterministic, and free testing.
 */

// Set environment variables for testing
process.env.USE_LLM_RECORDINGS = process.env.USE_LLM_RECORDINGS || 'true';
process.env.RECORD_LLM = process.env.RECORD_LLM || 'false';

export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      useESM: true,
    }],
  },
  testMatch: [
    '**/__tests__/**/*.test.ts',
    '**/?(*.)+(spec|test).ts'
  ],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
  ],
};
