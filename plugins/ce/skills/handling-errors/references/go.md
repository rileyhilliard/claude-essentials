# Go Error Handling

Go-specific patterns for handling errors.

## Contents

- [Key Patterns](#key-patterns)
- [Explicit Checking with Wrapping](#explicit-checking-with-wrapping)
- [Sentinel Errors for Expected Conditions](#sentinel-errors-for-expected-conditions)
- [Defer for Guaranteed Cleanup](#defer-for-guaranteed-cleanup)
- [Custom Error Types](#custom-error-types)
- [Error Wrapping Best Practices](#error-wrapping-best-practices)
- [Multiple Return Values Pattern](#multiple-return-values-pattern)
- [Panic and Recover](#panic-and-recover-use-sparingly)
- [Error Group Pattern](#error-group-pattern)

## Key Patterns

**Explicit error returns:** Always check returned errors - Go doesn't have exceptions.

**Error wrapping:** Use `fmt.Errorf` with `%w` to preserve error chains.

**Sentinel errors:** Define package-level `var Err...` for expected conditions.

**Defer for cleanup:** Use `defer` to ensure resources are released.

## Explicit Checking with Wrapping

```go
// ✅ Explicit checking with wrapping
func loadConfig(path string) (Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return Config{}, fmt.Errorf("read config %s: %w", path, err)
    }

    var config Config
    if err := json.Unmarshal(data, &config); err != nil {
        return Config{}, fmt.Errorf("parse config: %w", err)
    }
    return config, nil
}
```

## Sentinel Errors for Expected Conditions

```go
// ✅ Sentinel errors for expected conditions
var (
    ErrNotFound = errors.New("not found")
    ErrInvalid  = errors.New("invalid input")
)

func getUser(id string) (*User, error) {
    if id == "" {
        return nil, ErrInvalid
    }
    user, err := db.Query(id)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, ErrNotFound
    }
    if err != nil {
        return nil, fmt.Errorf("query user: %w", err)
    }
    return user, nil
}

// Caller can check with errors.Is()
user, err := getUser(id)
if errors.Is(err, ErrNotFound) {
    return http.StatusNotFound, "User not found"
}
```

## Defer for Guaranteed Cleanup

```go
// ✅ Defer for guaranteed cleanup
func process(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("open: %w", err)
    }
    defer f.Close()  // Runs even if error occurs below

    data, err := io.ReadAll(f)
    if err != nil {
        return fmt.Errorf("read: %w", err)
    }
    return handleData(data)
}
```

## Custom Error Types

```go
// Custom error type with additional context
type ValidationError struct {
    Field string
    Value interface{}
    Err   error
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("invalid %s: %v (%v)", e.Field, e.Value, e.Err)
}

func (e *ValidationError) Unwrap() error {
    return e.Err
}

// Usage
func validateAge(age int) error {
    if age < 0 || age > 150 {
        return &ValidationError{
            Field: "age",
            Value: age,
            Err:   errors.New("must be 0-150"),
        }
    }
    return nil
}

// Caller can check type
if err := validateAge(age); err != nil {
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        // Handle validation error specifically
        return fmt.Errorf("field %s invalid", validationErr.Field)
    }
    return err
}
```

## Error Wrapping Best Practices

```go
// ❌ Bad: No context
func loadUser(id string) (*User, error) {
    return db.Get(id)  // Just returns db error
}

// ❌ Bad: Loses error chain
func loadUser(id string) (*User, error) {
    _, err := db.Get(id)
    if err != nil {
        return nil, errors.New("load failed")  // %v loses chain
    }
}

// ✅ Good: Wraps with %w
func loadUser(id string) (*User, error) {
    user, err := db.Get(id)
    if err != nil {
        return nil, fmt.Errorf("load user %s: %w", id, err)
    }
    return user, nil
}
```

## Multiple Return Values Pattern

```go
// Common pattern: (result, error)
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Usage: Always check error
result, err := divide(10, 0)
if err != nil {
    log.Printf("Division failed: %v", err)
    return
}
fmt.Printf("Result: %f\n", result)
```

## Panic and Recover (Use Sparingly)

```go
// Use panic only for truly unrecoverable errors
func mustConnect(dsn string) *sql.DB {
    db, err := sql.Open("postgres", dsn)
    if err != nil {
        panic(fmt.Sprintf("cannot connect to database: %v", err))
    }
    return db
}

// Recover from panics in goroutines
func worker() {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Worker panic: %v", r)
        }
    }()

    // Risky work that might panic
    doWork()
}
```

## Error Group Pattern

```go
import "golang.org/x/sync/errgroup"

func processFiles(paths []string) error {
    g := new(errgroup.Group)

    for _, path := range paths {
        path := path  // Capture for goroutine
        g.Go(func() error {
            return processFile(path)
        })
    }

    // Wait for all and return first error
    if err := g.Wait(); err != nil {
        return fmt.Errorf("file processing failed: %w", err)
    }
    return nil
}
```
