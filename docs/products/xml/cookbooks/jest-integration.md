# Jest Integration

Use XML serialization and validation in Jest test suites.

## Overview

This cookbook shows how to integrate XML message validation into Jest tests for TypeScript/JavaScript applications.

---

## Test Structure

```
tests/
├── testData/
│   ├── input/          # Input XML files
│   └── expected/       # Expected output XML files
├── fixtures/
│   └── setup.ts        # Test setup
└── messages.test.ts    # Message tests
```

---

## Installation

```bash
npm install --save-dev jest @jest/globals ts-jest @types/jest
npm install @microsoft/agents-xml
```

---

## Jest Configuration

### jest.config.js

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts'
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/fixtures/setup.ts']
};
```

---

## Complete Test Example

### fixtures/setup.ts - Test Setup

```typescript
import { beforeAll, afterAll } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';

// Global test data
export const testDataDir = path.join(__dirname, '..', 'testData');

// Helper to load XML files
export function loadXML(filename: string, subdir: 'input' | 'expected' = 'input'): string {
  const filePath = path.join(testDataDir, subdir, filename);
  return fs.readFileSync(filePath, 'utf-8');
}

// Helper to load all test cases
export function loadTestCases(): Array<{ name: string; input: string; expected: string }> {
  const inputDir = path.join(testDataDir, 'input');
  const expectedDir = path.join(testDataDir, 'expected');
  
  const testCases: Array<{ name: string; input: string; expected: string }> = [];
  
  const inputFiles = fs.readdirSync(inputDir).filter(f => f.endsWith('.xml'));
  
  for (const file of inputFiles) {
    const expectedFile = path.join(expectedDir, file);
    if (fs.existsSync(expectedFile)) {
      testCases.push({
        name: path.basename(file, '.xml'),
        input: fs.readFileSync(path.join(inputDir, file), 'utf-8'),
        expected: fs.readFileSync(expectedFile, 'utf-8')
      });
    }
  }
  
  return testCases;
}
```

### messages.test.ts - Message Tests

```typescript
import { describe, it, expect, beforeEach } from '@jest/globals';
import { 
  MessageSerializer, 
  ThreadValidator, 
  preprocessEvalXML 
} from '@microsoft/agents-xml';
import { 
  UserMessage, 
  AgentMessage, 
  TextContent 
} from '@microsoft/agents-protocol';
import { loadXML, loadTestCases } from './fixtures/setup';

describe('XML Message Serialization', () => {
  let serializer: MessageSerializer;

  beforeEach(() => {
    serializer = new MessageSerializer();
  });

  describe('Serialize Messages', () => {
    it('should serialize user message to XML', () => {
      // Arrange
      const message: UserMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Hello, agent!' }]
      };

      // Act
      const xml = serializer.serialize(message);

      // Assert
      expect(xml).toBeDefined();
      expect(xml).toContain('<?xml');
      expect(xml).toContain('<user-message');
      expect(xml).toContain('Hello, agent!');
    });

    it('should serialize agent message to XML', () => {
      // Arrange
      const message: AgentMessage = {
        role: 'agent',
        content: [{ type: 'text', text: 'Hello, user!' }]
      };

      // Act
      const xml = serializer.serialize(message);

      // Assert
      expect(xml).toBeDefined();
      expect(xml).toContain('<agent-message');
      expect(xml).toContain('Hello, user!');
    });

    it('should handle roundtrip serialization', () => {
      // Arrange
      const original: UserMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Test message' }]
      };

      // Act
      const xml = serializer.serialize(original);
      const deserialized = serializer.deserialize(xml);

      // Assert
      expect(deserialized.role).toBe(original.role);
      expect(deserialized.content).toHaveLength(original.content.length);
      expect(deserialized.content[0].text).toBe(original.content[0].text);
    });
  });

  describe('Multimodal Content', () => {
    it('should serialize image content', () => {
      // Arrange
      const message: UserMessage = {
        role: 'user',
        content: [
          { type: 'text', text: 'Look at this:' },
          { type: 'image', url: 'https://example.com/image.jpg' }
        ]
      };

      // Act
      const xml = serializer.serialize(message);

      // Assert
      expect(xml).toContain('<text>');
      expect(xml).toContain('<image');
      expect(xml).toContain('https://example.com/image.jpg');
    });
  });
});

describe('XML Validation', () => {
  let validator: ThreadValidator;

  beforeEach(() => {
    validator = new ThreadValidator();
  });

  describe('Validate XML', () => {
    it('should validate valid XML', () => {
      // Arrange
      const validXml = loadXML('basic_message.xml');

      // Act
      const errors = validator.validate(validXml);

      // Assert
      expect(errors).toHaveLength(0);
    });

    it('should detect invalid XML', () => {
      // Arrange
      const invalidXml = '<invalid>Not a valid message</invalid>';

      // Act
      const errors = validator.validate(invalidXml);

      // Assert
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0].message).toMatch(/schema/i);
    });

    it('should validate all test data files', () => {
      // Arrange
      const testCases = loadTestCases();

      // Act & Assert
      testCases.forEach(testCase => {
        const inputErrors = validator.validate(testCase.input);
        expect(inputErrors).toHaveLength(0);

        const expectedErrors = validator.validate(testCase.expected);
        expect(expectedErrors).toHaveLength(0);
      });
    });
  });

  describe('Validation Errors', () => {
    it('should provide detailed error messages', () => {
      // Arrange
      const invalidXml = `
        <?xml version="1.0"?>
        <thread xmlns="urn:messages">
          <unknown-element>Invalid</unknown-element>
        </thread>
      `;

      // Act
      const errors = validator.validate(invalidXml);

      // Assert
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toHaveProperty('message');
      expect(errors[0]).toHaveProperty('line');
    });
  });
});

describe('EvalXML Preprocessing', () => {
  describe('CDATA Wrapping', () => {
    it('should wrap assertion blocks in CDATA', () => {
      // Arrange
      const input = '<assert>x == 5</assert>';

      // Act
      const result = preprocessEvalXML(input);

      // Assert
      expect(result).toBe('<assert><![CDATA[x == 5]]></assert>');
    });

    it('should protect comparison operators in metrics', () => {
      // Arrange
      const input = '<metric>x > 5 && y < 10</metric>';

      // Act
      const result = preprocessEvalXML(input);

      // Assert
      expect(result).toContain('<![CDATA[');
      expect(result).toContain('x > 5 && y < 10');
      expect(result).toContain(']]>');
    });

    it('should handle multiple blocks', () => {
      // Arrange
      const input = `
        <eval>
          <assert>x == 1</assert>
          <result>true</result>
          <metric>y > 0</metric>
        </eval>
      `;

      // Act
      const result = preprocessEvalXML(input);

      // Assert
      expect(result).toContain('<assert><![CDATA[x == 1]]></assert>');
      expect(result).toContain('<metric><![CDATA[y > 0]]></metric>');
      expect(result).toContain('<result>true</result>'); // Not wrapped
    });
  });

  describe('Special Characters', () => {
    it('should protect XML special characters', () => {
      // Arrange
      const input = '<args>{"name": "test", "value": "x < 5 && y > 3"}</args>';

      // Act
      const result = preprocessEvalXML(input);

      // Assert
      expect(result).toContain('<![CDATA[');
      expect(result).toContain('x < 5 && y > 3');
    });
  });
});

describe('Integration Tests', () => {
  let serializer: MessageSerializer;
  let validator: ThreadValidator;

  beforeEach(() => {
    serializer = new MessageSerializer();
    validator = new ThreadValidator();
  });

  describe('End-to-End Workflow', () => {
    it('should serialize, validate, and deserialize', () => {
      // Arrange
      const message: UserMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Integration test' }]
      };

      // Act
      const xml = serializer.serialize(message);
      const errors = validator.validate(xml);
      const deserialized = serializer.deserialize(xml);

      // Assert
      expect(errors).toHaveLength(0);
      expect(deserialized.role).toBe(message.role);
      expect(deserialized.content[0].text).toBe(message.content[0].text);
    });
  });

  describe('Test Data Cases', () => {
    it.each(loadTestCases())('should process $name', ({ input, expected }) => {
      // Validate input
      const inputErrors = validator.validate(input);
      expect(inputErrors).toHaveLength(0);

      // Validate expected
      const expectedErrors = validator.validate(expected);
      expect(expectedErrors).toHaveLength(0);
    });
  });
});

// Run with: npm test
```

---

## Test Data Organization

### Input XML Files

Create `testData/input/basic_message.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<thread xmlns="urn:messages">
  <user-message>
    <text>Hello, agent!</text>
  </user-message>
</thread>
```

### Expected Output Files

Create `testData/expected/basic_message.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<thread xmlns="urn:messages">
  <agent-message>
    <text>Hello, user!</text>
  </agent-message>
</thread>
```

---

## Running Tests

### Run All Tests

```bash
npm test
```

### Run Specific Test File

```bash
npm test -- messages.test.ts
```

### Run With Coverage

```bash
npm test -- --coverage
```

### Watch Mode

```bash
npm test -- --watch
```

### Generate HTML Report

```bash
npm test -- --coverage --coverageReporters=html
```

---

## Advanced Patterns

### Custom Matchers

```typescript
expect.extend({
  toBeValidXML(received: string) {
    const validator = new ThreadValidator();
    const errors = validator.validate(received);
    
    return {
      pass: errors.length === 0,
      message: () => 
        errors.length === 0
          ? 'Expected XML to be invalid'
          : `XML validation failed: ${errors.map(e => e.message).join(', ')}`
    };
  }
});

// Usage
expect(xml).toBeValidXML();
```

### Snapshot Testing

```typescript
it('should match XML snapshot', () => {
  const message: UserMessage = {
    role: 'user',
    content: [{ type: 'text', text: 'Snapshot test' }]
  };

  const xml = serializer.serialize(message);
  expect(xml).toMatchSnapshot();
});
```

---

## See Also

- [pytest Integration](pytest-integration.md)
- [xUnit Integration](xunit-integration.md)
- [How-To: Validation](../how-to-guides/validation.md)
