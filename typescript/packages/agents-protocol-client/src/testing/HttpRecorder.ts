/**
 * HTTP Recording functionality for deterministic testing.
 * Records HTTP request/response pairs for Agent Protocol client tests.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface HttpRequest {
  method: string;
  path: string;
  body?: string;
}

export interface HttpResponse {
  status: number;
  headers?: Record<string, string>;
  body: string;
}

export interface RecordedInteraction {
  callId: number;
  timestamp: string;
  hash: string;
  statusCode: number;
  body: string;
}

/**
 * Records HTTP request/response pairs for test replay.
 */
export class HttpRecorder {
  private recordingsDir: string;
  private callCount = 0;

  constructor(recordingsDir: string) {
    this.recordingsDir = recordingsDir;

    // Create directory if it doesn't exist
    if (!fs.existsSync(recordingsDir)) {
      fs.mkdirSync(recordingsDir, { recursive: true });
    }
  }

  /**
   * Generate deterministic hash for HTTP request.
   * CRITICAL: Must match C# implementation exactly for cross-language compatibility.
   */
  hashRequest(method: string, path: string, body?: string): string {
    // Normalize request for hashing (must match C# exactly)
    const normalized: any = {
      method: method.toUpperCase(),
      path,
      body: body ?? '',
    };

    // Convert to JSON string for hashing with camelCase naming
    // CRITICAL: Must match C# JsonSerializer with CamelCase policy
    const jsonStr = JSON.stringify({
      method: normalized.method,
      path: normalized.path,
      body: normalized.body,
    });

    // Generate SHA256 hash, first 16 characters, lowercase
    return crypto
      .createHash('sha256')
      .update(jsonStr, 'utf8')
      .digest('hex')
      .substring(0, 16)
      .toLowerCase();
  }

  /**
   * Record an HTTP interaction.
   */
  async recordAsync(
    method: string,
    path: string,
    requestBody: string | undefined,
    statusCode: number,
    responseBody: string
  ): Promise<void> {
    const hashKey = this.hashRequest(method, path, requestBody);
    this.callCount++;

    // Save request for debugging
    const requestPath = path.join(this.recordingsDir, `${hashKey}.request.json`);
    fs.writeFileSync(
      requestPath,
      JSON.stringify(
        {
          callId: this.callCount,
          timestamp: new Date().toISOString(),
          hash: hashKey,
          method: method.toUpperCase(),
          path,
          body: requestBody,
        },
        null,
        2
      )
    );

    // Save response
    const responsePath = path.join(this.recordingsDir, `${hashKey}.response.json`);
    const recordedInteraction: RecordedInteraction = {
      callId: this.callCount,
      timestamp: new Date().toISOString(),
      hash: hashKey,
      statusCode,
      body: responseBody,
    };

    fs.writeFileSync(responsePath, JSON.stringify(recordedInteraction, null, 2));

    console.log(`  📼 Recorded HTTP call #${this.callCount}: ${method} ${path} → ${hashKey}`);
  }
}
