# TypeScript Waiting Patterns

## Contents

**Jest / Testing Library:**
- [Query types](#query-types)
- [waitFor specifications](#waitfor-specifications)
- [Fake timers](#fake-timers)
- [Custom polling helpers](#custom-polling-helpers)

**Playwright:**
- [Auto-waiting](#auto-waiting)
- [Web-first assertions](#web-first-assertions)
- [Network waiting](#network-waiting)
- [Custom polling](#custom-polling)

**Anti-patterns:**
- [Common mistakes](#anti-patterns)

---

## Query types

Testing Library provides async queries that handle waiting:

| Query | Sync/Async | Throws | Returns | Use Case |
|-------|-----------|--------|---------|----------|
| **getBy** | Sync | Yes | Element | Element must exist now |
| **queryBy** | Sync | No | Element/null | Assert element absence |
| **findBy** | Async | Yes | Promise\<Element\> | Element appears after async op |

**Priority order:** findBy > getBy > queryBy (unless testing absence)

```typescript
// Prefer findBy for async
const result = await screen.findByText('Data loaded')
expect(result).toBeInTheDocument()

// Instead of:
await waitFor(() => screen.getByText('Data loaded'))
```

## waitFor specifications

**Default behavior:**
- Timeout: 1000ms (configurable)
- Interval: 50ms
- Callback executes immediately, then retries at intervals

**Critical:** Callback must **throw an error to trigger retry**:

```typescript
// Good: assertion throws on failure
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument()
})

// Bad: returning false doesn't trigger retry
await waitFor(() => {
  return screen.queryByText('Success') !== null  // Won't retry!
})
```

**waitForElementToBeRemoved:**

```typescript
await waitForElementToBeRemoved(() => screen.queryByText('Loading...'))
```

## Fake timers

**Setup pattern (critical for Testing Library compatibility):**

```typescript
beforeEach(() => {
  jest.useFakeTimers({ advanceTimers: true })  // Critical option!
})

afterEach(() => {
  jest.runOnlyPendingTimers()
  jest.useRealTimers()
})
```

**Use async timer APIs to prevent deadlocks:**

```typescript
// Old approach (can deadlock):
jest.advanceTimersByTime(300)

// Recommended:
await jest.advanceTimersByTimeAsync(300)
```

## Custom polling helpers

When built-in utilities aren't enough:

```typescript
export function waitForEvent<T extends { type: string }>(
  getEvents: () => T[],
  eventType: string,
  timeoutMs = 5000
): Promise<T> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now()

    const check = () => {
      const events = getEvents()
      const event = events.find((e) => e.type === eventType)

      if (event) {
        resolve(event)
      } else if (Date.now() - startTime > timeoutMs) {
        reject(new Error(`Timeout waiting for ${eventType} after ${timeoutMs}ms`))
      } else {
        setTimeout(check, 50)
      }
    }

    check()
  })
}

export function waitForEventCount<T extends { type: string }>(
  getEvents: () => T[],
  eventType: string,
  count: number,
  timeoutMs = 5000
): Promise<T[]> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now()

    const check = () => {
      const events = getEvents()
      const matching = events.filter((e) => e.type === eventType)

      if (matching.length >= count) {
        resolve(matching)
      } else if (Date.now() - startTime > timeoutMs) {
        reject(new Error(
          `Timeout waiting for ${count} ${eventType} events (got ${matching.length})`
        ))
      } else {
        setTimeout(check, 50)
      }
    }

    check()
  })
}
```

---

## Auto-waiting

Playwright automatically waits for elements to be actionable before interacting:

**Five actionability checks:**

| Check | Description |
|-------|-------------|
| **Visible** | Non-empty bounding box, no `visibility:hidden` |
| **Stable** | Dimensions consistent across animation frames |
| **Enabled** | Not disabled via HTML or ARIA |
| **Editable** | Enabled and not read-only |
| **Receives Events** | Will capture pointer at target location |

```typescript
// Playwright automatically waits for all checks
await page.click('button[type="submit"]')
```

## Web-first assertions

Assertions auto-retry until condition is met (default 5s):

```typescript
await expect(page.locator('.success-message')).toBeVisible()
await expect(page.locator('h1')).toHaveText('Welcome')
await expect(page.locator('.item')).toHaveCount(5)
```

**Negation with retry:**

```typescript
await expect(page.locator('.loading')).not.toBeVisible()
```

## Network waiting

```typescript
// Start waiting BEFORE the action that triggers the request
const responsePromise = page.waitForResponse('/api/users')
await page.click('button.load-users')
const response = await responsePromise

expect(response.status()).toBe(200)
```

**With predicate:**

```typescript
const response = await page.waitForResponse(
  (response) =>
    response.url().includes('/api/') &&
    response.status() === 200
)
```

## Custom polling

For conditions not covered by built-ins:

```typescript
await page.waitForFunction(() => {
  const app = window.__APP_STATE__
  return app?.initialized && app?.user?.loaded
})

// With polling options
await page.waitForFunction(
  () => document.querySelectorAll('.item').length >= 10,
  { polling: 100, timeout: 10000 }
)
```

---

## Anti-patterns

### Using waitFor for element presence

```typescript
// Anti-pattern
await waitFor(() => screen.getByText('Loaded'))

// Better: use findBy
await screen.findByText('Loaded')
```

### Empty waitFor callbacks

```typescript
// Anti-pattern
await waitFor(() => {})

// Better: explicit assertion
await waitFor(() => {
  expect(screen.getByText('Ready')).toBeInTheDocument()
})
```

### Side effects inside waitFor

```typescript
// Anti-pattern (clicks repeatedly!)
await waitFor(() => {
  fireEvent.click(button)
  expect(result).toBeInTheDocument()
})

// Better
fireEvent.click(button)
await waitFor(() => {
  expect(result).toBeInTheDocument()
})
```

### Arbitrary setTimeout delays

```typescript
// Anti-pattern
await new Promise(resolve => setTimeout(resolve, 2000))
expect(element).toBeInTheDocument()

// Better
await screen.findByText('Loaded')
```

### Incorrect network wait order

```typescript
// Anti-pattern: might miss the response
await page.click('button.submit')
const response = await page.waitForResponse('/api/submit')  // Too late!

// Better: start waiting BEFORE action
const responsePromise = page.waitForResponse('/api/submit')
await page.click('button.submit')
const response = await responsePromise
```

### Synchronous Playwright checks

```typescript
// Anti-pattern: no auto-retry
expect(await element.isVisible()).toBe(true)

// Better: web-first assertion
await expect(element).toBeVisible()
```
