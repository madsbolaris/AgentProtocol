/**
 * Shared Test Utilities
 * Helper functions for E2E tests
 */

import { Page, expect } from '@playwright/test'
import type { FixtureName } from './api-mock'
import { routeHandlers } from './api-mock'

/**
 * Navigate to app and wait for it to load
 */
export async function navigateToApp(page: Page) {
  await page.goto('/')
  await page.waitForLoadState('networkidle')
}

/**
 * Setup API mock with specific fixture
 */
export async function setupFixture(page: Page, fixtureName: FixtureName) {
  const mock = routeHandlers.mockSuccessWithFixture(fixtureName)
  await page.route(mock.url, mock.handler)
}

/**
 * Setup API error mock
 */
export async function setupErrorMock(page: Page) {
  const mock = routeHandlers.mockError()
  await page.route(mock.url, mock.handler)
}

/**
 * Setup network error mock
 */
export async function setupNetworkErrorMock(page: Page) {
  const mock = routeHandlers.mockNetworkError()
  await page.route(mock.url, mock.handler)
}

/**
 * Setup invalid JSON mock
 */
export async function setupInvalidJSONMock(page: Page) {
  const mock = routeHandlers.mockInvalidJSON()
  await page.route(mock.url, mock.handler)
}

/**
 * Wait for app to finish loading (no spinner visible)
 */
export async function waitForAppReady(page: Page) {
  // Wait for loading spinner to disappear
  await page.waitForSelector('[class*="animate-spin"]', {
    state: 'hidden',
    timeout: 10000
  }).catch(() => {
    // Spinner might not appear if load is fast, that's okay
  })

  // Wait for network to be idle
  await page.waitForLoadState('networkidle')
}

/**
 * Check for console errors
 */
export async function checkNoConsoleErrors(page: Page): Promise<string[]> {
  const errors: string[] = []

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text())
    }
  })

  return errors
}

/**
 * Take screenshot with descriptive name
 */
export async function takeScreenshot(page: Page, name: string) {
  await page.screenshot({
    path: `test-results/${name}.png`,
    fullPage: true
  })
}

/**
 * Get localStorage value
 */
export async function getLocalStorage(page: Page, key: string): Promise<any> {
  return await page.evaluate((storageKey) => {
    const value = localStorage.getItem(storageKey)
    return value ? JSON.parse(value) : null
  }, key)
}

/**
 * Set localStorage value
 */
export async function setLocalStorage(page: Page, key: string, value: any) {
  await page.evaluate(({ storageKey, storageValue }) => {
    localStorage.setItem(storageKey, JSON.stringify(storageValue))
  }, { storageKey: key, storageValue: value })
}

/**
 * Clear localStorage
 */
export async function clearLocalStorage(page: Page) {
  await page.evaluate(() => localStorage.clear())
}

/**
 * Wait for element with retry
 */
export async function waitForElement(
  page: Page,
  selector: string,
  options?: { timeout?: number; state?: 'attached' | 'detached' | 'visible' | 'hidden' }
) {
  await page.waitForSelector(selector, {
    timeout: options?.timeout || 5000,
    state: options?.state || 'visible',
  })
}

/**
 * Format duration for display (matches app logic)
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

/**
 * Format cost for display
 */
export function formatCost(cost: number): string {
  return `$${cost.toFixed(4)}`
}

/**
 * Assert element is visible
 */
export async function assertVisible(page: Page, selector: string) {
  await expect(page.locator(selector)).toBeVisible()
}

/**
 * Assert element is hidden
 */
export async function assertHidden(page: Page, selector: string) {
  await expect(page.locator(selector)).toBeHidden()
}

/**
 * Assert text content
 */
export async function assertText(page: Page, selector: string, text: string) {
  await expect(page.locator(selector)).toHaveText(text)
}

/**
 * Assert text contains
 */
export async function assertTextContains(page: Page, selector: string, text: string) {
  await expect(page.locator(selector)).toContainText(text)
}

/**
 * Click element with retry
 */
export async function clickElement(page: Page, selector: string) {
  await page.locator(selector).click()
}

/**
 * Hover element
 */
export async function hoverElement(page: Page, selector: string) {
  await page.locator(selector).hover()
}

/**
 * Get element count
 */
export async function getElementCount(page: Page, selector: string): Promise<number> {
  return await page.locator(selector).count()
}

/**
 * Assert element count
 */
export async function assertElementCount(page: Page, selector: string, count: number) {
  await expect(page.locator(selector)).toHaveCount(count)
}

/**
 * Set viewport size
 */
export async function setViewport(page: Page, width: number, height: number) {
  await page.setViewportSize({ width, height })
}

/**
 * Common viewport sizes
 */
export const viewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1920, height: 1080 },
  laptop: { width: 1366, height: 768 },
}
