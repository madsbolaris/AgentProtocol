import { chromium } from 'playwright';

async function checkWrapper() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('\n=== PROTOTYPE ===');
  await page.goto('http://localhost:8000/phase-02-synthesis-iter1/index.html?view=conversation&agent=synthesis-agent&phase=phase-02');
  await page.waitForTimeout(1000);
  
  const prototypeInfo = await page.evaluate(() => {
    const wrapper = document.querySelector('.detail-content-wrapper');
    const header = document.querySelector('.detail-header');
    const conversation = document.querySelector('.conversation-view');
    
    return {
      wrapper: wrapper ? {
        top: wrapper.getBoundingClientRect().top,
        bottom: wrapper.getBoundingClientRect().bottom,
        padding: window.getComputedStyle(wrapper).padding,
        overflow: window.getComputedStyle(wrapper).overflowY
      } : null,
      header: header ? {
        top: header.getBoundingClientRect().top,
        bottom: header.getBoundingClientRect().bottom
      } : null,
      conversation: conversation ? {
        top: conversation.getBoundingClientRect().top
      } : null
    };
  });
  
  console.log(prototypeInfo);
  
  // Calculate spacing
  if (prototypeInfo.header && prototypeInfo.conversation) {
    console.log('Gap between header.bottom and conversation.top:', 
      prototypeInfo.conversation.top - prototypeInfo.header.bottom);
  }
  
  console.log('\n=== REACT ===');
  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForTimeout(1000);
  
  const reactInfo = await page.evaluate(() => {
    const wrapper = document.querySelector('.detail-content-wrapper');
    const header = document.querySelector('.detail-header');
    const conversation = document.querySelector('.conversation-view');
    
    return {
      wrapper: wrapper ? {
        top: wrapper.getBoundingClientRect().top,
        bottom: wrapper.getBoundingClientRect().bottom,
        padding: window.getComputedStyle(wrapper).padding,
        overflow: window.getComputedStyle(wrapper).overflowY
      } : null,
      header: header ? {
        top: header.getBoundingClientRect().top,
        bottom: header.getBoundingClientRect().bottom
      } : null,
      conversation: conversation ? {
        top: conversation.getBoundingClientRect().top
      } : null
    };
  });
  
  console.log(reactInfo);
  
  // Calculate spacing
  if (reactInfo.header && reactInfo.conversation) {
    console.log('Gap between header.bottom and conversation.top:', 
      reactInfo.conversation.top - reactInfo.header.bottom);
  }

  await browser.close();
}

checkWrapper().catch(console.error);
