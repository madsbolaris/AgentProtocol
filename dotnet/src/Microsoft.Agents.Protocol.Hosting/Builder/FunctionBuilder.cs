namespace Microsoft.Agents.Protocol.Hosting.Builder;

/// <summary>
/// Builder for adding functions/tools to an agent.
/// </summary>
public class FunctionBuilder
{
    private readonly List<FunctionDefinition> _functions = new();

    /// <summary>
    /// Adds a function with no parameters.
    /// </summary>
    /// <param name="name">Function name (include @v1 suffix for versioning).</param>
    /// <param name="description">Human-readable description.</param>
    /// <param name="implementation">The function implementation.</param>
    /// <returns>The builder for method chaining.</returns>
    public FunctionBuilder Add(string name, string description, Func<string> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = Array.Empty<Type>()
        });
        return this;
    }

    /// <summary>
    /// Adds a function with one parameter.
    /// </summary>
    public FunctionBuilder Add<T1>(string name, string description, Func<T1, string> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = new[] { typeof(T1) }
        });
        return this;
    }

    /// <summary>
    /// Adds a function with two parameters.
    /// </summary>
    public FunctionBuilder Add<T1, T2>(string name, string description, Func<T1, T2, string> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = new[] { typeof(T1), typeof(T2) }
        });
        return this;
    }

    /// <summary>
    /// Adds a function with three parameters.
    /// </summary>
    public FunctionBuilder Add<T1, T2, T3>(string name, string description, Func<T1, T2, T3, string> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = new[] { typeof(T1), typeof(T2), typeof(T3) }
        });
        return this;
    }

    /// <summary>
    /// Adds an async function with no parameters.
    /// </summary>
    public FunctionBuilder Add(string name, string description, Func<Task<string>> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = Array.Empty<Type>()
        });
        return this;
    }

    /// <summary>
    /// Adds an async function with one parameter.
    /// </summary>
    public FunctionBuilder Add<T1>(string name, string description, Func<T1, Task<string>> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = new[] { typeof(T1) }
        });
        return this;
    }

    /// <summary>
    /// Adds an async function with two parameters.
    /// </summary>
    public FunctionBuilder Add<T1, T2>(string name, string description, Func<T1, T2, Task<string>> implementation)
    {
        _functions.Add(new FunctionDefinition
        {
            Name = name,
            Description = description,
            Implementation = implementation,
            ParameterTypes = new[] { typeof(T1), typeof(T2) }
        });
        return this;
    }

    internal List<FunctionDefinition> Build()
    {
        return _functions;
    }
}
