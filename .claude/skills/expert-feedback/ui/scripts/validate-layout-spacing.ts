import { chromium, type Page } from 'playwright';

interface SpacingCheck {
  name: string;
  selector1: string;  // First element (e.g., header)
  selector2: string;  // Second element (e.g., first message)
  edge1: 'top' | 'bottom';  // Which edge of first element
  edge2: 'top' | 'bottom';  // Which edge of second element
  tolerance: number;  // Acceptable difference in pixels
}

const SPACING_CHECKS: SpacingCheck[] = [
  {
    name: 'Detail header to first message',
    selector1: '.detail-header',
    selector2: '.messages-container .message:first-child, .conversation-view .message:first-child',
    edge1: 'bottom',
    edge2: 'top',
    tolerance: 2  // Allow 2px difference
  },
  {
    name: 'Detail header to document view',
    selector1: '.detail-header',
    selector2: '.document-view',
    edge1: 'bottom',
    edge2: 'top',
    tolerance: 2
  }
];

async function measureSpacing(page: Page, check: SpacingCheck): Promise<number | null> {
  return await page.evaluate(({ selector1, selector2, edge1, edge2 }) => {
    const el1 = document.querySelector(selector1);
    const el2 = document.querySelector(selector2);

    if (!el1 || !el2) {
      return null;
    }

    const rect1 = el1.getBoundingClientRect();
    const rect2 = el2.getBoundingClientRect();

    const pos1 = edge1 === 'top' ? rect1.top : rect1.bottom;
    const pos2 = edge2 === 'top' ? rect2.top : rect2.bottom;

    return pos2 - pos1;
  }, { selector1: check.selector1, selector2: check.selector2, edge1: check.edge1, edge2: check.edge2 });
}

async function validateLayoutSpacing(prototypeUrl: string, reactUrl: string) {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

  let passed = 0;
  let failed = 0;
  const failures: string[] = [];

  console.log('\n=== Layout Spacing Validation ===\n');

  for (const check of SPACING_CHECKS) {
    const prototypePage = await context.newPage();
    await prototypePage.goto(prototypeUrl);
    await prototypePage.waitForTimeout(1000);
    const prototypeSpacing = await measureSpacing(prototypePage, check);
    await prototypePage.close();

    const reactPage = await context.newPage();
    await reactPage.goto(reactUrl);
    await reactPage.waitForTimeout(1000);
    const reactSpacing = await measureSpacing(reactPage, check);
    await reactPage.close();

    if (prototypeSpacing === null || reactSpacing === null) {
      console.log(`⚠️  ${check.name}: Skipped (elements not found)`);
      continue;
    }

    const difference = Math.abs(reactSpacing - prototypeSpacing);
    const isWithinTolerance = difference <= check.tolerance;

    if (isWithinTolerance) {
      const diffStr = difference.toFixed(2);
      const reactStr = reactSpacing.toFixed(2);
      const protoStr = prototypeSpacing.toFixed(2);
      console.log(`✅ ${check.name}: ${reactStr}px (prototype: ${protoStr}px, diff: ${diffStr}px)`);
      passed++;
    } else {
      const diffStr = difference.toFixed(2);
      const reactStr = reactSpacing.toFixed(2);
      const protoStr = prototypeSpacing.toFixed(2);
      console.log(`❌ ${check.name}: ${reactStr}px (prototype: ${protoStr}px, diff: ${diffStr}px, tolerance: ${check.tolerance}px)`);
      failures.push(`${check.name}: Expected ~${protoStr}px, got ${reactStr}px (difference: ${diffStr}px)`);
      failed++;
    }
  }

  await browser.close();

  console.log(`\n=== Summary ===`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);

  if (failures.length > 0) {
    console.log(`\nFailures:`);
    failures.forEach(f => console.log(`  - ${f}`));
  }

  return failed === 0;
}

// Main execution
const prototypeUrl = process.argv[2] || 'http://localhost:8000/phase-02-synthesis-iter1/index.html?view=conversation&agent=synthesis-agent&phase=phase-02';
const reactUrl = process.argv[3] || 'http://localhost:5173/?phase=phase-02&agent=synthesis-agent&view=conversation';

validateLayoutSpacing(prototypeUrl, reactUrl)
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });
