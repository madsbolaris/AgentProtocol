import { chromium } from 'playwright';

async function measureGap() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('\n=== PROTOTYPE ===');
  await page.goto('http://localhost:8000/phase-02-synthesis-iter1/index.html?view=conversation&agent=synthesis-agent&phase=phase-02');
  await page.waitForTimeout(1000);
  
  const prototypeGap = await page.evaluate(() => {
    const wrapper = document.querySelector('.detail-content-wrapper');
    const wrapperRect = wrapper?.getBoundingClientRect();
    
    // Find first visible element
    const conversation = document.querySelector('.conversation-view');
    const allChildren = conversation?.children || [];
    
    let firstVisibleElement = null;
    let firstVisibleTop = null;
    
    for (let child of allChildren) {
      const rect = child.getBoundingClientRect();
      if (rect.top >= (wrapperRect?.top || 0)) {
        firstVisibleElement = child;
        firstVisibleTop = rect.top;
        break;
      }
    }
    
    return {
      wrapperTop: wrapperRect?.top,
      firstVisibleElementTag: firstVisibleElement?.tagName,
      firstVisibleElementClass: firstVisibleElement?.className,
      firstVisibleTop: firstVisibleTop,
      gap: firstVisibleTop && wrapperRect?.top ? firstVisibleTop - wrapperRect.top : null
    };
  });
  
  console.log(prototypeGap);
  
  console.log('\n=== REACT ===');
  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForTimeout(1000);
  
  const reactGap = await page.evaluate(() => {
    const wrapper = document.querySelector('.detail-content-wrapper');
    const wrapperRect = wrapper?.getBoundingClientRect();
    
    // Find first visible element
    const messagesContainer = document.querySelector('.messages-container');
    const allChildren = messagesContainer?.children || [];
    
    let firstVisibleElement = allChildren[0] || null;
    let firstVisibleTop = firstVisibleElement?.getBoundingClientRect().top || null;
    
    return {
      wrapperTop: wrapperRect?.top,
      firstVisibleElementTag: firstVisibleElement?.tagName,
      firstVisibleElementClass: firstVisibleElement?.className,
      firstVisibleTop: firstVisibleTop,
      gap: firstVisibleTop && wrapperRect?.top ? firstVisibleTop - wrapperRect.top : null
    };
  });
  
  console.log(reactGap);
  
  console.log('\nDifference:', (prototypeGap.gap || 0) - (reactGap.gap || 0), 'px');

  await browser.close();
}

measureGap().catch(console.error);
