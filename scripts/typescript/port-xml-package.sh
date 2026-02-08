#!/bin/bash
# Script to create the XML package for TypeScript

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

DEST_DIR="$REPO_ROOT/typescript/packages/agents-xml"

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Creating XML Package for TypeScript               ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${BLUE}Destination: $DEST_DIR${NC}"
echo

# Create directory structure
echo -e "${GREEN}Creating directory structure...${NC}"
mkdir -p "$DEST_DIR/src"/{serialization,parsers}
mkdir -p "$DEST_DIR/tests"

# Create package.json
echo -e "${GREEN}Creating package.json...${NC}"
cat > "$DEST_DIR/package.json" << 'EOF'
{
  "name": "@microsoft/agents-xml",
  "version": "0.1.0",
  "description": "XML serialization/deserialization for Microsoft Agents Protocol",
  "main": "./dist/index.js",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsc -b",
    "clean": "rm -rf dist *.tsbuildinfo",
    "dev": "tsc -b --watch",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "keywords": [
    "agents",
    "xml",
    "serialization",
    "typescript",
    "microsoft"
  ],
  "author": "Microsoft",
  "license": "MIT",
  "dependencies": {
    "@microsoft/agents": "^0.1.0"
  },
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.0",
    "typescript": "^5.8.0"
  }
}
EOF

# Create tsconfig.json
echo -e "${GREEN}Creating tsconfig.json...${NC}"
cat > "$DEST_DIR/tsconfig.json" << 'EOF'
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"],
  "references": [
    { "path": "../agents" }
  ]
}
EOF

# Create source files
echo -e "${GREEN}Creating source files...${NC}"

# MessageSerializer
cat > "$DEST_DIR/src/serialization/MessageSerializer.ts" << 'EOF'
import type { ChatMessage, AIContent } from '@microsoft/agents';

/**
 * Serializes ChatMessage objects to XML format
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
        return `  <text>${this.escapeXml((content as any).text || '')}</text>`;
      case 'image':
        return `  <image uri="${this.escapeXml((content as any).imageUri || '')}" />`;
      case 'functionCall':
        return this.serializeFunctionCall(content as any);
      case 'functionResult':
        return this.serializeFunctionResult(content as any);
      default:
        return `  <${kind} />`;
    }
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
EOF

# MessageDeserializer
cat > "$DEST_DIR/src/serialization/MessageDeserializer.ts" << 'EOF'
import type { ChatMessage } from '@microsoft/agents';

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
EOF

# ThreadSerializer
cat > "$DEST_DIR/src/serialization/ThreadSerializer.ts" << 'EOF'
import type { Thread } from '@microsoft/agents';
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
EOF

# Index file
cat > "$DEST_DIR/src/index.ts" << 'EOF'
/**
 * Microsoft Agents - XML Serialization
 *
 * XML serialization and deserialization for Agent Protocol messages and threads.
 *
 * @packageDocumentation
 */

export * from './serialization/MessageSerializer';
export * from './serialization/MessageDeserializer';
export * from './serialization/ThreadSerializer';
EOF

# README
cat > "$DEST_DIR/README.md" << 'EOF'
# @microsoft/agents-xml

XML serialization and deserialization for Microsoft Agents Protocol.

## Installation

```bash
npm install @microsoft/agents-xml
```

## Usage

### Serialize Messages

```typescript
import { MessageSerializer } from '@microsoft/agents-xml';
import type { ChatMessage } from '@microsoft/agents';

const message: ChatMessage = {
  messageId: 'msg_123',
  role: 'user',
  userId: 'user_456',
  contents: [
    { kind: 'text', text: 'Hello, agent!' }
  ],
  createdAt: new Date().toISOString()
};

const serializer = new MessageSerializer();
const xml = serializer.serialize(message);

console.log(xml);
// <user message-id="msg_123" user-id="user_456" created-at="...">
//   <text>Hello, agent!</text>
// </user>
```

### Deserialize Messages

```typescript
import { MessageDeserializer } from '@microsoft/agents-xml';

const xml = `
<user message-id="msg_123" user-id="user_456">
  <text>Hello, agent!</text>
</user>
`;

const deserializer = new MessageDeserializer();
const message = deserializer.deserialize(xml);

console.log(message);
// {
//   role: 'user',
//   messageId: 'msg_123',
//   userId: 'user_456',
//   contents: [{ kind: 'text', text: 'Hello, agent!' }]
// }
```

### Serialize Threads

```typescript
import { ThreadSerializer } from '@microsoft/agents-xml';
import type { Thread } from '@microsoft/agents';

const thread: Thread = {
  threadId: 'thread_123',
  status: 'active',
  participants: [],
  messages: [
    {
      messageId: 'msg_1',
      role: 'user',
      contents: [{ kind: 'text', text: 'Hello!' }],
      createdAt: new Date().toISOString()
    }
  ],
  createdAt: new Date().toISOString()
};

const serializer = new ThreadSerializer();
const xml = serializer.serialize(thread);

console.log(xml);
// <thread thread-id="thread_123" status="active" created-at="...">
//   <user message-id="msg_1" created-at="...">
//     <text>Hello!</text>
//   </user>
// </thread>
```

## Features

- Serialize ChatMessage to XML
- Deserialize XML to ChatMessage
- Serialize Thread (conversation) to XML
- Support for all message roles (user, assistant, tool, system, etc.)
- Support for multiple content types (text, image, function calls, etc.)
- XML attribute mapping for IDs and metadata
- Proper XML escaping and unescaping

## License

MIT
EOF

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ XML package created successfully!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Location: $DEST_DIR${NC}"
echo
