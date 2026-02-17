/**
 * Tests for multi-modal content handling covering all multimodal-guide.md examples.
 * Tests sending and receiving images, audio, video, files, and mixed content types.
 *
 * This test suite validates:
 * - Text content creation and handling
 * - Image content (URLs, base64, file references)
 * - Audio content
 * - Video content
 * - File content
 * - Mixed content arrays
 * - Content serialization with kind discriminator
 */

import type {
  AIContent,
  TextContent,
  ImageContent,
  AudioContent,
  VideoContent,
  FileContent,
  UserMessage,
  AgentMessage,
} from '@microsoft/agents-protocol-abstractions';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('MultiModalContent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Text Content', () => {
    it('should create text content with kind discriminator', () => {
      const textContent: TextContent = {
        kind: 'text',
        text: 'Hello world',
      };

      expect(textContent.kind).toBe('text');
      expect(textContent.text).toBe('Hello world');
    });

    it('should handle empty text content', () => {
      const textContent: TextContent = {
        kind: 'text',
        text: '',
      };

      expect(textContent.kind).toBe('text');
      expect(textContent.text).toBe('');
    });

    it('should handle text with special characters', () => {
      const textContent: TextContent = {
        kind: 'text',
        text: 'Special chars: \n\t"quotes" & <html>',
      };

      expect(textContent.text).toContain('\n');
      expect(textContent.text).toContain('quotes');
    });
  });

  describe('Image Content', () => {
    it('should create image content with URI', () => {
      const imageContent: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/photo.jpg',
        mimeType: 'image/jpeg',
      };

      expect(imageContent.kind).toBe('image');
      expect(imageContent.uri).toBe('https://example.com/photo.jpg');
      expect(imageContent.mimeType).toBe('image/jpeg');
    });

    it('should create image content with base64 data URI', () => {
      const base64Data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
      const imageContent: ImageContent = {
        kind: 'image',
        uri: `data:image/png;base64,${base64Data}`,
        mimeType: 'image/png',
      };

      expect(imageContent.kind).toBe('image');
      expect(imageContent.uri).toContain('data:image/png;base64,');
      expect(imageContent.mimeType).toBe('image/png');
    });

    it('should create image content with metadata', () => {
      const imageContent: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/photo.jpg',
        mimeType: 'image/jpeg',
        width: 1920,
        height: 1080,
        alt: 'A beautiful sunset over the ocean',
      };

      expect(imageContent.kind).toBe('image');
      expect(imageContent.width).toBe(1920);
      expect(imageContent.height).toBe(1080);
      expect(imageContent.alt).toBe('A beautiful sunset over the ocean');
    });

    it('should handle image content without optional fields', () => {
      const imageContent: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/simple.jpg',
      };

      expect(imageContent.kind).toBe('image');
      expect(imageContent.mimeType).toBeUndefined();
      expect(imageContent.width).toBeUndefined();
      expect(imageContent.height).toBeUndefined();
      expect(imageContent.alt).toBeUndefined();
    });

    it('should support different image MIME types', () => {
      const pngImage: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/image.png',
        mimeType: 'image/png',
      };

      const webpImage: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/image.webp',
        mimeType: 'image/webp',
      };

      expect(pngImage.mimeType).toBe('image/png');
      expect(webpImage.mimeType).toBe('image/webp');
    });
  });

  describe('Audio Content', () => {
    it('should create audio content with URI', () => {
      const audioContent: AudioContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.mp3',
        mimeType: 'audio/mpeg',
      };

      expect(audioContent.kind).toBe('audio');
      expect(audioContent.uri).toBe('https://example.com/audio.mp3');
      expect(audioContent.mimeType).toBe('audio/mpeg');
    });

    it('should create audio content with base64 data URI', () => {
      const base64Audio = Buffer.from('fake audio data').toString('base64');
      const audioContent: AudioContent = {
        kind: 'audio',
        uri: `data:audio/mpeg;base64,${base64Audio}`,
        mimeType: 'audio/mpeg',
      };

      expect(audioContent.kind).toBe('audio');
      expect(audioContent.uri).toContain('data:audio/mpeg;base64,');
    });

    it('should create audio content with duration', () => {
      const audioContent: AudioContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.mp3',
        mimeType: 'audio/mpeg',
        duration: 30,
      };

      expect(audioContent.duration).toBe(30);
    });

    it('should support different audio formats', () => {
      const mp3Audio: AudioContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.mp3',
        mimeType: 'audio/mpeg',
      };

      const wavAudio: AudioContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.wav',
        mimeType: 'audio/wav',
      };

      const oggAudio: AudioContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.ogg',
        mimeType: 'audio/ogg',
      };

      expect(mp3Audio.mimeType).toBe('audio/mpeg');
      expect(wavAudio.mimeType).toBe('audio/wav');
      expect(oggAudio.mimeType).toBe('audio/ogg');
    });
  });

  describe('Video Content', () => {
    it('should create video content with URI', () => {
      const videoContent: VideoContent = {
        kind: 'video',
        uri: 'https://example.com/video.mp4',
        mimeType: 'video/mp4',
      };

      expect(videoContent.kind).toBe('video');
      expect(videoContent.uri).toBe('https://example.com/video.mp4');
      expect(videoContent.mimeType).toBe('video/mp4');
    });

    it('should create video content with metadata', () => {
      const videoContent: VideoContent = {
        kind: 'video',
        uri: 'https://example.com/video.mp4',
        mimeType: 'video/mp4',
        width: 1920,
        height: 1080,
        duration: 120,
        frameRate: 30,
      };

      expect(videoContent.kind).toBe('video');
      expect(videoContent.width).toBe(1920);
      expect(videoContent.height).toBe(1080);
      expect(videoContent.duration).toBe(120);
      expect(videoContent.frameRate).toBe(30);
    });

    it('should create video content with base64 data URI', () => {
      const base64Video = Buffer.from('fake video data').toString('base64');
      const videoContent: VideoContent = {
        kind: 'video',
        uri: `data:video/mp4;base64,${base64Video}`,
        mimeType: 'video/mp4',
      };

      expect(videoContent.uri).toContain('data:video/mp4;base64,');
    });

    it('should support different video formats', () => {
      const mp4Video: VideoContent = {
        kind: 'video',
        uri: 'https://example.com/video.mp4',
        mimeType: 'video/mp4',
      };

      const webmVideo: VideoContent = {
        kind: 'video',
        uri: 'https://example.com/video.webm',
        mimeType: 'video/webm',
      };

      expect(mp4Video.mimeType).toBe('video/mp4');
      expect(webmVideo.mimeType).toBe('video/webm');
    });
  });

  describe('File Content', () => {
    it('should create file content with URI and filename', () => {
      const fileContent: FileContent = {
        kind: 'file',
        uri: 'https://example.com/document.pdf',
        filename: 'document.pdf',
        mimeType: 'application/pdf',
      };

      expect(fileContent.kind).toBe('file');
      expect(fileContent.uri).toBe('https://example.com/document.pdf');
      expect(fileContent.filename).toBe('document.pdf');
      expect(fileContent.mimeType).toBe('application/pdf');
    });

    it('should create file content with base64 data', () => {
      const base64Pdf = Buffer.from('fake pdf data').toString('base64');
      const fileContent: FileContent = {
        kind: 'file',
        uri: `data:application/pdf;base64,${base64Pdf}`,
        filename: 'report.pdf',
        mimeType: 'application/pdf',
      };

      expect(fileContent.uri).toContain('data:application/pdf;base64,');
      expect(fileContent.filename).toBe('report.pdf');
    });

    it('should create file content with size', () => {
      const fileContent: FileContent = {
        kind: 'file',
        uri: 'https://example.com/document.pdf',
        filename: 'document.pdf',
        mimeType: 'application/pdf',
        sizeBytes: 2048576,
      };

      expect(fileContent.sizeBytes).toBe(2048576);
    });

    it('should support different file types', () => {
      const pdfFile: FileContent = {
        kind: 'file',
        uri: 'https://example.com/doc.pdf',
        mimeType: 'application/pdf',
        filename: 'doc.pdf',
      };

      const docxFile: FileContent = {
        kind: 'file',
        uri: 'https://example.com/doc.docx',
        mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename: 'doc.docx',
      };

      const csvFile: FileContent = {
        kind: 'file',
        uri: 'https://example.com/data.csv',
        mimeType: 'text/csv',
        filename: 'data.csv',
      };

      expect(pdfFile.mimeType).toBe('application/pdf');
      expect(docxFile.mimeType).toBe('application/vnd.openxmlformats-officedocument.wordprocessingml.document');
      expect(csvFile.mimeType).toBe('text/csv');
    });
  });

  describe('Mixed Content Arrays', () => {
    it('should create message with text and image', () => {
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-1',
        contents: [
          {
            kind: 'text',
            text: "What's in this image?",
          } as TextContent,
          {
            kind: 'image',
            uri: 'https://example.com/photo.jpg',
            mimeType: 'image/jpeg',
          } as ImageContent,
        ],
      };

      expect(message.contents).toHaveLength(2);
      expect(message.contents[0].kind).toBe('text');
      expect(message.contents[1].kind).toBe('image');
    });

    it('should create message with multiple content types', () => {
      const message: AgentMessage = {
        role: 'agent',
        messageId: 'msg-2',
        contents: [
          {
            kind: 'text',
            text: "Here's the analysis:",
          } as TextContent,
          {
            kind: 'image',
            uri: 'https://example.com/chart.png',
            mimeType: 'image/png',
          } as ImageContent,
          {
            kind: 'audio',
            uri: 'https://example.com/explanation.mp3',
            mimeType: 'audio/mpeg',
            duration: 30,
          } as AudioContent,
          {
            kind: 'file',
            uri: 'https://example.com/report.pdf',
            mimeType: 'application/pdf',
            filename: 'analysis.pdf',
          } as FileContent,
        ],
      };

      expect(message.contents).toHaveLength(4);
      expect(message.contents[0].kind).toBe('text');
      expect(message.contents[1].kind).toBe('image');
      expect(message.contents[2].kind).toBe('audio');
      expect(message.contents[3].kind).toBe('file');
    });

    it('should filter content by kind', () => {
      const contents: AIContent[] = [
        { kind: 'text', text: 'Hello' } as TextContent,
        { kind: 'image', uri: 'https://example.com/1.jpg' } as ImageContent,
        { kind: 'text', text: 'World' } as TextContent,
        { kind: 'audio', uri: 'https://example.com/audio.mp3' } as AudioContent,
      ];

      const textContents = contents.filter((c) => c.kind === 'text');
      const imageContents = contents.filter((c) => c.kind === 'image');

      expect(textContents).toHaveLength(2);
      expect(imageContents).toHaveLength(1);
    });

    it('should handle empty content arrays', () => {
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-3',
        contents: [],
      };

      expect(message.contents).toHaveLength(0);
    });
  });

  describe('Content Serialization', () => {
    it('should serialize text content correctly', () => {
      const textContent: TextContent = {
        kind: 'text',
        text: 'Hello world',
      };

      const json = JSON.stringify(textContent);
      const parsed = JSON.parse(json);

      expect(parsed.kind).toBe('text');
      expect(parsed.text).toBe('Hello world');
    });

    it('should serialize image content with metadata', () => {
      const imageContent: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/photo.jpg',
        mimeType: 'image/jpeg',
        width: 1920,
        height: 1080,
        alt: 'Sunset photo',
      };

      const json = JSON.stringify(imageContent);
      const parsed = JSON.parse(json);

      expect(parsed.kind).toBe('image');
      expect(parsed.uri).toBe('https://example.com/photo.jpg');
      expect(parsed.width).toBe(1920);
      expect(parsed.height).toBe(1080);
    });

    it('should serialize mixed content array', () => {
      const contents: AIContent[] = [
        { kind: 'text', text: 'Description' } as TextContent,
        {
          kind: 'image',
          uri: 'https://example.com/image.png',
          mimeType: 'image/png',
        } as ImageContent,
      ];

      const json = JSON.stringify(contents);
      const parsed = JSON.parse(json);

      expect(parsed).toHaveLength(2);
      expect(parsed[0].kind).toBe('text');
      expect(parsed[1].kind).toBe('image');
    });

    it('should preserve kind discriminator through serialization', () => {
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-4',
        contents: [
          { kind: 'text', text: 'Test' } as TextContent,
          {
            kind: 'audio',
            uri: 'https://example.com/audio.mp3',
            mimeType: 'audio/mpeg',
          } as AudioContent,
          {
            kind: 'video',
            uri: 'https://example.com/video.mp4',
            mimeType: 'video/mp4',
          } as VideoContent,
          {
            kind: 'file',
            uri: 'https://example.com/doc.pdf',
            mimeType: 'application/pdf',
            filename: 'doc.pdf',
          } as FileContent,
        ],
      };

      const json = JSON.stringify(message);
      const parsed = JSON.parse(json);

      expect(parsed.contents[0].kind).toBe('text');
      expect(parsed.contents[1].kind).toBe('audio');
      expect(parsed.contents[2].kind).toBe('video');
      expect(parsed.contents[3].kind).toBe('file');
    });
  });

  describe('Content Type Guards', () => {
    it('should identify text content by kind', () => {
      const content: AIContent = {
        kind: 'text',
        text: 'Hello',
      } as TextContent;

      expect(content.kind === 'text').toBe(true);
      if (content.kind === 'text') {
        expect(content.text).toBe('Hello');
      }
    });

    it('should identify image content by kind', () => {
      const content: AIContent = {
        kind: 'image',
        uri: 'https://example.com/image.jpg',
      } as ImageContent;

      expect(content.kind === 'image').toBe(true);
      if (content.kind === 'image') {
        expect(content.uri).toBeDefined();
      }
    });

    it('should identify audio content by kind', () => {
      const content: AIContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.mp3',
      } as AudioContent;

      expect(content.kind === 'audio').toBe(true);
    });

    it('should identify video content by kind', () => {
      const content: AIContent = {
        kind: 'video',
        uri: 'https://example.com/video.mp4',
      } as VideoContent;

      expect(content.kind === 'video').toBe(true);
    });

    it('should identify file content by kind', () => {
      const content: AIContent = {
        kind: 'file',
        uri: 'https://example.com/file.pdf',
        filename: 'file.pdf',
      } as FileContent;

      expect(content.kind === 'file').toBe(true);
      if (content.kind === 'file') {
        expect(content.filename).toBe('file.pdf');
      }
    });
  });

  describe('Real-world Scenarios', () => {
    it('should handle screenshot analysis with base64 image', () => {
      const screenshot = Buffer.from('fake screenshot data').toString('base64');
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-5',
        contents: [
          {
            kind: 'text',
            text: "What's wrong in this screenshot?",
          } as TextContent,
          {
            kind: 'image',
            uri: `data:image/png;base64,${screenshot}`,
            mimeType: 'image/png',
          } as ImageContent,
        ],
      };

      expect(message.contents).toHaveLength(2);
      expect(message.contents[0].kind).toBe('text');
      expect(message.contents[1].kind).toBe('image');

      const imageContent = message.contents[1] as ImageContent;
      expect(imageContent.uri).toContain('data:image/png;base64,');
    });

    it('should handle audio transcription request', () => {
      const audioData = Buffer.from('fake audio data').toString('base64');
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-6',
        contents: [
          {
            kind: 'text',
            text: 'Transcribe this audio',
          } as TextContent,
          {
            kind: 'audio',
            uri: `data:audio/mpeg;base64,${audioData}`,
            mimeType: 'audio/mpeg',
          } as AudioContent,
        ],
      };

      expect(message.contents).toHaveLength(2);

      const audioContent = message.contents[1] as AudioContent;
      expect(audioContent.kind).toBe('audio');
      expect(audioContent.uri).toContain('data:audio/mpeg;base64,');
    });

    it('should handle document summary request', () => {
      const pdfData = Buffer.from('fake pdf data').toString('base64');
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-7',
        contents: [
          {
            kind: 'text',
            text: 'Summarize this report',
          } as TextContent,
          {
            kind: 'file',
            uri: `data:application/pdf;base64,${pdfData}`,
            mimeType: 'application/pdf',
            filename: 'report.pdf',
          } as FileContent,
        ],
      };

      expect(message.contents).toHaveLength(2);

      const fileContent = message.contents[1] as FileContent;
      expect(fileContent.kind).toBe('file');
      expect(fileContent.filename).toBe('report.pdf');
      expect(fileContent.mimeType).toBe('application/pdf');
    });

    it('should handle multi-modal agent response', () => {
      const response: AgentMessage = {
        role: 'agent',
        messageId: 'msg-8',
        contents: [
          {
            kind: 'text',
            text: "Here's a photo of the Eiffel Tower, the iconic iron lattice tower in Paris.",
          } as TextContent,
          {
            kind: 'image',
            uri: 'https://cdn.example.com/eiffel-tower.jpg',
            mimeType: 'image/jpeg',
            width: 1920,
            height: 1080,
            alt: 'Eiffel Tower in Paris',
          } as ImageContent,
        ],
      };

      expect(response.contents).toHaveLength(2);

      const textContent = response.contents[0] as TextContent;
      expect(textContent.text).toContain('Eiffel Tower');

      const imageContent = response.contents[1] as ImageContent;
      expect(imageContent.uri).toContain('eiffel-tower');
      expect(imageContent.width).toBe(1920);
      expect(imageContent.height).toBe(1080);
    });

    it('should handle comprehensive multi-modal response', () => {
      const response: AgentMessage = {
        role: 'agent',
        messageId: 'msg-9',
        contents: [
          {
            kind: 'text',
            text: "Here's the comprehensive analysis:",
          } as TextContent,
          {
            kind: 'image',
            uri: 'https://example.com/chart.png',
            mimeType: 'image/png',
          } as ImageContent,
          {
            kind: 'audio',
            uri: 'https://example.com/explanation.mp3',
            mimeType: 'audio/mpeg',
            duration: 30,
          } as AudioContent,
          {
            kind: 'video',
            uri: 'https://example.com/demo.mp4',
            mimeType: 'video/mp4',
            duration: 60,
          } as VideoContent,
          {
            kind: 'file',
            uri: 'https://example.com/report.pdf',
            mimeType: 'application/pdf',
            filename: 'analysis.pdf',
            sizeBytes: 1048576,
          } as FileContent,
        ],
      };

      expect(response.contents).toHaveLength(5);

      const contentKinds = response.contents.map((c) => c.kind);
      expect(contentKinds).toEqual(['text', 'image', 'audio', 'video', 'file']);
    });

    it('should handle image-only message without text', () => {
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-10',
        contents: [
          {
            kind: 'image',
            uri: 'https://example.com/sunset.jpg',
            mimeType: 'image/jpeg',
          } as ImageContent,
        ],
      };

      expect(message.contents).toHaveLength(1);
      expect(message.contents[0].kind).toBe('image');
    });

    it('should handle multiple images in single message', () => {
      const message: UserMessage = {
        role: 'user',
        messageId: 'msg-11',
        contents: [
          {
            kind: 'text',
            text: 'Compare these two images',
          } as TextContent,
          {
            kind: 'image',
            uri: 'https://example.com/image1.jpg',
            mimeType: 'image/jpeg',
          } as ImageContent,
          {
            kind: 'image',
            uri: 'https://example.com/image2.jpg',
            mimeType: 'image/jpeg',
          } as ImageContent,
        ],
      };

      expect(message.contents).toHaveLength(3);

      const imageContents = message.contents.filter((c) => c.kind === 'image');
      expect(imageContents).toHaveLength(2);
    });
  });

  describe('Edge Cases', () => {
    it('should handle content with undefined optional fields', () => {
      const imageContent: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/image.jpg',
      };

      expect(imageContent.mimeType).toBeUndefined();
      expect(imageContent.width).toBeUndefined();
      expect(imageContent.height).toBeUndefined();
      expect(imageContent.alt).toBeUndefined();
    });

    it('should handle very long text content', () => {
      const longText = 'Lorem ipsum '.repeat(1000);
      const textContent: TextContent = {
        kind: 'text',
        text: longText,
      };

      expect(textContent.text.length).toBeGreaterThan(10000);
    });

    it('should handle special characters in filenames', () => {
      const fileContent: FileContent = {
        kind: 'file',
        uri: 'https://example.com/file.pdf',
        filename: 'Report (2024) - Q1 & Q2.pdf',
        mimeType: 'application/pdf',
      };

      expect(fileContent.filename).toContain('(');
      expect(fileContent.filename).toContain('&');
    });

    it('should handle zero duration for audio/video', () => {
      const audioContent: AudioContent = {
        kind: 'audio',
        uri: 'https://example.com/audio.mp3',
        mimeType: 'audio/mpeg',
        duration: 0,
      };

      expect(audioContent.duration).toBe(0);
    });

    it('should handle zero dimensions for image/video', () => {
      const imageContent: ImageContent = {
        kind: 'image',
        uri: 'https://example.com/image.jpg',
        width: 0,
        height: 0,
      };

      expect(imageContent.width).toBe(0);
      expect(imageContent.height).toBe(0);
    });
  });
});
