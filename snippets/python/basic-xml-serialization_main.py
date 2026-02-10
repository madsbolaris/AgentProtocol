# from microsoft.agents.xml import MessageSerializer
# from microsoft.agents.xml.models import ChatMessage, TextContent
#
# # Create a simple text message
# message = ChatMessage(
#     role="user",
#     message_id="msg-001",
#     contents=[
#         TextContent(text="Hello, how can you help me today?")
#     ]
# )
#
# # Serialize to XML
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
#
# print(xml_output)