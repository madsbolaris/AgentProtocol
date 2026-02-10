// Stream the response with a callback
const onTextChunk = (text: string) => {
  process.stdout.write(text);
};

try {
  await client.streamChat('Tell me a story about a robot', onTextChunk);
  console.log();
} catch (error) {
  // Expected without full SSE mock
}