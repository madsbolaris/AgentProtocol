# from microsoft.agents.xml.models import AgentMessage, ErrorContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create message with error
# message = AgentMessage(
#     role="assistant",
#     agent_id="agent-456",
#     message_id="msg-error-1",
#     contents=[
#         ErrorContent(
#             code="rate_limit_exceeded",
#             message="Rate limit exceeded. Please try again in 60 seconds."
#         )
#     ]
# )
#
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
# print(xml_output)