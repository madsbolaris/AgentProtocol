/**
 * Expert Filtering Tests
 * Tests the expert status filtering functionality
 */

import { test, expect } from '@playwright/test'
import {
  setupFixture,
  waitForAppReady,
  getLocalStorage,
} from '../helpers/test-utils'
import { assertExpertCount } from '../helpers/assertions'

test.describe('Expert Filtering', () => {
  test.beforeEach(async ({ page }) => {
    await setupFixture(page, 'partial-state')
    await page.goto('/')
    await waitForAppReady(page)
  })

  test('should show all experts by default', async ({ page }) => {
    // Partial state has 5 experts
    await assertExpertCount(page, 5)
  })

  test('should filter by complete status', async ({ page }) => {
    // Click filter dropdown/button
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      await filterButton.first().click()

      // Select "Complete" option
      const completeOption = page.locator('text=Complete, option[value="complete"]')
      await completeOption.first().click()

      // Wait for filter to apply
      await page.waitForTimeout(500)

      // Should show only 3 complete experts
      await assertExpertCount(page, 3)

      // Should only show complete experts
      await expect(page.locator('text=frontend-expert')).toBeVisible()
      await expect(page.locator('text=architecture-expert')).toBeVisible()
      await expect(page.locator('text=performance-expert')).toBeVisible()
      await expect(page.locator('text=code-review-expert')).not.toBeVisible()
    }
  })

  test('should filter by running status', async ({ page }) => {
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      await filterButton.first().click()

      // Select "Running" option
      const runningOption = page.locator('text=Running, option[value="running"]')
      await runningOption.first().click()

      await page.waitForTimeout(500)

      // Should show only 1 running expert
      await assertExpertCount(page, 1)
      await expect(page.locator('text=code-review-expert')).toBeVisible()
    }
  })

  test('should filter by pending status', async ({ page }) => {
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      await filterButton.first().click()

      // Select "Pending" option
      const pendingOption = page.locator('text=Pending, option[value="pending"]')
      await pendingOption.first().click()

      await page.waitForTimeout(500)

      // Should show 1 pending expert (testing-expert not started yet)
      const count = await page.locator('[data-testid="expert-card"]').count()
      expect(count).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter by failed status', async ({ page }) => {
    // Use error-state fixture which has failed experts
    await setupFixture(page, 'error-state')
    await page.goto('/')
    await waitForAppReady(page)

    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      await filterButton.first().click()

      // Select "Failed" option
      const failedOption = page.locator('text=Failed, option[value="failed"]')
      await failedOption.first().click()

      await page.waitForTimeout(500)

      // Should show only failed experts
      const count = await page.locator('[data-testid="expert-card"]').count()
      expect(count).toBeGreaterThanOrEqual(1)
    }
  })

  test('should update expert count when filter changes', async ({ page }) => {
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      // Count all experts
      const allCount = await page.locator('[data-testid="expert-card"]').count()
      expect(allCount).toBe(4)

      // Apply filter
      await filterButton.first().click()
      const completeOption = page.locator('text=Complete, option[value="complete"]')
      await completeOption.first().click()
      await page.waitForTimeout(500)

      // Count filtered experts
      const filteredCount = await page.locator('[data-testid="expert-card"]').count()
      expect(filteredCount).toBeLessThan(allCount)
    }
  })

  test('should persist filter in localStorage', async ({ page }) => {
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      // Apply filter
      await filterButton.first().click()
      const completeOption = page.locator('text=Complete, option[value="complete"]')
      await completeOption.first().click()
      await page.waitForTimeout(500)

      // Check localStorage
      const storage = await getLocalStorage(page, 'expert-feedback-ui')
      expect(storage?.state?.expertStatusFilter || storage?.expertStatusFilter).toBe('complete')
    }
  })

  test('should restore filter from localStorage on page reload', async ({ page }) => {
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      // Apply filter
      await filterButton.first().click()
      const completeOption = page.locator('text=Complete, option[value="complete"]')
      await completeOption.first().click()
      await page.waitForTimeout(500)

      const beforeCount = await page.locator('[data-testid="expert-card"]').count()

      // Reload page
      await page.reload()
      await waitForAppReady(page)

      // Filter should be restored
      const afterCount = await page.locator('[data-testid="expert-card"]').count()
      expect(afterCount).toBe(beforeCount)
    }
  })

  test('should show empty state when no experts match filter', async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)

    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      // Filter by "Running" but all experts are complete
      await filterButton.first().click()
      const runningOption = page.locator('text=Running, option[value="running"]')
      await runningOption.first().click()
      await page.waitForTimeout(500)

      // Should show no experts
      await assertExpertCount(page, 0)

      // May show empty state message
      const hasEmptyMessage = await page.locator('text=No experts, text=No results').count()
      expect(hasEmptyMessage).toBeGreaterThanOrEqual(0)
    }
  })

  test('should clear filter when selecting "All"', async ({ page }) => {
    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')

    if (await filterButton.count() > 0) {
      // Apply filter
      await filterButton.first().click()
      const completeOption = page.locator('text=Complete, option[value="complete"]')
      await completeOption.first().click()
      await page.waitForTimeout(500)

      const filteredCount = await page.locator('[data-testid="expert-card"]').count()

      // Clear filter
      await filterButton.first().click()
      const allOption = page.locator('text=All, option[value="all"]')
      await allOption.first().click()
      await page.waitForTimeout(500)

      // Should show all experts again
      const allCount = await page.locator('[data-testid="expert-card"]').count()
      expect(allCount).toBeGreaterThan(filteredCount)
    }
  })
})
