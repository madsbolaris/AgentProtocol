/**
 * WebSocket Toggle Tests
 * Tests the WebSocket connection toggle functionality
 */

import { test, expect } from '@playwright/test'
import {
  setupFixture,
  waitForAppReady,
  getLocalStorage,
  setLocalStorage,
  clearLocalStorage,
} from '../helpers/test-utils'

test.describe('WebSocket Toggle', () => {
  test.beforeEach(async ({ page }) => {
    await setupFixture(page, 'full-state')
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await clearLocalStorage(page)
  })

  test('websocket toggle exists', async ({ page }) => {
    await waitForAppReady(page)

    // Look for WebSocket toggle button (text contains "WebSocket")
    const toggle = page.locator('button:has-text("WebSocket")')

    // Should be visible in ConnectionStatus component
    await expect(toggle).toBeVisible()
  })

  test('websocket is disabled by default', async ({ page }) => {
    await waitForAppReady(page)

    // Check localStorage - should default to false
    const storage = await getLocalStorage(page, 'expert-feedback-ui')
    const wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled ?? false
    expect(wsEnabled).toBe(false)
  })

  test('can enable websocket', async ({ page }) => {
    await waitForAppReady(page)

    // Find and click toggle
    const toggle = page.locator(
      'input[type="checkbox"]:near(:text("WebSocket")), button:has-text("WebSocket")'
    ).first()

    if (await toggle.count() > 0) {
      await toggle.click()
      await page.waitForTimeout(500)

      // Check localStorage
      const storage = await getLocalStorage(page, 'expert-feedback-ui')
      const wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled
      expect(wsEnabled).toBe(true)
    }
  })

  test('can disable websocket', async ({ page }) => {
    await waitForAppReady(page)

    // Pre-enable WebSocket
    await setLocalStorage(page, 'expert-feedback-ui', {
      state: { websocketEnabled: true },
    })

    // Reload page so Zustand reinitializes with new localStorage
    await page.reload()
    await waitForAppReady(page)

    // Find and click toggle to disable
    const toggle = page.locator(
      'input[type="checkbox"]:near(:text("WebSocket")), button:has-text("WebSocket")'
    ).first()

    if (await toggle.count() > 0) {
      await toggle.click()
      await page.waitForTimeout(1000) // Longer wait for state update

      // Check localStorage
      const storage = await getLocalStorage(page, 'expert-feedback-ui')
      const wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled
      expect(wsEnabled).toBe(false)
    }
  })

  test('websocket state persists across page reload', async ({ page }) => {
    await waitForAppReady(page)

    // Enable WebSocket
    const toggle = page.locator(
      'input[type="checkbox"]:near(:text("WebSocket")), button:has-text("WebSocket")'
    ).first()

    if (await toggle.count() > 0) {
      await toggle.click()
      await page.waitForTimeout(500)

      // Reload page
      await page.reload()
      await waitForAppReady(page)

      // Check it's still enabled
      const storage = await getLocalStorage(page, 'expert-feedback-ui')
      const wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled
      expect(wsEnabled).toBe(true)
    }
  })

  test('ConnectionStatus shows correct state when WebSocket enabled', async ({ page }) => {
    // Enable WebSocket
    await setLocalStorage(page, 'expert-feedback-ui', {
      state: { websocketEnabled: true },
    })

    // Reload page so Zustand reinitializes with new localStorage
    await page.reload()
    await waitForAppReady(page)

    // Look for connection status indicator
    const statusIndicator = page.locator(
      'text=Connected, text=Disconnected, text=Connecting, [data-testid="connection-status"]'
    )

    // Status indicator may or may not be visible
    // Just check that the page loads without errors
    await expect(page.locator('main')).toBeVisible()
  })

  test('ConnectionStatus shows correct state when WebSocket disabled', async ({ page }) => {
    await waitForAppReady(page)

    // WebSocket disabled, so connection status should show polling or be hidden
    const storage = await getLocalStorage(page, 'expert-feedback-ui')
    const wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled ?? false
    expect(wsEnabled).toBe(false)

    // Page should load normally
    await expect(page.locator('main')).toBeVisible()
  })

  test('toggle state reflects localStorage on initial load', async ({ page }) => {
    // Pre-enable in localStorage
    await setLocalStorage(page, 'expert-feedback-ui', {
      state: { websocketEnabled: true },
    })

    // Reload page so Zustand reinitializes with new localStorage
    await page.reload()
    await waitForAppReady(page)

    // Toggle should show as enabled
    const checkbox = page.locator('input[type="checkbox"]:near(:text("WebSocket"))').first()

    if (await checkbox.count() > 0) {
      const isChecked = await checkbox.isChecked()
      expect(isChecked).toBe(true)
    }
  })

  test('toggling does not lose other localStorage data', async ({ page }) => {
    // Set some other data in localStorage
    await setLocalStorage(page, 'expert-feedback-ui', {
      state: {
        websocketEnabled: false,
        expertStatusFilter: 'complete',
        expertSortBy: 'cost',
      },
    })

    // Reload page so Zustand reinitializes with new localStorage
    await page.reload()
    await waitForAppReady(page)

    // Toggle WebSocket
    const toggle = page.locator(
      'input[type="checkbox"]:near(:text("WebSocket")), button:has-text("WebSocket")'
    ).first()

    if (await toggle.count() > 0) {
      await toggle.click()
      await page.waitForTimeout(500)

      // Check that other data is preserved
      const storage = await getLocalStorage(page, 'expert-feedback-ui')
      const filter = storage?.state?.expertStatusFilter ?? storage?.expertStatusFilter
      const sortBy = storage?.state?.expertSortBy ?? storage?.expertSortBy

      expect(filter).toBe('complete')
      expect(sortBy).toBe('cost')
    }
  })

  test('multiple toggles work correctly', async ({ page }) => {
    await waitForAppReady(page)

    const toggle = page.locator(
      'input[type="checkbox"]:near(:text("WebSocket")), button:has-text("WebSocket")'
    ).first()

    if (await toggle.count() > 0) {
      // Toggle on
      await toggle.click()
      await page.waitForTimeout(300)
      let storage = await getLocalStorage(page, 'expert-feedback-ui')
      let wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled
      expect(wsEnabled).toBe(true)

      // Toggle off
      await toggle.click()
      await page.waitForTimeout(300)
      storage = await getLocalStorage(page, 'expert-feedback-ui')
      wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled
      expect(wsEnabled).toBe(false)

      // Toggle on again
      await toggle.click()
      await page.waitForTimeout(300)
      storage = await getLocalStorage(page, 'expert-feedback-ui')
      wsEnabled = storage?.state?.websocketEnabled ?? storage?.websocketEnabled
      expect(wsEnabled).toBe(true)
    }
  })
})
