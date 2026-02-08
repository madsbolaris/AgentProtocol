# Example: Multimodal message with text and image
# Simulated Python implementation

xml_output = """<?xml version="1.0" encoding="utf-8"?>
<message role="user" messageId="msg-002">
  <text>What's in this image?</text>
  <image uri="https://example.com/photo.jpg" altText="A photo of a sunset" />
</message>"""

print(xml_output)
