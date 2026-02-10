// Resume existing conversation
var resumed = client.ResumeConversation("thread_abc123");
var response = await resumed.SendAsync("Tell me about its landmarks");