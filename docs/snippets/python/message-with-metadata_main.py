# Example: Message with custom metadata
# Simulated Python implementation

xml_output = """<?xml version="1.0" encoding="utf-8"?>
<message role="user" messageId="msg-001">
  <metadata>
    <userId>user_123</userId>
    <sessionId>session_456</sessionId>
    <timestamp>2026-02-07T22:15:00Z</timestamp>
  </metadata>
  <text>What's the weather today?</text>
</message>"""

print(xml_output)
