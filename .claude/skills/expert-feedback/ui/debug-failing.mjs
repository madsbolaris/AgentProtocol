import { chromium } from 'playwright'

const BASE_URL = 'http://localhost:5174'

async function debugFailingPhases() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  // Test 1: address-concerns
  console.log('=== Testing address-concerns ===\n')
  await page.goto(`${BASE_URL}?phase=address-concerns`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(1000)

  let bodyText = await page.evaluate(() => document.body.innerText)

  console.log('Looking for: "Enhanced Type Guards"')
  console.log('Found:', bodyText.includes('Enhanced Type Guards') ? 'YES' : 'NO')
  console.log('Looking for: "Branded types"')
  console.log('Found:', bodyText.includes('Branded types') ? 'YES' : 'NO')
  console.log('\nSnippet of content:')
  console.log(bodyText.substring(0, 800))

  // Test 2: user-approval
  console.log('\n\n=== Testing user-approval ===\n')
  await page.goto(`${BASE_URL}?phase=user-approval`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(1000)

  bodyText = await page.evaluate(() => document.body.innerText)

  console.log('Looking for: "Expert Convergence: 95%"')
  console.log('Found:', bodyText.includes('Expert Convergence: 95%') ? 'YES' : 'NO')
  console.log('Looking for: "156000"')
  console.log('Found:', bodyText.includes('156000') ? 'YES' : 'NO')
  console.log('\nSnippet of content:')
  console.log(bodyText.substring(bodyText.indexOf('Final Multi-Language'), bodyText.indexOf('Final Multi-Language') + 1000))

  await browser.close()
}

debugFailingPhases().catch(console.error)
