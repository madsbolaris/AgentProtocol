/**
 * Hook for agent operations (runs/executions)
 */

import { useState, useCallback } from 'react';
import type { Run, AITool, ChatMessage } from '@microsoft/agents-protocol-abstractions';
import { useAgentContext } from '../context/AgentProvider';

export interface CreateRunOptions {
  agentId: string;
  threadId?: string;
  input?: ChatMessage[];
  instructions?: string;
  tools?: AITool[];
  wait?: boolean;
}

export interface UseAgentResult {
  currentRun: Run | null;
  isRunning: boolean;
  error: Error | null;

  // Actions
  createRun: (options: CreateRunOptions) => Promise<Run>;
  cancelRun: (runId: string) => Promise<void>;
  submitToolOutputs: (
    runId: string,
    outputs: Array<{ toolCallId: string; output: string }>
  ) => Promise<void>;
}

export function useAgent(): UseAgentResult {
  const { client } = useAgentContext();

  const [currentRun, setCurrentRun] = useState<Run | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const createRun = useCallback(
    async (options: CreateRunOptions): Promise<Run> => {
      try {
        setIsRunning(true);
        setError(null);

        const run = options.wait
          ? await client.runs.createAndWait({
              agentId: options.agentId,
              threadId: options.threadId,
              input: options.input,
              instructions: options.instructions,
              tools: options.tools,
            })
          : await client.runs.create({
              agentId: options.agentId,
              threadId: options.threadId,
              input: options.input,
              instructions: options.instructions,
              tools: options.tools,
            });

        setCurrentRun(run);
        return run;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setIsRunning(false);
      }
    },
    [client]
  );

  const cancelRun = useCallback(
    async (runId: string) => {
      try {
        await client.runs.cancel(runId);
        setCurrentRun(null);
        setIsRunning(false);
      } catch (err) {
        setError(err as Error);
      }
    },
    [client]
  );

  const submitToolOutputs = useCallback(
    async (runId: string, outputs: Array<{ toolCallId: string; output: string }>) => {
      try {
        const run = await client.runs.submitToolOutputs(runId, {
          toolOutputs: outputs,
        });
        setCurrentRun(run);
      } catch (err) {
        setError(err as Error);
      }
    },
    [client]
  );

  return {
    currentRun,
    isRunning,
    error,
    createRun,
    cancelRun,
    submitToolOutputs,
  };
}
