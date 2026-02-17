import { chromium } from 'playwright'

const BASE_URL = 'http://localhost:5174'

const TEST_PHASES = [
  { name: 'iteration-1', url: '?phase=iteration-1', checks: ['Questions from Experts', 'TypeScript Expert', 'Should we use strict mode'] },
  { name: 'iteration-3', url: '?phase=iteration-3', checks: ['Expert Convergence Analysis', 'Consensus Reached: 62%', 'Type Safety Approach'] },
  { name: 'artifact-gen', url: '?phase=artifact-gen', checks: ['Draft ADR', 'Multi-Language SDK Design', 'Key Requirements'] },
  { name: 'concern-review', url: '?phase=concern-review', checks: ['Generated Draft Artifact', 'API Surface', 'Review Status'] },
  { name: 'synthesize-concerns', url: '?phase=synthesize-concerns', checks: ['Concerns Synthesis', 'TypeScript Expert Concerns', 'Type Safety in Edge Cases'] },
  { name: 'user-concern-review', url: '?phase=user-concern-review', checks: ['Review Concerns', 'Type safety in edge cases', 'Performance implications'] },
  { name: 'address-concerns', url: '?phase=address-concerns', checks: ['Addressing Type Safety Concerns', 'Enhanced Type Guards', 'Branded types'] },
  { name: 'synthesize-updates', url: '?phase=synthesize-updates', checks: ['Concern Resolution Updates', 'TypeScript Expert Updates', 'Frontend Expert Updates'] },
  { name: 'regenerate-artifact', url: '?phase=regenerate-artifact', checks: ['Updated Draft ADR', 'v2.0', 'Branded types prevent ID confusion'] },
  { name: 'user-approval', url: '?phase=user-approval', checks: ['Final Multi-Language SDK Specification', '95%', '156,000'] }
]

async function testPhases() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  console.log('Testing phase configurations...\n')

  let passed = 0
  let failed = 0

  for (const test of TEST_PHASES) {
    process.stdout.write(`Testing ${test.name}... `)

    try {
      await page.goto(`${BASE_URL}${test.url}`, { waitUntil: 'networkidle' })
      await page.waitForTimeout(500) // Allow state to settle

      const content = await page.content()

      const missing = test.checks.filter(check => !content.includes(check))

      if (missing.length === 0) {
        console.log('✓ PASS')
        passed++
      } else {
        console.log('✗ FAIL')
        console.log(`  Missing: ${missing.join(', ')}`)
        failed++
      }
    } catch (error) {
      console.log('✗ ERROR')
      console.log(`  ${error.message}`)
      failed++
    }
  }

  await browser.close()

  console.log(`\n${passed}/${TEST_PHASES.length} tests passed`)

  if (failed > 0) {
    process.exit(1)
  }
}

testPhases().catch(console.error)
