/**
 * Expert Sorting Tests
 * Tests the expert sorting functionality
 */

import { test, expect } from '@playwright/test'
import {
  setupFixture,
  waitForAppReady,
  getLocalStorage,
} from '../helpers/test-utils'

test.describe('Expert Sorting', () => {
  test.beforeEach(async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await waitForAppReady(page)
  })

  test('should sort by index (default)', async ({ page }) => {
    // Default sort is by index (order in experts array)
    const firstExpert = page.locator('[data-testid="expert-card"]').first()
    await expect(firstExpert).toContainText('testing-expert')
  })

  test('should sort by name (alphabetically)', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      await sortButton.first().click()

      // Select "Name" sort
      const nameOption = page.locator('text=Name, option[value="name"]')
      await nameOption.first().click()
      await page.waitForTimeout(500)

      // First expert should be "accessibility-expert" (alphabetically first)
      const firstExpert = page.locator('[data-testid="expert-card"]').first()
      await expect(firstExpert).toContainText('accessibility-expert')
    }
  })

  test('should sort by duration', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      await sortButton.first().click()

      // Select "Duration" sort
      const durationOption = page.locator('text=Duration, option[value="duration"]')
      await durationOption.first().click()
      await page.waitForTimeout(500)

      // Should sort by duration (ascending by default)
      // performance-expert has 98s (shortest)
      const firstExpert = page.locator('[data-testid="expert-card"]').first()
      await expect(firstExpert).toContainText('performance-expert')
    }
  })

  test('should sort by cost', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      await sortButton.first().click()

      // Select "Cost" sort
      const costOption = page.locator('text=Cost, option[value="cost"]')
      await costOption.first().click()
      await page.waitForTimeout(500)

      // Should sort by cost (ascending by default)
      // performance-expert has $0.0156 (cheapest)
      const firstExpert = page.locator('[data-testid="expert-card"]').first()
      await expect(firstExpert).toContainText('performance-expert')
    }
  })

  test('should sort by status', async ({ page }) => {
    // Use partial-state which has mixed statuses
    await setupFixture(page, 'partial-state')
    await page.goto('/')
    await waitForAppReady(page)

    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      await sortButton.first().click()

      // Select "Status" sort
      const statusOption = page.locator('text=Status, option[value="status"]')
      await statusOption.first().click()
      await page.waitForTimeout(500)

      // Complete status should come first (status order: complete, running, failed, timeout, cancelled, pending)
      const firstExpert = page.locator('[data-testid="expert-card"]').first()
      const hasComplete = await firstExpert.evaluate((el) => {
        return el.className.includes('green')
      })
      expect(hasComplete).toBeTruthy()
    }
  })

  test('should toggle sort order (asc/desc)', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')
    const orderButton = page.locator('button:has-text("↑"), button:has-text("↓")')

    if (await sortButton.count() > 0 && await orderButton.count() > 0) {
      // Sort by duration (ascending)
      await sortButton.first().click()
      const durationOption = page.locator('text=Duration, option[value="duration"]')
      await durationOption.first().click()
      await page.waitForTimeout(500)

      // First expert: performance-expert (98s - shortest)
      let firstExpert = page.locator('[data-testid="expert-card"]').first()
      await expect(firstExpert).toContainText('performance-expert')

      // Toggle to descending
      await orderButton.first().click()
      await page.waitForTimeout(500)

      // First expert should now be accessibility-expert (178s - longest)
      firstExpert = page.locator('[data-testid="expert-card"]').first()
      await expect(firstExpert).toContainText('accessibility-expert')
    }
  })

  test('should persist sort preferences in localStorage', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      // Apply sort
      await sortButton.first().click()
      const nameOption = page.locator('text=Name, option[value="name"]')
      await nameOption.first().click()
      await page.waitForTimeout(500)

      // Check localStorage
      const storage = await getLocalStorage(page, 'expert-feedback-ui')
      const sortBy = storage?.state?.expertSortBy || storage?.expertSortBy
      expect(sortBy).toBe('name')
    }
  })

  test('should restore sort from localStorage on page reload', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      // Apply sort by name
      await sortButton.first().click()
      const nameOption = page.locator('text=Name, option[value="name"]')
      await nameOption.first().click()
      await page.waitForTimeout(500)

      // First expert should be alphabetically first
      let firstExpert = page.locator('[data-testid="expert-card"]').first()
      const firstExpertName = await firstExpert.textContent()

      // Reload page
      await page.reload()
      await waitForAppReady(page)

      // Sort should be restored
      firstExpert = page.locator('[data-testid="expert-card"]').first()
      const reloadedFirstExpertName = await firstExpert.textContent()
      expect(reloadedFirstExpertName).toBe(firstExpertName)
    }
  })

  test('should update visual order when sorting changes', async ({ page }) => {
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await sortButton.count() > 0) {
      // Get initial order
      const initialFirst = await page.locator('[data-testid="expert-card"]').first().textContent()

      // Change sort
      await sortButton.first().click()
      const costOption = page.locator('text=Cost, option[value="cost"]')
      await costOption.first().click()
      await page.waitForTimeout(500)

      // Order should change
      const newFirst = await page.locator('[data-testid="expert-card"]').first().textContent()
      expect(newFirst).not.toBe(initialFirst)
    }
  })

  test('should combine sorting with filtering', async ({ page }) => {
    // Use partial state with mixed statuses
    await setupFixture(page, 'partial-state')
    await page.goto('/')
    await waitForAppReady(page)

    const filterButton = page.locator('button:has-text("All"), select[name="filter"]')
    const sortButton = page.locator('button:has-text("Sort"), select[name="sort"]')

    if (await filterButton.count() > 0 && await sortButton.count() > 0) {
      // Filter by complete
      await filterButton.first().click()
      const completeOption = page.locator('text=Complete, option[value="complete"]')
      await completeOption.first().click()
      await page.waitForTimeout(500)

      // Sort by duration
      await sortButton.first().click()
      const durationOption = page.locator('text=Duration, option[value="duration"]')
      await durationOption.first().click()
      await page.waitForTimeout(500)

      // Should show only complete experts, sorted by duration
      const expertCards = page.locator('[data-testid="expert-card"]')
      const count = await expertCards.count()
      expect(count).toBe(3) // 3 complete experts in partial-state
    }
  })
})
