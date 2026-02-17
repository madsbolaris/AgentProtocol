import { chromium } from 'playwright';

async function checkScroll() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('\n=== PROTOTYPE ===');
  await page.goto('http://localhost:8000/phase-02-synthesis-iter1/index.html?view=conversation&agent=synthesis-agent&phase=phase-02');
  await page.waitForTimeout(1000);
  
  const prototypeInfo = await page.evaluate(() => {
    const wrapper = document.querySelector('.detail-content-wrapper');
    const conversation = document.querySelector('.conversation-view');
    const firstChild = conversation?.firstElementChild;
    
    return {
      wrapperScrollTop: wrapper?.scrollTop || 0,
      conversationPaddingTop: conversation ? window.getComputedStyle(conversation).paddingTop : null,
      firstChildTag: firstChild?.tagName,
      firstChildClass: firstChild?.className,
      firstChildMarginTop: firstChild ? window.getComputedStyle(firstChild).marginTop : null,
      firstChildHeight: firstChild ? firstChild.getBoundingClientRect().height : null
    };
  });
  
  console.log(prototypeInfo);
  
  console.log('\n=== REACT ===');
  await page.goto('http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation');
  await page.waitForTimeout(1000);
  
  const reactInfo = await page.evaluate(() => {
    const wrapper = document.querySelector('.detail-content-wrapper');
    const conversation = document.querySelector('.conversation-view');
    const firstChild = conversation?.firstElementChild;
    
    return {
      wrapperScrollTop: wrapper?.scrollTop || 0,
      conversationPaddingTop: conversation ? window.getComputedStyle(conversation).paddingTop : null,
      firstChildTag: firstChild?.tagName,
      firstChildClass: firstChild?.className,
      firstChildMarginTop: firstChild ? window.getComputedStyle(firstChild).marginTop : null,
      firstChildHeight: firstChild ? firstChild.getBoundingClientRect().height : null
    };
  });
  
  console.log(reactInfo);

  await browser.close();
}

checkScroll().catch(console.error);
