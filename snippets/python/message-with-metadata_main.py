# from microsoft.agents.xml.models import ChatMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create message with metadata
# message = ChatMessage(
#     role="user",
#     message_id="msg-meta-1",
#     timestamp="2024-01-15T10:30:00Z",
#     contents=[
#         TextContent(text="Hello!")
#     ]
# )
#
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
# print(xml_output)