const playwright = require('playwright');

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto('http://localhost:8000/phase-02-synthesis-iter1/index.html?view=document&agent=synthesis-agent&phase=phase-02');
  await page.waitForTimeout(500);

  const structure = await page.evaluate(() => {
    const badge = document.querySelector('.convergence-badge');
    const panelHeader = document.querySelector('.panel-header');

    return {
      badgeHTML: badge?.innerHTML,
      allSpans: Array.from(badge?.querySelectorAll('span') || []).map(s => ({
        text: s.textContent?.trim(),
        class: s.className,
        style: s.getAttribute('style')
      })),
      hasLabel: !!badge?.querySelector('.convergence-label'),
      hasValue: !!badge?.querySelector('.convergence-value'),
      fullHeaderHTML: panelHeader?.innerHTML
    };
  });

  console.log(JSON.stringify(structure, null, 2));
  await browser.close();
})();
