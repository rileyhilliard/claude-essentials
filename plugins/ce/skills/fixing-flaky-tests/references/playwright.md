# Playwright Isolation Patterns

## Contents

- [Browser context isolation](#browser-context-isolation)
- [Parallel execution](#parallel-execution)
- [Database cleanup](#database-cleanup)
- [Unique test data](#unique-test-data)
- [Authentication state](#authentication-state)
- [Anti-patterns](#anti-patterns)

**For waiting/timing patterns:** See [writing-tests waiting-typescript](../../writing-tests/references/waiting-typescript.md).

---

## Browser context isolation

Playwright provides automatic isolation - each test gets a fresh browser context (like a new incognito window):

```typescript
// Each test automatically gets:
// - Fresh browser context (cookies, localStorage cleared)
// - New page instance
// - No shared state from previous tests

test('first test', async ({ page }) => {
  await page.goto('/login')
  // Login state won't leak to other tests
})

test('second test', async ({ page }) => {
  // Starts fresh - not logged in
})
```

## Parallel execution

Tests in a single file run sequentially by default. Tests across files run in parallel:

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,  // Run tests in files in parallel too
  // Keep parallelism enabled to catch isolation bugs!
  // Only reduce workers if CI resources are constrained
})
```

## Database cleanup

For E2E tests hitting a real database:

```typescript
// global-setup.ts
async function globalSetup() {
  // Reset database to known state before test run
  await resetDatabase()
}

// Or per-test cleanup via API
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/reset')
})
```

## Unique test data

Avoid conflicts in parallel runs by using unique identifiers:

```typescript
test('creates user', async ({ page }) => {
  const uniqueEmail = `test-${Date.now()}@example.com`
  await page.fill('[name="email"]', uniqueEmail)
  // ...
})
```

## Authentication state

### Reuse authentication across tests

Save login state to avoid logging in for every test:

```typescript
// auth.setup.ts
import { test as setup } from '@playwright/test'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'user@example.com')
  await page.fill('[name="password"]', 'password')
  await page.click('button[type="submit"]')

  // Save signed-in state
  await page.context().storageState({ path: '.auth/user.json' })
})

// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'tests',
      dependencies: ['setup'],
      use: { storageState: '.auth/user.json' },
    },
  ],
})
```

### Per-test authentication override

```typescript
test.use({ storageState: { cookies: [], origins: [] } })  // No auth

test('unauthenticated user sees login', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL('/login')
})
```

---

## Anti-patterns

### Shared database state

```typescript
// Bad: tests depend on shared data
test('edits user', async ({ page }) => {
  await page.goto('/users/1/edit')  // Assumes user 1 exists
})

// Good: create or reset data per test
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/seed-user', { id: 1, name: 'Test' })
})
```

### Login in every test

```typescript
// Bad: slow, repetitive
test('views dashboard', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'user@example.com')
  await page.fill('[name="password"]', 'password')
  await page.click('button[type="submit"]')
  await page.goto('/dashboard')
})

// Good: use storageState
test.use({ storageState: '.auth/user.json' })
test('views dashboard', async ({ page }) => {
  await page.goto('/dashboard')  // Already authenticated
})
```

### Hardcoded test data

```typescript
// Bad: conflicts in parallel runs
test('creates user', async ({ page }) => {
  await page.fill('[name="email"]', 'test@example.com')
  // Another parallel test might create same email
})

// Good: unique identifiers
test('creates user', async ({ page }) => {
  const email = `test-${Date.now()}-${Math.random().toString(36)}@example.com`
  await page.fill('[name="email"]', email)
})
```

### Not cleaning up after tests

```typescript
// Bad: test creates data that affects others
test('creates post', async ({ page }) => {
  await page.fill('[name="title"]', 'My Post')
  await page.click('button[type="submit"]')
  // Post persists in database, affects other tests
})

// Good: cleanup in afterEach or use transactions
test.afterEach(async ({ request }) => {
  await request.post('/api/test/cleanup')
})
```
