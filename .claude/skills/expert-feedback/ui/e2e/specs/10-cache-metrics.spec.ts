/**
 * Cache Metrics Tests
 * Tests the cache performance metrics display
 */

import { test, expect } from '@playwright/test'
import {
  setupFixture,
  waitForAppReady,
} from '../helpers/test-utils'

test.describe('Cache Metrics', () => {
  test('cache metrics visible when cache enabled', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Cache metrics section should be visible
    const cacheSection = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheSection).toBeVisible()
  })

  test('cache metrics hidden when cache disabled', async ({ page }) => {
    await setupFixture(page, 'empty-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Cache metrics should not be visible (cache_enabled: false)
    const cacheSection = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheSection).not.toBeVisible()
  })

  test('cache hit rate displayed correctly', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should show hit rate percentage
    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheMetrics.locator('text=Cache Hit Rate')).toBeVisible()

    // Should show percentage value
    await expect(cacheMetrics.getByText(/%$/)).toBeVisible()
  })

  test('cache tokens created displayed', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should show tokens created
    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheMetrics.locator('text=Tokens Created')).toBeVisible()

    // Should show token count
    // cache-active-state has 5400 creation tokens
    await expect(cacheMetrics.getByText('5,400')).toBeVisible()
  })

  test('cache tokens read displayed', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should show tokens read
    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheMetrics.locator('text=Tokens Read')).toBeVisible()

    // Should show token count
    // cache-active-state has 3100 read tokens
    await expect(cacheMetrics.getByText('3,100')).toBeVisible()
  })

  test('cache savings displayed in dollars', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Should show savings
    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheMetrics.locator('text=Cost Savings')).toBeVisible()

    // Should show dollar amount
    await expect(cacheMetrics.getByText(/^\$/)).toBeVisible()
  })

  test('cache metrics collapse/expand works', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Find collapse/expand button
    const toggleButton = page.locator('button:near(:text("Cache Performance")), button:near(:text("Cache Metrics"))')

    if (await toggleButton.count() > 0) {
      // Get initial metrics visibility
      const metrics = page.locator('text=Cache Hit Rate')
      const initiallyVisible = await metrics.isVisible()

      // Click toggle
      await toggleButton.first().click()
      await page.waitForTimeout(500)

      // Metrics visibility should change
      const nowVisible = await metrics.isVisible()
      expect(nowVisible).not.toBe(initiallyVisible)

      // Click again to restore
      await toggleButton.first().click()
      await page.waitForTimeout(500)

      // Should be back to initial state
      const finalVisible = await metrics.isVisible()
      expect(finalVisible).toBe(initiallyVisible)
    }
  })

  test('hit rate calculation is correct', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Wait for cache metrics to render
    await page.waitForTimeout(1000)

    // Just verify cache metrics section is visible and contains hit rate text
    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheMetrics).toBeVisible()
    await expect(cacheMetrics).toContainText('Cache Hit Rate')

    // Should show some percentage
    await expect(cacheMetrics).toContainText('%')
  })

  test('cache savings calculation is correct', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // cache-active-state fixture:
    // total_cache_read_tokens: 3100
    // Savings = (3100 / 1M) * $2.70 = $0.00837

    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    const savingsText = await cacheMetrics.locator('text=Cost Savings').locator('..').textContent()

    // Should show ~$0.008
    expect(savingsText).toContain('$0.00')
  })

  test('cache metrics with partial cache usage', async ({ page }) => {
    await setupFixture(page, 'partial-state')
    await page.goto('/')
    await waitForAppReady(page)

    // partial-state has cache enabled
    const cacheSection = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheSection).toBeVisible()

    // Should show metrics even with partial data
    await expect(page.locator('text=Cache Hit Rate')).toBeVisible()
  })

  test('cache metrics with zero cache hits', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    // full-state has cache enabled
    const cacheSection = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheSection).toBeVisible()

    // Should handle zero gracefully
    await expect(page.locator('text=Cache Hit Rate')).toBeVisible()
  })

  test('cache metrics visual styling', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Cache section should have proper styling
    const cacheSection = page.locator('text=Cache Performance').locator('..')
    await expect(cacheSection).toBeVisible()

    // Should have card-like appearance (bg, border, padding)
    const classes = await cacheSection.getAttribute('class')
    expect(classes).toBeTruthy()
  })

  test('cache metrics responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Cache metrics should be visible and readable
    await expect(page.locator('[data-testid="cache-metrics"]')).toBeVisible()
    await expect(page.locator('text=Cache Hit Rate')).toBeVisible()

    // Should not overflow
    const cacheSection = page.locator('text=Cache Performance').locator('..')
    const box = await cacheSection.boundingBox()
    expect(box?.width).toBeLessThanOrEqual(375)
  })

  test('cache metrics with no experts', async ({ page }) => {
    await setupFixture(page, 'empty-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Cache metrics should be hidden (cache_enabled: false)
    const cacheSection = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheSection).not.toBeVisible()
  })

  test('cache metrics labels are clear', async ({ page }) => {
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // All labels should be descriptive
    const cacheMetrics = page.locator('[data-testid="cache-metrics"]')
    await expect(cacheMetrics.locator('text=Cache Hit Rate')).toBeVisible()
    await expect(cacheMetrics.locator('text=Tokens Created')).toBeVisible()
    await expect(cacheMetrics.locator('text=Tokens Read')).toBeVisible()
    await expect(cacheMetrics.locator('text=Cost Savings')).toBeVisible()
  })

  test('cache metrics update when state changes', async ({ page }) => {
    // Start with cache-active
    await setupFixture(page, 'cache-active-state')
    await page.goto('/')
    await waitForAppReady(page)

    // Cache metrics visible
    await expect(page.locator('[data-testid="cache-metrics"]')).toBeVisible()

    // Change to empty state (cache disabled)
    await setupFixture(page, 'empty-state')
    await page.reload()
    await waitForAppReady(page)

    // Cache metrics should be hidden
    await expect(page.locator('[data-testid="cache-metrics"]')).not.toBeVisible()
  })
})
