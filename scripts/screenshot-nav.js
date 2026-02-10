const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1200 });

  await page.goto('http://127.0.0.1:8001/products/client-sdk/quickstart/', {
    waitUntil: 'networkidle2'
  });

  // Wait for navigation to load
  await page.waitForSelector('nav#sidebar-nav', { timeout: 5000 });

  // Take screenshot of just the navigation
  const nav = await page.$('nav#sidebar-nav');
  if (nav) {
    await nav.screenshot({ path: '/tmp/nav-screenshot.png' });
    console.log('Screenshot saved to /tmp/nav-screenshot.png');
  }

  await browser.close();
})();
