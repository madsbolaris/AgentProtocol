/**
 * Mock Phase Data - All 5 Phases
 * Generated from prototype HTML files
 * Generated: 2026-02-17T07:46:35.482Z
 */

import { type AgentStatus, type Message } from '../types/workspace'

export interface Phase01MockData {
  agentStatuses: Record<string, AgentStatus>
  newContentAgents: string[]
  convergencePercent: number
  messageHistory: Record<string, Message[]>
  actionPaneMessage: string
}

export function loadPhase01MockData(): Phase01MockData {
  return {
    agentStatuses: {
      'typescript-expert': {
        status: 'running',
        hasConcerns: false,
        hasNewContent: false
      },
      'python-expert': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'synthesis-agent': {
        status: 'disabled',
        hasConcerns: false,
      },
      'artifact-generator': {
        status: 'disabled',
        hasConcerns: false,
      },
    },
    newContentAgents: [],
    convergencePercent: 55,
    messageHistory: {
      'typescript-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197208,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237207,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'python-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197208,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237207,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'synthesis-agent': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197208,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237207,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'artifact-generator': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197208,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237207,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
    },
    actionPaneMessage: "Waiting for experts to complete their reviews..."
  }
}

export interface Phase02MockData {
  agentStatuses: Record<string, AgentStatus>
  newContentAgents: string[]
  convergencePercent: number
  messageHistory: Record<string, Message[]>
  actionPaneMessage: string
}

export function loadPhase02MockData(): Phase02MockData {
  return {
    agentStatuses: {
      'typescript-expert': {
        status: 'running',
        hasConcerns: false,
        hasNewContent: false
      },
      'python-expert': {
        status: 'running',
        hasConcerns: false,
        hasNewContent: false
      },
      'synthesis-agent': {
        status: 'disabled',
        hasConcerns: false,
      },
      'artifact-generator': {
        status: 'disabled',
        hasConcerns: false,
      },
    },
    newContentAgents: [],
    convergencePercent: 55,
    messageHistory: {
      'typescript-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197178,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237178,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'python-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197178,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237178,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'synthesis-agent': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197178,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237178,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'artifact-generator': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197178,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237178,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
    },
    actionPaneMessage: "Synthesis agent is consolidating expert feedback..."
  }
}

export interface Phase03MockData {
  agentStatuses: Record<string, AgentStatus>
  newContentAgents: string[]
  convergencePercent: number
  messageHistory: Record<string, Message[]>
  actionPaneMessage: string
}

export function loadPhase03MockData(): Phase03MockData {
  return {
    agentStatuses: {
      'typescript-expert': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'python-expert': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'synthesis-agent': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'artifact-generator': {
        status: 'disabled',
        hasConcerns: false,
      },
    },
    newContentAgents: [],
    convergencePercent: 55,
    messageHistory: {
      'typescript-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197148,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237148,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'python-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197148,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237148,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'synthesis-agent': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197148,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237148,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'artifact-generator': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197148,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237148,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
    },
    actionPaneMessage: "Please answer the questions from experts."
  }
}

export interface Phase04MockData {
  agentStatuses: Record<string, AgentStatus>
  newContentAgents: string[]
  convergencePercent: number
  messageHistory: Record<string, Message[]>
  actionPaneMessage: string
}

export function loadPhase04MockData(): Phase04MockData {
  return {
    agentStatuses: {
      'typescript-expert': {
        status: 'running',
        hasConcerns: false,
        hasNewContent: false
      },
      'python-expert': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'synthesis-agent': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'artifact-generator': {
        status: 'disabled',
        hasConcerns: false,
      },
    },
    newContentAgents: [],
    convergencePercent: 55,
    messageHistory: {
      'typescript-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197128,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237127,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'python-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197128,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237127,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'synthesis-agent': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197128,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237127,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'artifact-generator': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197128,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237127,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
    },
    actionPaneMessage: "Experts reviewing based on your answers..."
  }
}

export interface Phase05MockData {
  agentStatuses: Record<string, AgentStatus>
  newContentAgents: string[]
  convergencePercent: number
  messageHistory: Record<string, Message[]>
  actionPaneMessage: string
}

export function loadPhase05MockData(): Phase05MockData {
  return {
    agentStatuses: {
      'typescript-expert': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'python-expert': {
        status: 'pending',
        hasConcerns: false,
        hasNewContent: false
      },
      'synthesis-agent': {
        status: 'running',
        hasConcerns: false,
        hasNewContent: false
      },
      'artifact-generator': {
        status: 'disabled',
        hasConcerns: false,
      },
    },
    newContentAgents: [],
    convergencePercent: 55,
    messageHistory: {
      'typescript-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197103,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237103,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'python-expert': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197103,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237103,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'synthesis-agent': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197103,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237103,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
      'artifact-generator': [
        {
          id: "msg-0",
          role: "user",
          content: "Please review the simple-calculator codebase and provide feedback on its production readiness.\nI need you to evaluate the following aspects comprehensively:\n1. Type Safety and TypeScript Configuration\n- Review tsconfig.json settings for strictness\n- Check for proper type annotations throughout the codebase\n- Identify any usage of 'any' types that should be replaced\n- Verify that type definitions are comprehensive\n- Ensure proper handling of null/undefined values\n2. Error Handling and Validation\n- Check for input validation on all public APIs\n- Review error handling patterns and consistency\n- Verify that errors are properly typed and informative\n- Look for edge cases that might not be handled\n- Ensure graceful degradation for unexpected inputs\n3. Testing Coverage\n- Assess unit test coverage and quality\n- Check for integration tests where appropriate\n- Review test organization and naming conventions\n- Identify critical paths that lack test coverage\n- Verify that edge cases are properly tested\n4. Code Quality and Maintainability\n- Review code structure and organization\n- Check for proper separation of concerns\n- Identify potential code smells or anti-patterns\n- Assess naming conventions and code readability\n- Look for opportunities to reduce complexity\n5. Performance Considerations\n- Identify any obvious performance bottlenecks\n- Check for inefficient algorithms or data structures\n- Review memory usage patterns\n- Look for opportunities for optimization\n6. Security Best Practices\n- Check for potential security vulnerabilities\n- Review input sanitization approaches\n- Verify that sensitive data is properly handled\n- Identify any unsafe operations or eval usage\n7. Documentation and Comments\n- Assess the quality and completeness of documentation\n- Check for inline comments where needed\n- Verify that README provides clear usage instructions\n- Look for JSDoc comments on public APIs\n8. Build and Deployment\n- Review build configuration\n- Check for proper environment handling\n- Verify that dependencies are up to date\n- Assess the deployment strategy\nPlease provide specific, actionable recommendations for each area, prioritized by importance. Include code examples where appropriate to illustrate suggested improvements.\nFor each issue identified, please specify:\n- Severity level (Critical, High, Medium, Low)\n- Impact on production readiness\n- Estimated effort to fix\n- Recommended approach or solution",
          timestamp: Date.now() - 197103,
        },
        {
          id: "msg-1",
          role: "assistant",
          content: "",
          timestamp: Date.now() - 237103,
          metadata: {
            toolCalls: [
              {
                id: "tool-1-0",
                name: "Glob",
                input: {"pattern":"**/*.{ts,js,json}"},
                output: {"summary":"Found 8 files in simple-calculator","status":"completed"}
              },
              {
                id: "tool-1-1",
                name: "Read",
                input: {"file_path":"src/calculator.ts"},
                output: {"summary":"Read 45 lines from main calculator implementation","status":"completed"}
              },
              {
                id: "tool-1-2",
                name: "Grep",
                input: {"pattern":"test|spec"},
              },
            ]
          }
        },
      ],
    },
    actionPaneMessage: "Synthesis agent finalizing iteration 2..."
  }
}
