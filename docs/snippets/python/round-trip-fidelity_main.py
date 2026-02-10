# from microsoft.agents.xml.models import ChatMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Original message
# original = ChatMessage(
#     role="user",
#     message_id="msg-roundtrip",
#     contents=[TextContent(text="Test message")]
# )
#
# # Serialize then deserialize
# serializer = MessageSerializer()
# xml = serializer.serialize(original)
# restored = serializer.deserialize(xml)
#
# # Verify fidelity
# assert restored.role == original.role
# assert restored.message_id == original.message_id
# assert restored.contents[0].text == original.contents[0].text
#
# print("✓ Round-trip successful")