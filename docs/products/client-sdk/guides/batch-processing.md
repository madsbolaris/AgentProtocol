# Batch Processing

Process multiple requests efficiently with parallel execution and batch APIs.

## Overview

When you need to process many requests (e.g., analyzing hundreds of documents, generating summaries for multiple articles, or processing user questions in bulk), batch processing improves throughput and resource utilization through parallel execution and optimized API usage.

---

## Sequential Processing (Baseline)

The naive approach processes requests one at a time:

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient

    client = AgentProtocolClient("http://localhost:5000")

    documents = ["doc1.txt", "doc2.txt", "doc3.txt", ...]  # 100 documents

    # Sequential processing - SLOW
    summaries = []
    for doc in documents:
        with open(doc) as f:
            content = f.read()
        summary = await client.complete_chat(f"Summarize: {content}")
        summaries.append(summary)

    # Total time: ~5 seconds × 100 = 500 seconds (8+ minutes)
    ```

=== "TypeScript"

    ```typescript
    const client = new AgentProtocolClient("http://localhost:5000");

    const documents = ["doc1.txt", "doc2.txt", "doc3.txt", ...];

    // Sequential processing - SLOW
    const summaries = [];
    for (const doc of documents) {
        const content = await fs.readFile(doc, 'utf-8');
        const summary = await client.completeChat(`Summarize: ${content}`);
        summaries.push(summary);
    }
    ```

=== "C#"

    ```csharp
    var client = new AgentProtocolClient("http://localhost:5000");

    var documents = new[] { "doc1.txt", "doc2.txt", "doc3.txt", ... };

    // Sequential processing - SLOW
    var summaries = new List<string>();
    foreach (var doc in documents)
    {
        var content = File.ReadAllText(doc);
        var summary = await client.CompleteChatAsync($"Summarize: {content}");
        summaries.Add(summary);
    }
    ```

**Problem:** Each request waits for the previous one to complete.

---

## Parallel Processing

Process multiple requests concurrently:

=== "Python"

    ```python
    import asyncio

    async def process_document(doc: str) -> str:
        """Process a single document."""
        with open(doc) as f:
            content = f.read()
        return await client.complete_chat(f"Summarize: {content}")

    # Process all documents in parallel
    documents = ["doc1.txt", "doc2.txt", "doc3.txt", ...]
    summaries = await asyncio.gather(*[
        process_document(doc) for doc in documents
    ])

    # Total time: ~5 seconds (limited by slowest request)
    # 100x faster than sequential!
    ```

=== "TypeScript"

    ```typescript
    async function processDocument(doc: string): Promise<string> {
        const content = await fs.readFile(doc, 'utf-8');
        return await client.completeChat(`Summarize: ${content}`);
    }

    // Process all documents in parallel
    const documents = ["doc1.txt", "doc2.txt", "doc3.txt", ...];
    const summaries = await Promise.all(
        documents.map(doc => processDocument(doc))
    );
    ```

=== "C#"

    ```csharp
    async Task<string> ProcessDocumentAsync(string doc)
    {
        var content = await File.ReadAllTextAsync(doc);
        return await client.CompleteChatAsync($"Summarize: {content}");
    }

    // Process all documents in parallel
    var documents = new[] { "doc1.txt", "doc2.txt", "doc3.txt", ... };
    var tasks = documents.Select(doc => ProcessDocumentAsync(doc));
    var summaries = await Task.WhenAll(tasks);
    ```

**Benefit:** All requests execute concurrently, dramatically reducing total time.

---

## Controlled Concurrency

Limit concurrent requests to avoid overwhelming the server:

=== "Python"

    ```python
    from asyncio import Semaphore

    async def process_with_limit(doc: str, semaphore: Semaphore) -> str:
        """Process document with concurrency limit."""
        async with semaphore:
            with open(doc) as f:
                content = f.read()
            return await client.complete_chat(f"Summarize: {content}")

    # Limit to 10 concurrent requests
    semaphore = Semaphore(10)
    documents = ["doc1.txt", "doc2.txt", ...]  # 100 documents

    summaries = await asyncio.gather(*[
        process_with_limit(doc, semaphore) for doc in documents
    ])

    # Total time: ~50 seconds (10 batches of 10 documents)
    ```

=== "TypeScript"

    ```typescript
    import pLimit from 'p-limit';

    const limit = pLimit(10);  // Max 10 concurrent

    async function processDocument(doc: string): Promise<string> {
        const content = await fs.readFile(doc, 'utf-8');
        return await client.completeChat(`Summarize: ${content}`);
    }

    const documents = ["doc1.txt", "doc2.txt", ...];
    const summaries = await Promise.all(
        documents.map(doc => limit(() => processDocument(doc)))
    );
    ```

=== "C#"

    ```csharp
    using System.Threading;

    var semaphore = new SemaphoreSlim(10);  // Max 10 concurrent

    async Task<string> ProcessWithLimit(string doc)
    {
        await semaphore.WaitAsync();
        try
        {
            var content = await File.ReadAllTextAsync(doc);
            return await client.CompleteChatAsync($"Summarize: {content}");
        }
        finally
        {
            semaphore.Release();
        }
    }

    var documents = new[] { "doc1.txt", "doc2.txt", ... };
    var tasks = documents.Select(doc => ProcessWithLimit(doc));
    var summaries = await Task.WhenAll(tasks);
    ```

---

## Batched Processing

Process items in fixed-size batches:

=== "Python"

    ```python
    from typing import List

    def chunk_list(items: List[str], chunk_size: int) -> List[List[str]]:
        """Split list into chunks."""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    async def process_batch(batch: List[str]) -> List[str]:
        """Process a batch of documents."""
        return await asyncio.gather(*[
            process_document(doc) for doc in batch
        ])

    # Process in batches of 10
    documents = ["doc1.txt", "doc2.txt", ...]
    batches = chunk_list(documents, chunk_size=10)

    all_summaries = []
    for i, batch in enumerate(batches):
        print(f"Processing batch {i+1}/{len(batches)}...")
        summaries = await process_batch(batch)
        all_summaries.extend(summaries)

        # Optional: Add delay between batches to respect rate limits
        if i < len(batches) - 1:
            await asyncio.sleep(1)
    ```

=== "TypeScript"

    ```typescript
    function chunkArray<T>(array: T[], chunkSize: number): T[][] {
        const chunks: T[][] = [];
        for (let i = 0; i < array.length; i += chunkSize) {
            chunks.push(array.slice(i, i + chunkSize));
        }
        return chunks;
    }

    async function processBatch(batch: string[]): Promise<string[]> {
        return await Promise.all(batch.map(doc => processDocument(doc)));
    }

    const documents = ["doc1.txt", "doc2.txt", ...];
    const batches = chunkArray(documents, 10);

    const allSummaries: string[] = [];
    for (const [i, batch] of batches.entries()) {
        console.log(`Processing batch ${i+1}/${batches.length}...`);
        const summaries = await processBatch(batch);
        allSummaries.push(...summaries);
    }
    ```

=== "C#"

    ```csharp
    IEnumerable<List<T>> ChunkList<T>(List<T> items, int chunkSize)
    {
        for (int i = 0; i < items.Count; i += chunkSize)
        {
            yield return items.Skip(i).Take(chunkSize).ToList();
        }
    }

    var documents = new List<string> { "doc1.txt", "doc2.txt", ... };
    var batches = ChunkList(documents, chunkSize: 10);

    var allSummaries = new List<string>();
    int batchNum = 0;
    foreach (var batch in batches)
    {
        Console.WriteLine($"Processing batch {++batchNum}...");
        var tasks = batch.Select(doc => ProcessDocumentAsync(doc));
        var summaries = await Task.WhenAll(tasks);
        allSummaries.AddRange(summaries);
    }
    ```

---

## Progress Tracking

Track progress for long-running batch operations:

```python
from tqdm import tqdm  # pip install tqdm

async def process_with_progress(documents: List[str]) -> List[str]:
    """Process documents with progress bar."""
    results = []

    with tqdm(total=len(documents), desc="Processing documents") as pbar:
        for doc in documents:
            summary = await process_document(doc)
            results.append(summary)
            pbar.update(1)

    return results

# Or with parallel processing:
async def process_parallel_with_progress(documents: List[str]) -> List[str]:
    """Process documents in parallel with progress tracking."""
    results = []
    semaphore = Semaphore(10)

    async def process_and_update(doc: str) -> str:
        async with semaphore:
            result = await process_document(doc)
            pbar.update(1)
            return result

    with tqdm(total=len(documents), desc="Processing documents") as pbar:
        results = await asyncio.gather(*[
            process_and_update(doc) for doc in documents
        ])

    return results
```

**Output:**
```
Processing documents: 100%|██████████| 100/100 [00:47<00:00,  2.11it/s]
```

---

## Error Handling in Batches

Handle failures gracefully without stopping the entire batch:

=== "Python"

    ```python
    from typing import Union

    async def process_document_safe(doc: str) -> Union[str, Exception]:
        """Process document, returning exception on failure."""
        try:
            with open(doc) as f:
                content = f.read()
            return await client.complete_chat(f"Summarize: {content}")
        except Exception as e:
            return e

    # Process all documents, collecting both successes and failures
    results = await asyncio.gather(*[
        process_document_safe(doc) for doc in documents
    ])

    # Separate successes and failures
    successes = [r for r in results if isinstance(r, str)]
    failures = [(i, r) for i, r in enumerate(results) if isinstance(r, Exception)]

    print(f"Successful: {len(successes)}, Failed: {len(failures)}")

    # Retry failures
    if failures:
        print("Retrying failed documents...")
        retry_results = await asyncio.gather(*[
            process_document_safe(documents[i]) for i, _ in failures
        ])
    ```

=== "TypeScript"

    ```typescript
    async function processDocumentSafe(doc: string): Promise<string | Error> {
        try {
            const content = await fs.readFile(doc, 'utf-8');
            return await client.completeChat(`Summarize: ${content}`);
        } catch (error) {
            return error as Error;
        }
    }

    const results = await Promise.all(
        documents.map(doc => processDocumentSafe(doc))
    );

    const successes = results.filter(r => typeof r === 'string');
    const failures = results
        .map((r, i) => ({ index: i, error: r }))
        .filter(({ error }) => error instanceof Error);

    console.log(`Successful: ${successes.length}, Failed: ${failures.length}`);
    ```

=== "C#"

    ```csharp
    async Task<Result<string>> ProcessDocumentSafe(string doc)
    {
        try
        {
            var content = await File.ReadAllTextAsync(doc);
            var summary = await client.CompleteChatAsync($"Summarize: {content}");
            return Result<string>.Success(summary);
        }
        catch (Exception ex)
        {
            return Result<string>.Failure(ex);
        }
    }

    var results = await Task.WhenAll(
        documents.Select(doc => ProcessDocumentSafe(doc))
    );

    var successes = results.Where(r => r.IsSuccess).Select(r => r.Value);
    var failures = results.Where(r => !r.IsSuccess);

    Console.WriteLine($"Successful: {successes.Count()}, Failed: {failures.Count()}");
    ```

---

## Batch API Pattern

Some agents may support batch APIs for more efficient processing:

```python
# Check if agent supports batch API
if client.supports_batch_api:
    # Submit batch request
    batch = await client.create_batch(
        requests=[
            {"message": f"Summarize: {content}"}
            for content in documents
        ]
    )

    # Poll for completion
    while batch.status != "completed":
        await asyncio.sleep(5)
        batch = await client.get_batch(batch.id)

    # Retrieve results
    results = await client.get_batch_results(batch.id)
else:
    # Fall back to parallel processing
    results = await asyncio.gather(*[
        process_document(doc) for doc in documents
    ])
```

---

## Practical Examples

### Example 1: Document Summarization Pipeline

```python
import asyncio
from pathlib import Path
from typing import List, Dict

class DocumentProcessor:
    def __init__(self, client: AgentProtocolClient, max_concurrency: int = 10):
        self.client = client
        self.semaphore = Semaphore(max_concurrency)

    async def process_document(self, path: Path) -> Dict[str, str]:
        """Process a single document."""
        async with self.semaphore:
            content = path.read_text()
            summary = await self.client.complete_chat(
                f"Provide a concise summary:\n\n{content}"
            )
            return {
                "file": path.name,
                "summary": summary
            }

    async def process_directory(self, directory: Path) -> List[Dict[str, str]]:
        """Process all documents in a directory."""
        docs = list(directory.glob("*.txt"))
        print(f"Processing {len(docs)} documents...")

        results = await asyncio.gather(*[
            self.process_document(doc) for doc in docs
        ], return_exceptions=True)

        # Filter out exceptions
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = sum(1 for r in results if isinstance(r, Exception))

        print(f"Completed: {len(successful)} successful, {failed} failed")
        return successful

# Usage
processor = DocumentProcessor(client, max_concurrency=10)
results = await processor.process_directory(Path("./documents"))

# Save results
import json
with open("summaries.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Example 2: Multi-Language Translation

```python
async def translate_content(text: str, target_lang: str) -> str:
    """Translate text to target language."""
    return await client.complete_chat(
        f"Translate to {target_lang}:\n\n{text}"
    )

async def translate_to_multiple_languages(
    text: str,
    languages: List[str]
) -> Dict[str, str]:
    """Translate text to multiple languages in parallel."""
    translations = await asyncio.gather(*[
        translate_content(text, lang) for lang in languages
    ])

    return dict(zip(languages, translations))

# Usage
original = "Hello, how are you?"
languages = ["Spanish", "French", "German", "Italian", "Japanese"]

translations = await translate_to_multiple_languages(original, languages)
# Returns: {
#   "Spanish": "Hola, ¿cómo estás?",
#   "French": "Bonjour, comment allez-vous?",
#   ...
# }
```

---

## Best Practices

1. **Choose Appropriate Concurrency**
   - Too low: Underutilizes resources
   - Too high: Overwhelms server, triggers rate limits
   - Start with 10-20 concurrent requests, adjust based on performance

2. **Respect Rate Limits**
   ```python
   # Add delays between batches
   for batch in batches:
       await process_batch(batch)
       await asyncio.sleep(1)  # Respect rate limits
   ```

3. **Handle Failures Gracefully**
   - Don't let one failure stop the entire batch
   - Collect and retry failed requests
   - Log failures for investigation

4. **Monitor Progress**
   - Use progress bars for long operations
   - Log batch completion
   - Track success/failure rates

5. **Optimize Payload Size**
   - Don't send unnecessary data
   - Truncate very long documents if appropriate
   - Consider preprocessing (e.g., extract key sections)

6. **Consider Costs**
   - Batch processing consumes API quota quickly
   - Monitor usage and implement budgets
   - Use caching to avoid reprocessing

---

## Next Steps

<div class="grid cards" markdown>

- **:material-alert-circle: Error Handling**

    Handle batch errors

    [:octicons-arrow-right-24: Error Handling](../concepts/error-handling.md)

- **:material-test-tube: Testing**

    Test batch operations

    [:octicons-arrow-right-24: Testing Guide](testing.md)

- **:material-speedometer: Performance**

    Optimize batch performance

    [:octicons-arrow-right-24: Best Practices](best-practices/)

</div>
