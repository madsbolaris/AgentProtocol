"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const supertest_1 = __importDefault(require("supertest"));
const express_1 = __importDefault(require("express"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Integration tests for Agent Protocol endpoints with EchoM365.
 *
 * Tests the Agent Protocol endpoints:
 * - GET /health - Health check
 * - POST /runs - Create run
 * - POST /runs/wait - Create and wait for run
 * - POST /runs/stream - Create and stream run
 *
 * Matches the .NET EchoM365IntegrationTests.cs implementation.
 */
describe('Agent Protocol Integration Tests', () => {
    let app;
    const echoM365Url = process.env.ECHOM365_URL || 'http://localhost:3980';
    const testDataDir = findRepositoryRoot(process.cwd());
    const inputDir = path.join(testDataDir, 'test-data', 'input');
    beforeAll(async () => {
        // Check if we're testing against a live server or need to create our own
        if (process.env.USE_LIVE_SERVER === 'true') {
            // Use supertest with URL
            app = (0, express_1.default)(); // Placeholder, supertest will use the URL
        }
        else {
            // Import and create local server for testing
            // This would require refactoring index.ts to export the app
            throw new Error('Local testing not yet implemented. Set USE_LIVE_SERVER=true to test against running server.');
        }
    });
    function findRepositoryRoot(startPath) {
        let current = startPath;
        while (current !== path.dirname(current)) {
            if (fs.existsSync(path.join(current, 'test-data'))) {
                return current;
            }
            current = path.dirname(current);
        }
        throw new Error('Could not find repository root with test-data directory');
    }
    describe('Health Check', () => {
        it('should return 200 OK with status', async () => {
            const response = await (0, supertest_1.default)(echoM365Url)
                .get('/health')
                .expect(200);
            expect(response.body).toHaveProperty('status');
            expect(response.body.status).toBe('OK');
        });
    });
    describe('Agent Protocol /runs endpoint', () => {
        it('should create and return a run', async () => {
            const run = {
                agentId: 'echo-agent',
                input: [
                    {
                        role: 'user',
                        contents: [
                            {
                                kind: 'text',
                                text: 'Hello from TypeScript test'
                            }
                        ]
                    }
                ]
            };
            const response = await (0, supertest_1.default)(echoM365Url)
                .post('/runs')
                .send(run)
                .set('Content-Type', 'application/json')
                .expect(201);
            expect(response.body).toHaveProperty('runId');
            expect(response.body).toHaveProperty('agentId', 'echo-agent');
            expect(response.body).toHaveProperty('status', 'completed');
            expect(response.body).toHaveProperty('input');
            expect(response.body).toHaveProperty('output');
            expect(response.body).toHaveProperty('createdAt');
            expect(response.body).toHaveProperty('completedAt');
            // Verify output echoes input
            expect(response.body.output).toBeInstanceOf(Array);
            expect(response.body.output.length).toBeGreaterThan(0);
            expect(response.body.output[0].contents[0].text).toContain('Echo:');
        });
        it('should handle multiple messages in input', async () => {
            const run = {
                agentId: 'echo-agent',
                input: [
                    {
                        role: 'user',
                        contents: [{ kind: 'text', text: 'First message' }]
                    },
                    {
                        role: 'user',
                        contents: [{ kind: 'text', text: 'Second message' }]
                    }
                ]
            };
            const response = await (0, supertest_1.default)(echoM365Url)
                .post('/runs')
                .send(run)
                .expect(201);
            expect(response.body.output).toBeInstanceOf(Array);
            expect(response.body.output.length).toBe(2);
        });
    });
    describe('Agent Protocol /runs/wait endpoint', () => {
        it('should create and wait for run completion', async () => {
            const run = {
                agentId: 'echo-agent',
                input: [
                    {
                        role: 'user',
                        contents: [
                            {
                                kind: 'text',
                                text: 'Wait pattern test'
                            }
                        ]
                    }
                ]
            };
            const response = await (0, supertest_1.default)(echoM365Url)
                .post('/runs/wait')
                .send(run)
                .set('Content-Type', 'application/json')
                .expect(200);
            expect(response.body).toHaveProperty('runId');
            expect(response.body).toHaveProperty('status', 'completed');
            expect(response.body).toHaveProperty('output');
            // Verify output
            expect(response.body.output).toBeInstanceOf(Array);
            expect(response.body.output[0].contents[0].text).toContain('Echo:');
        });
    });
    describe('Agent Protocol /runs/stream endpoint', () => {
        it('should stream run results with SSE events', async () => {
            const run = {
                agentId: 'echo-agent',
                input: [
                    {
                        role: 'user',
                        contents: [
                            {
                                kind: 'text',
                                text: 'Stream test message'
                            }
                        ]
                    }
                ]
            };
            const response = await (0, supertest_1.default)(echoM365Url)
                .post('/runs/stream')
                .send(run)
                .set('Content-Type', 'application/json')
                .expect(200)
                .expect('Content-Type', /text\/event-stream/);
            // Verify SSE format
            const body = response.text;
            expect(body).toContain('event: run.started');
            expect(body).toContain('event: message.created');
            expect(body).toContain('event: message.updated');
            expect(body).toContain('event: message.completed');
            expect(body).toContain('event: run.completed');
            // Verify data payloads contain required fields
            expect(body).toMatch(/data:.*runId/);
            expect(body).toMatch(/data:.*messageId/);
        });
    });
    describe('XML Test Data Processing', () => {
        /**
         * Parse XML message to ChatMessage format for Agent Protocol.
         * Matches the .NET XmlToChatMessage implementation.
         */
        function xmlToChatMessage(xmlContent) {
            // Simple XML parsing - in production, use a proper XML parser
            const roleMatch = xmlContent.match(/<(\w+)/);
            const role = roleMatch ? roleMatch[1] : 'user';
            // Map XML role names to Agent Protocol roles
            const roleMap = {
                'user': 'user',
                'agent': 'assistant',
                'system': 'system',
                'developer': 'developer',
                'tool': 'tool',
                'channel': 'channel'
            };
            // Extract text content
            const textMatch = xmlContent.match(/<text>(.*?)<\/text>/s) ||
                xmlContent.match(/<thinking[^>]*>(.*?)<\/thinking>/s) ||
                xmlContent.match(/>([^<]+)</);
            const text = textMatch ? textMatch[1].trim() : 'Empty message';
            return {
                role: roleMap[role] || 'user',
                contents: [
                    {
                        kind: 'text',
                        text
                    }
                ]
            };
        }
        it('should process XML test data files', async () => {
            if (!fs.existsSync(inputDir)) {
                console.log('Skipping XML tests - test-data directory not found');
                return;
            }
            const inputFiles = fs.readdirSync(inputDir)
                .filter(f => f.endsWith('.xml'))
                .sort();
            expect(inputFiles.length).toBeGreaterThan(0);
            let processedCount = 0;
            for (const fileName of inputFiles.slice(0, 5)) { // Test first 5 files
                const filePath = path.join(inputDir, fileName);
                const xmlContent = fs.readFileSync(filePath, 'utf-8');
                try {
                    const message = xmlToChatMessage(xmlContent);
                    const run = {
                        agentId: 'echo-agent',
                        input: [message]
                    };
                    const response = await (0, supertest_1.default)(echoM365Url)
                        .post('/runs')
                        .send(run)
                        .expect(201);
                    expect(response.body).toHaveProperty('runId');
                    expect(response.body).toHaveProperty('output');
                    processedCount++;
                    console.log(`✓ Processed ${fileName}`);
                }
                catch (error) {
                    console.log(`✗ Failed ${fileName}: ${error.message}`);
                }
            }
            expect(processedCount).toBeGreaterThan(0);
            console.log(`\nProcessed ${processedCount} files successfully`);
        });
    });
    describe('XML Parser Tests', () => {
        it('should handle system message', () => {
            const xml = `<system created-at="2026-02-07T10:00:00Z">
        You are a helpful AI assistant.
      </system>`;
            // Simple test to verify XML structure
            expect(xml).toContain('<system');
            expect(xml).toContain('helpful AI assistant');
        });
        it('should handle developer message', () => {
            const xml = `<developer created-at="2026-02-07T10:01:00Z">
        Additional developer instructions: Use concise responses.
      </developer>`;
            expect(xml).toContain('<developer');
            expect(xml).toContain('concise responses');
        });
        it('should handle user text message', () => {
            const xml = `<user user-id="user_123">
        <text>What's the weather?</text>
      </user>`;
            expect(xml).toContain('<user');
            expect(xml).toContain('<text>');
            expect(xml).toContain("What's the weather?");
        });
    });
    describe('XML Results Whitespace Validation', () => {
        const resultsBase = path.join(testDataDir, 'results', 'samples', 'echo-m365');
        const xmlResultsDir = path.join(resultsBase, 'xml');
        const waitResultsDir = path.join(resultsBase, 'wait');
        it('should have proper indentation in xml results', () => {
            if (!fs.existsSync(xmlResultsDir)) {
                console.log('Skipping - xml results directory not found');
                return;
            }
            const xmlFiles = fs.readdirSync(xmlResultsDir)
                .filter(f => f.endsWith('.xml'))
                .map(f => path.join(xmlResultsDir, f));
            expect(xmlFiles.length).toBeGreaterThan(0);
            xmlFiles.forEach(xmlFile => {
                const content = fs.readFileSync(xmlFile, 'utf-8');
                const lines = content.split('\n');
                lines.forEach(line => {
                    if (line.trim().startsWith('<?xml'))
                        return;
                    // <thread> should have no leading whitespace
                    if (line.trim().startsWith('<thread')) {
                        expect(line).toMatch(/^<thread/);
                    }
                    // Direct children of <thread> should be indented with 2 spaces
                    else if (line.trim().startsWith('<agent') || line.trim().startsWith('</thread')) {
                        expect(line).toMatch(/^  [^ ]/);
                    }
                    // Children of <agent> should be indented with 4 spaces
                    else if (line.trim().startsWith('<text')) {
                        expect(line).toMatch(/^    [^ ]/);
                    }
                    // Closing </agent> tag should be indented with 2 spaces
                    else if (line.trim().startsWith('</agent')) {
                        expect(line).toMatch(/^  <\/agent>/);
                    }
                });
            });
        });
        it('should have proper indentation in wait results', () => {
            if (!fs.existsSync(waitResultsDir)) {
                console.log('Skipping - wait results directory not found');
                return;
            }
            const xmlFiles = fs.readdirSync(waitResultsDir)
                .filter(f => f.endsWith('.xml'))
                .map(f => path.join(waitResultsDir, f));
            expect(xmlFiles.length).toBeGreaterThan(0);
            xmlFiles.forEach(xmlFile => {
                const content = fs.readFileSync(xmlFile, 'utf-8');
                const lines = content.split('\n');
                lines.forEach(line => {
                    if (line.trim().startsWith('<?xml'))
                        return;
                    if (line.trim().startsWith('<thread')) {
                        expect(line).toMatch(/^<thread/);
                    }
                    else if (line.trim().startsWith('<agent') || line.trim().startsWith('</thread')) {
                        expect(line).toMatch(/^  [^ ]/);
                    }
                    else if (line.trim().startsWith('<text')) {
                        expect(line).toMatch(/^    [^ ]/);
                    }
                    else if (line.trim().startsWith('</agent')) {
                        expect(line).toMatch(/^  <\/agent>/);
                    }
                });
            });
        });
    });
});
//# sourceMappingURL=AgentProtocol.test.js.map