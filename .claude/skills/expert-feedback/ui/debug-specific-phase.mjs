import { chromium } from 'playwright'

const BASE_URL = 'http://localhost:5174'

async function debugPhase() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  console.log('Testing iteration-3...\n')

  await page.goto(`${BASE_URL}?phase=iteration-3`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(1000)

  // Check what text is actually on the page
  const bodyText = await page.evaluate(() => document.body.innerText)

  console.log('=== Body Text ===')
  console.log(bodyText)
  console.log('\n=== End Body Text ===\n')

  // Check specific elements
  const documentView = await page.locator('.document-view').count()
  const documentContent = await page.locator('.document-content').count()

  console.log(`Document view found: ${documentView}`)
  console.log(`Document content found: ${documentContent}`)

  // Get the document content text
  if (documentContent > 0) {
    const contentText = await page.locator('.document-content').innerText()
    console.log('\n=== Document Content ===')
    console.log(contentText.substring(0, 500))
    console.log('...')
  }

  // Check if specific strings are present
  const checks = ['Consensus Reached: 62%', 'Type Safety Approach', 'Expert Convergence Analysis']
  for (const check of checks) {
    const found = bodyText.includes(check)
    console.log(`\n"${check}": ${found ? '✓ FOUND' : '✗ NOT FOUND'}`)
  }

  await browser.close()
}

debugPhase().catch(console.error)
