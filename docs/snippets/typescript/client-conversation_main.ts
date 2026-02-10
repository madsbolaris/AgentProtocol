// Create a persistent conversation
const conversation = client.createConversation();

// Send messages that maintain context
const response1 = await conversation.send('My name is Alice');
console.log(response1);

const response2 = await conversation.send("What's my name?");
console.log(response2);