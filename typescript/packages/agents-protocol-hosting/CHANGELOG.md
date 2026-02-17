# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-08

### Added
- Initial release of the TypeScript Hosting SDK
- AgentHostBuilder with fluent API
- AgentBuilder for configuring individual agents
- FunctionBuilder with explicit JSON schema support
- IAgentContext for turn processing
- TurnResult enum for message flow control
- IOutOfBandPublisher for background messaging
- IStorage interface with InMemoryStorage implementation
- IQueue interface with InMemoryQueue implementation
- Health check support
- Graceful shutdown support
- Retry policy configuration
- Rate limiting configuration
- Logging configuration
- Agent routing support
- Streaming response support
- Security-first function execution with trust levels
- Mock implementations for testing
- Complete TypeScript type safety
- Comprehensive JSDoc documentation
