const puppeteer = require("puppeteer");

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Check HashiCorp reference - a nested page
  await page.goto("https://developer.hashicorp.com/terraform/docs/configuration/blocks", {
    waitUntil: "networkidle2",
    timeout: 15000
  });

  const hashicorpActive = await page.evaluate(() => {
    const nav = document.querySelector("nav[aria-label=\"Sidebar\"]");
    if (!nav) return { error: "Nav not found" };

    // Find expanded buttons
    const expandedButtons = Array.from(nav.querySelectorAll("button[data-open=\"true\"]"))
      .map(btn => ({
        text: btn.textContent.trim().substring(0, 30),
        classes: btn.className,
        hasActiveBg: window.getComputedStyle(btn).backgroundColor
      }));

    // Find active links
    const activeLinks = Array.from(nav.querySelectorAll("a[aria-current=\"page\"]"))
      .map(link => ({
        text: link.textContent.trim().substring(0, 30),
        classes: link.className,
        hasActiveBg: window.getComputedStyle(link).backgroundColor
      }));

    return { expandedButtons, activeLinks };
  });

  console.log("HashiCorp Reference (nested page):");
  console.log("\nExpanded buttons:");
  hashicorpActive.expandedButtons.forEach(btn => {
    console.log(`  ${btn.text}`);
    console.log(`    Background: ${btn.hasActiveBg}`);
  });

  console.log("\nActive links:");
  hashicorpActive.activeLinks.forEach(link => {
    console.log(`  ${link.text}`);
    console.log(`    Background: ${link.hasActiveBg}`);
  });

  await browser.close();
})();
