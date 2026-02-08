# Example: Tool/Function call message
# Simulated Python implementation

xml_output = """<?xml version="1.0" encoding="utf-8"?>
<tool>
  <functionCall name="get_weather" callId="call_001">
    <arguments>{"location": "San Francisco", "unit": "celsius"}</arguments>
  </functionCall>
</tool>"""

print(xml_output)
