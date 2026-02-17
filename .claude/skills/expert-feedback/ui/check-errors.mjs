import { chromium } from 'playwright'

const BASE_URL = 'http://localhost:5174'

async function checkErrors() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const errors = []
  const warnings = []

  page.on('console', msg => {
    const type = msg.type()
    const text = msg.text()

    if (type === 'error') {
      errors.push(text)
      console.log('[ERROR]', text)
    } else if (type === 'warning') {
      warnings.push(text)
      console.log('[WARN]', text)
    }
  })

  page.on('pageerror', error => {
    errors.push(error.message)
    console.log('[PAGE ERROR]', error.message)
  })

  console.log('Loading page...\n')

  try {
    await page.goto(`${BASE_URL}?phase=iteration-1`, { waitUntil: 'networkidle', timeout: 10000 })
    await page.waitForTimeout(2000)

    console.log(`\n${errors.length} errors, ${warnings.length} warnings`)

    // Check if app mounted
    const appContainer = await page.locator('.app-container').count()
    console.log(`\nApp container found: ${appContainer > 0 ? 'Yes' : 'No'}`)

    // Try to get the root HTML
    const html = await page.evaluate(() => {
      const root = document.getElementById('root')
      return root ? root.innerHTML.substring(0, 500) : 'No root element'
    })
    console.log('\nRoot HTML:', html)

  } catch (error) {
    console.log('Page load error:', error.message)
  }

  await browser.close()
}

checkErrors().catch(console.error)
