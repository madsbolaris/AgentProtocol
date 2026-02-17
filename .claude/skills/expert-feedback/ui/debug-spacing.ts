import { chromium } from 'playwright';

async function debugSpacing() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForSelector('.detail-header', { timeout: 5000 });
  await page.waitForTimeout(1000);

  const result = await page.evaluate(() => {
    const el1 = document.querySelector('.detail-header');
    const el2 = document.querySelector('.messages-container .message:first-child, .conversation-view .message:first-child');
    
    if (!el1 || !el2) {
      return {
        error: 'Elements not found',
        el1Found: !!el1,
        el2Found: !!el2,
        messagesContainer: !!document.querySelector('.messages-container'),
        messages: document.querySelectorAll('.message').length
      };
    }
    
    const rect1 = el1.getBoundingClientRect();
    const rect2 = el2.getBoundingClientRect();
    
    return {
      el1Bottom: rect1.bottom,
      el2Top: rect2.top,
      spacing: rect2.top - rect1.bottom
    };
  });

  console.log('Result:', result);

  await browser.close();
}

debugSpacing().catch(console.error);
