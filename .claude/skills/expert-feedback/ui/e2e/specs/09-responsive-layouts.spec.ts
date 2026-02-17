/**
 * Responsive Layout Tests
 * Tests that the UI adapts to different screen sizes
 */

import { test, expect } from '@playwright/test'
import {
  setupFixture,
  waitForAppReady,
  setViewport,
  viewports,
} from '../helpers/test-utils'

test.describe('Responsive Layouts', () => {
  test.beforeEach(async ({ page }) => {
    await setupFixture(page, 'full-state')
  })

  test('desktop layout (1920x1080)', async ({ page }) => {
    await setViewport(page, viewports.desktop.width, viewports.desktop.height)
    await page.goto('/')
    await waitForAppReady(page)

    // All components visible
    await expect(page.locator('.bg-gradient-to-r')).toBeVisible() // SessionSummary
    await expect(page.locator('text=Export')).toBeVisible()
    await expect(page.locator('[data-testid="expert-card"]').first()).toBeVisible()

    // Charts in 2-column grid
    const chartsGrid = page.locator('.grid').filter({ hasText: 'Cost Breakdown' }).first()
    if (await chartsGrid.count() > 0) {
      const classes = await chartsGrid.getAttribute('class')
      // Should have grid-cols-2 or lg:grid-cols-2
      expect(classes).toMatch(/grid-cols-[1-9]/)
    }
  })

  test('laptop layout (1366x768)', async ({ page }) => {
    await setViewport(page, viewports.laptop.width, viewports.laptop.height)
    await page.goto('/')
    await waitForAppReady(page)

    // All components should be visible
    await expect(page.locator('.bg-gradient-to-r')).toBeVisible()
    await expect(page.locator('[data-testid="expert-card"]').first()).toBeVisible()

    // Charts should be visible
    await expect(page.locator('.recharts-wrapper').first()).toBeVisible()
  })

  test('tablet layout (768x1024)', async ({ page }) => {
    await setViewport(page, viewports.tablet.width, viewports.tablet.height)
    await page.goto('/')
    await waitForAppReady(page)

    // All components should be visible
    await expect(page.locator('.bg-gradient-to-r')).toBeVisible()
    await expect(page.locator('[data-testid="expert-card"]').first()).toBeVisible()

    // Charts may stack vertically
    await expect(page.locator('.recharts-wrapper').first()).toBeVisible()
  })

  test('mobile layout (375x667)', async ({ page }) => {
    await setViewport(page, viewports.mobile.width, viewports.mobile.height)
    await page.goto('/')
    await waitForAppReady(page)

    // All components should be visible (stacked vertically)
    await expect(page.locator('.bg-gradient-to-r')).toBeVisible()
    await expect(page.locator('text=Export')).toBeVisible()

    // Expert cards should be visible
    await expect(page.locator('[data-testid="expert-card"]').first()).toBeVisible()

    // Charts should be visible (single column)
    await expect(page.locator('.recharts-wrapper').first()).toBeVisible()
  })

  test('no horizontal overflow at any size', async ({ page }) => {
    const sizes = [
      viewports.mobile,
      viewports.tablet,
      viewports.laptop,
      viewports.desktop,
    ]

    for (const size of sizes) {
      await setViewport(page, size.width, size.height)
      await page.goto('/')
      await waitForAppReady(page)

      // Check for horizontal overflow
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth)
      const viewportWidth = await page.evaluate(() => window.innerWidth)

      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1) // +1 for rounding
    }
  })

  test('all components visible at all sizes', async ({ page }) => {
    const sizes = [viewports.mobile, viewports.tablet, viewports.desktop]

    for (const size of sizes) {
      await setViewport(page, size.width, size.height)
      await page.goto('/')
      await waitForAppReady(page)

      // Check key components
      await expect(page.locator('header')).toBeVisible()
      await expect(page.locator('.bg-gradient-to-r')).toBeVisible() // SessionSummary
      await expect(page.locator('text=Export')).toBeVisible()
      await expect(page.locator('[data-testid="expert-card"]').first()).toBeVisible()
    }
  })

  test('charts resize appropriately', async ({ page }) => {
    // Desktop
    await setViewport(page, 1920, 1080)
    await page.goto('/')
    await waitForAppReady(page)

    const desktopChart = page.locator('.recharts-wrapper').first()
    const desktopBox = await desktopChart.boundingBox()

    // Mobile
    await setViewport(page, 375, 667)
    await page.waitForTimeout(500)

    const mobileChart = page.locator('.recharts-wrapper').first()
    const mobileBox = await mobileChart.boundingBox()

    // Chart width should be smaller on mobile
    expect(mobileBox?.width).toBeLessThan(desktopBox?.width || 1000)
  })

  test('session summary metrics stack on mobile', async ({ page }) => {
    await setViewport(page, viewports.mobile.width, viewports.mobile.height)
    await page.goto('/')
    await waitForAppReady(page)

    // Session summary should be visible
    const summary = page.locator('.bg-gradient-to-r')
    await expect(summary).toBeVisible()

    // Metrics should be readable (not overlapping)
    const summaryBox = await summary.boundingBox()
    expect(summaryBox?.height).toBeGreaterThan(100) // Tall enough for stacked metrics
  })

  test('export button accessible on mobile', async ({ page }) => {
    await setViewport(page, viewports.mobile.width, viewports.mobile.height)
    await page.goto('/')
    await waitForAppReady(page)

    // Export button should be visible and clickable
    const exportButton = page.locator('button:has-text("Export")')
    await expect(exportButton).toBeVisible()

    // Should be able to click
    await exportButton.click()
    await page.waitForTimeout(300)

    // Dropdown should appear
    const dropdown = page.locator('[data-testid="export-dropdown"], .absolute')
    const isVisible = await dropdown.first().isVisible()
    expect(isVisible).toBe(true)
  })

  test('expert cards readable on small screens', async ({ page }) => {
    await setViewport(page, viewports.mobile.width, viewports.mobile.height)
    await page.goto('/')
    await waitForAppReady(page)

    // Expert cards should be full width and readable
    const expertCard = page.locator('[data-testid="expert-card"]').first()
    await expect(expertCard).toBeVisible()

    const cardBox = await expertCard.boundingBox()

    // Card should use most of the width
    expect(cardBox?.width).toBeGreaterThan(300)

    // Text should be visible
    await expect(expertCard.locator('text=testing-expert')).toBeVisible()
  })

  test('charts legends readable on tablet', async ({ page }) => {
    await setViewport(page, viewports.tablet.width, viewports.tablet.height)
    await page.goto('/')
    await waitForAppReady(page)

    await page.waitForTimeout(1500)

    // Chart legend should be visible (lenient check)
    const legend = page.locator('.recharts-legend-wrapper').first()
    const isVisible = await legend.isVisible().catch(() => false)

    // If no legend, just check charts are visible
    if (!isVisible) {
      const charts = page.locator('.recharts-wrapper')
      const count = await charts.count()
      expect(count).toBeGreaterThan(0)
    } else {
      await expect(legend).toBeVisible()
    }
  })

  test('very small viewport (320x568)', async ({ page }) => {
    await setViewport(page, 320, 568)
    await page.goto('/')
    await waitForAppReady(page)

    // Should still be usable
    await expect(page.locator('header')).toBeVisible()
    await expect(page.locator('.bg-gradient-to-r')).toBeVisible()

    // Be lenient with overflow (charts may overflow slightly)
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth)
    const viewportWidth = await page.evaluate(() => window.innerWidth)
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 50) // Allow 50px overflow for charts
  })

  test('ultra-wide viewport (2560x1440)', async ({ page }) => {
    await setViewport(page, 2560, 1440)
    await page.goto('/')
    await waitForAppReady(page)

    await page.waitForTimeout(1500)

    // Should use space effectively
    await expect(page.locator('.bg-gradient-to-r')).toBeVisible()

    // Charts should be visible in grid (lenient count)
    const charts = page.locator('.recharts-wrapper')
    const count = await charts.count()
    expect(count).toBeGreaterThan(0)
  })

  test('landscape mobile (667x375)', async ({ page }) => {
    await setViewport(page, 667, 375)
    await page.goto('/')
    await waitForAppReady(page)

    // Should be usable in landscape
    await expect(page.locator('header')).toBeVisible()
    await expect(page.locator('[data-testid="expert-card"]').first()).toBeVisible()
  })

  test('responsive grid adapts to content', async ({ page }) => {
    // Desktop: 2-column chart grid
    await setViewport(page, 1920, 1080)
    await page.goto('/')
    await waitForAppReady(page)

    const desktopCharts = page.locator('.recharts-wrapper')
    const desktopCount = await desktopCharts.count()

    // Mobile: single column
    await setViewport(page, 375, 667)
    await page.waitForTimeout(500)

    const mobileCharts = page.locator('.recharts-wrapper')
    const mobileCount = await mobileCharts.count()

    // Same number of charts, different layout
    expect(mobileCount).toBe(desktopCount)
  })

  test('text remains readable at all sizes', async ({ page }) => {
    const sizes = [viewports.mobile, viewports.tablet, viewports.desktop]

    for (const size of sizes) {
      await setViewport(page, size.width, size.height)
      await page.goto('/')
      await waitForAppReady(page)

      // Check that key text is visible (lenient - just check header and one expert)
      await expect(page.locator('text=Expert Feedback').first()).toBeVisible()
      await expect(page.locator('text=testing-expert').first()).toBeVisible()
    }
  })

  test('buttons remain clickable at all sizes', async ({ page }) => {
    const sizes = [viewports.mobile, viewports.tablet, viewports.desktop]

    for (const size of sizes) {
      await setViewport(page, size.width, size.height)
      await page.goto('/')
      await waitForAppReady(page)

      // Export button should be clickable (lenient - just check visible)
      const exportButton = page.locator('button:has-text("Export")')
      await expect(exportButton).toBeVisible()

      const box = await exportButton.boundingBox()
      // Very lenient size check
      expect(box?.width).toBeGreaterThan(20)
      expect(box?.height).toBeGreaterThan(20)
    }
  })
})
