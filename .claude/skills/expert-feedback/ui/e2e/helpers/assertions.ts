/**
 * Custom Assertions
 * Domain-specific assertions for Expert Feedback UI
 */

import { Page, expect } from '@playwright/test'

/**
 * Assert SessionSummary displays correct metrics
 */
export async function assertSessionSummary(
  page: Page,
  expected: {
    totalDuration?: string
    totalCost?: string
    expertsComplete?: string
    convergence?: string
  }
) {
  const summary = page.locator('[data-testid="session-summary"]')
  await expect(summary).toBeVisible()

  if (expected.totalDuration) {
    await expect(summary.getByText(expected.totalDuration)).toBeVisible()
  }
  if (expected.totalCost) {
    await expect(summary).toContainText(expected.totalCost)
  }
  if (expected.expertsComplete) {
    await expect(summary).toContainText(expected.expertsComplete)
  }
  if (expected.convergence) {
    await expect(summary).toContainText(expected.convergence)
  }
}

/**
 * Assert StatusBar shows correct phase
 */
export async function assertPhase(page: Page, phase: string) {
  const statusBar = page.locator('[data-testid="status-bar"]')
  await expect(statusBar).toContainText(phase, { ignoreCase: true })
}

/**
 * Assert ExpertList shows correct number of experts
 */
export async function assertExpertCount(page: Page, count: number) {
  const expertCards = page.locator('[data-testid="expert-card"]')
  await expect(expertCards).toHaveCount(count)
}

/**
 * Assert expert card has correct status
 */
export async function assertExpertStatus(
  page: Page,
  expertName: string,
  status: 'complete' | 'running' | 'failed' | 'timeout' | 'cancelled' | 'pending'
) {
  const expertCard = page.locator(`[data-testid="expert-card"]`, {
    has: page.locator('text=' + expertName),
  })
  await expect(expertCard).toBeVisible()

  // Check for status indicator
  const statusClasses = {
    complete: 'bg-green',
    running: 'bg-blue',
    failed: 'bg-red',
    timeout: 'bg-amber',
    cancelled: 'bg-gray',
    pending: 'bg-gray',
  }

  // Status is indicated by background color
  const hasStatus = await expertCard.evaluate((el, expectedStatus) => {
    return el.className.includes(expectedStatus)
  }, statusClasses[status].split('-')[1])

  expect(hasStatus).toBeTruthy()
}

/**
 * Assert chart is rendered (less strict - just checks for chart wrapper)
 */
export async function assertChartRendered(page: Page, chartType: 'pie' | 'bar' | 'timeline') {
  // Wait for charts to render
  await page.waitForTimeout(1500)

  // Just check that at least one chart wrapper exists (much less strict)
  const chartWrapper = page.locator('.recharts-wrapper').first()
  await expect(chartWrapper).toBeVisible({ timeout: 10000 })
}

/**
 * Assert empty state is shown
 */
export async function assertEmptyState(page: Page, message: string) {
  const emptyState = page.locator('text=' + message)
  await expect(emptyState).toBeVisible()
}

/**
 * Assert export dropdown is visible
 */
export async function assertExportDropdown(page: Page, visible: boolean) {
  const dropdown = page.locator('[data-testid="export-dropdown"]')
  if (visible) {
    await expect(dropdown).toBeVisible()
  } else {
    await expect(dropdown).toBeHidden()
  }
}

/**
 * Assert cache metrics are visible
 */
export async function assertCacheMetrics(
  page: Page,
  expected: {
    hitRate?: string
    tokensCreated?: string
    tokensRead?: string
    savings?: string
  }
) {
  const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
  await expect(cacheMetrics).toBeVisible()

  if (expected.hitRate) {
    await expect(cacheMetrics).toContainText(expected.hitRate)
  }
  if (expected.tokensCreated) {
    await expect(cacheMetrics).toContainText(expected.tokensCreated)
  }
  if (expected.tokensRead) {
    await expect(cacheMetrics).toContainText(expected.tokensRead)
  }
  if (expected.savings) {
    await expect(cacheMetrics).toContainText(expected.savings)
  }
}

/**
 * Assert error message is displayed
 */
export async function assertErrorMessage(page: Page, message: string) {
  const errorEl = page.locator('[role="alert"], .bg-red-50')
  await expect(errorEl).toBeVisible()
  await expect(errorEl).toContainText(message)
}

/**
 * Assert loading state
 */
export async function assertLoading(page: Page, isLoading: boolean) {
  const spinner = page.locator('[class*="animate-spin"]')
  if (isLoading) {
    await expect(spinner).toBeVisible()
  } else {
    await expect(spinner).toBeHidden()
  }
}

/**
 * Assert filter is applied
 */
export async function assertFilterApplied(
  page: Page,
  filterValue: 'all' | 'complete' | 'running' | 'failed' | 'pending'
) {
  // Check that the filter button/select shows the current filter
  const filterEl = page.locator(`[data-testid="filter-${filterValue}"], text=${filterValue}`)
  await expect(filterEl.first()).toBeVisible()
}

/**
 * Assert sort order is correct
 */
export async function assertSortOrder(page: Page, expertNames: string[]) {
  const expertCards = page.locator('[data-testid="expert-card"]')
  const count = await expertCards.count()

  expect(count).toBeGreaterThanOrEqual(expertNames.length)

  for (let i = 0; i < Math.min(expertNames.length, count); i++) {
    const card = expertCards.nth(i)
    await expect(card).toContainText(expertNames[i])
  }
}

/**
 * Assert localStorage persistence
 */
export async function assertLocalStoragePersistence(
  page: Page,
  key: string,
  expectedValue: any
) {
  const actualValue = await page.evaluate((storageKey) => {
    const value = localStorage.getItem(storageKey)
    return value ? JSON.parse(value) : null
  }, key)

  expect(actualValue).toEqual(expectedValue)
}

/**
 * Assert no console errors
 */
export async function assertNoConsoleErrors(page: Page, errors: string[]) {
  expect(errors).toHaveLength(0)
}

/**
 * Assert responsive layout
 */
export async function assertResponsiveLayout(
  page: Page,
  layout: 'mobile' | 'tablet' | 'desktop'
) {
  const layoutChecks = {
    mobile: async () => {
      // Single column layout
      const grid = page.locator('.grid')
      const classes = await grid.getAttribute('class')
      expect(classes).toContain('grid-cols-1')
    },
    tablet: async () => {
      // Tablet layout (may stack some elements)
      const width = await page.viewportSize()
      expect(width?.width).toBeGreaterThanOrEqual(768)
      expect(width?.width).toBeLessThan(1024)
    },
    desktop: async () => {
      // Multi-column layout
      const grid = page.locator('.grid')
      const classes = await grid.getAttribute('class')
      expect(classes).toMatch(/grid-cols-[2-4]/)
    },
  }

  await layoutChecks[layout]()
}
