# from microsoft.agents.xml.models import AgentMessage, FunctionCallContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create agent message with tool call
# message = AgentMessage(
#     role="assistant",
#     agent_id="agent-456",
#     message_id="msg-call-1",
#     contents=[
#         FunctionCallContent(
#             call_id="call_abc123",
#             name="get_weather",
#             arguments='{"location": "Seattle", "unit": "fahrenheit"}'
#         )
#     ]
# )
#
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
# print(xml_output)