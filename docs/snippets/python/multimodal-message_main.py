# from microsoft.agents.xml import MessageSerializer
# from microsoft.agents.xml.models import ChatMessage, TextContent, ImageContent
#
# # Create a message with text and image
# message = ChatMessage(
#     role="user",
#     message_id="msg-002",
#     contents=[
#         TextContent(text="What's in this image?"),
#         ImageContent(
#             uri="https://example.com/image.jpg",
#             alt_text="A photo of a sunset"
#         )
#     ]
# )
#
# # Serialize to XML
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)