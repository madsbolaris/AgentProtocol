/**
 * Compare navigation styles between local site and HashiCorp reference
 * Usage: node scripts/compare-nav-styles.js
 */

const puppeteer = require('puppeteer');

async function getNavStyles(page, url, description, isHashiCorp = false) {
  console.log(`\n=== ${description} ===`);
  console.log(`URL: ${url}\n`);

  await page.goto(url, { waitUntil: 'networkidle2' });

  // Wait for navigation to be present
  if (isHashiCorp) {
    // HashiCorp has a specific sidebar structure
    await page.waitForSelector('[class*="sidebar"]', { timeout: 5000 });
  } else {
    await page.waitForSelector('nav', { timeout: 5000 });
  }

  // Get styles for navigation container
  const navStyles = await page.evaluate((isHashi) => {
    const nav = isHashi
      ? document.querySelector('[class*="sidebar_nav"]') || document.querySelector('aside nav')
      : document.querySelector('nav#sidebar-nav') || document.querySelector('nav');
    if (!nav) return null;

    const styles = window.getComputedStyle(nav);
    return {
      padding: styles.padding,
      margin: styles.margin,
      width: styles.width,
      backgroundColor: styles.backgroundColor,
    };
  }, isHashiCorp);

  console.log('Navigation container:', navStyles);

  // Get styles for top-level nav items
  const topLevelItems = await page.evaluate((isHashi) => {
    // Find navigation items - try multiple selectors
    const selector = isHashi
      ? '[class*="sidebar"] [class*="sidebarNavMenuItem"]:not([class*="submenu"] *)'
      : 'nav#sidebar-nav > ul > li > a, nav#sidebar-nav > ul > li > button';
    const items = document.querySelectorAll(selector);
    if (items.length === 0) {
      // Fallback
      const fallbackItems = document.querySelectorAll('nav a, nav button');
      return [];
    }

    // Get the first few items
    const results = [];
    for (let i = 0; i < Math.min(5, items.length); i++) {
      const item = items[i];
      const styles = window.getComputedStyle(item);
      const text = item.textContent.trim().substring(0, 30);

      results.push({
        text,
        tagName: item.tagName,
        classes: item.className,
        paddingLeft: styles.paddingLeft,
        paddingRight: styles.paddingRight,
        paddingTop: styles.paddingTop,
        paddingBottom: styles.paddingBottom,
        marginLeft: styles.marginLeft,
        marginTop: styles.marginTop,
        marginBottom: styles.marginBottom,
        height: styles.height,
        lineHeight: styles.lineHeight,
        fontSize: styles.fontSize,
        fontWeight: styles.fontWeight,
        backgroundColor: styles.backgroundColor,
        color: styles.color,
      });
    }
    return results;
  }, isHashiCorp);

  console.log('\nTop-level items:');
  topLevelItems.forEach((item, i) => {
    console.log(`\n${i + 1}. ${item.text}`);
    console.log(`   Tag: ${item.tagName}`);
    console.log(`   Padding: ${item.paddingTop} ${item.paddingRight} ${item.paddingBottom} ${item.paddingLeft}`);
    console.log(`   Margin: ${item.marginTop} 0 ${item.marginBottom} ${item.marginLeft}`);
    console.log(`   Height: ${item.height}, Line-height: ${item.lineHeight}`);
    console.log(`   Font: ${item.fontWeight} ${item.fontSize}`);
    console.log(`   Background: ${item.backgroundColor}`);
    console.log(`   Color: ${item.color}`);
  });

  // Get styles for nested/child nav items
  const nestedItems = await page.evaluate((isHashi) => {
    // Look for nested items - they might be in a submenu or indented
    const selector = isHashi
      ? '[class*="sidebar"] ul ul [class*="sidebarNavMenuItem"]'
      : 'nav .nav-submenu a, nav ul ul a';
    const items = document.querySelectorAll(selector);
    if (items.length === 0) return [];

    const results = [];
    for (let i = 0; i < Math.min(3, items.length); i++) {
      const item = items[i];
      const styles = window.getComputedStyle(item);
      const text = item.textContent.trim().substring(0, 30);

      results.push({
        text,
        tagName: item.tagName,
        classes: item.className,
        paddingLeft: styles.paddingLeft,
        paddingRight: styles.paddingRight,
        paddingTop: styles.paddingTop,
        paddingBottom: styles.paddingBottom,
        marginLeft: styles.marginLeft,
        height: styles.height,
        lineHeight: styles.lineHeight,
        fontSize: styles.fontSize,
        fontWeight: styles.fontWeight,
        backgroundColor: styles.backgroundColor,
        color: styles.color,
      });
    }
    return results;
  }, isHashiCorp);

  if (nestedItems.length > 0) {
    console.log('\n\nNested/child items:');
    nestedItems.forEach((item, i) => {
      console.log(`\n${i + 1}. ${item.text}`);
      console.log(`   Tag: ${item.tagName}`);
      console.log(`   Padding: ${item.paddingTop} ${item.paddingRight} ${item.paddingBottom} ${item.paddingLeft}`);
      console.log(`   Margin-left: ${item.marginLeft}`);
      console.log(`   Height: ${item.height}, Line-height: ${item.lineHeight}`);
      console.log(`   Font: ${item.fontWeight} ${item.fontSize}`);
      console.log(`   Background: ${item.backgroundColor}`);
      console.log(`   Color: ${item.color}`);
    });
  } else {
    console.log('\n\nNo nested items found');
  }

  // Get styles for active/selected items
  const activeItems = await page.evaluate(() => {
    const items = document.querySelectorAll('nav .sidebar-nav-item--active, nav [class*="active"], nav [aria-current], nav .md-nav__link--active');
    if (items.length === 0) return [];

    const results = [];
    for (let i = 0; i < Math.min(2, items.length); i++) {
      const item = items[i];
      const styles = window.getComputedStyle(item);
      const text = item.textContent.trim().substring(0, 30);

      results.push({
        text,
        classes: item.className,
        backgroundColor: styles.backgroundColor,
        color: styles.color,
        fontWeight: styles.fontWeight,
      });
    }
    return results;
  });

  if (activeItems.length > 0) {
    console.log('\n\nActive/selected items:');
    activeItems.forEach((item, i) => {
      console.log(`\n${i + 1}. ${item.text}`);
      console.log(`   Background: ${item.backgroundColor}`);
      console.log(`   Color: ${item.color}`);
      console.log(`   Font-weight: ${item.fontWeight}`);
    });
  }

  return {
    navStyles,
    topLevelItems,
    nestedItems,
    activeItems,
  };
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // Compare local site
    const localData = await getNavStyles(
      page,
      'http://127.0.0.1:8001/products/client-sdk/quickstart/',
      'LOCAL SITE',
      false
    );

    // Compare HashiCorp reference
    const hashicorpData = await getNavStyles(
      page,
      'https://developer.hashicorp.com/vault/docs/get-started/developer-qs',
      'HASHICORP REFERENCE',
      true
    );

    console.log('\n\n=== COMPARISON SUMMARY ===\n');

    // Compare padding differences
    if (localData.topLevelItems[0] && hashicorpData.topLevelItems[0]) {
      const local = localData.topLevelItems[0];
      const hashi = hashicorpData.topLevelItems[0];

      console.log('Top-level item padding:');
      console.log(`  Local:     ${local.paddingLeft} (left)`);
      console.log(`  HashiCorp: ${hashi.paddingLeft} (left)`);
      console.log(`  Difference: ${parseFloat(local.paddingLeft) - parseFloat(hashi.paddingLeft)}px\n`);
    }

    // Compare nested item padding
    if (localData.nestedItems[0] && hashicorpData.nestedItems[0]) {
      const local = localData.nestedItems[0];
      const hashi = hashicorpData.nestedItems[0];

      console.log('Nested item padding:');
      console.log(`  Local:     ${local.paddingLeft} (left)`);
      console.log(`  HashiCorp: ${hashi.paddingLeft} (left)`);
      console.log(`  Difference: ${parseFloat(local.paddingLeft) - parseFloat(hashi.paddingLeft)}px\n`);
    }

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
})();
