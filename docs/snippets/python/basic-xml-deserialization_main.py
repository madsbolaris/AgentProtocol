# from microsoft.agents.xml.serialization import MessageSerializer
#
# xml_input = """<?xml version="1.0" encoding="utf-8"?>
# <chat role="user" messageId="msg-001">
#   <text>Hello, agent!</text>
# </chat>"""
#
# # Deserialize XML to object
# serializer = MessageSerializer()
# message = serializer.deserialize(xml_input)
#
# print(f"Role: {message.role}")
# print(f"Text: {message.contents[0].text}")