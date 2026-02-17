import { chromium } from 'playwright'

const BASE_URL = 'http://localhost:5174'

async function debugPhase() {
  const browser = await chromium.launch({ headless: false })
  const page = await browser.newPage()

  console.log('Loading iteration-1...\n')

  await page.goto(`${BASE_URL}?phase=iteration-1`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(1000)

  // Check what's in the DOM
  const bodyText = await page.evaluate(() => document.body.innerText)
  console.log('Body text (first 1000 chars):')
  console.log(bodyText.substring(0, 1000))
  console.log('\n---\n')

  // Check for specific elements
  const hasQuestions = await page.locator('.questions-panel').count()
  const hasActionPane = await page.locator('.action-pane').count()
  const hasAgentList = await page.locator('.agent-list').count()

  console.log(`Questions panel: ${hasQuestions}`)
  console.log(`Action pane: ${hasActionPane}`)
  console.log(`Agent list: ${hasAgentList}`)

  // Check zustand state
  const state = await page.evaluate(() => {
    return window.__ZUSTAND_STORE_STATE__ || 'No state found'
  })
  console.log('\nZustand state:', JSON.stringify(state, null, 2))

  await page.waitForTimeout(5000) // Keep browser open for inspection
  await browser.close()
}

debugPhase().catch(console.error)
