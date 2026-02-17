import { type UIPhase, type PhaseConfig } from '../types/workspace'

export const phaseConfigs: Record<UIPhase, PhaseConfig> = {
  'phase-01': {
    name: 'Iteration 1: Expert Review',
    description: 'Experts independently review the proposal',
    agentStatuses: {
      'typescript-expert': { status: 'running', hasConcerns: false },
      'python-expert': { status: 'running', hasConcerns: false, hasNewContent: true },
      'synthesis-agent': { status: 'disabled', hasConcerns: false },
      'artifact-generator': { status: 'disabled', hasConcerns: false }
    },
    detailView: {
      type: 'conversation',
      title: 'Expert Feedback',
      content: ''
    },
    actionPane: {
      type: 'empty',
      title: 'Actions',
      content: {
        icon: 'users',
        title: 'Experts reviewing',
        description: 'Expert agents are analyzing the codebase'
      }
    }
  },

  'phase-02': {
    name: 'Iteration 1: Synthesis',
    description: 'Synthesis agent consolidates expert feedback',
    agentStatuses: {
      'typescript-expert': { status: 'pending', hasConcerns: false, hasNewContent: false },
      'python-expert': { status: 'pending', hasConcerns: false, hasNewContent: false },
      'synthesis-agent': { status: 'running', hasConcerns: false },
      'artifact-generator': { status: 'disabled', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Synthesis Agent',
      content: ''
    },
    actionPane: {
      type: 'empty',
      title: 'Status',
      content: {
        message: 'Synthesis agent is consolidating expert feedback and identifying areas that need clarification.'
      }
    }
  },

  'phase-03': {
    name: 'Questions for User',
    description: 'User answers questions from experts',
    agentStatuses: {
      'typescript-expert': { status: 'running', hasConcerns: false, hasNewContent: false },
      'python-expert': { status: 'running', hasConcerns: false, hasNewContent: false },
      'synthesis-agent': { status: 'disabled', hasConcerns: false },
      'artifact-generator': { status: 'disabled', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Synthesized Questions',
      content: '# Questions from Iteration 1\n\nBased on expert feedback, we need clarification on the following points...'
    },
    actionPane: {
      type: 'questions',
      title: 'Actions',
      convergencePercent: 45,
      convergenceTarget: 60,
      consensusReached: false,
      content: {
        statusLabel: 'Synthesis Complete',
        showHeader: true,
        questions: [
          {
            id: 'q1',
            question: 'What is the expected scale of this application?',
            context: '',
            expert: 'synthesis-agent',
            type: 'radio',
            options: [
              { value: 'small', label: 'Small (1-10 users)', description: 'Personal or small team use' },
              { value: 'medium', label: 'Medium (10-1000 users)', description: 'Department or small organization' },
              { value: 'large', label: 'Large (1000+ users)', description: 'Enterprise-scale deployment' },
              { value: 'other-scale', label: 'Other', description: 'Specify below' }
            ],
            allowOther: true
          },
          {
            id: 'q2',
            question: 'Are there specific performance requirements we should target?',
            context: '',
            expert: 'synthesis-agent',
            type: 'radio',
            options: [
              { value: 'no-specific', label: 'No specific requirements', description: 'General best practices are sufficient' },
              { value: 'response-time', label: 'Response time critical', description: 'Sub-100ms response times needed' },
              { value: 'throughput', label: 'High throughput', description: 'Handle 1000+ requests/second' },
              { value: 'other-perf', label: 'Other', description: 'Specify below' }
            ],
            allowOther: true
          },
          {
            id: 'q3',
            question: 'What is the deployment environment?',
            context: '',
            expert: 'synthesis-agent',
            type: 'radio',
            options: [
              { value: 'cloud', label: 'Cloud (AWS, Azure, GCP)', description: '' },
              { value: 'on-premise', label: 'On-Premise', description: '' },
              { value: 'hybrid', label: 'Hybrid', description: '' },
              { value: 'other-deploy', label: 'Other', description: '' }
            ],
            allowOther: true
          },
          {
            id: 'q4',
            question: "What's the primary deployment target for the SDK? We need to understand the runtime environment to make architectural decisions.",
            context: '',
            expert: 'synthesis-agent',
            type: 'radio',
            options: [
              { value: 'nodejs', label: 'Node.js Server', description: 'Backend services and server-side applications' },
              { value: 'browser', label: 'Browser', description: 'Frontend web applications' },
              { value: 'both', label: 'Both (Universal)', description: 'Support both Node.js and browser environments with conditional exports, dual package hazard mitigation, and environment-specific polyfills for platform APIs' },
              { value: 'other-target', label: 'Other', description: '' }
            ],
            allowOther: true
          },
          {
            id: 'q5',
            question: 'Which validation approaches should be supported? (Select all that apply)',
            context: '',
            expert: 'synthesis-agent',
            type: 'checkbox',
            options: [
              { value: 'zod', label: 'Zod', description: 'TypeScript-first schema validation' },
              { value: 'joi', label: 'Joi', description: 'Popular Node.js validation library' },
              { value: 'yup', label: 'Yup', description: 'Schema builder for value parsing' },
              { value: 'other-validation', label: 'Other', description: '' }
            ],
            allowOther: true
          }
        ]
      }
    }
  },

  'phase-04': {
    name: 'Iteration 2: Expert Review',
    description: 'Second iteration of expert reviews based on user answers',
    agentStatuses: {
      'typescript-expert': { status: 'running', hasConcerns: false, hasNewContent: false },
      'python-expert': { status: 'running', hasConcerns: false, hasNewContent: false },
      'synthesis-agent': { status: 'disabled', hasConcerns: false },
      'artifact-generator': { status: 'disabled', hasConcerns: false }
    },
    detailView: {
      type: 'conversation',
      title: 'C# Expert Feedback',
      content: ''
    },
    actionPane: {
      type: 'empty',
      title: 'Status',
      content: {
        message: 'Experts are reviewing based on your answers from Iteration 1. No additional questions at this time.'
      }
    }
  },

  'phase-05': {
    name: 'Iteration 2: Synthesis',
    description: 'Synthesis agent consolidates iteration 2 feedback',
    agentStatuses: {
      'typescript-expert': { status: 'running', hasConcerns: false, hasNewContent: false },
      'python-expert': { status: 'running', hasConcerns: false, hasNewContent: false },
      'synthesis-agent': { status: 'disabled', hasConcerns: false },
      'artifact-generator': { status: 'disabled', hasConcerns: false }
    },
    detailView: {
      type: 'conversation',
      title: 'Synthesis Agent',
      content: ''
    },
    actionPane: {
      type: 'empty',
      title: 'Status',
      content: {
        message: 'Synthesis agent is consolidating feedback from Iteration 2. Convergence: 75%.'
      }
    }
  },

  'phase-06': {
    name: 'Iteration 3: Expert Review (Optional)',
    description: 'Optional third iteration of expert reviews',
    agentStatuses: {
      'typescript-expert': { status: 'completed', hasConcerns: false },
      'python-expert': { status: 'completed', hasConcerns: false },
      'csharp-expert': { status: 'completed', hasConcerns: false },
      'frontend-expert': { status: 'completed', hasConcerns: false },
      'security-expert': { status: 'completed', hasConcerns: false },
      'synthesis-agent': { status: 'disabled', hasConcerns: false }
    },
    detailView: {
      type: 'conversation',
      title: 'Expert Feedback',
      content: ''
    },
    actionPane: {
      type: 'empty',
      title: 'Status',
      content: {
        message: 'Final expert review in progress. This is the last iteration before artifact generation.'
      }
    }
  },

  'phase-07': {
    name: 'Iteration 3: Synthesis (Optional)',
    description: 'Synthesis agent consolidates iteration 3 feedback',
    agentStatuses: {
      'typescript-expert': { status: 'completed', hasConcerns: false },
      'python-expert': { status: 'completed', hasConcerns: false },
      'csharp-expert': { status: 'completed', hasConcerns: false },
      'frontend-expert': { status: 'completed', hasConcerns: false },
      'security-expert': { status: 'completed', hasConcerns: false },
      'synthesis-agent': { status: 'running', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Expert Convergence Analysis',
      content: '# Expert Convergence Analysis - Iteration 3\n\n## Consensus Reached: 92%\n\nAll experts have completed their final reviews.'
    },
    actionPane: {
      type: 'empty',
      title: 'Status',
      content: {
        message: 'All experts have completed their reviews. Expert convergence: 92% (above 60% threshold). Proceeding to artifact generation.'
      }
    }
  },

  'phase-08': {
    name: 'Artifact Generation',
    description: 'Finalization agent generates the artifact',
    agentStatuses: {
      'artifact-generator': { status: 'running', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Draft ADR (Architecture Decision Record)',
      content: '# Architecture Decision Record: Multi-Language SDK Design\n\n## Status\nDraft - In Progress\n\n## Context\n\nWe are building a set of SDKs...'
    },
    actionPane: {
      type: 'empty',
      title: 'Status',
      content: {
        message: 'Artifact is being generated based on expert consensus. The finalization agent is synthesizing recommendations from all five experts into a cohesive specification.'
      }
    }
  },

  'phase-09': {
    name: 'Expert Concern Review',
    description: 'Experts review the generated artifact',
    agentStatuses: {
      'typescript-expert': { status: 'completed', hasConcerns: true },
      'python-expert': { status: 'completed', hasConcerns: false },
      'csharp-expert': { status: 'running', hasConcerns: false },
      'frontend-expert': { status: 'pending', hasConcerns: false },
      'security-expert': { status: 'pending', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Generated Draft Artifact',
      content: '# Multi-Language SDK Design Specification (Draft v1)\n\n## Overview\n\nThis specification outlines the design...'
    },
    actionPane: {
      type: 'empty',
      title: 'Review Progress',
      content: {
        message: 'Experts are reviewing the generated artifact for potential concerns. 3 of 5 experts have completed their review. TypeScript Expert has raised a concern about type safety in edge cases.'
      }
    }
  },

  'phase-10': {
    name: 'User Concern Decisions',
    description: 'User reviews and approves/rejects concerns',
    agentStatuses: {
      'typescript-expert': { status: 'completed', hasConcerns: true },
      'python-expert': { status: 'completed', hasConcerns: false },
      'csharp-expert': { status: 'completed', hasConcerns: false },
      'frontend-expert': { status: 'completed', hasConcerns: true },
      'security-expert': { status: 'completed', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Synthesized Concerns',
      content: '# Expert Concerns Summary\n\n## High Priority Concerns\n\n### TypeScript Expert: Type Safety in Edge Cases...'
    },
    actionPane: {
      type: 'concern-review',
      title: 'Review Concerns',
      content: {
        concerns: [
          {
            id: 'c1',
            expert: 'typescript-expert',
            text: 'Type safety in edge cases needs improvement',
            context: 'Specifically around nullable types and union handling when converting between different data formats.'
          },
          {
            id: 'c2',
            expert: 'frontend-expert',
            text: 'Performance implications of the proposed approach',
            context: 'Large datasets (>10k items) may cause rendering issues due to synchronous processing.'
          }
        ]
      }
    }
  },

  'phase-11': {
    name: 'Address Concerns',
    description: 'Experts address approved concerns',
    agentStatuses: {
      'typescript-expert': { status: 'running', hasConcerns: false },
      'frontend-expert': { status: 'pending', hasConcerns: false }
    },
    detailView: {
      type: 'conversation',
      title: 'TypeScript Expert - Addressing Type Safety Concerns',
      content: ''
    },
    actionPane: {
      type: 'empty',
      title: 'Resolution Progress',
      content: {
        message: 'Experts are addressing the approved concerns. TypeScript Expert is working on type safety enhancements.'
      }
    }
  },

  'phase-12': {
    name: 'Regenerate Artifact',
    description: 'Finalization agent regenerates artifact with updates',
    agentStatuses: {
      'artifact-generator': { status: 'running', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Updated Draft ADR (v2.0)',
      content: '# Architecture Decision Record: Multi-Language SDK Design (v2.0)\n\n## Status\nProposed - Revised after expert concern resolution...'
    },
    actionPane: {
      type: 'empty',
      title: 'Regeneration Progress',
      content: {
        message: 'Incorporating all expert updates into a revised artifact.'
      }
    }
  },

  'phase-13': {
    name: 'Final Approval',
    description: 'Final user approval or request for revisions',
    agentStatuses: {
      'typescript-expert': { status: 'completed', hasConcerns: false },
      'python-expert': { status: 'completed', hasConcerns: false },
      'csharp-expert': { status: 'completed', hasConcerns: false },
      'frontend-expert': { status: 'completed', hasConcerns: false },
      'security-expert': { status: 'completed', hasConcerns: false }
    },
    detailView: {
      type: 'document',
      title: 'Final Multi-Language SDK Specification',
      content: '# Multi-Language SDK Design Specification (v2.0 - Final)\n\n## Overview\nThis specification outlines the final design...'
    },
    actionPane: {
      type: 'approval',
      title: 'Final Approval',
      content: {
        summary: {
          iterations: 3,
          concernsAddressed: 2,
          totalTime: '24m 15s',
          tokensUsed: 156000,
          cost: 0.52,
          expertCount: 5,
          convergencePercent: 95
        }
      }
    }
  }
}

export const phaseGroups = {
  'Iteration Loop': ['phase-01', 'phase-02', 'phase-03', 'phase-04', 'phase-05', 'phase-06', 'phase-07'] as UIPhase[],
  'Artifact Phase': ['phase-08', 'phase-09'] as UIPhase[],
  'Concern Resolution Loop': ['phase-10', 'phase-11', 'phase-12'] as UIPhase[],
  'Final Phase': ['phase-13'] as UIPhase[]
}
