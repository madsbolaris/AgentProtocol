# from microsoft.agents.xml.models import ChatMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create batch of messages
# messages = [
#     ChatMessage(role="user", contents=[TextContent(text="Message 1")]),
#     ChatMessage(role="user", contents=[TextContent(text="Message 2")]),
#     ChatMessage(role="user", contents=[TextContent(text="Message 3")])
# ]
#
# # Process batch
# serializer = MessageSerializer()
# xml_outputs = [serializer.serialize(msg) for msg in messages]
#
# print(f"Processed {len(xml_outputs)} messages")