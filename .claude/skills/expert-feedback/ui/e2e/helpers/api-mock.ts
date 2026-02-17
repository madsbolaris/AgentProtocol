/**
 * MSW API Mocking Helpers
 * Intercepts API requests and returns mock fixtures
 */

import { http, HttpResponse } from 'msw'
import emptyState from '../fixtures/empty-state.json' with { type: 'json' }
import fullState from '../fixtures/full-state.json' with { type: 'json' }
import partialState from '../fixtures/partial-state.json' with { type: 'json' }
import errorState from '../fixtures/error-state.json' with { type: 'json' }
import cacheActiveState from '../fixtures/cache-active-state.json' with { type: 'json' }

/**
 * Map of fixture names to their data
 */
const fixtures = {
  'empty-state': emptyState,
  'full-state': fullState,
  'partial-state': partialState,
  'error-state': errorState,
  'cache-active-state': cacheActiveState,
}

export type FixtureName = keyof typeof fixtures

/**
 * Get fixture data by name
 */
export function getFixture(name: FixtureName) {
  return fixtures[name]
}

/**
 * MSW handlers for API endpoints
 */
export const handlers = [
  // GET /api/state - Return workspace state
  http.get('http://localhost:8765/api/state', ({ request }) => {
    const url = new URL(request.url)
    const fixtureName = url.searchParams.get('fixture') as FixtureName

    // Default to full-state if no fixture specified
    const fixture = fixtureName && fixtures[fixtureName]
      ? fixtures[fixtureName]
      : fullState

    return HttpResponse.json(fixture)
  }),

  // Simulate API error (for error handling tests)
  http.get('http://localhost:8765/api/state-error', () => {
    return new HttpResponse(null, {
      status: 500,
      statusText: 'Internal Server Error'
    })
  }),

  // Simulate network timeout (for timeout tests)
  http.get('http://localhost:8765/api/state-timeout', async () => {
    await new Promise((resolve) => setTimeout(resolve, 35000)) // Longer than test timeout
    return HttpResponse.json(fullState)
  }),

  // Simulate invalid JSON (for parse error tests)
  http.get('http://localhost:8765/api/state-invalid', () => {
    return new HttpResponse('{ invalid json }', {
      headers: { 'Content-Type': 'application/json' },
    })
  }),
]

/**
 * Route handlers for Playwright
 * These can be used to mock API responses in browser tests
 */
export const routeHandlers = {
  /**
   * Mock successful API response with specific fixture
   */
  mockSuccessWithFixture: (fixtureName: FixtureName) => ({
    url: '**/api/state',
    handler: (route: any) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(getFixture(fixtureName)),
      })
    },
  }),

  /**
   * Mock API error
   */
  mockError: () => ({
    url: '**/api/state',
    handler: (route: any) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      })
    },
  }),

  /**
   * Mock network error
   */
  mockNetworkError: () => ({
    url: '**/api/state',
    handler: (route: any) => {
      route.abort('failed')
    },
  }),

  /**
   * Mock invalid JSON
   */
  mockInvalidJSON: () => ({
    url: '**/api/state',
    handler: (route: any) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: '{ invalid json }',
      })
    },
  }),
}
