# Python Waiting Patterns

## Contents

- [Polling helpers](#polling-helpers)
- [tenacity library](#tenacity-library)
- [pytest-asyncio patterns](#pytest-asyncio-patterns)
- [Container readiness](#container-readiness)
- [Anti-patterns](#anti-patterns)

---

## Polling helpers

### Generic polling with timeout

```python
import asyncio
import time
from typing import TypeVar, Callable, Awaitable

T = TypeVar('T')

async def wait_for(
    condition: Callable[[], Awaitable[T | None]],
    description: str,
    timeout: float = 5.0,
    poll_interval: float = 0.05
) -> T:
    """Wait for async condition to return truthy value."""
    start = time.monotonic()

    while True:
        result = await condition()
        if result:
            return result

        elapsed = time.monotonic() - start
        if elapsed > timeout:
            raise TimeoutError(f"Timeout waiting for {description} after {timeout}s")

        await asyncio.sleep(poll_interval)
```

### HTTP job polling

```python
async def wait_for_job(
    client: AsyncClient,
    job_id: str | UUID,
    timeout: int = 60,
    poll_interval: float = 0.5,
) -> dict[str, Any]:
    """Poll job endpoint until complete or failed."""
    start = time.time()
    while time.time() - start < timeout:
        response = await client.get(f"/v1/jobs/{job_id}")
        response.raise_for_status()
        data = response.json()

        if data["status"] in ("completed", "failed"):
            return data

        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Job {job_id} did not complete in {timeout}s")
```

### Sync polling helper

```python
import time

def wait_for_sync(
    condition: Callable[[], T | None],
    description: str,
    timeout: float = 5.0,
    poll_interval: float = 0.05
) -> T:
    """Synchronous wait for condition."""
    start = time.time()

    while True:
        result = condition()
        if result:
            return result

        if time.time() - start > timeout:
            raise TimeoutError(f"Timeout waiting for {description} after {timeout}s")

        time.sleep(poll_interval)
```

## tenacity library

For retry logic, use [tenacity](https://tenacity.readthedocs.io/):

**Stop strategies:**
- `stop_after_attempt(n)` - limit by count
- `stop_after_delay(seconds)` - limit by time
- Combine: `stop_after_attempt(5) | stop_after_delay(30)`

**Wait strategies:**
- `wait_fixed(seconds)` - consistent intervals
- `wait_exponential(multiplier, min, max)` - backoff

```python
from tenacity import retry, stop_after_delay, wait_fixed

# For tests: use fixed short intervals (not exponential)
@retry(stop=stop_after_delay(5), wait=wait_fixed(0.1))
def wait_for_service_ready():
    response = requests.get("http://localhost:8000/health")
    response.raise_for_status()
    return response
```

**Result-based retry:**

```python
from tenacity import retry, retry_if_result

@retry(retry=retry_if_result(lambda x: x is None))
def poll_for_result():
    return get_result()  # Retries while None
```

**Callbacks for observability:**

```python
from tenacity import retry, before_sleep_log
import logging

logger = logging.getLogger(__name__)

@retry(before_sleep=before_sleep_log(logger, logging.WARNING))
def flaky_operation():
    ...
```

## pytest-asyncio patterns

### Async fixtures with cleanup

```python
import pytest
import pytest_asyncio

@pytest_asyncio.fixture
async def database():
    db = await Database.connect()
    yield db
    await db.disconnect()

@pytest.mark.asyncio
async def test_creates_record(database):
    record = await database.create({"name": "test"})

    # Wait for async side effects
    async def check_record():
        return await database.get(record.id)

    result = await wait_for(
        check_record,
        description=f"record {record.id} to be queryable"
    )
    assert result.name == "test"
```

### Timeout on entire test

```python
@pytest.mark.asyncio
@pytest.mark.timeout(10)  # Fail test if takes > 10s
async def test_long_running_operation():
    result = await process_large_dataset()
    assert result.complete
```

## Container readiness

### CompositeWaitStrategy (log + port)

Wait for multiple conditions to handle edge cases:

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import (
    CompositeWaitStrategy,
    LogMessageWaitStrategy,
    PortWaitStrategy,
)

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container with composite wait strategy."""
    container = (
        DockerContainer("postgres:15")
        .with_env("POSTGRES_USER", "test")
        .with_env("POSTGRES_PASSWORD", "test")
        .with_env("POSTGRES_DB", "test")
        .with_exposed_ports(5432)
        .waiting_for(
            CompositeWaitStrategy(
                LogMessageWaitStrategy(
                    "database system is ready to accept connections",
                    times=2  # Postgres logs this twice
                ),
                PortWaitStrategy(5432),
            )
        )
    )
    with container:
        yield container
```

### Retry logic for transient connection issues

```python
def _run_sql_in_container(
    container: DockerContainer, sql: str, retries: int = 3, delay: float = 1.0
) -> subprocess.CompletedProcess:
    """Execute SQL with retry logic for container startup race conditions."""
    last_result = None

    for attempt in range(retries):
        result = subprocess.run(
            ["docker", "exec", container.get_wrapped_container().id,
             "psql", "-U", "test", "-c", sql],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result
        last_result = result
        time.sleep(delay)

    raise RuntimeError(f"SQL failed after {retries} attempts: {last_result.stderr}")
```

---

## Anti-patterns

### Exponential backoff in tests

```python
# Bad: 1s, 2s, 4s, 8s... too slow for tests
@retry(wait=wait_exponential())
def wait_for_condition():
    ...

# Good: fixed short interval
@retry(wait=wait_fixed(0.1), stop=stop_after_delay(5))
def wait_for_condition():
    ...
```

### Guessed delays

```python
# Bad: arbitrary sleep
await asyncio.sleep(2)
result = get_result()

# Good: poll for condition
result = await wait_for(get_result, description="result to be available")
```

### Blocking calls in async context

```python
# Bad: blocks event loop
def check_ready():
    time.sleep(0.1)  # Blocking!
    return is_ready()

# Good: async all the way
async def check_ready():
    await asyncio.sleep(0.1)
    return await is_ready()
```

### No timeout

```python
# Bad: infinite wait possible
while not condition():
    await asyncio.sleep(0.1)

# Good: bounded with clear error
await asyncio.wait_for(wait_for_condition(), timeout=10.0)
```
