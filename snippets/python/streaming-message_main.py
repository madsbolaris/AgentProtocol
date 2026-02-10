# from microsoft.agents.xml.models import AgentMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create streaming chunk
# chunk = AgentMessage(
#     role="assistant",
#     agent_id="agent-456",
#     message_id="msg-stream-1",
#     contents=[
#         TextContent(text="The weather ")
#     ]
# )
#
# serializer = MessageSerializer()
# xml_chunk = serializer.serialize(chunk)
# print(f"Chunk: {xml_chunk}")