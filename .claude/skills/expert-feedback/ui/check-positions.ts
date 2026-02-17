import { chromium } from 'playwright';

async function checkPositions() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('\n=== PROTOTYPE ===');
  await page.goto('http://localhost:8000/phase-02-synthesis-iter1/index.html?view=conversation&agent=synthesis-agent&phase=phase-02');
  await page.waitForTimeout(1000);
  
  const prototypeInfo = await page.evaluate(() => {
    const header = document.querySelector('.detail-header');
    const conversation = document.querySelector('.conversation-view');
    const firstMessage = document.querySelector('.conversation-view .message');
    
    return {
      header: header ? {
        bottom: header.getBoundingClientRect().bottom,
        height: header.getBoundingClientRect().height,
        padding: window.getComputedStyle(header).padding
      } : null,
      conversation: conversation ? {
        top: conversation.getBoundingClientRect().top,
        padding: window.getComputedStyle(conversation).padding,
        margin: window.getComputedStyle(conversation).margin
      } : null,
      firstMessage: firstMessage ? {
        top: firstMessage.getBoundingClientRect().top,
        margin: window.getComputedStyle(firstMessage).margin
      } : null
    };
  });
  
  console.log('Header:', prototypeInfo.header);
  console.log('Conversation:', prototypeInfo.conversation);
  console.log('First Message:', prototypeInfo.firstMessage);
  
  console.log('\n=== REACT ===');
  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForTimeout(1000);
  
  const reactInfo = await page.evaluate(() => {
    const header = document.querySelector('.detail-header');
    const conversation = document.querySelector('.conversation-view');
    const messagesContainer = document.querySelector('.messages-container');
    const firstMessage = document.querySelector('.messages-container .message');
    
    return {
      header: header ? {
        bottom: header.getBoundingClientRect().bottom,
        height: header.getBoundingClientRect().height,
        padding: window.getComputedStyle(header).padding
      } : null,
      conversation: conversation ? {
        top: conversation.getBoundingClientRect().top,
        padding: window.getComputedStyle(conversation).padding,
        margin: window.getComputedStyle(conversation).margin
      } : null,
      messagesContainer: messagesContainer ? {
        top: messagesContainer.getBoundingClientRect().top,
        padding: window.getComputedStyle(messagesContainer).padding,
        margin: window.getComputedStyle(messagesContainer).margin
      } : null,
      firstMessage: firstMessage ? {
        top: firstMessage.getBoundingClientRect().top,
        margin: window.getComputedStyle(firstMessage).margin
      } : null
    };
  });
  
  console.log('Header:', reactInfo.header);
  console.log('Conversation:', reactInfo.conversation);
  console.log('Messages Container:', reactInfo.messagesContainer);
  console.log('First Message:', reactInfo.firstMessage);

  await browser.close();
}

checkPositions().catch(console.error);
