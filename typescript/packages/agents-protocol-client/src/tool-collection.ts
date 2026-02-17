/**
 * Tool collection for agent function calling
 */

/**
 * Represents a single tool definition with handler
 */
export interface ToolDefinition {
  /**
   * Tool name (unique identifier)
   */
  name: string;

  /**
   * Tool description for the LLM
   */
  description: string;

  /**
   * JSON Schema for tool parameters
   */
  schema: object;

  /**
   * Handler function to execute when tool is called
   */
  handler: Function;
}

/**
 * Collection of tools (functions) that can be called by the agent
 * Supports automatic schema generation from function signatures
 */
export class ToolCollection {
  private readonly tools = new Map<string, ToolDefinition>();

  /**
   * Adds a tool to the collection
   * @param name Tool name
   * @param handler Function to execute
   * @param description Optional description (defaults to "Executes {name}")
   */
  add(name: string, handler: Function, description?: string): void {
    const tool: ToolDefinition = {
      name,
      description: description ?? `Executes ${name}`,
      schema: this.generateSchema(handler),
      handler,
    };
    this.tools.set(name, tool);
  }

  /**
   * Gets a tool by name
   * @param name Tool name
   * @returns Tool definition or undefined if not found
   */
  get(name: string): ToolDefinition | undefined {
    return this.tools.get(name);
  }

  /**
   * Gets all tool definitions
   * @returns Array of all tool definitions
   */
  getAll(): ToolDefinition[] {
    return Array.from(this.tools.values());
  }

  /**
   * Converts tools to AITool format for the protocol
   * @returns Array of tool objects
   */
  toAITools(): Array<{
    name: string;
    description: string;
    parameters: any;
  }> {
    return this.getAll().map((tool) => ({
      name: tool.name,
      description: tool.description,
      parameters: tool.schema as any,
    }));
  }

  /**
   * Executes a tool by name with JSON arguments
   * @param toolName Name of the tool to execute
   * @param argumentsJson JSON-encoded arguments
   * @returns Promise resolving to the tool result
   */
  async execute(toolName: string, argumentsJson: string): Promise<unknown> {
    const tool = this.get(toolName);
    if (!tool) {
      throw new Error(`Tool '${toolName}' not found`);
    }

    return this.executeTool(tool, argumentsJson);
  }

  /**
   * Executes a tool definition with JSON arguments
   * @param tool Tool definition
   * @param argumentsJson JSON-encoded arguments
   * @returns Promise resolving to the tool result
   */
  private async executeTool(
    tool: ToolDefinition,
    argumentsJson: string
  ): Promise<unknown> {
    const args = JSON.parse(argumentsJson);
    const handler = tool.handler;

    // Extract parameters based on handler arity
    const paramValues: unknown[] = [];

    // Build parameter array based on schema
    const schema = tool.schema as any;
    if (schema?.properties) {
      for (const paramName of Object.keys(schema.properties)) {
        paramValues.push(args[paramName]);
      }
    }

    // Execute handler (supports both sync and async)
    const result = handler(...paramValues);

    // Handle promises
    if (result instanceof Promise) {
      return await result;
    }

    return result;
  }

  /**
   * Generates JSON schema from function signature
   * Note: TypeScript doesn't preserve parameter names at runtime,
   * so this is a basic implementation. For better results, pass
   * schema explicitly or use decorators.
   * @param handler Function to analyze
   * @returns JSON Schema object
   */
  private generateSchema(handler: Function): object {
    const paramCount = handler.length;

    // Basic schema - in real usage, schema should be provided explicitly
    const properties: Record<string, object> = {};
    const required: string[] = [];

    // Generate generic parameter names
    for (let i = 0; i < paramCount; i++) {
      const paramName = `param${i}`;
      properties[paramName] = {
        type: 'string',
        description: `Parameter ${i}`,
      };
      required.push(paramName);
    }

    return {
      type: 'object',
      properties,
      required,
    };
  }

  /**
   * Creates a ToolCollection from tool definitions with handlers
   * @param tools Array of tool definitions
   * @param handlers Map of tool names to handler functions
   * @returns ToolCollection instance
   */
  static fromAITools(
    tools: Array<{ name: string; description: string; parameters?: any }>,
    handlers: Map<string, Function>
  ): ToolCollection {
    const collection = new ToolCollection();

    for (const tool of tools) {
      const handler = handlers.get(tool.name);
      if (!handler) {
        throw new Error(`No handler provided for tool '${tool.name}'`);
      }

      const definition: ToolDefinition = {
        name: tool.name,
        description: tool.description,
        schema: (tool.parameters as object) ?? {},
        handler,
      };

      collection.tools.set(tool.name, definition);
    }

    return collection;
  }

  /**
   * Gets the number of tools in the collection
   */
  get size(): number {
    return this.tools.size;
  }

  /**
   * Checks if a tool exists in the collection
   * @param name Tool name
   * @returns True if tool exists
   */
  has(name: string): boolean {
    return this.tools.has(name);
  }

  /**
   * Removes a tool from the collection
   * @param name Tool name
   * @returns True if tool was removed
   */
  remove(name: string): boolean {
    return this.tools.delete(name);
  }

  /**
   * Clears all tools from the collection
   */
  clear(): void {
    this.tools.clear();
  }

  /**
   * Iterates over all tool names
   */
  *[Symbol.iterator](): Iterator<string> {
    yield* this.tools.keys();
  }
}
