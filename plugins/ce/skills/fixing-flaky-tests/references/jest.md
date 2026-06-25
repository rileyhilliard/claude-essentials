# Jest Isolation Patterns

## Contents

- [Test isolation](#test-isolation)
- [Module and mock cleanup](#module-and-mock-cleanup)
- [Singleton reset pattern](#singleton-reset-pattern)
- [MSW for network mocking](#msw-for-network-mocking)
- [Anti-patterns](#anti-patterns)

**For waiting/timing patterns:** See [writing-tests waiting-typescript](../../writing-tests/references/waiting-typescript.md).

---

## Test isolation

### Reset mocks between tests

```typescript
beforeEach(() => {
  jest.clearAllMocks()  // Clear call history
})

afterEach(() => {
  jest.restoreAllMocks()  // Restore original implementations
})
```

### Reset module state

When modules have internal state that persists between tests:

```typescript
beforeEach(() => {
  jest.resetModules()  // Clear module cache
})

// Or isolate specific modules
jest.isolateModules(() => {
  const freshModule = require('./stateful-module')
})
```

### Global state cleanup

```typescript
// Store original values
const originalFetch = global.fetch
const originalEnv = { ...process.env }

afterEach(() => {
  global.fetch = originalFetch
  process.env = { ...originalEnv }
})
```

### Dynamic port allocation

```typescript
import { createServer } from 'http'

function getTestServer(handler: RequestListener) {
  const server = createServer(handler)
  server.listen(0)  // OS assigns available port
  const { port } = server.address() as AddressInfo
  return { server, port, url: `http://localhost:${port}` }
}
```

## Module and mock cleanup

### Jest mock lifecycle

```typescript
// In setupFilesAfterEnv or test file
beforeEach(() => {
  jest.clearAllMocks()    // Reset call counts
  jest.clearAllTimers()   // Clear pending timers
})

afterEach(() => {
  jest.restoreAllMocks()  // Restore spied functions
  jest.useRealTimers()    // Restore real timers
})
```

## Singleton reset pattern

```typescript
// singleton.ts
class Database {
  private static instance: Database | undefined
  static getInstance() {
    if (!this.instance) this.instance = new Database()
    return this.instance
  }
  static resetInstance() {
    this.instance = undefined
  }
}

// test file
afterEach(() => {
  Database.resetInstance()
})
```

## MSW for network mocking

MSW isolates network state between tests by resetting handlers after each test.

**Setup pattern (MSW 2.x):**

```typescript
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

// 1. Define handlers
const handlers = [
  http.get('https://api.example.com/users/:id', async ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'John' })
  }),

  http.post('https://api.example.com/users', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: 1, ...body }, { status: 201 })
  })
]

// 2. Setup server
const server = setupServer(...handlers)

// 3. Configure lifecycle (critical for isolation)
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())  // Reset to original handlers
afterAll(() => server.close())
```

**Per-test overrides:**

```typescript
test('handles error responses', async () => {
  server.use(
    http.get('https://api.example.com/users/:id', () => {
      return HttpResponse.json({ message: 'Not found' }, { status: 404 })
    })
  )

  render(<UserProfile userId="999" />)
  await screen.findByText('User not found')
})
// Override is automatically reset after this test
```

---

## Anti-patterns

### Not resetting mocks

```typescript
// Bad: mock state persists between tests
jest.mock('./api')
const mockFetch = api.fetchData as jest.Mock
mockFetch.mockResolvedValue({ data: 'test' })
// Call count accumulates across tests!

// Good: reset in afterEach
afterEach(() => {
  jest.clearAllMocks()
})
```

### Module cache leakage

```typescript
// Bad: imported module keeps state
import { counter } from './counter'
test('first test', () => {
  counter.increment()
  expect(counter.value).toBe(1)
})
test('second test', () => {
  expect(counter.value).toBe(0)  // Fails! Still 1
})

// Good: reset modules
beforeEach(() => {
  jest.resetModules()
})
```

### Shared mock servers

```typescript
// Bad: no handler reset
const server = setupServer(...handlers)
beforeAll(() => server.listen())
afterAll(() => server.close())
// Overrides from one test leak to others!

// Good: reset after each test
afterEach(() => server.resetHandlers())
```

### Global state pollution

```typescript
// Bad: pollutes global scope
test('sets config', () => {
  window.__CONFIG__ = { debug: true }
  // Persists to next test!
})

// Good: save and restore
let originalConfig: any
beforeEach(() => {
  originalConfig = window.__CONFIG__
})
afterEach(() => {
  window.__CONFIG__ = originalConfig
})
```
