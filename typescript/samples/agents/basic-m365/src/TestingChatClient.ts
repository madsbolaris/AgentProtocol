// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

/**
 * Testing wrapper for OpenAI client that supports recording and playback of LLM interactions.
 * This enables deterministic testing by recording real LLM responses and playing them back.
 */

import OpenAI from 'openai'
import * as fs from 'fs'
import * as path from 'path'
import * as crypto from 'crypto'

export class TestingChatClient {
  private readonly realClient: OpenAI | null
  private readonly recordingsDir: string
  private readonly modelId: string
  private readonly recordMode: boolean
  private readonly playbackMode: boolean
  private callCount: number = 0

  constructor(
    realClient: OpenAI | null,
    recordingsDir: string,
    modelId: string,
    recordMode: boolean = false,
    playbackMode: boolean = false
  ) {
    if (recordMode && playbackMode) {
      throw new Error('Cannot enable both record and playback mode simultaneously')
    }

    if (recordMode && !realClient) {
      throw new Error('Real client required for recording mode')
    }

    if (playbackMode && !fs.existsSync(recordingsDir)) {
      throw new Error(`Recordings directory not found: ${recordingsDir}`)
    }

    this.realClient = realClient
    this.recordingsDir = recordingsDir
    this.modelId = modelId
    this.recordMode = recordMode
    this.playbackMode = playbackMode

    if (this.recordMode) {
      fs.mkdirSync(this.recordingsDir, { recursive: true })
      console.log(`📹 LLM Recording enabled: ${this.recordingsDir}`)
    } else if (this.playbackMode) {
      console.log(`▶️  LLM Playback enabled: ${this.recordingsDir}`)
      console.log('   Using recorded LLM responses (test mode)')
    }
  }

  async createCompletion(
    messages: OpenAI.Chat.ChatCompletionMessageParam[],
    tools?: OpenAI.Chat.ChatCompletionTool[]
  ): Promise<OpenAI.Chat.ChatCompletion> {
    this.callCount++
    const callId = this.callCount
    const hashKey = this.computeRequestHash(messages, tools || [])

    if (this.playbackMode) {
      return this.playbackResponse(callId, hashKey, messages, tools || [])
    }

    // Call real LLM (works in both normal and recording mode)
    if (!this.realClient) {
      throw new Error('Real client not available. Use recording mode with a valid OpenAI client.')
    }

    const response = await this.realClient.chat.completions.create({
      model: this.modelId,
      messages: messages,
      tools: tools && tools.length > 0 ? tools : undefined
    })

    if (this.recordMode) {
      await this.recordInteraction(callId, hashKey, messages, tools || [], response)
    }

    return response
  }

  private playbackResponse(
    callId: number,
    hashKey: string,
    messages: OpenAI.Chat.ChatCompletionMessageParam[],
    tools: OpenAI.Chat.ChatCompletionTool[]
  ): OpenAI.Chat.ChatCompletion {
    const responseFile = path.join(this.recordingsDir, `${hashKey}.response.json`)

    if (!fs.existsSync(responseFile)) {
      throw new Error(
        `No recorded LLM response found for request hash: ${hashKey}\n` +
        `Expected file: ${responseFile}\n\n` +
        `This usually means:\n` +
        `1. Tests need to be run in generation mode first: RECORD_LLM=true\n` +
        `2. The request parameters have changed (different hash)\n` +
        `3. The recording file was deleted\n\n` +
        `Request details:\n` +
        `  Messages: ${messages.length} messages\n` +
        `  Tools: ${tools.length > 0 ? 'provided' : 'null'}\n`
      )
    }

    console.log(`  ▶️  Replaying LLM call #${callId}: ${hashKey}`)

    const recordingData = JSON.parse(fs.readFileSync(responseFile, 'utf-8'))
    const responseData = recordingData.response

    return this.deserializeCompletion(responseData)
  }

  private async recordInteraction(
    callId: number,
    hashKey: string,
    messages: OpenAI.Chat.ChatCompletionMessageParam[],
    tools: OpenAI.Chat.ChatCompletionTool[],
    response: OpenAI.Chat.ChatCompletion
  ): Promise<void> {
    console.log(`  📹 Recording LLM call #${callId}: ${hashKey}`)

    // Save request
    const requestFile = path.join(this.recordingsDir, `${hashKey}.request.json`)
    const requestData = {
      callId,
      timestamp: new Date().toISOString(),
      hash: hashKey,
      model: this.modelId,
      messages: this.normalizeMessages(messages),
      tools: tools.length > 0 ? tools.map(t => ({
        type: 'function',
        function: {
          name: t.function.name,
          description: t.function.description || '',
          parameters: t.function.parameters || {}
        }
      })) : undefined
    }

    fs.writeFileSync(requestFile, JSON.stringify(requestData, null, 2))

    // Save response
    const responseFile = path.join(this.recordingsDir, `${hashKey}.response.json`)
    const choice = response.choices[0]

    // Extract content
    const contentList: any[] = []
    if (choice.message.content) {
      contentList.push({ text: choice.message.content })
    }

    // Extract tool calls
    const toolCallsList: any[] = []
    if (choice.message.tool_calls) {
      for (const tc of choice.message.tool_calls) {
        toolCallsList.push({
          id: tc.id,
          type: 'Function',
          function: {
            name: tc.function.name,
            arguments: tc.function.arguments
          }
        })
      }
    }

    const responseData = {
      callId,
      timestamp: new Date().toISOString(),
      hash: hashKey,
      response: {
        id: response.id,
        model: response.model,
        created: response.created,
        finishReason: choice.finish_reason ? this.capitalizeFirstLetter(choice.finish_reason) : 'Stop',
        content: contentList,
        toolCalls: toolCallsList
      }
    }

    fs.writeFileSync(responseFile, JSON.stringify(responseData, null, 2))
  }

  private computeRequestHash(
    messages: OpenAI.Chat.ChatCompletionMessageParam[],
    tools: OpenAI.Chat.ChatCompletionTool[]
  ): string {
    // Build request dict matching C# format exactly
    const requestDict: any = {
      model: this.modelId,
      messages: this.normalizeMessages(messages),
      temperature: 0.0
    }

    if (tools && tools.length > 0) {
      requestDict.tools = tools.map(t => ({
        type: 'function',
        function: {
          name: t.function.name,
          description: t.function.description || '',
          parameters: JSON.stringify(t.function.parameters || {})
        }
      }))
    }

    // Serialize to JSON with sorted keys (recursively)
    const sortedDict = this.sortJsonKeys(requestDict)
    const jsonStr = JSON.stringify(sortedDict)

    // Log the JSON being hashed for debugging
    console.log(`🔍 [TypeScript] Computing hash for:`)
    console.log(`   JSON length: ${jsonStr.length} chars`)
    console.log(`   FULL JSON: ${jsonStr}`)
    fs.writeFileSync('/tmp/typescript_json.txt', jsonStr)

    // Hash and truncate (SHA256, first 16 chars)
    const hash = crypto.createHash('sha256').update(jsonStr, 'utf8').digest('hex')
    const hashStr = hash.substring(0, 16).toLowerCase()
    console.log(`   Hash: ${hashStr}`)
    return hashStr
  }

  private normalizeMessages(messages: OpenAI.Chat.ChatCompletionMessageParam[]): any[] {
    return messages.map((msg: any) => {
      const normalized: any = { role: msg.role }

      // Add content if present
      if (msg.content !== undefined && msg.content !== null) {
        normalized.content = msg.content
      }

      // Add tool_calls if present
      if (msg.tool_calls && msg.tool_calls.length > 0) {
        normalized.tool_calls = msg.tool_calls.map((tc: any) => ({
          id: tc.id,
          type: tc.type || 'function',
          function: {
            name: tc.function.name,
            arguments: tc.function.arguments
          }
        }))
      }

      // Add tool_call_id if present
      if (msg.tool_call_id) {
        normalized.tool_call_id = msg.tool_call_id
      }

      return normalized
    })
  }

  private deserializeCompletion(responseElement: any): OpenAI.Chat.ChatCompletion {
    const completionId = responseElement.id || 'mock-completion'
    const model = responseElement.model || 'unknown'
    const finishReasonStr = responseElement.finishReason || 'Stop'

    // Map finish reason
    const finishReasonMap: Record<string, string> = {
      'ToolCalls': 'tool_calls',
      'Stop': 'stop',
      'Length': 'length'
    }
    const finishReason = finishReasonMap[finishReasonStr] || 'stop'

    // Parse content
    let content: string | null = null
    const contentArray = responseElement.content || []
    if (contentArray.length > 0) {
      content = contentArray[0].text || ''
    }

    // Parse tool calls
    let toolCalls: OpenAI.Chat.ChatCompletionMessageToolCall[] | undefined = undefined
    const toolCallsArray = responseElement.toolCalls || []
    if (toolCallsArray.length > 0) {
      toolCalls = toolCallsArray.map((tc: any) => ({
        id: tc.id,
        type: 'function' as const,
        function: {
          name: tc.function.name,
          arguments: tc.function.arguments
        }
      }))
    }

    // Build mock completion object
    const completion: OpenAI.Chat.ChatCompletion = {
      id: completionId,
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: model,
      choices: [{
        index: 0,
        message: {
          role: 'assistant',
          content: content,
          refusal: null,
          tool_calls: toolCalls
        },
        finish_reason: finishReason as any,
        logprobs: null
      }],
      usage: {
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0
      }
    }

    return completion
  }

  /**
   * Recursively sorts all keys in an object or array to ensure consistent JSON serialization.
   * This matches the behavior of C#'s SortJsonKeys method.
   */
  private sortJsonKeys(value: any): any {
    if (value === null || value === undefined) {
      return value
    }

    // Handle arrays by recursively sorting each element
    if (Array.isArray(value)) {
      return value.map(item => this.sortJsonKeys(item))
    }

    // Handle objects by sorting keys and recursively sorting values
    if (typeof value === 'object') {
      const sorted: any = {}
      const keys = Object.keys(value).sort()
      for (const key of keys) {
        sorted[key] = this.sortJsonKeys(value[key])
      }
      return sorted
    }

    // Primitive values (string, number, boolean) pass through
    return value
  }

  private capitalizeFirstLetter(str: string): string {
    if (!str) return str
    // Handle snake_case to PascalCase (tool_calls -> ToolCalls)
    return str.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join('')
  }
}
