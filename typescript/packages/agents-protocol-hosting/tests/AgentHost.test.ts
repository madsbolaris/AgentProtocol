import { AgentHost } from '../src/hosting/AgentHost.js';
import { AgentHostBuilder } from '../src/builder/AgentHostBuilder.js';
import { InMemoryStorage } from '../src/storage/InMemoryStorage.js';
import { InMemoryQueue } from '../src/queue/InMemoryQueue.js';

describe('AgentHost', () => {
  let host: AgentHost;
  let currentPort = 3100; // Start from 3100 to avoid conflicts

  beforeEach(() => {
    const builder = new AgentHostBuilder()
      .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Test agent'));
    host = builder.build();
    currentPort++; // Increment port for each test
  });

  afterEach(async () => {
    // Clean up: stop the host after each test to avoid port conflicts
    try {
      await host.stop();
    } catch (e) {
      // Host may not be running, ignore
    }
    // Add small delay to ensure port is fully released
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  describe('start', () => {
    it('should start the agent host on default port', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);

      expect(consoleLogSpy).toHaveBeenCalledWith(`Agent host started on port ${currentPort}`);
      consoleLogSpy.mockRestore();
    });

    it('should start the agent host on custom port', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort + 1000);

      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host started on port ${currentPort + 1000}');
      consoleLogSpy.mockRestore();
    });

    it('should throw error if already running', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);

      await expect(host.start(currentPort)).rejects.toThrow('Agent host is already running');

      consoleLogSpy.mockRestore();
    });

    it('should set isRunning flag', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);

      const health = await host.checkHealth();
      expect(health.checks.server).toBe(true);

      consoleLogSpy.mockRestore();
    });
  });

  describe('stop', () => {
    it('should stop the agent host', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);
      await host.stop();

      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host stopped');
      consoleLogSpy.mockRestore();
    });

    it('should stop with custom grace period', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);
      await host.stop({ gracePeriodMs: 5000 });

      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host stopped');
      consoleLogSpy.mockRestore();
    });

    it('should stop with finishQueued option', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);
      await host.stop({ finishQueued: true });

      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host stopped');
      consoleLogSpy.mockRestore();
    });

    it('should stop with both options', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);
      await host.stop({ gracePeriodMs: 10000, finishQueued: true });

      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host stopped');
      consoleLogSpy.mockRestore();
    });

    it('should do nothing if not running', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.stop();

      expect(consoleLogSpy).not.toHaveBeenCalledWith('Agent host stopped');
      consoleLogSpy.mockRestore();
    });

    it('should set isRunning to false', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);
      await host.stop();

      const health = await host.checkHealth();
      expect(health.checks.server).toBe(false);

      consoleLogSpy.mockRestore();
    });
  });

  describe('checkHealth', () => {
    it('should return healthy status when running', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);
      const health = await host.checkHealth();

      expect(health.status).toBe('healthy');
      expect(health.checks.server).toBe(true);
      expect(health.checks.storage).toBe(true);
      expect(health.checks.queue).toBe(true);
      expect(health.checks.llmConnection).toBe(true);
      expect(health.uptimeMs).toBeGreaterThanOrEqual(0);

      consoleLogSpy.mockRestore();
    });

    it('should return degraded status when some checks fail', async () => {
      // Create a mock storage that fails health check
      const mockStorage = new InMemoryStorage();
      mockStorage.checkHealth = jest.fn().mockResolvedValue(false);

      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Test agent'))
        .useStorage(mockStorage);

      const hostWithFailingStorage = builder.build();

      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      await hostWithFailingStorage.start(currentPort);

      const health = await hostWithFailingStorage.checkHealth();

      expect(health.status).toBe('degraded');
      expect(health.checks.storage).toBe(false);

      consoleLogSpy.mockRestore();
    });

    it('should return degraded status when most checks fail', async () => {
      // Create mocks that fail (llmConnection is hardcoded to true, so we can't get all to fail)
      const mockStorage = new InMemoryStorage();
      mockStorage.checkHealth = jest.fn().mockResolvedValue(false);

      const mockQueue = new InMemoryQueue();
      mockQueue.checkHealth = jest.fn().mockResolvedValue(false);

      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Test agent'))
        .useStorage(mockStorage)
        .useQueue(mockQueue);

      const hostWithAllFailing = builder.build();

      const health = await hostWithAllFailing.checkHealth();

      // Status is degraded because llmConnection is always true
      expect(health.status).toBe('degraded');
      expect(health.checks.server).toBe(false);
      expect(health.checks.storage).toBe(false);
      expect(health.checks.queue).toBe(false);
      expect(health.checks.llmConnection).toBe(true);
    });

    it('should track uptime correctly', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      await host.start(currentPort);

      // Wait a small amount of time
      await new Promise(resolve => setTimeout(resolve, 50));

      const health = await host.checkHealth();
      expect(health.uptimeMs).toBeGreaterThanOrEqual(50);

      consoleLogSpy.mockRestore();
    });

    it('should return uptime even when not started', async () => {
      const health = await host.checkHealth();
      expect(health.uptimeMs).toBeGreaterThanOrEqual(0);
    });
  });

  describe('getPublisher', () => {
    it('should return a publisher instance', () => {
      const publisher = host.getPublisher();

      expect(publisher).toBeDefined();
      expect(publisher.sendToThreadAsync).toBeInstanceOf(Function);
    });

    it('should send message with string content', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      const publisher = host.getPublisher();

      await publisher.sendToThreadAsync('thread-123', 'Test message');

      expect(consoleLogSpy).toHaveBeenCalledWith('Sending out-of-band message to thread thread-123');
      consoleLogSpy.mockRestore();
    });

    it('should send message with AIContent', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      const publisher = host.getPublisher();

      await publisher.sendToThreadAsync('thread-456', {
        kind: 'text',
        text: 'AIContent message'
      });

      expect(consoleLogSpy).toHaveBeenCalledWith('Sending out-of-band message to thread thread-456');
      consoleLogSpy.mockRestore();
    });

    it('should send message with runId', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      const publisher = host.getPublisher();

      await publisher.sendToThreadAsync('thread-789', 'Message', 'run-123');

      expect(consoleLogSpy).toHaveBeenCalledWith('Sending out-of-band message to thread thread-789');
      consoleLogSpy.mockRestore();
    });

    it('should send message with idempotency key', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      const publisher = host.getPublisher();

      await publisher.sendToThreadAsync('thread-abc', 'Message', undefined, 'key-123');

      expect(consoleLogSpy).toHaveBeenCalledWith('Sending out-of-band message to thread thread-abc');
      consoleLogSpy.mockRestore();
    });

    it('should send message with cancellation token', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      const publisher = host.getPublisher();
      const controller = new AbortController();

      await publisher.sendToThreadAsync('thread-def', 'Message', undefined, undefined, controller.signal);

      expect(consoleLogSpy).toHaveBeenCalledWith('Sending out-of-band message to thread thread-def');
      consoleLogSpy.mockRestore();
    });

    it('should send message with all parameters', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
      const publisher = host.getPublisher();
      const controller = new AbortController();

      await publisher.sendToThreadAsync('thread-ghi', 'Message', 'run-456', 'key-789', controller.signal);

      expect(consoleLogSpy).toHaveBeenCalledWith('Sending out-of-band message to thread thread-ghi');
      consoleLogSpy.mockRestore();
    });
  });

  describe('processMessage', () => {
    it('should process a message without threadId', async () => {
      const response = await host.processMessage('Hello');

      expect(response).toBeDefined();
      expect(response?.kind).toBe('text');
      if (response?.kind === 'text') {
        expect(response.text).toBe('Response from agent');
      }
    });

    it('should process a message with threadId', async () => {
      const response = await host.processMessage('Hello', 'thread-123');

      expect(response).toBeDefined();
      expect(response?.kind).toBe('text');
      if (response?.kind === 'text') {
        expect(response.text).toBe('Response from agent');
      }
    });
  });

  describe('integration', () => {
    it('should support complete lifecycle', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      // Start
      await host.start(currentPort);
      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host started on port 3000');

      // Check health
      let health = await host.checkHealth();
      expect(health.status).toBe('healthy');

      // Get publisher
      const publisher = host.getPublisher();
      await publisher.sendToThreadAsync('thread-test', 'Test message');

      // Process message
      const response = await host.processMessage('Hello', 'thread-test');
      expect(response).toBeDefined();

      // Stop
      await host.stop();
      expect(consoleLogSpy).toHaveBeenCalledWith('Agent host stopped');

      // Check health after stop
      health = await host.checkHealth();
      expect(health.checks.server).toBe(false);

      consoleLogSpy.mockRestore();
    });

    it('should work with custom storage and queue', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      const customStorage = new InMemoryStorage();
      const customQueue = new InMemoryQueue();

      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Test agent'))
        .useStorage(customStorage)
        .useQueue(customQueue);

      const customHost = builder.build();

      await customHost.start(currentPort);
      const health = await customHost.checkHealth();

      expect(health.status).toBe('healthy');
      expect(health.checks.storage).toBe(true);
      expect(health.checks.queue).toBe(true);

      await customHost.stop();
      consoleLogSpy.mockRestore();
    });

    it('should work with multiple agents', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Default agent'))
        .addAgent('sales', agent => agent.useLLM('gpt-4', 'Sales agent'))
        .addAgent('support', agent => agent.useLLM('gpt-4', 'Support agent'));

      const multiAgentHost = builder.build();

      await multiAgentHost.start(currentPort);
      const health = await multiAgentHost.checkHealth();

      expect(health.status).toBe('healthy');

      await multiAgentHost.stop();
      consoleLogSpy.mockRestore();
    });
  });
});
