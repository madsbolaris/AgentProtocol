# Agent XML Eval Strategy: Beyond Exact Matching

> **Problem**: XML exact matching is too brittle for real-world evals. Agents should pass if they're semantically correct, even if wording differs.

---

## The Eval Pyramid

Different eval scenarios require different levels of strictness:

```
┌─────────────────────────────┐
│   Exact Match (5%)          │  Structure validation, schema compliance
├─────────────────────────────┤
│   Structural Match (15%)    │  Right elements, flexible content
├─────────────────────────────┤
│   Semantic Match (30%)      │  Fuzzy matching, synonyms, paraphrasing
├─────────────────────────────┤
│   LLM-as-Judge (40%)        │  Meaning, quality, appropriateness
├─────────────────────────────┤
│   Hybrid (10%)              │  Combine multiple approaches
└─────────────────────────────┘
```

**Key insight**: Most evals should use semantic matching or LLM-as-judge, not exact matching.

---

## Current State: Exact Matching (Too Brittle)

**Example Test**:
```xml
<!-- expected.xml -->
<agent>
  <text>The weather in Seattle is 52°F and cloudy.</text>
</agent>
```

**Actual Output**:
```xml
<!-- actual.xml -->
<agent>
  <text>It's 52°F and cloudy in Seattle.</text>
</agent>
```

**Problem**: Fails exact match, but semantically correct ❌

---

## Approach 1: Structural Assertions

**Concept**: Assert on XML structure, not exact content.

### Pattern 1.1: Element Presence

```csharp
// Assert: Agent must include a function call to "get_weather"
var actualDoc = XDocument.Parse(actualXml);

var functionCall = actualDoc
    .Descendants("function-call")
    .FirstOrDefault(fc => fc.Attribute("name")?.Value == "get_weather");

Assert.NotNull(functionCall); // Passes if function was called
```

### Pattern 1.2: Content Containment

```csharp
// Assert: Agent must mention "Seattle" and "52"
var text = actualDoc.Descendants("text").First().Value;

Assert.Contains("Seattle", text, StringComparison.OrdinalIgnoreCase);
Assert.Contains("52", text);
```

### Pattern 1.3: Attribute Validation

```csharp
// Assert: Function call must include location parameter
var functionCallContent = actualDoc.Descendants("function-call").First().Value;
var args = JsonSerializer.Deserialize<Dictionary<string, object>>(functionCallContent);

Assert.True(args.ContainsKey("location"));
Assert.Contains("Seattle", args["location"].ToString());
```

### When to Use
- ✅ Testing agent follows correct flow (calls right functions)
- ✅ Ensuring required information is present
- ✅ Validating structure before content
- ❌ Not suitable for nuanced quality judgments

---

## Approach 2: Fuzzy Matching

**Concept**: Allow variations in phrasing, formatting, and synonyms.

### Pattern 2.1: Normalized String Comparison

```csharp
public class FuzzyMatcher
{
    public static bool FuzzyEquals(string expected, string actual, double threshold = 0.85)
    {
        // Normalize: lowercase, trim, remove punctuation
        var normalizedExpected = Normalize(expected);
        var normalizedActual = Normalize(actual);

        // Calculate similarity score (Levenshtein distance, Jaccard, etc.)
        var similarity = CalculateSimilarity(normalizedExpected, normalizedActual);

        return similarity >= threshold;
    }

    private static string Normalize(string text)
    {
        return Regex.Replace(
            text.ToLowerInvariant().Trim(),
            @"[^\w\s]", // Remove punctuation
            ""
        );
    }

    private static double CalculateSimilarity(string s1, string s2)
    {
        // Jaccard similarity: intersection / union of words
        var words1 = new HashSet<string>(s1.Split(' '));
        var words2 = new HashSet<string>(s2.Split(' '));

        var intersection = words1.Intersect(words2).Count();
        var union = words1.Union(words2).Count();

        return (double)intersection / union;
    }
}

// Usage
var expected = "The weather in Seattle is 52°F and cloudy.";
var actual = "It's 52°F and cloudy in Seattle.";

Assert.True(FuzzyMatcher.FuzzyEquals(expected, actual));
// Passes: 85% word overlap
```

### Pattern 2.2: Synonym Matching

```csharp
public class SemanticMatcher
{
    private static readonly Dictionary<string, HashSet<string>> Synonyms = new()
    {
        ["weather"] = new() { "weather", "conditions", "forecast", "temperature" },
        ["cloudy"] = new() { "cloudy", "overcast", "gray", "grey", "clouds" },
        ["degrees"] = new() { "°F", "°C", "degrees", "fahrenheit", "celsius" }
    };

    public static bool ContainsSynonym(string text, string term)
    {
        var textLower = text.ToLowerInvariant();

        if (Synonyms.TryGetValue(term.ToLowerInvariant(), out var synonyms))
        {
            return synonyms.Any(syn => textLower.Contains(syn));
        }

        return textLower.Contains(term.ToLowerInvariant());
    }
}

// Usage
var text = "The forecast shows 52 degrees with overcast skies.";

Assert.True(SemanticMatcher.ContainsSynonym(text, "weather"));   // "forecast" is synonym
Assert.True(SemanticMatcher.ContainsSynonym(text, "cloudy"));    // "overcast" is synonym
Assert.True(SemanticMatcher.ContainsSynonym(text, "degrees"));   // exact match
```

### Pattern 2.3: Regex-Based Assertions

```csharp
// Assert: Agent must mention temperature in range 50-55°F
var text = actualDoc.Descendants("text").First().Value;

var tempPattern = @"5[0-5]\s*°?F";
Assert.True(Regex.IsMatch(text, tempPattern));

// Assert: Agent must mention Seattle (with flexible spelling)
var locationPattern = @"Seattle|Seatle|Sea-ttle"; // Common misspellings
Assert.True(Regex.IsMatch(text, locationPattern, RegexOptions.IgnoreCase));
```

### When to Use
- ✅ Allow natural language variation
- ✅ Handle different number formats (52°F, 52 degrees, 52F)
- ✅ Accept synonyms and paraphrasing
- ❌ Still limited to predefined patterns

---

## Approach 3: LLM-as-Judge (Most Flexible)

**Concept**: Use an LLM to evaluate if actual output is semantically equivalent to expected.

### Pattern 3.1: Binary Pass/Fail

```csharp
public class LLMJudge
{
    private readonly LLMClient _llm;

    public async Task<bool> IsSemanticMatch(string expected, string actual)
    {
        var prompt = $@"
Compare these two agent responses. Are they semantically equivalent?

Expected: {expected}
Actual: {actual}

Answer ONLY 'YES' or 'NO'.
";

        var response = await _llm.GenerateAsync(prompt);
        return response.Trim().ToUpperInvariant() == "YES";
    }
}

// Usage
var judge = new LLMJudge(llmClient);

var expected = "<agent><text>The weather in Seattle is 52°F and cloudy.</text></agent>";
var actual = "<agent><text>It's 52°F and cloudy in Seattle.</text></agent>";

var passed = await judge.IsSemanticMatch(expected, actual);
// Returns: true (semantically equivalent)
```

### Pattern 3.2: Scored Evaluation

```csharp
public class ScoredLLMJudge
{
    public async Task<EvalResult> EvaluateQuality(string expected, string actual)
    {
        var prompt = $@"
Evaluate this agent response on a scale of 1-5.

Expected response: {expected}
Actual response: {actual}

Rate on these criteria:
- Accuracy (correct information)
- Completeness (all required info)
- Clarity (easy to understand)
- Naturalness (sounds human)

Return JSON:
{{
  ""accuracy"": 1-5,
  ""completeness"": 1-5,
  ""clarity"": 1-5,
  ""naturalness"": 1-5,
  ""overall"": 1-5,
  ""reasoning"": ""explanation""
}}
";

        var response = await _llm.GenerateAsync(prompt);
        return JsonSerializer.Deserialize<EvalResult>(response);
    }
}

// Usage
var result = await judge.EvaluateQuality(expectedXml, actualXml);

Console.WriteLine($"Overall: {result.Overall}/5");
Console.WriteLine($"Accuracy: {result.Accuracy}/5");
Console.WriteLine($"Reasoning: {result.Reasoning}");

Assert.True(result.Overall >= 4); // Pass if 4+ overall
```

### Pattern 3.3: Rubric-Based Evaluation

```csharp
public class RubricJudge
{
    public async Task<RubricResult> EvaluateAgainstRubric(
        string actual,
        EvalRubric rubric)
    {
        var criteriaText = string.Join("\n", rubric.Criteria.Select((c, i) =>
            $"{i + 1}. {c.Name}: {c.Description}"
        ));

        var prompt = $@"
Evaluate this agent response against the rubric below.

Agent response:
{actual}

Rubric:
{criteriaText}

For each criterion, assign:
- PASS: Fully meets criterion
- PARTIAL: Partially meets criterion
- FAIL: Does not meet criterion

Return JSON:
{{
  ""results"": [
    {{""criterion"": ""name"", ""score"": ""PASS|PARTIAL|FAIL"", ""reason"": ""explanation""}},
    ...
  ]
}}
";

        var response = await _llm.GenerateAsync(prompt);
        return JsonSerializer.Deserialize<RubricResult>(response);
    }
}

// Usage
var rubric = new EvalRubric
{
    Criteria = new[]
    {
        new Criterion("Calls get_weather function", "Agent must call get_weather"),
        new Criterion("Mentions Seattle", "Response includes Seattle location"),
        new Criterion("Includes temperature", "Response states temperature"),
        new Criterion("Describes conditions", "Response mentions weather conditions")
    }
};

var result = await judge.EvaluateAgainstRubric(actualXml, rubric);

foreach (var criterionResult in result.Results)
{
    Console.WriteLine($"{criterionResult.Criterion}: {criterionResult.Score}");
    Console.WriteLine($"  Reason: {criterionResult.Reason}");
}

var passedAll = result.Results.All(r => r.Score == "PASS");
```

### Pattern 3.4: Comparative Ranking (A/B Testing)

```csharp
public class ComparativeJudge
{
    public async Task<ComparisonResult> CompareResponses(
        string responseA,
        string responseB,
        string criteria)
    {
        var prompt = $@"
Compare these two agent responses based on: {criteria}

Response A:
{responseA}

Response B:
{responseB}

Which is better?

Return JSON:
{{
  ""winner"": ""A"" | ""B"" | ""TIE"",
  ""confidence"": 1-5,
  ""reasoning"": ""explanation""
}}
";

        var response = await _llm.GenerateAsync(prompt);
        return JsonSerializer.Deserialize<ComparisonResult>(response);
    }
}

// Usage - A/B test two agent versions
var modelA = await agentV1.ProcessAsync(input);
var modelB = await agentV2.ProcessAsync(input);

var result = await judge.CompareResponses(
    serializer.Serialize(modelA),
    serializer.Serialize(modelB),
    "Helpfulness and accuracy"
);

Console.WriteLine($"Winner: {result.Winner}");
Console.WriteLine($"Confidence: {result.Confidence}/5");
Console.WriteLine($"Reasoning: {result.Reasoning}");
```

### When to Use
- ✅ Evaluating natural language quality
- ✅ Nuanced judgments (tone, helpfulness, clarity)
- ✅ When human eval would be subjective
- ✅ A/B testing different agent versions
- ⚠️ More expensive (LLM API costs)
- ⚠️ Non-deterministic (can vary between runs)

---

## Approach 4: Hybrid Strategies

**Concept**: Combine multiple approaches for robust evals.

### Pattern 4.1: Tiered Evaluation

```csharp
public class TieredEvaluator
{
    public async Task<TieredResult> Evaluate(string expected, string actual)
    {
        var result = new TieredResult();

        // Tier 1: Structural validation (fast, strict)
        result.StructuralMatch = ValidateStructure(expected, actual);
        if (!result.StructuralMatch)
        {
            result.FailureReason = "Structure mismatch";
            return result; // Fail fast
        }

        // Tier 2: Fuzzy content matching (fast, flexible)
        result.FuzzyMatch = FuzzyMatcher.FuzzyEquals(
            ExtractText(expected),
            ExtractText(actual),
            threshold: 0.7
        );

        if (result.FuzzyMatch)
        {
            result.Passed = true;
            return result; // Pass early if fuzzy match succeeds
        }

        // Tier 3: LLM judge (slow, most flexible)
        result.LLMScore = await LLMJudge.EvaluateQuality(expected, actual);
        result.Passed = result.LLMScore.Overall >= 4;

        return result;
    }
}

// Usage
var result = await evaluator.Evaluate(expectedXml, actualXml);

Console.WriteLine($"Structural: {result.StructuralMatch}");
Console.WriteLine($"Fuzzy: {result.FuzzyMatch}");
Console.WriteLine($"LLM Score: {result.LLMScore?.Overall}/5");
Console.WriteLine($"PASSED: {result.Passed}");
```

### Pattern 4.2: Critical vs Non-Critical Assertions

```csharp
public class CriticalityEvaluator
{
    public EvalResult Evaluate(string actual, EvalSpec spec)
    {
        var result = new EvalResult { Passed = true };

        // Critical assertions (must pass)
        foreach (var assertion in spec.CriticalAssertions)
        {
            var passed = EvaluateAssertion(actual, assertion);
            result.CriticalResults.Add(assertion.Name, passed);

            if (!passed)
            {
                result.Passed = false;
                result.FailureReason = $"Critical assertion failed: {assertion.Name}";
                return result; // Fail immediately
            }
        }

        // Non-critical assertions (nice to have)
        foreach (var assertion in spec.NonCriticalAssertions)
        {
            var passed = EvaluateAssertion(actual, assertion);
            result.NonCriticalResults.Add(assertion.Name, passed);
            // Continue even if failed
        }

        result.QualityScore = CalculateQualityScore(result);
        return result;
    }
}

// Usage
var spec = new EvalSpec
{
    CriticalAssertions = new[]
    {
        new Assertion("Calls get_weather function", AssertionType.ElementExists, "function-call[@name='get_weather']"),
        new Assertion("Includes location", AssertionType.ContentContains, "Seattle")
    },
    NonCriticalAssertions = new[]
    {
        new Assertion("Mentions temperature unit", AssertionType.Regex, @"°F|degrees"),
        new Assertion("Polite tone", AssertionType.LLMJudge, "Response is polite and professional")
    }
};

var result = evaluator.Evaluate(actualXml, spec);

Console.WriteLine($"Passed: {result.Passed}");
Console.WriteLine($"Quality Score: {result.QualityScore}/100");
```

### Pattern 4.3: Human-in-the-Loop Fallback

```csharp
public class HumanInLoopEvaluator
{
    public async Task<EvalResult> Evaluate(string expected, string actual)
    {
        // Try automated evals first
        var structuralMatch = ValidateStructure(expected, actual);
        var fuzzyMatch = FuzzyMatcher.FuzzyEquals(ExtractText(expected), ExtractText(actual));
        var llmScore = await LLMJudge.EvaluateQuality(expected, actual);

        // If clear pass or fail, no human needed
        if (structuralMatch && fuzzyMatch && llmScore.Overall >= 4)
        {
            return EvalResult.Pass("Automated evals passed");
        }

        if (!structuralMatch || llmScore.Overall <= 2)
        {
            return EvalResult.Fail("Automated evals failed");
        }

        // Ambiguous case - request human review
        return await RequestHumanReview(expected, actual, new
        {
            StructuralMatch = structuralMatch,
            FuzzyScore = fuzzyMatch ? 1.0 : 0.0,
            LLMScore = llmScore.Overall
        });
    }

    private async Task<EvalResult> RequestHumanReview(
        string expected,
        string actual,
        object automatedScores)
    {
        // Queue for human review
        var reviewId = await _reviewQueue.EnqueueAsync(new ReviewRequest
        {
            Expected = expected,
            Actual = actual,
            AutomatedScores = automatedScores,
            Priority = "medium"
        });

        // Wait for human decision (or timeout)
        var review = await _reviewQueue.WaitForReviewAsync(reviewId, timeout: TimeSpan.FromHours(24));

        return review.Approved
            ? EvalResult.Pass($"Human approved: {review.Comments}")
            : EvalResult.Fail($"Human rejected: {review.Comments}");
    }
}
```

---

## Recommended Eval Framework

### Complete Implementation

```csharp
public class AgentXmlEvaluator
{
    private readonly XmlComparer _comparer;
    private readonly FuzzyMatcher _fuzzyMatcher;
    private readonly LLMJudge _llmJudge;

    public async Task<EvalResult> Evaluate(string expectedXml, string actualXml, EvalOptions options)
    {
        var result = new EvalResult { TestName = options.TestName };

        // Step 1: Parse XML
        var expectedDoc = XDocument.Parse(expectedXml);
        var actualDoc = XDocument.Parse(actualXml);

        // Step 2: Structural validation (always run)
        result.Structural = EvaluateStructure(expectedDoc, actualDoc, options);

        if (!result.Structural.Passed && options.StructureRequired)
        {
            result.Passed = false;
            result.FailureReason = "Structure validation failed";
            return result;
        }

        // Step 3: Custom assertions (if provided)
        if (options.Assertions?.Any() == true)
        {
            result.Assertions = EvaluateAssertions(actualDoc, options.Assertions);

            var criticalFailed = result.Assertions.Any(a => a.Critical && !a.Passed);
            if (criticalFailed)
            {
                result.Passed = false;
                result.FailureReason = "Critical assertion failed";
                return result;
            }
        }

        // Step 4: Content evaluation (fuzzy or LLM)
        switch (options.ContentEvalMode)
        {
            case EvalMode.Exact:
                result.Content = EvaluateExact(expectedXml, actualXml);
                break;

            case EvalMode.Fuzzy:
                result.Content = EvaluateFuzzy(expectedDoc, actualDoc, options.FuzzyThreshold);
                break;

            case EvalMode.LLM:
                result.Content = await EvaluateLLM(expectedXml, actualXml, options.LLMPrompt);
                break;

            case EvalMode.Hybrid:
                result.Content = await EvaluateHybrid(expectedDoc, actualDoc, options);
                break;
        }

        result.Passed = result.Content.Passed;
        result.Score = CalculateOverallScore(result);

        return result;
    }

    private ContentEvalResult EvaluateFuzzy(XDocument expected, XDocument actual, double threshold)
    {
        var expectedText = string.Join(" ", expected.Descendants("text").Select(e => e.Value));
        var actualText = string.Join(" ", actual.Descendants("text").Select(e => e.Value));

        var similarity = _fuzzyMatcher.CalculateSimilarity(expectedText, actualText);

        return new ContentEvalResult
        {
            Passed = similarity >= threshold,
            Score = similarity,
            Details = $"Similarity: {similarity:P}"
        };
    }

    private async Task<ContentEvalResult> EvaluateLLM(
        string expectedXml,
        string actualXml,
        string promptTemplate)
    {
        var score = await _llmJudge.EvaluateQuality(expectedXml, actualXml, promptTemplate);

        return new ContentEvalResult
        {
            Passed = score.Overall >= 4,
            Score = score.Overall / 5.0,
            Details = score.Reasoning
        };
    }
}
```

### Usage Examples

```csharp
// Example 1: Structural + Fuzzy
var options = new EvalOptions
{
    TestName = "weather_query",
    StructureRequired = true,
    ContentEvalMode = EvalMode.Fuzzy,
    FuzzyThreshold = 0.8
};

var result = await evaluator.Evaluate(expectedXml, actualXml, options);

// Example 2: Structural + Assertions + LLM
var options = new EvalOptions
{
    TestName = "customer_support",
    StructureRequired = false,
    ContentEvalMode = EvalMode.LLM,
    LLMPrompt = "Evaluate helpfulness and professionalism",
    Assertions = new[]
    {
        new Assertion("Acknowledges issue", "//text[contains(., 'sorry') or contains(., 'understand')]"),
        new Assertion("Provides solution", "//text[contains(., 'can help') or contains(., 'will resolve')]")
    }
};

// Example 3: Hybrid approach
var options = new EvalOptions
{
    ContentEvalMode = EvalMode.Hybrid,
    FuzzyThreshold = 0.7,
    LLMFallbackThreshold = 0.85 // Use LLM if fuzzy score is between 0.7-0.85
};
```

---

## Best Practices

### 1. Choose the Right Evaluation Mode

| Scenario | Recommended Mode | Why |
|----------|------------------|-----|
| Schema validation | Exact | Need precise structure |
| Function call verification | Structural | Element presence matters, content flexible |
| Natural language responses | Fuzzy or LLM | Allow rephrasing |
| Creative outputs | LLM | Subjective quality judgment needed |
| High-stakes decisions | Hybrid + Human | Combine multiple approaches |

### 2. Start Strict, Relax Over Time

```csharp
// Phase 1: Development - strict matching to catch obvious issues
var devOptions = new EvalOptions { ContentEvalMode = EvalMode.Exact };

// Phase 2: Testing - fuzzy matching to allow natural variation
var testOptions = new EvalOptions { ContentEvalMode = EvalMode.Fuzzy, FuzzyThreshold = 0.8 };

// Phase 3: Production - LLM judge for quality
var prodOptions = new EvalOptions { ContentEvalMode = EvalMode.LLM };
```

### 3. Cache LLM Judgments

```csharp
public class CachedLLMJudge
{
    private readonly ICache _cache;

    public async Task<LLMScore> EvaluateQuality(string expected, string actual)
    {
        var cacheKey = ComputeHash(expected + actual);

        if (_cache.TryGet(cacheKey, out LLMScore cached))
        {
            return cached; // Reuse previous judgment
        }

        var score = await _llm.GenerateAsync(expected, actual);
        _cache.Set(cacheKey, score, TimeSpan.FromDays(30));

        return score;
    }
}
```

### 4. Track Eval Metrics Over Time

```csharp
public class EvalMetricsTracker
{
    public void RecordEval(EvalResult result)
    {
        _metrics.Record(new
        {
            Timestamp = DateTime.UtcNow,
            TestName = result.TestName,
            Passed = result.Passed,
            Score = result.Score,
            EvalMode = result.Options.ContentEvalMode,
            DurationMs = result.DurationMs
        });
    }

    public EvalReport GenerateReport(DateTime since)
    {
        var evals = _metrics.GetEvalsSince(since);

        return new EvalReport
        {
            TotalEvals = evals.Count,
            PassRate = evals.Average(e => e.Passed ? 1.0 : 0.0),
            AverageScore = evals.Average(e => e.Score),
            ByMode = evals.GroupBy(e => e.EvalMode)
                .ToDictionary(g => g.Key, g => new
                {
                    Count = g.Count(),
                    PassRate = g.Average(e => e.Passed ? 1.0 : 0.0)
                })
        };
    }
}
```

---

## Implementation Roadmap

### Phase 1: Structural + Fuzzy (Week 1-2)

- ✅ Implement XML structure validator
- ✅ Build fuzzy text matcher with configurable threshold
- ✅ Create assertion framework (XPath-based)
- ✅ Add fuzzy eval mode to evaluator

### Phase 2: LLM Integration (Week 3-4)

- ✅ Integrate LLM client (OpenAI, Anthropic, etc.)
- ✅ Implement prompt templates for binary/scored/rubric evals
- ✅ Add LLM eval mode to evaluator
- ✅ Cache LLM judgments

### Phase 3: Hybrid Strategies (Week 5-6)

- ✅ Implement tiered evaluation (fast → slow)
- ✅ Add critical vs non-critical assertion support
- ✅ Build human-in-the-loop fallback
- ✅ Create eval metrics tracking

### Phase 4: Optimization (Week 7-8)

- ✅ Batch eval processing
- ✅ Parallel evaluation
- ✅ Cost optimization (prefer cheap methods)
- ✅ Performance profiling

---

## Summary

**Key Takeaway**: XML exact matching is a starting point, not the end goal.

**Recommended Approach**:
1. **Always**: Validate XML structure (fast, catches obvious errors)
2. **Usually**: Use fuzzy matching for content (balances flexibility and speed)
3. **When needed**: Add LLM-as-judge for subjective quality (expensive but flexible)
4. **Best practice**: Combine multiple approaches in a tiered strategy

**Cost vs Accuracy Trade-off**:
```
Exact Match:     $0.00 / eval,  60% accuracy  ❌ Too brittle
Fuzzy Match:     $0.00 / eval,  85% accuracy  ✅ Good balance
LLM-as-Judge:    $0.05 / eval,  95% accuracy  ✅ Best quality
Hybrid:          $0.01 / eval,  90% accuracy  ✅ Optimal
```

**Start here**: Implement structural assertions + fuzzy matching. Add LLM-as-judge for 20% of evals where fuzzy matching is ambiguous.

---

*Last Updated: 2026-02-08*
