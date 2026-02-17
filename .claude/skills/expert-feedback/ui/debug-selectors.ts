import { chromium } from 'playwright';

async function debugSelectors() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('\n=== REACT ===');
  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForTimeout(2000);

  const found = await page.evaluate(() => {
    return {
      detailHeader: !!document.querySelector('.detail-header'),
      messagesContainer: !!document.querySelector('.messages-container'),
      firstMessage: !!document.querySelector('.messages-container .message:first-child'),
      conversationView: !!document.querySelector('.conversation-view'),
      conversationFirstMessage: !!document.querySelector('.conversation-view .message:first-child')
    };
  });

  console.log('Elements found:', found);

  await browser.close();
}

debugSelectors().catch(console.error);
