import { chromium } from 'playwright'

const BASE_URL = 'http://localhost:5174'

async function debugUserApproval() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  console.log('Loading user-approval phase...\n')

  await page.goto(`${BASE_URL}?phase=user-approval`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(2000)

  const bodyText = await page.evaluate(() => document.body.innerText)

  console.log('=== Full Page Text ===\n')
  console.log(bodyText)
  console.log('\n=== End ===\n')

  // Check for specific text
  console.log('Searching for: "Expert Convergence: 95%"')
  console.log('Found:', bodyText.includes('Expert Convergence: 95%') ? 'YES ✓' : 'NO ✗')
  console.log('Also checking: "95%"')
  console.log('Found:', bodyText.includes('95%') ? 'YES ✓' : 'NO ✗')

  console.log('\nSearching for: "156000"')
  console.log('Found:', bodyText.includes('156000') ? 'YES ✓' : 'NO ✗')
  console.log('Also checking: "156,000"')
  console.log('Found:', bodyText.includes('156,000') ? 'YES ✓' : 'NO ✗')

  console.log('\n=== Document View Content ===')
  const docContent = await page.locator('.document-content').count()
  console.log('Document content elements found:', docContent)

  if (docContent > 0) {
    const text = await page.locator('.document-content').first().innerText()
    console.log('First 500 chars:')
    console.log(text.substring(0, 500))
  }

  console.log('\n=== Action Panel Content ===')
  const approvalPanel = await page.locator('.approval-panel').count()
  console.log('Approval panel found:', approvalPanel)

  if (approvalPanel > 0) {
    const text = await page.locator('.approval-panel').first().innerText()
    console.log('Approval panel text:')
    console.log(text)
  }

  await browser.close()
}

debugUserApproval().catch(console.error)
