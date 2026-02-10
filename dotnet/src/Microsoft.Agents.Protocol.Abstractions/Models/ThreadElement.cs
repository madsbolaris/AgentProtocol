// Manual interface definition for ThreadElement
// This interface marks types that can be thread elements

namespace Microsoft.Agents
{
    /// <summary>
    /// Thread Element Union
    ///
    /// Marker interface for all possible thread children.
    /// Enables heterogeneous content with preserved ordering.
    ///
    /// ELEMENTS:
    /// - ChatMessage: User, agent, tool, system messages
    /// - Expect: Evaluation expectation with judges and assertions
    /// - EvalRun: Goal-based execution instruction
    /// - Review: Post-run evaluation
    ///
    /// SERIALIZATION:
    /// - XML: Element type determined by XML element name (&lt;user&gt;, &lt;expect&gt;, &lt;run&gt;, &lt;review&gt;)
    /// - JSON: Type determined by object structure/properties
    /// </summary>
    public interface ThreadElement
    {
    }
}
