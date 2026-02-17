const { chromium } = require('playwright');
const { waitForRender } = require('./wait-for-render');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const params = { agent: 'synthesis-agent', view: 'document', phase: 'phase-02' };
  await waitForRender(page, 'http://localhost:5173', params);
  await page.waitForTimeout(2000);
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  const structure = await page.evaluate(() => {
    const detailContent = document.querySelector('.detail-content-wrapper');
    const documentView = document.querySelector('.document-view');
    const documentContent = document.querySelector('.document-content');
    const loadingState = document.querySelector('.loading-state');
    const emptyState = document.querySelector('.empty-state');
    
    const getStyles = (el) => {
      if (!el) return null;
      const computed = window.getComputedStyle(el);
      return {
        display: computed.display,
        visibility: computed.visibility,
        opacity: computed.opacity,
        height: computed.height,
        overflow: computed.overflow
      };
    };
    
    return {
      detailContentWrapper: {
        exists: !!detailContent,
        styles: getStyles(detailContent),
        innerHTML: detailContent?.innerHTML.substring(0, 500)
      },
      documentView: {
        exists: !!documentView,
        styles: getStyles(documentView),
        innerHTML: documentView?.innerHTML.substring(0, 500)
      },
      documentContent: {
        exists: !!documentContent,
        styles: getStyles(documentContent),
        innerHTML: documentContent?.innerHTML.substring(0, 1000)
      },
      loadingState: {
        exists: !!loadingState,
        styles: getStyles(loadingState)
      },
      emptyState: {
        exists: !!emptyState,
        styles: getStyles(emptyState)
      }
    };
  });

  console.log('=== DOM STRUCTURE ===\n');
  console.log(JSON.stringify(structure, null, 2));

  await browser.close();
})();
