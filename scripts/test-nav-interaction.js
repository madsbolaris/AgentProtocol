const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1400 });

  await page.goto('http://127.0.0.1:8001/products/client-sdk/quickstart/', {
    waitUntil: 'networkidle2'
  });

  // Wait for navigation to load
  await page.waitForSelector('nav#sidebar-nav', { timeout: 5000 });

  console.log('Navigation loaded');

  // Get all expandable buttons and click the first one
  const buttons = await page.$$('button[data-nav-toggle]');
  console.log(`Found ${buttons.length} expandable buttons`);

  // Click the first button (Guides or similar)
  if (buttons.length > 0) {
    await buttons[0].click();
    console.log('Clicked first expandable button');
  }

  // Wait for animation
  await new Promise(resolve => setTimeout(resolve, 500));

  // Take screenshot
  const nav = await page.$('nav#sidebar-nav');
  if (nav) {
    await nav.screenshot({ path: '/tmp/nav-expanded-clicked.png' });
    console.log('Screenshot saved to /tmp/nav-expanded-clicked.png');
  }

  // Log the HTML structure for debugging
  const navHTML = await page.evaluate(() => {
    const nav = document.querySelector('nav#sidebar-nav');
    const expandables = nav.querySelectorAll('[data-nav-toggle]');
    return Array.from(expandables).map(btn => ({
      text: btn.textContent.trim().substring(0, 20),
      hasExpandedClass: btn.classList.contains('nav-expanded'),
      nextSiblingClass: btn.nextElementSibling ? btn.nextElementSibling.className : 'none'
    }));
  });

  console.log('\nExpandable sections:', JSON.stringify(navHTML, null, 2));

  await browser.close();
})();
