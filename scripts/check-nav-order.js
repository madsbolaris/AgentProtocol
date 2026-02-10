const puppeteer = require("puppeteer");

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto("http://127.0.0.1:8001/products/client-sdk/", {
    waitUntil: "networkidle2",
    timeout: 15000
  });
  await page.waitForSelector("nav#sidebar-nav", { timeout: 10000 });

  const navOrder = await page.evaluate(() => {
    const allItems = [];
    const navList = document.querySelector("nav#sidebar-nav > ul");

    if (navList) {
      const children = Array.from(navList.children);

      children.forEach((li) => {
        const button = li.querySelector("button[data-nav-toggle]");
        const link = li.querySelector("a");

        if (button) {
          allItems.push(button.textContent.trim());
        } else if (link) {
          const text = link.textContent.trim();
          if (text.includes("Quickstart") || text === "Client SDK" || text === "Examples" || text === "Patterns" || text === "Troubleshooting") {
            allItems.push(text);
          }
        }
      });
    }

    return allItems.slice(0, 12); // Get first 12 items
  });

  console.log("✅ Final Navigation Order:");
  console.log("═══════════════════════════════════════════════════\n");
  navOrder.forEach((item, idx) => {
    console.log((idx + 1) + ". " + item);
  });
  console.log("\n═══════════════════════════════════════════════════");
  console.log("Learning flow: Try → Inspire → Understand → Practice");
  console.log("Reference at bottom for lookup");
  console.log("═══════════════════════════════════════════════════\n");

  await browser.close();
})();
