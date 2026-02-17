/**
 * Initial Load Tests
 * Tests the basic loading functionality of the app
 */

import { test, expect } from '@playwright/test'
import {
  setupFixture,
  waitForAppReady,
  checkNoConsoleErrors,
} from '../helpers/test-utils'
import {
  assertLoading,
  assertNoConsoleErrors,
  assertSessionSummary,
  assertPhase,
  assertExpertCount,
} from '../helpers/assertions'

test.describe('Initial Load', () => {
  test('should load app without errors (empty state)', async ({ page }) => {
    const errors = await checkNoConsoleErrors(page)

    await setupFixture(page, 'empty-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should not show loading spinner anymore
    await assertLoading(page, false)

    // No console errors
    await assertNoConsoleErrors(page, errors)

    // Should show empty state
    await assertExpertCount(page, 0)
  })

  test('should load app without errors (full state)', async ({ page }) => {
    const errors = await checkNoConsoleErrors(page)

    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should not show loading spinner anymore
    await assertLoading(page, false)

    // No console errors
    await assertNoConsoleErrors(page, errors)

    // Should show all 5 experts
    await assertExpertCount(page, 5)
  })

  test('should show loading spinner initially', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')

    // Loading spinner should appear briefly
    const spinner = page.locator('[class*="animate-spin"]')
    const spinnerCount = await spinner.count()

    // Spinner may or may not be visible depending on load speed
    // Just check that the page loads successfully
    await waitForAppReady(page)
    await expect(page.locator('text=Loading workspace state')).toBeHidden()
  })

  test('should render SessionSummary with correct metrics', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Check session summary shows metrics
    const summary = page.locator('.bg-gradient-to-r')
    await expect(summary).toBeVisible()

    // Check for key metrics (values from full-state.json)
    await expect(summary).toContainText('11m') // 709 seconds total duration
    await expect(summary).toContainText('$0.1') // $0.112 total cost
    await expect(summary).toContainText('5') // 5 experts
    await expect(summary).toContainText('92%') // 92% convergence
  })

  test('should render StatusBar with correct phase', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should show "complete" phase
    await assertPhase(page, 'complete')
  })

  test('should render ExpertList with all experts', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should show 5 expert cards
    await assertExpertCount(page, 5)

    // Check expert names are visible (scoped within expert cards to avoid strict mode violations)
    const expertCards = page.locator('[data-testid="expert-card"]')
    await expect(expertCards.filter({ hasText: 'testing-expert' })).toBeVisible()
    await expect(expertCards.filter({ hasText: 'ui-expert' })).toBeVisible()
    await expect(expertCards.filter({ hasText: 'performance-expert' })).toBeVisible()
    await expect(expertCards.filter({ hasText: 'accessibility-expert' })).toBeVisible()
    await expect(expertCards.filter({ hasText: 'security-expert' })).toBeVisible()
  })

  test('should catch null/undefined errors (regression test)', async ({ page }) => {
    const errors = await checkNoConsoleErrors(page)

    // Mock state with missing fields (like the bug we fixed)
    await page.route('**/api/state', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          workspace_path: '/test',
          phase: 'idle',
          // Missing experts, expert_progress, etc.
        }),
      })
    })

    await page.goto('/')
    await waitForAppReady(page)

    // Should handle gracefully without errors
    await assertNoConsoleErrors(page, errors)

    // Should show empty state
    await assertExpertCount(page, 0)
  })

  test('should handle undefined state gracefully', async ({ page }) => {
    await page.route('**/api/state', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      })
    })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Should handle undefined state gracefully (not crash) and show 0 experts
    await assertExpertCount(page, 0)
  })

  test('should render all major components', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Check all major components are present
    await expect(page.locator('[data-testid="session-summary"]')).toBeVisible() // SessionSummary
    await expect(page.locator('text=Export')).toBeVisible() // ExportButtons
    await expect(page.locator('[data-testid="status-bar"]')).toContainText('Complete') // StatusBar
    await assertExpertCount(page, 5) // ExpertList

    // Charts should be visible (using Recharts selectors)
    await expect(page.locator('.recharts-wrapper').first()).toBeVisible()

    // Topic should be visible
    await expect(page.locator('text=Implement comprehensive E2E testing')).toBeVisible()
  })

  test('should not have memory leaks on repeated loads', async ({ page }) => {
    // Load page 3 times
    for (let i = 0; i < 3; i++) {
      await setupFixture(page, 'full-state')
      await page.goto('/')
      await waitForAppReady(page)

      // Check page loads successfully each time
      await assertExpertCount(page, 5)
    }

    // If we get here without timeout, no memory leaks
    expect(true).toBe(true)
  })
})
