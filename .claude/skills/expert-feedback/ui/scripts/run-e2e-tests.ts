/**
 * Automated E2E Test Runner
 * Runs Playwright tests and reports results
 */

import { exec } from 'child_process'
import { promisify } from 'util'
import * as fs from 'fs'
import * as path from 'path'

const execAsync = promisify(exec)

interface TestResults {
  passed: number
  failed: number
  total: number
  duration: number
}

async function runTests(): Promise<TestResults> {
  console.log('🚀 Starting E2E test suite...\n')

  const startTime = Date.now()

  try {
    // Run Playwright tests
    const { stdout, stderr } = await execAsync('npx playwright test', {
      cwd: path.resolve(__dirname, '..'),
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
    })

    const duration = Math.round((Date.now() - startTime) / 1000)

    // Parse results from output
    const passedMatch = stdout.match(/(\d+) passed/)
    const failedMatch = stdout.match(/(\d+) failed/)
    const totalMatch = stdout.match(/(\d+) total/)

    const passed = passedMatch ? parseInt(passedMatch[1]) : 0
    const failed = failedMatch ? parseInt(failedMatch[1]) : 0
    const total = totalMatch ? parseInt(totalMatch[1]) : passed + failed

    console.log(stdout)
    if (stderr) console.error(stderr)

    return { passed, failed, total, duration }
  } catch (error: any) {
    const duration = Math.round((Date.now() - startTime) / 1000)

    // Tests failed, but we can still parse results
    const output = error.stdout || ''
    const passedMatch = output.match(/(\d+) passed/)
    const failedMatch = output.match(/(\d+) failed/)

    const passed = passedMatch ? parseInt(passedMatch[1]) : 0
    const failed = failedMatch ? parseInt(failedMatch[1]) : 0
    const total = passed + failed

    console.log(output)
    if (error.stderr) console.error(error.stderr)

    return { passed, failed, total, duration }
  }
}

async function generateReport(results: TestResults) {
  console.log('\n' + '='.repeat(60))
  console.log('📊 TEST RESULTS SUMMARY')
  console.log('='.repeat(60))
  console.log(`✅ Tests passed: ${results.passed}`)
  console.log(`❌ Tests failed: ${results.failed}`)
  console.log(`📝 Total tests: ${results.total}`)
  console.log(`⏱️  Duration: ${results.duration}s`)
  console.log('='.repeat(60))

  // Calculate success rate
  const successRate = results.total > 0
    ? ((results.passed / results.total) * 100).toFixed(1)
    : '0'
  console.log(`\n🎯 Success rate: ${successRate}%`)

  // Performance check
  if (results.duration < 60) {
    console.log('⚡ Performance: EXCELLENT (< 60s)')
  } else if (results.duration < 120) {
    console.log('✅ Performance: GOOD (< 2 minutes)')
  } else {
    console.log('⚠️  Performance: SLOW (> 2 minutes)')
  }

  // Check for failures
  if (results.failed > 0) {
    console.log('\n🔍 FAILURE DETAILS')
    console.log('='.repeat(60))
    console.log('Check test-results/ directory for screenshots')
    console.log('Run "npx playwright show-report" to see detailed HTML report')
    console.log('='.repeat(60))

    // List failed test screenshots
    const testResultsDir = path.resolve(__dirname, '..', 'test-results')
    if (fs.existsSync(testResultsDir)) {
      const files = fs.readdirSync(testResultsDir)
      const screenshots = files.filter((file) => file.endsWith('.png'))

      if (screenshots.length > 0) {
        console.log('\n📸 Screenshots captured:')
        screenshots.forEach((file) => {
          console.log(`   - ${file}`)
        })
      }
    }
  }
}

async function main() {
  try {
    const results = await runTests()
    await generateReport(results)

    // Exit with appropriate code
    if (results.failed > 0) {
      console.log('\n❌ Some tests failed. Fix the issues and try again.')
      process.exit(1)
    } else {
      console.log('\n🎉 All tests passed!')
      process.exit(0)
    }
  } catch (error: any) {
    console.error('\n💥 Fatal error running tests:')
    console.error(error.message)
    process.exit(1)
  }
}

main()
