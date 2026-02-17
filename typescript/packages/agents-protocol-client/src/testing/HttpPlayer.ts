/**
 * Replays recorded HTTP responses for deterministic testing.
 */

import * as fs from 'fs';
import * as path from 'path';
import { HttpRecorder, RecordedInteraction } from './HttpRecorder';

/**
 * Replays recorded HTTP responses for deterministic testing.
 */
export class HttpPlayer {
  private recordingsDir: string;
  private recorder: HttpRecorder;
  private callCount = 0;

  constructor(recordingsDir: string) {
    this.recordingsDir = recordingsDir;

    if (!fs.existsSync(recordingsDir)) {
      throw new Error(
        `Recordings directory not found: ${recordingsDir}\n` +
        `Run tests with RECORD_HTTP=true to create recordings.`
      );
    }

    // Use recorder for hash generation
    this.recorder = new HttpRecorder(recordingsDir);
  }

  /**
   * Generate hash - same as recorder.
   */
  hashRequest(method: string, path: string, body?: string): string {
    return this.recorder.hashRequest(method, path, body);
  }

  /**
   * Replay a recorded HTTP response.
   */
  async replayAsync(
    method: string,
    path: string,
    body?: string
  ): Promise<{ statusCode: number; body: string }> {
    const hashKey = this.hashRequest(method, path, body);
    this.callCount++;

    const responsePath = path.join(this.recordingsDir, `${hashKey}.response.json`);

    if (!fs.existsSync(responsePath)) {
      throw new Error(
        `No recording found for request.\n` +
        `Expected: ${responsePath}\n` +
        `Hash: ${hashKey}\n\n` +
        `Request details:\n` +
        `  Method: ${method}\n` +
        `  Path: ${path}\n` +
        `  Body: ${body ?? '(null)'}\n\n` +
        `This usually means:\n` +
        `1. Tests need to be run in recording mode first: RECORD_HTTP=true npm test\n` +
        `2. The request parameters have changed (different hash)\n` +
        `3. The recording file was deleted\n\n` +
        `Run with RECORD_HTTP=true to create recordings.`
      );
    }

    const responseData: RecordedInteraction = JSON.parse(
      fs.readFileSync(responsePath, 'utf-8')
    );

    console.log(`  ▶️  Replaying HTTP call #${this.callCount}: ${method} ${path} → ${hashKey}`);

    return {
      statusCode: responseData.statusCode,
      body: responseData.body,
    };
  }
}
