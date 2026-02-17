import { chromium } from 'playwright';

async function checkSpacing() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Check prototype
  await page.goto('http://localhost:8000/phase-02-synthesis-iter1/index.html?view=conversation&agent=synthesis-agent&phase=phase-02');
  await page.waitForTimeout(1000);
  
  const prototypeHeaderBottom = await page.evaluate(() => {
    const header = document.querySelector('.detail-header');
    const rect = header?.getBoundingClientRect();
    return rect ? rect.bottom : 0;
  });
  
  const prototypeFirstMessageTop = await page.evaluate(() => {
    const firstMessage = document.querySelector('.conversation-view .message');
    const rect = firstMessage?.getBoundingClientRect();
    return rect ? rect.top : 0;
  });
  
  const prototypeSpacing = prototypeFirstMessageTop - prototypeHeaderBottom;
  console.log('Prototype spacing between header and first message:', prototypeSpacing);

  // Check React
  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForTimeout(1000);
  
  const reactHeaderBottom = await page.evaluate(() => {
    const header = document.querySelector('.detail-header');
    const rect = header?.getBoundingClientRect();
    return rect ? rect.bottom : 0;
  });
  
  const reactFirstMessageTop = await page.evaluate(() => {
    const firstMessage = document.querySelector('.messages-container .message');
    const rect = firstMessage?.getBoundingClientRect();
    return rect ? rect.top : 0;
  });
  
  const reactSpacing = reactFirstMessageTop - reactHeaderBottom;
  console.log('React spacing between header and first message:', reactSpacing);
  
  console.log('Difference:', reactSpacing - prototypeSpacing);

  await browser.close();
}

checkSpacing().catch(console.error);
