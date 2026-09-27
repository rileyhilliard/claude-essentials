# Flaky Tests

For tests that pass alone and fail when run with the rest of the suite, or fail intermittently.

## Diagnose before fixing

Run the failing test about ten times alone, then about ten times with the suite, and compare.

| Symptom | Likely cause | Fix direction |
| --- | --- | --- |
| Same error every time with the suite, never alone | Shared state leaking between tests | Isolate state per test |
| Different or random failures | Race: the test doesn't wait for async work | Wait for the condition, not a duration |
| Port, file lock, or connection errors | Two tests or workers competing for one resource | Give each test or worker its own resource |

Find the polluting test by bisecting the suite order (`pytest -p randomly` with a fixed seed, `jest --runInBand` with a subset) rather than guessing.

## Shared state

| State | Isolation |
| --- | --- |
| Database | Transaction or savepoint rollback per test; a database per worker under parallel runs |
| Globals, singletons, module caches | Reset in setup/teardown, or build a fresh instance per test (`jest.resetModules()`) |
| Mocks and spies | `clearAllMocks` before each test, `restoreAllMocks` after |
| Files | Temp directories per test (`tmp_path`, `tempfile.TemporaryDirectory`) |
| Environment variables | Save and restore around the test (`monkeypatch.setenv`) |

Savepoint rollback with SQLAlchemy async:

```python
@pytest.fixture
async def db_session(db_engine):
    async with db_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        # yield a session bound to conn
        await conn.rollback()
```

## Races

Replace sleeps with waits on the observable condition. See [waiting-typescript.md](waiting-typescript.md) and [waiting-python.md](waiting-python.md).

## Resource conflicts

```python
# pytest-xdist: one database per worker
@pytest.fixture(scope="session")
def database_url(worker_id):
    return "postgresql://localhost/test" if worker_id == "master" else f"postgresql://localhost/test_{worker_id}"
```

```typescript
// Let the OS pick a free port
const server = app.listen(0);
const { port } = server.address();
```

## Confirming the fix

Repeat the test many times in the configuration that failed (`pytest --count=20 -n auto`, or `jest` in parallel after `jest --runInBand` passes). A single green run proves little for an intermittent failure.
