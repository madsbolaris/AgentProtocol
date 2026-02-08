# Voice Integration Guide

**Version**: 1.0
**Last Updated**: February 2025

## Overview

This guide demonstrates how to integrate voice capabilities with the Agent Runtime API using bidirectional streaming. Voice integration enables real-time, full-duplex conversations between users and AI agents with support for:

- **Bidirectional Audio Streaming**: Send and receive audio in real-time via WebSocket
- **Live Transcription**: Real-time speech-to-text with progressive results
- **Multi-Modal Responses**: Combine voice, text, and visual content
- **Voice Interruption**: Handle user interruptions during agent responses
- **Multi-Language Support**: Process audio in multiple languages
- **Adaptive Audio Quality**: Handle varying network conditions

### Voice Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Voice-Enabled Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Audio Input (WebSocket) ──────────────────────┐           │
│           │                                         │           │
│           ▼                                         │           │
│  ┌─────────────────────┐                            │           │
│  │  AudioContent       │  Raw audio bytes           │           │
│  │  chunks buffered    │  via WebSocket             │           │
│  └─────────────────────┘                            │           │
│           │                                         │           │
│           ▼                                         │           │
│  ┌─────────────────────┐                            │           │
│  │  Voice Activity     │  Detect speech vs.         │           │
│  │  Detection (VAD)    │  silence, endpoint         │           │
│  └─────────────────────┘                            │           │
│           │                                         │           │
│           ▼                                         │           │
│  ┌─────────────────────┐                            │           │
│  │  Speech-to-Text     │  Streaming                 │           │
│  │  (Whisper/Azure)    │  transcription             │           │
│  └─────────────────────┘                            │           │
│           │                                         │           │
│           ▼                                         │           │
│  ┌─────────────────────┐                            │           │
│  │  Agent Processing   │  LLM generates             │           │
│  │  (GPT-4/Claude)     │  text response             │           │
│  └─────────────────────┘                            │           │
│           │                                         │           │
│           ▼                                         │           │
│  ┌─────────────────────┐                            │           │
│  │  Text-to-Speech     │  Convert to audio          │           │
│  │  (Azure TTS/OpenAI) │  chunks                    │           │
│  └─────────────────────┘                            │           │
│           │                                         │           │
│           ▼                                         ▼           │
│  Agent Audio Output (WebSocket) ← MessageUpdatedEvent           │
│                      with AudioContent chunks                   │
└─────────────────────────────────────────────────────────────────┘
```

## Use Cases

### 1. Voice Assistant (Full Duplex)
Real-time conversational AI with natural turn-taking, interruption handling, and voice responses.

**Example**: Customer service bot, virtual receptionist, smart home assistant

### 2. Live Transcription Service
Real-time speech-to-text with progressive transcription updates as the user speaks.

**Example**: Meeting transcription, live captions, accessibility services

### 3. Voice Notes with AI Analysis
Users record voice messages, agent transcribes and analyzes content, responds with insights.

**Example**: Journaling app with AI insights, voice-based task management

### 4. Multi-Language Voice Support
Automatic language detection and transcription in multiple languages.

**Example**: International customer support, translation services

### 5. Voice-Controlled Tools
Voice commands trigger tool executions, agent confirms actions verbally.

**Example**: "Schedule a meeting for tomorrow at 3pm", "Send email to John"

## Architecture

### WebSocket Bidirectional Streaming Pattern

The Agent Runtime API supports bidirectional streaming via WebSocket for real-time voice interactions:

```
Client                                          Server
  │                                               │
  ├─── WebSocket Handshake ──────────────────────>│
  │<──────────── 101 Switching Protocols ─────────┤
  │                                               │
  │  ┌──────────────────────────────────────────┐ │
  │  │   Bidirectional Audio Stream             │ │
  │  │                                          │ │
  │  │  Client → Server (Input):                │ │
  │  │  ChatMessage with AudioContent           │ │
  │  ├───────────────────────────────────────────>│
  │  │                                          │ │
  │  │  Server → Client (Output):               │ │
  │  │  MessageCreatedEvent                     │ │
  │  │  MessageUpdatedEvent (with AudioContent) │ │
  │  │  MessageUpdatedEvent (with TranscriptContent) │
  │  │  MessageCompletedEvent                   │ │
  │  │<───────────────────────────────────────────┤
  │  │                                          │ │
  │  │  Simultaneous send/receive (full-duplex) │ │
  │  └──────────────────────────────────────────┘ │
  │                                               │
  ├─── Close Frame ──────────────────────────────>│
  │<────────────────── Close Acknowledgment ──────┤
```

### Content Types for Voice

#### AudioContent (Input & Output)
**TypeSpec Reference**: `AudioContent` model in `typespec/messages.tsp`

```typescript
{
  kind: "audio",
  data?: bytes,                  // Raw audio bytes (PCM preferred)
  uri?: string,                  // External audio URL (for reference-based streaming)
  dataUri?: string,              // Data URI (base64 encoded, for small files)
  mimeType?: "audio/pcm",        // audio/pcm, audio/opus, audio/wav, audio/mp3
  duration?: 100,                // Duration in seconds (optional)
  audience?: "user,assistant",   // Target audience filter (comma-separated string)
  encryption?: string            // Encryption metadata (optional)
}
```

**Real-Time Pattern**: Send audio continuously for real-time processing
- **Chunk size**: 100-200ms for low latency (optimal balance)
- **Sample rate**: 16kHz (telephony), 24kHz (high quality), 48kHz (music)
- **Format**: PCM 16-bit signed (uncompressed, best compatibility)
- **Delivery methods**:
  - `data`: Raw bytes (efficient for streaming)
  - `uri`: External URL (for large files)
  - `dataUri`: Base64 encoded (for small files in JSON)

#### TranscriptContent (Real-Time Transcription)
**TypeSpec Reference**: `TranscriptContent` model in `typespec/messages.tsp`

```typescript
{
  kind: "transcript",
  text: "Hello, can you help me with my order?",  // Full transcript
  associatedContentId?: "audio_1",               // Links to AudioContent
  language?: "en",                               // ISO 639-1 code
  confidence?: 0.94,                             // 0.0-1.0 confidence score
  wordTimings?: [                                // Word-level timing (optional)
    { word: "Hello", start: 0.0, end: 0.5, confidence: 0.95 },
    { word: "can", start: 0.6, end: 0.8, confidence: 0.92 }
  ],
  speaker?: "user_123"                           // Speaker identification (optional)
}
```

**Key Distinction**: TranscriptContent is a visual aid for humans, NOT sent to LLM
- The agent processes AudioContent directly
- Transcript shown in UI for user readability (like video captions)
- Filter TranscriptContent when building LLM context
- Set `audience = "user"` attribute to hide from LLM

#### Streaming Events

**TypeSpec Reference**: Streaming events in `typespec/streaming.tsp`

Server-Sent Events (SSE) format for voice streaming:

```text
event: message.created
data: {"eventSeq":1,"messageId":"msg-1","runId":"run-1","message":{"messageId":"msg-1","role":"assistant","contents":[],"createdAt":"2026-02-07T10:00:00Z"},"createdAt":"2026-02-07T10:00:00Z"}

event: message.updated
data: {"eventSeq":2,"messageId":"msg-1","runId":"run-1","message":{"contents":[{"kind":"audio","data":"...base64...","mimeType":"audio/pcm"}]}}

event: message.updated
data: {"eventSeq":3,"messageId":"msg-1","runId":"run-1","message":{"contents":[{"kind":"transcript","text":"Hello, how can I help you?","language":"en","confidence":0.95}]}}

event: message.completed
data: {"eventSeq":4,"messageId":"msg-1","runId":"run-1","usage":{"inputTokens":150,"outputTokens":75,"totalTokens":225},"completedAt":"2026-02-07T10:00:02Z"}
```

**Event Types**:
- `MessageCreatedEvent`: Emitted when message creation starts
- `MessageUpdatedEvent`: Emitted for each audio/transcript chunk
- `MessageCompletedEvent`: Emitted when message is fully generated

## Implementation

### Step 1: Establish WebSocket Connection

#### Python Client

```python
import asyncio
import websockets
import json
import base64
import pyaudio

WEBSOCKET_URL = "wss://your-agent-runtime.azure.com/ws/voice"

async def connect_voice_agent():
    """Establish WebSocket connection for voice interaction."""
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        print("Connected to voice agent")

        # Start parallel tasks for send and receive
        send_task = asyncio.create_task(send_audio(websocket))
        receive_task = asyncio.create_task(receive_responses(websocket))

        # Wait for both tasks
        await asyncio.gather(send_task, receive_task)
```

#### JavaScript Client

```javascript
const WEBSOCKET_URL = "wss://your-agent-runtime.azure.com/ws/voice";

async function connectVoiceAgent() {
  const ws = new WebSocket(WEBSOCKET_URL);

  ws.onopen = () => {
    console.log("Connected to voice agent");
    startAudioStreaming(ws);
  };

  ws.onmessage = (event) => {
    const sseData = event.data;
    // Parse SSE format: "event: message.updated\ndata: {...}"
    const lines = sseData.split('\n');
    const eventType = lines[0].replace('event: ', '');
    const data = JSON.parse(lines[1].replace('data: ', ''));
    handleAgentResponse(eventType, data);
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log("Connection closed");
  };
}
```

### Step 2: Stream Audio Input

#### Python: Microphone Streaming

```python
import pyaudio
import numpy as np

# Audio configuration
SAMPLE_RATE = 16000  # 16kHz for voice
CHANNELS = 1         # Mono
CHUNK_SIZE = 3200    # 200ms chunks at 16kHz (3200 samples)

async def send_audio(websocket):
    """Capture microphone audio and stream to agent."""

    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    print("Starting audio capture...")
    sequence_number = 0

    try:
        while True:
            # Read audio chunk from microphone
            audio_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)

            # Create ChatMessage with AudioContent
            message = {
                "role": "user",
                "contents": [{
                    "kind": "audio",
                    "data": base64.b64encode(audio_data).decode('utf-8'),
                    "mimeType": "audio/pcm"
                }]
            }

            # Send to WebSocket
            await websocket.send(json.dumps(message))
            sequence_number += 1

            # Small delay to prevent overwhelming server
            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping audio capture...")

        # Connection closing signals end of input

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
```

#### JavaScript: Browser Microphone Streaming

```javascript
async function startAudioStreaming(ws) {
  // Request microphone access
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      sampleRate: 16000,
      echoCancellation: true,
      noiseSuppression: true
    }
  });

  // Create AudioContext for processing
  const audioContext = new AudioContext({ sampleRate: 16000 });
  const source = audioContext.createMediaStreamSource(stream);

  // Use ScriptProcessorNode for audio chunks (or AudioWorklet for production)
  const processor = audioContext.createScriptProcessor(4096, 1, 1);
  let sequenceNumber = 0;

  processor.onaudioprocess = (e) => {
    const inputData = e.inputBuffer.getChannelData(0);

    // Convert Float32Array to Int16Array (PCM 16-bit)
    const pcmData = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
      const s = Math.max(-1, Math.min(1, inputData[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Convert to base64
    const base64Audio = btoa(
      String.fromCharCode.apply(null, new Uint8Array(pcmData.buffer))
    );

    // Send ChatMessage with AudioContent
    const message = {
      role: "user",
      contents: [{
        kind: "audio",
        data: base64Audio,
        mimeType: "audio/pcm"
      }]
    };

    ws.send(JSON.stringify(message));
  };

  // Connect nodes
  source.connect(processor);
  processor.connect(audioContext.destination);

  console.log("Audio streaming started");
}
```

### Step 3: Receive and Process Agent Responses

#### Python: Response Handling

```python
import wave

async def receive_responses(websocket):
    """Receive and process agent responses."""

    # Initialize audio playback
    audio = pyaudio.PyAudio()
    playback_stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=24000,  # Agent may use 24kHz for higher quality
        output=True
    )

    # Buffer for accumulating content
    transcript_buffer = []
    text_buffer = []
    audio_buffer = []

    try:
        async for message in websocket:
            # Parse SSE format
            lines = message.split('\n')
            event_type = lines[0].replace('event: ', '').strip()
            event_data = json.loads(lines[1].replace('data: ', ''))

            # Handle different event types
            if event_type == "message.updated":
                # Extract contents from the event
                if "message" in event_data and "contents" in event_data["message"]:
                    for content in event_data["message"]["contents"]:

                        # TranscriptContent: Display transcription
                        if content["kind"] == "transcript":
                            transcript_text = content["text"]
                            print(f"[Transcript] {transcript_text}")

                        # TextContent: Display agent response
                        elif content["kind"] == "text":
                            text_chunk = content["text"]
                            text_buffer.append(text_chunk)
                            print(f"[Agent] {text_chunk}", end='', flush=True)

                        # AudioContent: Play agent voice response
                        elif content["kind"] == "audio":
                            audio_data = base64.b64decode(content["data"])
                            # Play audio immediately
                            playback_stream.write(audio_data)

            # Check for completion
            elif event_type == "message.completed":
                message_id = event_data.get("messageId")
                print(f"\n[Response complete: {message_id}]")
                text_buffer.clear()

    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed by server")
    finally:
        playback_stream.stop_stream()
        playback_stream.close()
        audio.terminate()
```

#### JavaScript: Response Handling

```javascript
let audioContext;
let audioQueue = [];
let isPlaying = false;

async function handleAgentResponse(eventType, eventData) {
  if (eventType === "message.updated" && eventData.message && eventData.message.contents) {
    for (const content of eventData.message.contents) {
      // Handle transcript
      if (content.kind === "transcript") {
        const transcriptEl = document.getElementById("transcript");
        transcriptEl.textContent += content.text + "\n";
      }

      // Handle text response
      else if (content.kind === "text") {
        const responseEl = document.getElementById("response");
        responseEl.textContent += content.text;
      }

      // Handle audio response
      else if (content.kind === "audio") {
        await playAudioChunk(content.data);
      }
    }
  }

  // Check for completion
  if (eventType === "message.completed") {
    console.log(`Response complete: ${eventData.messageId}`);
  }
}

async function playAudioChunk(base64Audio) {
  // Initialize AudioContext on first use
  if (!audioContext) {
    audioContext = new AudioContext({ sampleRate: 24000 });
  }

  // Decode base64 to ArrayBuffer
  const binaryString = atob(base64Audio);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  // Convert PCM Int16 to Float32
  const int16Array = new Int16Array(bytes.buffer);
  const float32Array = new Float32Array(int16Array.length);
  for (let i = 0; i < int16Array.length; i++) {
    float32Array[i] = int16Array[i] / 32768.0;
  }

  // Create AudioBuffer
  const audioBuffer = audioContext.createBuffer(1, float32Array.length, 24000);
  audioBuffer.getChannelData(0).set(float32Array);

  // Queue for playback
  audioQueue.push(audioBuffer);

  // Start playback if not already playing
  if (!isPlaying) {
    playNextChunk();
  }
}

function playNextChunk() {
  if (audioQueue.length === 0) {
    isPlaying = false;
    return;
  }

  isPlaying = true;
  const audioBuffer = audioQueue.shift();

  // Create source and play
  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);

  // Play next chunk when this one finishes
  source.onended = () => {
    playNextChunk();
  };

  source.start();
}
```

## Examples

### Example 1: Full-Duplex Voice Assistant

Complete implementation of a voice assistant with concurrent speech recognition and response generation.

**Python Implementation:**

```python
import asyncio
import websockets
import json
import base64
import pyaudio
from collections import deque

class VoiceAssistant:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 3200  # 200ms

        # Buffers
        self.is_speaking = False
        self.audio_playback_queue = deque()

    async def run(self):
        """Main voice assistant loop."""
        async with websockets.connect(self.websocket_url) as ws:
            # Run input and output tasks concurrently
            await asyncio.gather(
                self.capture_and_send_audio(ws),
                self.receive_and_play_audio(ws)
            )

    async def capture_and_send_audio(self, ws):
        """Capture microphone input and send to agent."""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        print("Listening... (Press Ctrl+C to stop)")
        sequence_number = 0

        try:
            while True:
                # Skip input if agent is speaking (prevent feedback)
                if self.is_speaking:
                    await asyncio.sleep(0.05)
                    continue

                # Capture audio
                audio_data = stream.read(self.chunk_size,
                                        exception_on_overflow=False)

                # Detect voice activity (simple energy-based VAD)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                energy = np.abs(audio_array).mean()

                # Only send if speech detected (threshold: 500)
                if energy > 500:
                    message = {
                        "role": "user",
                        "contents": [{
                            "kind": "audio",
                            "data": base64.b64encode(audio_data).decode(),
                            "mimeType": "audio/pcm"
                        }]
                    }

                    await ws.send(json.dumps(message))
                    sequence_number += 1
                    print(".", end="", flush=True)  # Activity indicator

                await asyncio.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            stream.stop_stream()
            stream.close()

    async def receive_and_play_audio(self, ws):
        """Receive agent responses and play audio."""
        playback_stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )

        try:
            async for message in ws:
                # Parse SSE format
                lines = message.split('\n')
                event_type = lines[0].replace('event: ', '').strip()

                if len(lines) < 2:
                    continue

                event_data = json.loads(lines[1].replace('data: ', ''))

                if event_type != "message.updated":
                    continue

                if "message" not in event_data or "contents" not in event_data["message"]:
                    continue

                for content in event_data["message"]["contents"]:
                    # Display transcript
                    if content["kind"] == "transcript":
                        print(f"\n[You] {content['text']}")

                    # Display agent text
                    elif content["kind"] == "text":
                        if not self.is_speaking:
                            print("\n[Agent] ", end="")
                            self.is_speaking = True
                        print(content["text"], end="", flush=True)

                    # Play agent audio
                    elif content["kind"] == "audio":
                        audio_data = base64.b64decode(content["data"])
                        playback_stream.write(audio_data)

        finally:
            playback_stream.stop_stream()
            playback_stream.close()

# Run voice assistant
async def main():
    assistant = VoiceAssistant("wss://your-agent.azure.com/ws/voice")
    await assistant.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Live Transcription with TranscriptContent Streaming

Real-time transcription service that streams partial transcription results.

**Python Implementation:**

```python
class LiveTranscriptionService:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.current_transcript = ""
        self.final_transcript = ""

    async def start_transcription(self, audio_file_path):
        """Transcribe audio file with live updates."""
        async with websockets.connect(self.websocket_url) as ws:
            # Start parallel tasks
            send_task = asyncio.create_task(
                self.send_audio_file(ws, audio_file_path)
            )
            receive_task = asyncio.create_task(
                self.receive_transcripts(ws)
            )

            await asyncio.gather(send_task, receive_task)

    async def send_audio_file(self, ws, audio_file_path):
        """Send audio file in chunks for transcription."""
        import wave

        with wave.open(audio_file_path, 'rb') as wav:
            sample_rate = wav.getframerate()
            chunk_size = int(sample_rate * 0.2)  # 200ms chunks
            sequence_number = 0

            while True:
                audio_data = wav.readframes(chunk_size)
                if not audio_data:
                    break

                is_final = wav.tell() >= wav.getnframes()

                message = {
                    "role": "user",
                    "contents": [{
                        "kind": "audio",
                        "data": base64.b64encode(audio_data).decode(),
                        "mimeType": "audio/pcm"
                    }]
                }

                await ws.send(json.dumps(message))
                sequence_number += 1

                # Simulate real-time streaming
                await asyncio.sleep(0.2)

    async def receive_transcripts(self, ws):
        """Receive and display streaming transcripts."""
        print("Transcription started...\n")

        async for message in ws:
            # Parse SSE format
            lines = message.split('\n')
            event_type = lines[0].replace('event: ', '').strip()

            if len(lines) < 2 or event_type != "message.updated":
                continue

            event_data = json.loads(lines[1].replace('data: ', ''))

            if "message" not in event_data or "contents" not in event_data["message"]:
                continue

            for content in event_data["message"]["contents"]:
                if content["kind"] == "transcript":
                    text = content["text"]
                    confidence = content.get("confidence", 0.0)

                    # Check if this is a final transcript (typically higher confidence)
                    is_final = confidence > 0.9

                    if is_final:
                        # Final transcript: Add to permanent record
                        self.final_transcript += text + " "
                        print(f"\n[FINAL] {text} (confidence: {confidence:.2f})")
                        self.current_transcript = ""
                    else:
                        # Partial transcript: Update display
                        self.current_transcript = text
                        print(f"\r[PARTIAL] {self.current_transcript}",
                              end="", flush=True)

        print(f"\n\nComplete Transcript:\n{self.final_transcript}")

# Run transcription
async def main():
    service = LiveTranscriptionService("wss://your-agent.azure.com/ws/voice")
    await service.start_transcription("meeting_recording.wav")

asyncio.run(main())
```

### Example 3: Voice Interruption Handling

Handle user interruptions gracefully by stopping agent playback and processing new input.

**Python Implementation:**

```python
class InterruptibleVoiceAgent:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.is_agent_speaking = False
        self.playback_queue = asyncio.Queue()
        self.interrupt_event = asyncio.Event()

    async def run(self):
        async with websockets.connect(self.websocket_url) as ws:
            await asyncio.gather(
                self.audio_input_handler(ws),
                self.audio_output_handler(),
                self.response_receiver(ws)
            )

    async def audio_input_handler(self, ws):
        """Monitor input and detect interruptions."""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=3200
        )

        sequence_number = 0
        silence_threshold = 500

        try:
            while True:
                audio_data = stream.read(3200, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                energy = np.abs(audio_array).mean()

                # Detect speech
                if energy > silence_threshold:
                    # User is speaking - check for interruption
                    if self.is_agent_speaking:
                        print("\n[INTERRUPT DETECTED]")
                        self.interrupt_event.set()

                        # Clear playback queue
                        while not self.playback_queue.empty():
                            try:
                                self.playback_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                break

                    # Send audio to agent
                    message = {
                        "role": "user",
                        "contents": [{
                            "kind": "audio",
                            "data": base64.b64encode(audio_data).decode(),
                            "mimeType": "audio/pcm"
                        }]
                    }

                    await ws.send(json.dumps(message))
                    sequence_number += 1

                await asyncio.sleep(0.01)

        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    async def audio_output_handler(self):
        """Play audio from queue with interruption support."""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )

        try:
            while True:
                # Wait for audio chunk
                audio_data = await self.playback_queue.get()

                # Check for interruption before playing
                if self.interrupt_event.is_set():
                    print("[Skipping playback due to interruption]")
                    self.interrupt_event.clear()
                    continue

                # Play audio chunk
                stream.write(audio_data)

        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    async def response_receiver(self, ws):
        """Receive agent responses and queue audio."""
        async for message in ws:
            # Parse SSE format
            lines = message.split('\n')
            event_type = lines[0].replace('event: ', '').strip()

            if len(lines) < 2 or event_type != "message.updated":
                continue

            event_data = json.loads(lines[1].replace('data: ', ''))

            if "message" not in event_data or "contents" not in event_data["message"]:
                continue

            for content in event_data["message"]["contents"]:
                if content["kind"] == "audio":
                    self.is_agent_speaking = True
                    audio_data = base64.b64decode(content["data"])

                    # Queue audio for playback
                    await self.playback_queue.put(audio_data)

            # Check for completion
            if event_type == "message.completed":
                self.is_agent_speaking = False
                print("\n[Agent finished speaking]")

# Run interruptible agent
async def main():
    agent = InterruptibleVoiceAgent("wss://your-agent.azure.com/ws/voice")
    await agent.run()

asyncio.run(main())
```

### Example 4: Multi-Language Voice Support

Automatic language detection and multi-language transcription.

**Python Implementation:**

```python
class MultiLanguageVoiceAgent:
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ar': 'Arabic'
    }

    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.detected_language = None

    async def run(self):
        async with websockets.connect(self.websocket_url) as ws:
            await asyncio.gather(
                self.send_audio(ws),
                self.receive_responses(ws)
            )

    async def receive_responses(self, ws):
        """Receive responses with language detection."""
        async for message in ws:
            # Parse SSE format
            lines = message.split('\n')
            event_type = lines[0].replace('event: ', '').strip()

            if len(lines) < 2 or event_type != "message.updated":
                continue

            event_data = json.loads(lines[1].replace('data: ', ''))

            if "message" not in event_data or "contents" not in event_data["message"]:
                continue

            for content in event_data["message"]["contents"]:
                if content["kind"] == "transcript":
                    # Extract language from transcript
                    language = content.get("language", "en")

                    # Detect language change
                    if language != self.detected_language:
                        self.detected_language = language
                        lang_name = self.SUPPORTED_LANGUAGES.get(
                            language, language
                        )
                        print(f"\n[Language detected: {lang_name}]")

                    # Display transcript with language tag
                    text = content["text"]
                    confidence = content.get("confidence", 0.0)
                    is_final = confidence > 0.9

                    print(f"[{language.upper()}] {text}", end="")
                    if is_final:
                        print()

                elif content["kind"] == "text":
                    # Agent response (may be in detected language)
                    print(f"\n[Agent] {content['text']}", end="", flush=True)

# Run multi-language agent
async def main():
    agent = MultiLanguageVoiceAgent("wss://your-agent.azure.com/ws/voice")
    await agent.run()

asyncio.run(main())
```

### Example 5: Adaptive Audio Quality with Network Monitoring

Monitor network conditions and adapt audio quality dynamically.

**Python Implementation:**

```python
class AdaptiveQualityVoiceAgent:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url

        # Quality presets
        self.quality_presets = {
            'low': {
                'sample_rate': 8000,
                'chunk_size': 1600,  # 200ms at 8kHz
                'bitrate': '8kbps'
            },
            'medium': {
                'sample_rate': 16000,
                'chunk_size': 3200,  # 200ms at 16kHz
                'bitrate': '16kbps'
            },
            'high': {
                'sample_rate': 24000,
                'chunk_size': 4800,  # 200ms at 24kHz
                'bitrate': '24kbps'
            }
        }

        self.current_quality = 'medium'
        self.latency_samples = []

    async def run(self):
        async with websockets.connect(self.websocket_url) as ws:
            await asyncio.gather(
                self.send_audio_adaptive(ws),
                self.receive_and_monitor(ws)
            )

    async def send_audio_adaptive(self, ws):
        """Send audio with adaptive quality based on network."""
        audio = pyaudio.PyAudio()

        while True:
            # Get current quality settings
            preset = self.quality_presets[self.current_quality]
            sample_rate = preset['sample_rate']
            chunk_size = preset['chunk_size']

            # Open stream with current quality
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )

            print(f"[Quality: {self.current_quality} - "
                  f"{sample_rate}Hz - {preset['bitrate']}]")

            sequence_number = 0

            # Stream until quality change needed
            while True:
                audio_data = stream.read(chunk_size,
                                        exception_on_overflow=False)

                message = {
                    "role": "user",
                    "contents": [{
                        "kind": "audio",
                        "data": base64.b64encode(audio_data).decode(),
                        "mimeType": "audio/pcm",
                        "additionalProperties": {
                            "sampleRate": sample_rate,
                            "quality": self.current_quality
                        }
                    }]
                }

                send_time = asyncio.get_event_loop().time()
                await ws.send(json.dumps(message))

                # Track send time for latency calculation
                self.latency_samples.append(send_time)

                sequence_number += 1
                await asyncio.sleep(0.01)

                # Check if quality adjustment needed
                # (in real implementation, this would be event-driven)
                if len(self.latency_samples) > 50:
                    break

            stream.stop_stream()
            stream.close()

    async def receive_and_monitor(self, ws):
        """Receive responses and monitor network performance."""
        async for message in ws:
            receive_time = asyncio.get_event_loop().time()

            # Parse SSE format
            lines = message.split('\n')
            event_type = lines[0].replace('event: ', '').strip()

            if len(lines) < 2:
                continue

            # Calculate round-trip latency
            if self.latency_samples:
                send_time = self.latency_samples.pop(0)
                latency = (receive_time - send_time) * 1000  # ms

                # Adjust quality based on latency
                await self.adjust_quality(latency)

            # Handle content normally
            if event_type == "message.updated":
                event_data = json.loads(lines[1].replace('data: ', ''))
                if "message" in event_data and "contents" in event_data["message"]:
                    for content in event_data["message"]["contents"]:
                        if content["kind"] == "text":
                            print(content["text"], end="", flush=True)

    async def adjust_quality(self, latency_ms):
        """Adjust audio quality based on measured latency."""
        # Quality thresholds
        if latency_ms > 500:  # High latency
            if self.current_quality != 'low':
                self.current_quality = 'low'
                print(f"\n[Reducing quality due to latency: {latency_ms:.0f}ms]")
        elif latency_ms > 200:  # Medium latency
            if self.current_quality == 'high':
                self.current_quality = 'medium'
                print(f"\n[Adjusting to medium quality: {latency_ms:.0f}ms]")
        else:  # Low latency
            if self.current_quality != 'high':
                self.current_quality = 'high'
                print(f"\n[Increasing to high quality: {latency_ms:.0f}ms]")

# Run adaptive quality agent
async def main():
    agent = AdaptiveQualityVoiceAgent("wss://your-agent.azure.com/ws/voice")
    await agent.run()

asyncio.run(main())
```

## Troubleshooting

### Issue: High Latency in Voice Responses

**Symptoms**: Delays > 1 second between user speech and agent response

**Solutions**:

1. **Reduce audio chunk size**: Use 100ms chunks instead of 200ms
   ```python
   chunk_size = int(sample_rate * 0.1)  # 100ms
   ```

2. **Enable streaming transcription**: Don't wait for final transcript
   ```python
   # Process partial transcripts immediately
   if content["kind"] == "transcript":
       process_partial_transcript(content["text"])
   ```

3. **Use lower sample rate**: 16kHz instead of 24kHz for faster processing
   ```python
   sample_rate = 16000  # Adequate for speech
   ```

4. **Optimize buffer sizes**: Reduce buffering at all stages
   ```python
   frames_per_buffer=1600  # Smaller buffer = lower latency
   ```

### Issue: Audio Choppy or Distorted

**Symptoms**: Crackling, skipping, or garbled audio playback

**Solutions**:

1. **Increase playback buffer**: Queue more chunks before playing
   ```python
   # Wait for initial buffer before playback
   while audioQueue.length < 3:
       await asyncio.sleep(0.01)
   playNextChunk()
   ```

2. **Check sample rate mismatch**: Ensure input/output rates match
   ```python
   # Input and output must use same sample rate
   input_rate = 16000
   output_rate = 16000  # Match!
   ```

3. **Handle underrun**: Detect and recover from buffer underruns
   ```python
   try:
       playback_stream.write(audio_data)
   except IOError as e:
       if e.errno == pyaudio.paOutputUnderflowed:
           print("[Buffer underrun - recovering]")
           # Insert silence to recover
           silence = b'\x00' * len(audio_data)
           playback_stream.write(silence)
   ```

### Issue: WebSocket Connection Drops

**Symptoms**: Connection closes unexpectedly during conversation

**Solutions**:

1. **Implement reconnection logic**: Auto-reconnect on disconnect
   ```python
   async def run_with_reconnection(self):
       while True:
           try:
               await self.run()
           except websockets.exceptions.ConnectionClosed:
               print("[Reconnecting in 5 seconds...]")
               await asyncio.sleep(5)
   ```

2. **Send keepalive pings**: Prevent idle timeout
   ```python
   async def send_keepalive(ws):
       while True:
           await asyncio.sleep(30)
           await ws.ping()
   ```

3. **Handle backpressure**: Don't send faster than server can process
   ```python
   # Rate limit sending
   async def send_with_rate_limit(ws, message):
       await ws.send(message)
       await asyncio.sleep(0.02)  # 50 msgs/sec max
   ```

### Issue: Transcript Quality Poor

**Symptoms**: Low confidence scores, incorrect words, missing speech

**Solutions**:

1. **Enable noise suppression**: Use audio preprocessing
   ```javascript
   // Browser: Enable built-in processing
   audio: {
       echoCancellation: true,
       noiseSuppression: true,
       autoGainControl: true
   }
   ```

2. **Improve microphone quality**: Use external microphone
   ```python
   # List available input devices
   for i in range(audio.get_device_count()):
       info = audio.get_device_info_by_index(i)
       if info['maxInputChannels'] > 0:
           print(f"{i}: {info['name']}")
   ```

3. **Adjust VAD threshold**: Tune voice activity detection
   ```python
   # Lower threshold for quiet speakers
   silence_threshold = 300  # Default: 500

   # Higher threshold for noisy environments
   silence_threshold = 800
   ```

### Issue: Interruptions Not Working

**Symptoms**: Agent continues speaking when user interrupts

**Solutions**:

1. **Implement interrupt detection**: Monitor input during playback
   ```python
   # Detect speech energy during agent playback
   if energy > interrupt_threshold and self.is_agent_speaking:
       self.interrupt_event.set()
   ```

2. **Clear playback queue immediately**: Stop queued audio
   ```python
   # Clear queue on interrupt
   while not self.playback_queue.empty():
       self.playback_queue.get_nowait()
   ```

3. **Send interrupt signal to server**: Notify server of interruption
   ```python
   interrupt_message = {
       "role": "user",
       "contents": [{
           "kind": "event",
           "name": "user_interrupt",
           "text": "User interrupted agent"
       }]
   }
   await ws.send(json.dumps(interrupt_message))
   ```

### Issue: Memory Usage Increasing

**Symptoms**: Memory grows over time during long conversations

**Solutions**:

1. **Limit buffer sizes**: Cap maximum buffered chunks
   ```python
   MAX_BUFFER_SIZE = 100

   if len(audio_buffer) > MAX_BUFFER_SIZE:
       audio_buffer.pop(0)  # Remove oldest
   ```

2. **Clear completed messages**: Remove old conversation history
   ```python
   # Keep only last N messages
   MAX_MESSAGES = 50
   if len(conversation_history) > MAX_MESSAGES:
       conversation_history = conversation_history[-MAX_MESSAGES:]
   ```

3. **Stream to disk for long recordings**: Don't hold in memory
   ```python
   # Write to temp file instead of memory buffer
   import tempfile
   with tempfile.NamedTemporaryFile(suffix='.wav') as f:
       # Write chunks to file
       f.write(audio_data)
   ```

## Best Practices

### Audio Quality

- **Use PCM format**: Uncompressed PCM for best compatibility
- **Sample rate**: 16kHz for voice, 24kHz for higher quality, 48kHz for music
- **Chunk size**: 100-200ms for optimal latency/quality balance
- **Mono audio**: Use single channel for speech (stereo adds overhead)

### Network Efficiency

- **Compress long silence**: Skip sending silent audio chunks
- **Batch small chunks**: Combine very small chunks before sending
- **Monitor bandwidth**: Adapt quality to available bandwidth
- **Use binary WebSocket frames**: More efficient than JSON for large audio

### User Experience

- **Show visual feedback**: Display "listening" or "speaking" indicators
- **Progressive transcription**: Show partial transcripts in real-time
- **Graceful degradation**: Fall back to text if audio fails
- **Clear error messages**: Explain audio issues to users

### Error Handling

- **Retry on failure**: Auto-reconnect with exponential backoff
- **Validate audio format**: Check sample rate, channels, format before sending
- **Handle partial responses**: Gracefully handle incomplete audio streams
- **Timeout detection**: Detect and recover from stalled connections

## Performance Benchmarks

### Latency Targets

| Component | Target | Acceptable | Poor |
|-----------|--------|------------|------|
| Audio Capture | < 50ms | < 100ms | > 200ms |
| Network Transfer | < 50ms | < 150ms | > 300ms |
| Speech-to-Text | < 200ms | < 500ms | > 1000ms |
| LLM Processing | < 500ms | < 1500ms | > 3000ms |
| Text-to-Speech | < 200ms | < 500ms | > 1000ms |
| **Total E2E** | **< 1000ms** | **< 2500ms** | **> 5000ms** |

### Bandwidth Requirements

| Quality | Sample Rate | Bitrate (PCM) | Compressed (Opus) |
|---------|-------------|---------------|-------------------|
| Low | 8 kHz | 128 kbps | 8-12 kbps |
| Medium | 16 kHz | 256 kbps | 16-24 kbps |
| High | 24 kHz | 384 kbps | 24-40 kbps |
| Studio | 48 kHz | 768 kbps | 64-128 kbps |

*Note: Add ~33% overhead for base64 encoding in JSON*

## References

### TypeSpec Definitions

- **AudioContent**: `typespec/messages.tsp` - Line 675 (Audio content model)
- **TranscriptContent**: `typespec/messages.tsp` - Line 734 (Transcript content model)
- **MessageCreatedEvent**: `typespec/streaming.tsp` - Line 39 (Message created event)
- **MessageUpdatedEvent**: `typespec/streaming.tsp` - Line 60 (Message updated event)
- **MessageCompletedEvent**: `typespec/streaming.tsp` - Line 93 (Message completed event)

### Related Documentation

- [Streaming Specification](../specifications/streaming.md) - Streaming patterns and protocols
- [Content Encryption](../specifications/content-encryption.md) - Encrypting audio content for HIPAA compliance
- [Message Lifecycle](../specifications/message-lifecycle.md) - Message state transitions

### External Resources

- [WebRTC Audio Processing](https://webrtc.github.io/webrtc-org/architecture/) - Browser audio APIs
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/) - Python audio library
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) - Voice assistant patterns
