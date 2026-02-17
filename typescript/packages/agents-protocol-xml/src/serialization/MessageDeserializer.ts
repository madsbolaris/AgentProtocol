import type { ChatMessage } from '@microsoft/agents-protocol-abstractions';

/**
 * Deserializes XML to ChatMessage objects
 */
export class MessageDeserializer {
  /**
   * Deserialize XML to a message
   */
  deserialize(xml: string): ChatMessage {
    // Basic XML parsing - in production, use a proper XML parser
    const roleMatch = xml.match(/<(\w+)/);
    if (!roleMatch) {
      throw new Error('Invalid XML: no message role found');
    }

    const role = roleMatch[1] as any;
    const messageId = this.extractAttribute(xml, 'message-id');
    const userId = this.extractAttribute(xml, 'user-id');
    const agentId = this.extractAttribute(xml, 'agent-id');
    const createdAt = this.extractAttribute(xml, 'created-at');

    const contents = this.parseContents(xml);

    const message: any = {
      role,
      contents
    };

    if (messageId) message.messageId = messageId;
    if (userId) message.userId = userId;
    if (agentId) message.agentId = agentId;
    if (createdAt) message.createdAt = createdAt;

    return message as ChatMessage;
  }

  private extractAttribute(xml: string, attrName: string): string | undefined {
    const match = xml.match(new RegExp(`${attrName}="([^"]*)"`, 'i'));
    return match ? this.unescapeXml(match[1]) : undefined;
  }

  private parseContents(xml: string): any[] {
    const contents: any[] = [];

    // Parse text content
    const textMatches = xml.matchAll(/<text>(.*?)<\/text>/g);
    for (const match of textMatches) {
      contents.push({
        kind: 'text',
        text: this.unescapeXml(match[1])
      });
    }

    // Parse image content
    const imageMatches = xml.matchAll(/<image\s+uri="([^"]*)"\s*\/>/g);
    for (const match of imageMatches) {
      contents.push({
        kind: 'image',
        imageUri: this.unescapeXml(match[1])
      });
    }

    return contents;
  }

  private unescapeXml(str: string): string {
    return str
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&apos;/g, "'");
  }
}
