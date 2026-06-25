# Python Isolation Patterns

## Contents

- [Database isolation](#database-isolation)
- [Worker-specific resources](#worker-specific-resources)
- [Fixture cleanup](#fixture-cleanup)
- [Anti-patterns](#anti-patterns)

**For waiting/timing patterns:** See [writing-tests waiting-python](../../writing-tests/references/waiting-python.md).

---

## Database isolation

### Savepoint pattern (transaction rollback)

Each test runs in a savepoint that gets rolled back - no data pollution between tests:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Session using nested transactions for test isolation.

    - Each test runs in a savepoint that gets rolled back
    - Row data changes vanish automatically (no TRUNCATE needed)
    - Tests can call commit() without breaking isolation (commits to savepoint)
    - Supports parallel test execution since each test has its own savepoint
    """
    async with db_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()  # Savepoint

        async_session_factory = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with async_session_factory() as session:
            yield session

        await conn.rollback()  # All row changes vanish
```

### When savepoints aren't enough

Tests that spawn background jobs or workers need real commits because isolated sessions can't see savepoint-committed data:

```python
@pytest.fixture
async def db_session_real_commit(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Session with real commits for tests spawning isolated tasks.

    IMPORTANT: Use unique identifiers (UUIDs) to avoid conflicts in parallel runs.
    """
    async_session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session
```

## Worker-specific resources

### Separate database per pytest-xdist worker

```python
import os

def get_worker_id() -> str:
    """Get pytest-xdist worker ID, or 'main' if not running in parallel."""
    return os.environ.get("PYTEST_XDIST_WORKER", "main")

@pytest.fixture(scope="session")
def database_url(worker_id):
    """Each pytest-xdist worker gets its own database."""
    if worker_id == "master":
        return "postgresql://localhost/test"
    return f"postgresql://localhost/test_{worker_id}"
```

### Unique temp directories

```python
import tempfile

@pytest.fixture
def temp_dir():
    """Unique temp directory per test."""
    with tempfile.TemporaryDirectory() as d:
        yield d

@pytest.fixture
def unique_file(temp_dir):
    """Unique file path per test."""
    return os.path.join(temp_dir, "test_output.txt")
```

### Dynamic port allocation

```python
import socket

def get_free_port() -> int:
    """Get an available port from the OS."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@pytest.fixture
def server_port():
    return get_free_port()
```

## Fixture cleanup

### Environment variable isolation

```python
@pytest.fixture
def isolated_env():
    """Isolate environment variable changes."""
    original = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(original)
```

### Global state reset

```python
@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test."""
    import myapp.config as config
    original_settings = config.settings.copy()
    yield
    config.settings = original_settings
```

---

## Anti-patterns

### Shared database without isolation

```python
# Bad: tests pollute each other
@pytest.fixture
def db_session(db_engine):
    session = Session(db_engine)
    yield session
    session.close()  # Data persists!

# Good: explicit rollback ensures isolation
@pytest.fixture
def db_session(db_engine):
    conn = db_engine.connect()
    trans = conn.begin()
    try:
        yield Session(bind=conn)
    finally:
        trans.rollback()  # Always rollback, even on success
        conn.close()
```

### Hardcoded ports

```python
# Bad: port conflicts in parallel runs
SERVER_PORT = 8080

# Good: dynamic allocation
def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]
```

### Global state leakage

```python
# Bad: one test's setup affects others
def test_feature():
    os.environ["API_KEY"] = "test-key"
    # ... test runs ...
    # API_KEY persists!

# Good: save and restore
@pytest.fixture(autouse=True)
def clean_env():
    original = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original)
```
