import type { Thread } from '@microsoft/agents-protocol-abstractions';
import { MessageSerializer } from './MessageSerializer';

/**
 * Serializes Thread objects to XML format
 */
export class ThreadSerializer {
  private messageSerializer: MessageSerializer;

  constructor() {
    this.messageSerializer = new MessageSerializer();
  }

  /**
   * Serialize a thread to XML
   */
  serialize(thread: Thread): string {
    const attrs = this.buildThreadAttributes(thread);
    const messages = this.messageSerializer.serializeMany(thread.messages || []);

    return `<thread${attrs}>\n${messages}\n</thread>`;
  }

  private buildThreadAttributes(thread: Thread): string {
    const attrs: string[] = [];

    if (thread.threadId) {
      attrs.push(`thread-id="${this.escapeXml(thread.threadId)}"`);
    }

    if (thread.status) {
      attrs.push(`status="${thread.status}"`);
    }

    if (thread.createdAt) {
      attrs.push(`created-at="${this.escapeXml(thread.createdAt)}"`);
    }

    return attrs.length > 0 ? ' ' + attrs.join(' ') : '';
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
