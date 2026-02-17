import type { ChatMessage, AIContent } from '@microsoft/agents-protocol-abstractions';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Serializes ChatMessage objects to XML format with multi-modal content support
 */
export class MessageSerializer {
  /**
   * Serialize a message to XML
   */
  serialize(message: ChatMessage): string {
    const role = message.role;
    const attrs = this.buildMessageAttributes(message);
    const contents = this.serializeContents(message.contents || []);

    return `<${role}${attrs}>\n${contents}</${role}>`;
  }

  /**
   * Serialize multiple messages
   */
  serializeMany(messages: ChatMessage[]): string {
    return messages.map(msg => this.serialize(msg)).join('\n');
  }

  /**
   * Serialize a message to an XML file
   */
  serializeToFile(message: ChatMessage, filePath: string): void {
    const xml = this.serialize(message);
    const dir = path.dirname(filePath);

    // Ensure directory exists
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(filePath, xml, 'utf-8');
  }

  /**
   * Serialize multiple messages to an XML file
   */
  serializeManyToFile(messages: ChatMessage[], filePath: string): void {
    const xml = this.serializeMany(messages);
    const dir = path.dirname(filePath);

    // Ensure directory exists
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(filePath, xml, 'utf-8');
  }

  private buildMessageAttributes(message: ChatMessage): string {
    const attrs: string[] = [];

    if (message.messageId) {
      attrs.push(`message-id="${this.escapeXml(message.messageId)}"`);
    }

    if ('userId' in message && message.userId) {
      attrs.push(`user-id="${this.escapeXml(message.userId)}"`);
    }

    if ('agentId' in message && message.agentId) {
      attrs.push(`agent-id="${this.escapeXml(message.agentId)}"`);
    }

    if (message.createdAt) {
      attrs.push(`created-at="${this.escapeXml(message.createdAt)}"`);
    }

    return attrs.length > 0 ? ' ' + attrs.join(' ') : '';
  }

  private serializeContents(contents: AIContent[]): string {
    return contents.map(content => this.serializeContent(content)).join('\n');
  }

  private serializeContent(content: AIContent): string {
    const kind = content.kind;

    switch (kind) {
      case 'text':
        return this.serializeText(content as any);
      case 'image':
        return this.serializeImage(content as any);
      case 'audio':
        return this.serializeAudio(content as any);
      case 'video':
        return this.serializeVideo(content as any);
      case 'file':
        return this.serializeFile(content as any);
      case 'functionCall':
        return this.serializeFunctionCall(content as any);
      case 'functionResult':
        return this.serializeFunctionResult(content as any);
      case 'textReasoning':
        return this.serializeThinking(content as any);
      default:
        return `  <${kind} />`;
    }
  }

  private serializeText(content: any): string {
    const attrs: string[] = [];
    if (content.audience) {
      attrs.push(`audience="${this.escapeXml(content.audience)}"`);
    }
    const attrStr = attrs.length > 0 ? ' ' + attrs.join(' ') : '';
    return `  <text${attrStr}>${this.escapeXml(content.text || '')}</text>`;
  }

  private serializeImage(content: any): string {
    const attrs: string[] = [];
    attrs.push(`uri="${this.escapeXml(content.imageUri || content.uri || '')}"`);
    if (content.alt || content.altText) {
      attrs.push(`alt="${this.escapeXml(content.alt || content.altText)}"`);
    }
    if (content.mimeType) {
      attrs.push(`mime-type="${this.escapeXml(content.mimeType)}"`);
    }
    return `  <image ${attrs.join(' ')} />`;
  }

  private serializeAudio(content: any): string {
    const attrs: string[] = [];
    attrs.push(`uri="${this.escapeXml(content.uri || '')}"`);
    if (content.mimeType) {
      attrs.push(`mime-type="${this.escapeXml(content.mimeType)}"`);
    }
    return `  <audio ${attrs.join(' ')} />`;
  }

  private serializeVideo(content: any): string {
    const attrs: string[] = [];
    attrs.push(`uri="${this.escapeXml(content.uri || '')}"`);
    if (content.mimeType) {
      attrs.push(`mime-type="${this.escapeXml(content.mimeType)}"`);
    }
    return `  <video ${attrs.join(' ')} />`;
  }

  private serializeFile(content: any): string {
    const attrs: string[] = [];
    attrs.push(`uri="${this.escapeXml(content.uri || '')}"`);
    if (content.filename) {
      attrs.push(`filename="${this.escapeXml(content.filename)}"`);
    }
    if (content.mimeType) {
      attrs.push(`mime-type="${this.escapeXml(content.mimeType)}"`);
    }
    return `  <file ${attrs.join(' ')} />`;
  }

  private serializeThinking(content: any): string {
    const attrs: string[] = [];
    if (content.exposed !== undefined) {
      attrs.push(`exposed="${content.exposed}"`);
    }
    const attrStr = attrs.length > 0 ? ' ' + attrs.join(' ') : '';
    return `  <thinking${attrStr}>${this.escapeXml(content.text || content.content || '')}</thinking>`;
  }

  private serializeFunctionCall(content: any): string {
    return `  <function-call name="${this.escapeXml(content.name || '')}" arguments="${this.escapeXml(content.arguments || '')}" />`;
  }

  private serializeFunctionResult(content: any): string {
    return `  <function-result call-id="${this.escapeXml(content.callId || '')}">${this.escapeXml(content.result || '')}</function-result>`;
  }

  private escapeXml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}
