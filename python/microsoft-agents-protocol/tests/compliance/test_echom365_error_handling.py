"""
EchoM365 error handling compliance tests.

Tests that EchoM365 properly rejects invalid messages with appropriate HTTP status codes.
"""

import pytest
from pathlib import Path

# Get path to error test data
ERROR_TEST_DATA_PATH = Path(__file__).parent.parent.parent.parent.parent / "test-data" / "input" / "threads" / "invalid"


@pytest.fixture
def client():
    """Create test client for the echo bot."""
    pytest.skip("Client fixture not yet implemented - requires running echo bot")
    # TODO: When implementing:
    # - Start echo bot server
    # - Return httpx.AsyncClient or similar
    # - Ensure proper cleanup


def get_error_test_files():
    """Get all error XML test files."""
    if not ERROR_TEST_DATA_PATH.exists():
        return []
    return sorted(ERROR_TEST_DATA_PATH.glob("*.xml"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "xml_file",
    get_error_test_files(),
    ids=lambda f: f.name
)
async def test_echom365_rejects_invalid_message(client, xml_file: Path):
    """
    Test that EchoM365 properly rejects invalid messages with 400 Bad Request.

    Invalid messages should return:
    - HTTP 400 Bad Request
    - Error response body with meaningful error message
    - Appropriate error code

    Error test cases:
    - missing-user-id.xml - Missing required user-id attribute
    - malformed-xml.xml - Malformed XML structure
    - invalid-timestamp.xml - Invalid timestamp format
    - empty-text-content.xml - Empty text content
    - tool-call-in-user-message.xml - Invalid role/content combination
    - missing-message-content.xml - No content elements
    - invalid-url.xml - Invalid URL format
    - missing-function-name.xml - Missing function name
    - invalid-json-arguments.xml - Invalid JSON in arguments
    - unknown-role.xml - Unknown message role
    """
    # Arrange
    xml_content = xml_file.read_text(encoding="utf-8")

    # Act: POST invalid message to echo bot
    response = await client.post(
        "/runs",
        content=xml_content,
        headers={"Content-Type": "application/xml"}
    )

    # Assert: Should return 400 Bad Request
    assert response.status_code == 400, \
        f"{xml_file.name} should be rejected with 400 Bad Request"

    # Assert: Response should contain error details
    error_response = response.json() if response.headers.get("content-type") == "application/json" else None
    if error_response:
        assert "error" in error_response or "message" in error_response, \
            "Error response should contain error details"

    print(f"✅ {xml_file.name} - Properly rejected with 400 Bad Request")


@pytest.mark.asyncio
async def test_echom365_error_response_format(client):
    """
    Test that error responses follow a consistent format.

    Error responses should include:
    - HTTP 400 status code
    - Error message describing what went wrong
    - Optional: error code for programmatic handling
    """
    # Arrange: Use a known error case
    xml_file = ERROR_TEST_DATA_PATH / "missing-user-id.xml"
    xml_content = xml_file.read_text(encoding="utf-8")

    # Act
    response = await client.post(
        "/runs",
        content=xml_content,
        headers={"Content-Type": "application/xml"}
    )

    # Assert
    assert response.status_code == 400

    # Check response format
    if response.headers.get("content-type") == "application/json":
        error_data = response.json()
        assert "error" in error_data or "message" in error_data, \
            "Error response should have 'error' or 'message' field"


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", [
    ("missing-user-id.xml", "user-id", "Missing required attribute"),
    ("malformed-xml.xml", "xml", "XML parsing error"),
    ("invalid-timestamp.xml", "timestamp", "Invalid timestamp format"),
    ("empty-text-content.xml", "empty", "Content cannot be empty"),
    ("unknown-role.xml", "role", "Unknown message role"),
])
async def test_echom365_error_messages_are_meaningful(client, test_case):
    """
    Test that error messages provide meaningful information.

    Each error should clearly indicate what went wrong.
    """
    filename, keyword, description = test_case

    # Arrange
    xml_file = ERROR_TEST_DATA_PATH / filename
    xml_content = xml_file.read_text(encoding="utf-8")

    # Act
    response = await client.post(
        "/runs",
        content=xml_content,
        headers={"Content-Type": "application/xml"}
    )

    # Assert
    assert response.status_code == 400

    response_text = response.text.lower()
    assert keyword in response_text, \
        f"Error message should mention '{keyword}' for {filename}"


@pytest.mark.asyncio
async def test_echom365_accepts_valid_after_rejecting_invalid(client):
    """
    Test that EchoM365 can still process valid messages after rejecting invalid ones.

    This ensures error handling doesn't break the server state.
    """
    # Arrange: First send invalid message
    invalid_xml = (ERROR_TEST_DATA_PATH / "missing-user-id.xml").read_text()

    # Act: Send invalid message
    response1 = await client.post(
        "/runs",
        content=invalid_xml,
        headers={"Content-Type": "application/xml"}
    )
    assert response1.status_code == 400

    # Act: Send valid message
    valid_xml = """
    <user user-id="user_123" created-at="2026-02-07T10:00:00Z">
        <text>Hello after error</text>
    </user>
    """
    response2 = await client.post(
        "/runs",
        content=valid_xml,
        headers={"Content-Type": "application/xml"}
    )

    # Assert: Valid message should succeed
    assert response2.status_code in [200, 201], \
        "Server should still process valid messages after rejecting invalid ones"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
