const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1400 });

  await page.goto('http://127.0.0.1:8001/products/client-sdk/guides/best-practices/', {
    waitUntil: 'networkidle2'
  });

  // Wait for navigation to load
  await page.waitForSelector('nav#sidebar-nav', { timeout: 5000 });

  // Give time for JavaScript to initialize
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Take screenshot
  const nav = await page.$('nav#sidebar-nav');
  if (nav) {
    await nav.screenshot({ path: '/tmp/nav-best-practices.png' });
    console.log('Screenshot saved to /tmp/nav-best-practices.png');
  }

  // Debug: Check which sections are expanded
  const navState = await page.evaluate(() => {
    const buttons = document.querySelectorAll('button[data-nav-toggle]');
    return Array.from(buttons).map(btn => ({
      text: btn.textContent.trim().substring(0, 20),
      hasExpandedClass: btn.classList.contains('nav-expanded'),
      hasActiveClass: btn.classList.contains('sidebar-nav-item--active'),
      nextSiblingCollapsed: btn.nextElementSibling ? btn.nextElementSibling.classList.contains('nav-collapsed') : null
    }));
  });

  console.log('Navigation state:', JSON.stringify(navState, null, 2));

  // Check if Best Practices is in the nav
  const bestPracticesInfo = await page.evaluate(() => {
    const allLinks = document.querySelectorAll('nav a');
    const bestPractices = Array.from(allLinks).find(link =>
      link.textContent.includes('Best Practices')
    );
    return bestPractices ? {
      text: bestPractices.textContent.trim(),
      href: bestPractices.href,
      isActive: bestPractices.classList.contains('sidebar-nav-item--active')
    } : null;
  });

  console.log('Best Practices link:', bestPracticesInfo);

  await browser.close();
})();
