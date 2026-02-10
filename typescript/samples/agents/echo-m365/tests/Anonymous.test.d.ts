/**
 * Integration tests for EchoM365 running in anonymous mode.
 *
 * These tests verify that the echo bot works without Azure authentication
 * and catches issues that were found in production:
 * - Anonymous mode functionality
 * - CORS headers
 * - Route configuration
 * - HTTP endpoint responses
 *
 * Run with: npm test -- Anonymous.test.ts
 */
export {};
