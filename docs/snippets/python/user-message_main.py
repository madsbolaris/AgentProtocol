# from microsoft.agents.xml.models import ChatMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create user message
# message = ChatMessage(
#     role="user",
#     message_id="user-123",
#     contents=[
#         TextContent(text="What is the weather in Seattle?")
#     ]
# )
#
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
# print(xml_output)