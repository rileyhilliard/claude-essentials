# TypeScript/React Error Handling

Language-specific patterns for handling errors in TypeScript and React applications.

## Contents

- [Error Boundaries for React Components](#error-boundaries-for-react-components)
- [Typed Error Classes](#typed-error-classes)
- [Async Error Handling & Result Pattern](#async-error-handling--result-pattern)
- [UI Error Display Patterns](#ui-error-display-patterns)
- [Centralized Error Handling](#centralized-error-handling)

## Error Boundaries for React Components

Error boundaries catch JavaScript errors in component trees and display fallback UI.

```typescript
class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error("Component error", { error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <ErrorFallback />;
    }
    return this.props.children;
  }
}

// Usage: Wrap components to prevent full app crashes
<ErrorBoundary fallback={<ErrorPage />}>
  <UserProfile />
</ErrorBoundary>;
```

## Typed Error Classes

Create specific error types for different failure modes instead of generic Error.

```typescript
class ValidationError extends Error {
  constructor(message: string, public field: string, public value: unknown) {
    super(message);
    this.name = "ValidationError";
  }
}

class NotFoundError extends Error {
  constructor(message: string, public resource: string) {
    super(message);
    this.name = "NotFoundError";
  }
}

// Usage: Callers can handle specific types
try {
  const user = await fetchUser(userId);
} catch (error) {
  if (error instanceof ValidationError) {
    showFieldError(error.field, error.message);
  } else if (error instanceof NotFoundError) {
    show404Page();
  } else {
    showGenericError();
  }
}
```

## Async Error Handling & Result Pattern

Always handle promise rejections. Use Result types for predictable failures.

```typescript
// Result type for predictable errors
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

async function loadData(): Promise<Result<Data, Error>> {
  try {
    const data = await fetchData();
    return { success: true, data };
  } catch (error) {
    logger.error("Load failed:", error);
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error)),
    };
  }
}

// Usage
const result = await loadData();
if (result.success) {
  processData(result.data);
} else {
  showError(result.error.message);
}
```

## UI Error Display Patterns

Choose the right pattern based on error severity and user context. **Never show the same error in multiple places.**

| Pattern                | When to Use                                                                          | Example                                           |
| ---------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------- |
| **Toast/Notification** | Transient, non-blocking info (background save, network retry)                        | "Changes saved" / "Retrying connection..."        |
| **Inline/Field Error** | Form validation, field-specific issues                                               | "Email format invalid" below email input          |
| **Alert/Banner**       | Page-level warnings that don't block interaction                                     | "You're offline. Changes won't sync." at page top |
| **Modal/Dialog**       | Blocking issues requiring user decision (session expired, destructive action failed) | "Session expired. Please log in again."           |
| **Full Page**          | Complete feature/app failure (404, 500, maintenance)                                 | Dedicated error page with support contact         |

```typescript
// ❌ Wrong: Error fatigue - same error everywhere
function handleUploadError(error: Error) {
  showToast("Upload failed"); // Toast
  setFieldError("file", "Upload failed"); // Inline
  showBanner("Upload failed"); // Banner
  // User sees same error 3 times!
}

// ✅ Right: Single, contextual error
function handleUploadError(error: Error) {
  if (error instanceof FileSizeError) {
    // Inline - user can immediately fix
    setFieldError("file", `File too large. Max ${error.maxSize}MB`);
  } else if (error instanceof NetworkError) {
    // Toast - transient, will retry
    showToast("Upload failed. Retrying...", { type: "warning" });
  } else {
    // Modal - requires user action
    showModal({
      title: "Upload Failed",
      message: "Unable to upload file. Please try again or contact support.",
      actions: [
        { label: "Retry", onClick: retry },
        { label: "Cancel", onClick: cancel },
      ],
    });
  }
}
```

## Centralized Error Handling

Use global handlers to ensure consistent error logging and formatting.

```typescript
// Global error handler
class ErrorHandler {
  handleError(error: Error, context?: Record<string, any>) {
    const category = this.categorizeError(error);

    // Log with full context
    logger.error(error.message, {
      error: { name: error.name, stack: error.stack },
      context,
      category,
      environment: process.env.NODE_ENV,
    });

    // Return user-friendly message
    return process.env.NODE_ENV === "development"
      ? { message: error.message, stack: error.stack }
      : {
          message:
            category === "validation" ? error.message : "Something went wrong",
          supportId: this.generateSupportId(),
        };
  }
}

// API middleware
app.use((error: Error, req: Request, res: Response, next: NextFunction) => {
  const handler = new ErrorHandler();
  const userError = handler.handleError(error, {
    path: req.path,
    userId: req.user?.id,
  });

  const statusCode = error instanceof ValidationError ? 400 : 500;
  res.status(statusCode).json(userError);
});
```
