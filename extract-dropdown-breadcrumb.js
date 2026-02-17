const { chromium } = require('playwright');
const { waitForRender } = require('./wait-for-render');

(async () => {
  const browser = await chromium.launch();
  const protoPage = await browser.newPage();
  const reactPage = await browser.newPage();

  const params = { agent: 'typescript-expert', view: 'conversation', phase: 'phase-01' };
  await waitForRender(protoPage, 'http://localhost:8000/phase-01-expert-review-iter1/index.html', params);
  await waitForRender(reactPage, 'http://localhost:5173', params);

  const selectors = [
    '.breadcrumb',
    '.breadcrumb-item',
    '.breadcrumb-separator',
    '.agent-dropdown',
    '.agent-dropdown-toggle',
    '.dropdown-group',
    '.dropdown-group-header',
    '.dropdown-item-name',
    '.dropdown-status'
  ];

  const properties = ['fontSize', 'lineHeight', 'fontWeight', 'color', 'padding', 'margin'];

  console.log('DROPDOWN & BREADCRUMB STYLES:\n');

  for (const selector of selectors) {
    const protoStyles = await protoPage.evaluate(({ sel, props }) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const computed = window.getComputedStyle(el);
      const result = {};
      props.forEach(p => result[p] = computed[p]);
      return result;
    }, { sel: selector, props: properties });

    const reactStyles = await reactPage.evaluate(({ sel, props }) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const computed = window.getComputedStyle(el);
      const result = {};
      props.forEach(p => result[p] = computed[p]);
      return result;
    }, { sel: selector, props: properties });

    if (!protoStyles || !reactStyles) continue;

    const diffs = [];
    properties.forEach(prop => {
      if (protoStyles[prop] !== reactStyles[prop]) {
        diffs.push({ prop, proto: protoStyles[prop], react: reactStyles[prop] });
      }
    });

    if (diffs.length > 0) {
      console.log(`${selector}:`);
      diffs.forEach(d => console.log(`  ${d.prop}: ${d.react} → ${d.proto}`));
      console.log();
    }
  }

  await browser.close();
})();
