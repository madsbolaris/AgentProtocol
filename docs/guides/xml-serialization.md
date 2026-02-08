# XML Message Serialization

> **Core Concept**: Agent XML turns agent conversations into inspectable, versionable documents — not opaque runtime artifacts.

## Level 1: Why should I care? (30 seconds)

### The Problem: Conversations as Black Boxes

Most agent frameworks treat conversations as opaque payloads optimized for machines:

```json
{"messages":[{"role":"user","content":[{"type":"text","text":"What's the weather?"}]}]}
```

**Result**: Hard to read, hard to debug, hard to version, hard to reuse.

### The Solution: Conversations as Documents

Agent XML treats conversations as human-readable documents optimized for humans *and* machines:

```xml
<user user-id="alice" created-at="2026-02-07T10:00:00Z">
  <text>What's the weather in Seattle?</text>
</user>
```

**Result**: Readable at a glance, editable without tooling, diffable in Git.

---

### Why This Matters

Conversations become **artifacts**, not ephemeral logs:

- ✅ Read and edit without parsing code
- ✅ Version control with meaningful diffs
- ✅ Validate against schema at build time
- ✅ Reuse as test data, eval sets, compliance logs

*The same XML can also render directly as UI — no mapping, no adapters.*

---

## Level 2: Show me a quick example (2 minutes)

### Basic Usage

=== "Python"

    {% include-test "basic-xml-serialization" language="python" %}

=== "C#"

    {% include-test "basic-xml-serialization" language="csharp" %}

### Output

The serialized XML looks like this:

{% include-result "basic-xml-serialization" language="python" %}

### Deserialize Back

=== "Python"

    {% include-test "basic-xml-deserialization" language="python" %}

=== "C#"

    {% include-test "basic-xml-deserialization" language="csharp" %}

**This XML is now your log, test case, eval input, and UI preview.**

---

## Level 3: Real-world use cases (5 minutes)

### Use Case #1: Debugging & Production Observability

**Problem**: Agent misbehavior is hard to diagnose with logs alone.

**Solution**: Save complete conversations as XML artifacts.

```xml
<!-- logs/conversation-2026-02-07-error.xml -->
<thread thread-id="conv_abc123">
  <user user-id="alice">Book me a flight to Paris</user>
  <agent>
    <thinking exposed="true" audience="developer">
      User wants flight booking. Need departure city...
    </thinking>
    <function-call call-id="call_001" name="search_flights">
      {"origin": null, "destination": "Paris"}
    </function-call>
  </agent>
  <tool>
    <function-result call-id="call_001" is-error="true">
      {"error": "origin required"}
    </function-result>
  </tool>
</thread>
```

**Benefits**:
- Open the XML file, see the complete conversation
- Exposed thinking shows agent's internal reasoning
- Function calls and errors are clearly structured
- Reproduce the issue by replaying the XML

**Impact**: Debug production issues without instrumenting code.

---

### Use Case #2: Test & Eval Authoring

**Problem**: Writing test data as nested JSON objects is tedious and error-prone.

**Solution**: Author tests directly in XML.

```xml
<!-- test-data/scenarios/multimodal-query.xml -->
<user user-id="test_user">
  <text>What's in this image?</text>
  <image uri="https://example.com/photo.jpg" />
</user>
```

**Working with Multimodal Test Data**:

=== "Python"

    {% include-test "multimodal-message" language="python" %}

=== "C#"

    {% include-test "multimodal-message" language="csharp" %}

The multimodal message serializes to:

{% include-result "multimodal-message" language="python" %}

**Test Implementation**:
```csharp
[Theory]
[XmlFileData("test-data/scenarios/*.xml")]
public async Task Agent_Should_Handle_Scenario(string xmlPath)
{
    var xml = File.ReadAllText(xmlPath);
    var message = serializer.Deserialize(xml);

    var response = await agent.ProcessAsync(message);

    Assert.NotNull(response);
}
```

**Eval Pipeline**:
```csharp
// Run evals against all test scenarios
var testFiles = Directory.GetFiles("test-data/scenarios", "*.xml");
var results = await evaluator.RunBatchAsync(testFiles);

// Generate eval report
var report = EvalReport.Generate(results);
// Shows pass/fail rates, latency, quality scores
```

**Eval Results Matching**:
```csharp
// Compare actual output to expected output using XML
var expected = File.ReadAllText("test-data/expected/weather-query.xml");
var actual = serializer.Serialize(agentResponse);

// Option 1: Structural comparison (ignores timestamps, IDs)
var comparer = new XmlComparer(ignoreAttributes: new[] { "created-at", "call-id" });
var diff = comparer.Compare(expected, actual);

if (diff.HasDifferences)
{
    Console.WriteLine($"Differences found:");
    foreach (var change in diff.Changes)
    {
        Console.WriteLine($"  {change.Path}: expected '{change.Expected}', got '{change.Actual}'");
    }
}

// Option 2: Assert specific elements
var actualDoc = XDocument.Parse(actual);
Assert.Equal("get_weather", actualDoc.Descendants("function-call").First().Attribute("name").Value);
Assert.Contains("Seattle", actualDoc.Descendants("text").First().Value);

// Option 3: Git-style diff for human review
var diffText = XmlDiff.GenerateUnifiedDiff(expected, actual);
// Shows:
//   <agent>
// -   <text>The weather is 45°F</text>
// +   <text>The weather is 52°F</text>
//   </agent>
```

**Benefits**:
- Write test cases without C# boilerplate
- Same XML files used for unit tests, integration tests, and evals
- Non-engineers can contribute test scenarios
- Version control shows semantic diffs
- **XML diff tools show exactly what changed in eval results**
- **Expected vs actual comparisons are human-readable**
- **Assert on specific elements without parsing complex JSON**

**Impact**: Test authoring is significantly faster; eval datasets are easier to maintain; eval failures are easier to diagnose.

---

### Use Case #3: Compliance & Audit

**Problem**: Proving what an agent said requires complete conversation logs.

**Solution**: XML provides durable, validated records.

```xml
<thread thread-id="support_case_456" created-at="2026-02-07T14:23:10Z">
  <system>
    <text audience="developer">HIPAA-compliant agent session</text>
  </system>
  <user user-id="patient_789">
    <text encrypted="true" pii-category="health">...</text>
  </user>
  <agent agent-id="med-assistant">
    <text>Based on your symptoms, I recommend...</text>
  </agent>
</thread>
```

**Benefits**:
- Complete audit trail with timestamps
- PII and encryption markers visible
- Schema validation ensures structural integrity
- Human-readable for compliance reviews

**Impact**: Meet regulatory requirements with verifiable conversation records.

---

## Level 4: Advanced patterns (10 minutes)

### Working with Test Data Files

You can load and work with XML test data files:

{% include-test "read-xml-file" language="python" %}

### Result

{% include-result "read-xml-file" language="python" %}

### Schema Validation

Agent XML uses TypeSpec to define the schema, enabling validation at build and runtime:

=== "Python"

    {% include-test "content-validation" language="python" %}

=== "C#"

    {% include-test "content-validation" language="csharp" %}

**This is not a debug format — it's the canonical wire + storage + test format validated by the Agent Protocol contract.**

---

### Patterns You Unlock

Once conversations are artifacts, you can:

#### Pattern 1: Conversation-as-Test

**Tool execution flows**:

=== "C#"

    {% include-test "tool-call-message" language="csharp" %}

Result:

{% include-result "tool-call-message" language="csharp" %}

**Synthetic data generation**:
```bash
# Generate 1000 variations of a scenario
./generate-test-data --template base-scenario.xml --count 1000 --vary user-id,query
```

---

#### Pattern 2: Conversation-as-Data

**A/B testing**:
```xml
<!-- variant-a.xml -->
<agent persona="concise">
  <text>Weather: 52°F, cloudy.</text>
</agent>

<!-- variant-b.xml -->
<agent persona="friendly">
  <text>The weather in Seattle is currently 52°F with cloudy skies. Don't forget your jacket!</text>
</agent>
```

**Branching scenarios**:
```xml
<thread thread-id="demo">
  <user>Help me book a flight</user>
  <agent>
    <text>Where are you departing from?</text>
    <suggested-actions>
      <action title="San Francisco" value="SFO" />
      <action title="New York" value="JFK" />
    </suggested-actions>
  </agent>
  <!-- Branch 1: user selects SFO -->
  <!-- Branch 2: user selects JFK -->
</thread>
```

---

#### Pattern 3: Conversation-as-UI

The XML schema maps 1:1 to UI component structures. React makes this mapping trivial:

```
XML:  <user><text>Hello</text></user>
JSX:  <User><Text>Hello</Text></User>
```

Same structure, minimal adjustments. The XML you write for testing becomes the JSX you use for rendering.

*See [Full-Stack Integration Patterns](xml-full-stack-patterns.md) for React integration, Storybook, E2E testing, and backend templating.*

---

#### Pattern 4: Conversation-as-Audit

```xml
<thread thread-id="compliance_789">
  <system created-at="2026-02-07T10:00:00Z">
    <text audience="auditor">Session started - GDPR compliant</text>
  </system>
  <user user-id="customer_456">
    <text pii="true" encrypted="aes256">Personal data...</text>
  </user>
  <agent>
    <text audience="user">I can help with that.</text>
  </agent>
</thread>
```

Complete audit trails with timestamps, PII markers, and access control attributes.

---

## Level 5: Round-Trip Fidelity

The Agent Protocol guarantees perfect serialization/deserialization fidelity:

=== "C#"

    {% include-test "round-trip-fidelity" language="csharp" %}

This ensures that:
- Type safety is maintained
- All metadata is preserved
- Validation happens at build and runtime
- No data loss during serialization

---

## Level 6: Getting started now

### Install (1 minute)

```bash
dotnet add package Microsoft.Agents.Xml
```

### First Message (2 minutes)

=== "Python"

    {% include-test "user-message" language="python" %}

=== "C#"

    {% include-test "user-message" language="csharp" %}

### Add to Your Agent (5 minutes)

```csharp
// Log conversations
var xml = serializer.Serialize(conversation);
File.WriteAllText($"logs/{conversationId}.xml", xml);

// Load for debugging
var conversation = serializer.Deserialize(File.ReadAllText("logs/abc123.xml"));
```

### Next Steps

1. **Serialize one conversation** (5 min)
   - Add XML serialization to your agent's response handler
   - Print to console or save to file

2. **Create a test scenario** (5 min)
   - Write an XML file with a user message
   - Deserialize and process through your agent
   - Assert the response structure

3. **Add conversation logging** (10 min)
   - Log all conversations to XML files
   - Debug your next issue by examining the XML

---

## Resources

- 📚 [XML Schema Reference](../api-reference/xml-schema-reference.md) - All content types, validation
- 🚀 [Full-Stack Integration Patterns](xml-full-stack-patterns.md) - React integration, E2E testing, backend templating
- 🧪 [Eval Strategy Guide](xml-eval-strategy.md) - Beyond exact matching for robust evaluations
- 🧪 [400+ Test Examples](../../test-data/input/) - Real XML scenarios
- 📖 [Agent Protocol Spec](../specifications/index.md) - Complete specification

---

## Summary: Why Agent XML?

**Core value**: Conversations as inspectable, versionable documents.

**Key benefits**:
- Readable and editable without tooling
- Git-diffable for version control
- Schema-validated for correctness
- Reusable across debugging, testing, evaluation, UI, and compliance

**When to use**:
- You need to debug agent behavior
- You're building test/eval infrastructure
- You need audit trails for compliance
- You want full-stack consistency (backend → UI)

**When not to use**:
- Pure runtime communication where humans never inspect data
- Performance-critical paths requiring binary formats
- Simple logging where structure doesn't matter

---

**Start small**: Serialize one conversation today. See the value immediately.

**Scale up**: Use XML as your source of truth across debugging, testing, evals, UI, and compliance.

---

!!! tip "Test-Driven Documentation"
    All code examples on this page are extracted from actual test files and are guaranteed to work.
    The outputs shown are captured from running tests.

    - Python examples: `python/microsoft-agents-xml/tests/test_doc_examples.py`
    - C# examples: `dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/RoundTripTests.cs`
