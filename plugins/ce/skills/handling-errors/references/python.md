# Python Error Handling

Python-specific patterns for handling exceptions and errors.

## Contents

- [Key Patterns](#key-patterns)
- [EAFP Pattern with Specific Exceptions](#eafp-pattern-with-specific-exceptions)
- [Custom Exception Hierarchy](#custom-exception-hierarchy)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Key Patterns

**EAFP (Easier to Ask Forgiveness than Permission):** Use try-except instead of pre-checking conditions.

**Specific exceptions:** Never use bare `except:` - catch specific exception types.

**Context managers:** Use `with` statements for resource cleanup.

**Exception chaining:** Use `raise ... from e` to preserve error context.

## EAFP Pattern with Specific Exceptions

```python
# ✅ EAFP pattern with specific exceptions
def load_config(path: Path) -> Dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        raise ValueError(f"Malformed config: {path}") from e
```

## Custom Exception Hierarchy

```python
# ✅ Custom exception hierarchy
class AppError(Exception):
    """Base for all app errors."""
    pass

class ValidationError(AppError):
    def __init__(self, field: str, value: Any):
        super().__init__(f"Invalid {field}: {value}")
        self.field = field

# Usage
try:
    user = get_user(user_id)
except ValidationError as e:
    return {"error": e.message, "field": e.field}, 400
except AppError:
    logger.error("App error", exc_info=True)
    return {"error": "Internal error"}, 500
```

## Best Practices

### Always Use Specific Exceptions

```python
# ❌ Bad: Bare except catches everything
try:
    dangerous_operation()
except:  # Catches KeyboardInterrupt, SystemExit, etc.
    pass

# ✅ Good: Specific exceptions
try:
    dangerous_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### Use Context Managers for Resources

```python
# ✅ Context manager ensures cleanup
def process_file(path: Path) -> None:
    with open(path) as f:  # File closed automatically
        data = f.read()
        process_data(data)
```

### Preserve Error Context with Chaining

```python
# ❌ Bad: Loses original error
try:
    data = fetch_data()
except Exception as e:
    raise ValueError("Failed to fetch")  # Lost original error

# ✅ Good: Preserves chain
try:
    data = fetch_data()
except Exception as e:
    raise ValueError("Failed to fetch") from e  # Chain preserved
```

### Use exc_info for Stack Traces

```python
import logging

logger = logging.getLogger(__name__)

try:
    risky_operation()
except Exception as e:
    # Includes full stack trace in logs
    logger.error("Operation failed", exc_info=True)
    raise
```

## Common Patterns

### Result Type Pattern

```python
from typing import Union, TypedDict

class Success(TypedDict):
    success: bool
    data: Any

class Failure(TypedDict):
    success: bool
    error: str

Result = Union[Success, Failure]

def load_data() -> Result:
    try:
        data = fetch_data()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Load failed: {e}")
        return {"success": False, "error": str(e)}
```

### Retry with Exponential Backoff

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    initial_delay: float = 1.0
) -> T:
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = initial_delay * (2 ** attempt)
            logger.warning(
                f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
            )
            time.sleep(delay)
```
