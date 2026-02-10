# Stream the response with a callback
def on_chunk(text):
    print(text, end="")
await client.stream_chat("Tell me a story about a robot", on_chunk)
print()