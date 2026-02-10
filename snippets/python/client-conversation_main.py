# Create a persistent conversation
conversation = client.create_conversation()

# Send messages that maintain context
response1 = await conversation.send("My name is Alice")
print(response1)

response2 = await conversation.send("What's my name?")
print(response2)