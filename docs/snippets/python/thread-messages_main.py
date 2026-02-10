# from microsoft.agents.xml.models import SystemMessage, ChatMessage, AgentMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create conversation thread
# thread = [
#     SystemMessage(contents=[TextContent(text="You are a helpful assistant.")]),
#     ChatMessage(role="user", contents=[TextContent(text="Hello!")]),
#     AgentMessage(role="assistant", contents=[TextContent(text="Hi! How can I help?")])
# ]
#
# # Serialize thread
# serializer = MessageSerializer()
# thread_xml = [serializer.serialize(msg) for msg in thread]
#
# print(f"Thread length: {len(thread_xml)} messages")