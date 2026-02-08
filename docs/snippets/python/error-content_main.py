# Example: Error handling content
# Simulated Python implementation

xml_output = """<?xml version="1.0" encoding="utf-8"?>
<agent>
  <error code="TOOL_ERROR" message="Failed to execute function: API timeout">
    <details>The weather API did not respond within 5 seconds</details>
  </error>
</agent>"""

print(xml_output)
