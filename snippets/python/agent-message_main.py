# from microsoft.agents.xml.models import AgentMessage, TextContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create agent response
# message = AgentMessage(
#     role="assistant",
#     agent_id="agent-456",
#     message_id="msg-789",
#     contents=[
#         TextContent(text="The current weather in Seattle is 55°F and partly cloudy.")
#     ]
# )
#
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
# print(xml_output)