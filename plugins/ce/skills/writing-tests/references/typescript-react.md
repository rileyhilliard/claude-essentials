# TypeScript/React Testing Patterns

Language-specific patterns for testing TypeScript and React applications with Vitest, React Testing Library, and Playwright.

## Contents

- [Integration Test Pattern (React Testing Library)](#integration-test-pattern-react-testing-library)
- [E2E Test Pattern (Playwright)](#e2e-test-pattern-playwright)
- [Query Strategy](#query-strategy)
- [String Management](#string-management)
- [React-Specific Anti-Patterns](#react-specific-anti-patterns)
- [Async Waiting Patterns](#async-waiting-patterns)
- [Tooling Quick Reference](#tooling-quick-reference)
- [Setup Patterns](#setup-patterns)

## Integration Test Pattern (React Testing Library)

```typescript
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ItemList } from "./ItemList";
import { StateProvider } from "@/providers/StateProvider";

describe("ItemList", () => {
  const setup = (initialState: Partial<AppState> = {}) => {
    const user = userEvent.setup();
    const result = render(<ItemList />, {
      wrapper: ({ children }) => (
        <StateProvider initialState={initialState}>{children}</StateProvider>
      ),
    });
    return { user, ...result };
  };

  it("should show confirmation when user adds item", async () => {
    const { user } = setup({ items: [] });

    const button = screen.getByRole("button", { name: /add item/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/item added/i)).toBeVisible();
    });
  });
});
```

## E2E Test Pattern (Playwright)

```typescript
import { test, expect } from "@playwright/test";

test("should complete checkout workflow", async ({ page }) => {
  await page.goto("/dashboard");

  // Given: user is on dashboard
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

  // When: user adds item to cart
  await page.getByRole("button", { name: "Add to Cart" }).click();

  // Then: confirmation appears
  await expect(page.getByText("Added to cart")).toBeVisible();
});
```

## Query Strategy

**Use semantic queries (order of preference):**

1. `getByRole("button", { name: /submit/i })` - Accessibility-based
2. `getByLabelText(/email/i)` - Form labels
3. `getByText(/welcome/i)` - Visible text
4. `getByPlaceholderText(/search/i)` - Input placeholders

**Avoid:**

- `getByTestId` - Implementation detail
- CSS selectors - Brittle, breaks during refactoring
- Internal state queries - Not user-observable

## String Management

**Use source constants, not hard-coded strings:**

```typescript
// Good - References actual constant
import { MESSAGES } from "@/constants/messages";
expect(screen.getByText(MESSAGES.SUCCESS)).toBeVisible();

// Bad - Hard-coded, breaks when copy changes
expect(screen.getByText("Action completed successfully!")).toBeVisible();
```

## React-Specific Anti-Patterns

### Testing Mock Behavior

```typescript
// BAD: Testing mock existence, not real behavior
test("renders sidebar", () => {
  render(<Page />);
  expect(screen.getByTestId("sidebar-mock")).toBeInTheDocument();
});

// GOOD: Test real component with semantic query
test("renders sidebar", () => {
  render(<Page />);
  expect(screen.getByRole("navigation")).toBeInTheDocument();
});
```

### Mocking Internal Components

```typescript
// BAD: Mock internal dependencies
vi.mock("./Sidebar", () => ({
  Sidebar: () => <div data-testid="sidebar-mock" />,
}));

// GOOD: Use real components, mock at system boundaries only
// Only mock external APIs, not internal components
```

## Async Waiting Patterns

Use framework-provided waiting utilities, not arbitrary timeouts:

```typescript
// BAD: Guessing at timing
await new Promise((r) => setTimeout(r, 500));
expect(screen.getByText("Done")).toBeVisible();

// GOOD: Wait for the actual condition
await waitFor(() => {
  expect(screen.getByText("Done")).toBeVisible();
});

// GOOD: Playwright auto-waits
await expect(page.getByText("Done")).toBeVisible();
```

For flaky test debugging, invoke `Skill(condition-based-waiting)`.

## Tooling Quick Reference

| Tool                  | Purpose            | Best For                        |
| --------------------- | ------------------ | ------------------------------- |
| Vitest                | Test runner        | Vite projects, fast, TS native  |
| Jest                  | Test runner        | Legacy projects, wide ecosystem |
| React Testing Library | Component testing  | Integration tests with real DOM |
| Playwright            | Browser automation | E2E tests, cross-browser        |
| MSW                   | API mocking        | Mock fetch at network level     |

## Setup Patterns

### Vitest + RTL Setup

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
  },
});
```

```typescript
// vitest.setup.ts
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
```

### Playwright Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
  ],
});
```

### MSW Setup for API Mocking

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users", () => {
    return HttpResponse.json([
      { id: 1, name: "John" },
      { id: 2, name: "Jane" },
    ]);
  }),
];
```

```typescript
// mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

```typescript
// vitest.setup.ts
import { server } from "./mocks/server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```
