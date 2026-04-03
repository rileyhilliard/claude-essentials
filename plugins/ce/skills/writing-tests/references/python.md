# Python Testing Patterns

Language-specific patterns for testing Python applications with `pytest`, `httpx`, and modern architecture tools like `polyfactory` and `testcontainers`.

## Contents

- [Pytest Configuration](#pytest-configuration-pyprojecttoml)
- [Pytest Fixture Pattern](#pytest-fixture-pattern)
- [Data Generation (Polyfactory)](#data-generation-polyfactory)
- [Mocking External Boundaries (RESPX)](#mocking-external-boundaries-respx)
- [FastAPI Testing Patterns (Async)](#fastapi-testing-patterns-async)
- [Integration Testing (Testcontainers)](#integration-testing-testcontainers)
- [Table-Driven Tests (Parametrize)](#table-driven-tests-parametrize)
- [Tooling Quick Reference](#tooling-quick-reference)
- [Property-Based Testing (Hypothesis)](#property-based-testing-hypothesis)
- [Refactor-safe Assertions for Mock Kwargs](#refactor-safe-assertions-for-mocked-kwargs)

## Pytest Configuration (`pyproject.toml`)

Modern pytest setup uses `pyproject.toml` for configuration.

```toml
[tool.pytest.ini_options]
addopts = "-ra -q --cov=app --cov-report=term-missing"
testpaths = ["tests"]
asyncio_mode = "auto"  # Eliminates need for @pytest.mark.asyncio decorators
asyncio_default_fixture_loop_scope = "function"
```

## Pytest Fixture Pattern

Use `yield` for setup/teardown and prefer `scope="session"` for expensive resources (like containers) and `scope="function"` for isolation (like db transactions).

```python
import pytest

@pytest.fixture
def db_session(db_engine):
    """Creates a fresh database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def user(db_session):
    """Create a test user using a Factory (preferred over manual creation)."""
    return UserFactory.create_sync(session=db_session)

def test_user_update(db_session, user):
    # Arrange
    user.name = "Updated Name"
    db_session.commit()

    # Act & Assert
    refreshed = db_session.get(User, user.id)
    assert refreshed.name == "Updated Name"
```

## Data Generation (Polyfactory)

Replace manual object creation and `factory_boy` with **Polyfactory**. It uses type hints to automatically generate valid data.

```python
from polyfactory.factories.pydantic_factory import ModelFactory
from app.models import User, UserRole

# Automatically infers fields from the Pydantic model or Dataclass
class UserFactory(ModelFactory[User]):
    __model__ = User

    # Override defaults if specific values are needed
    role = UserRole.USER
    is_active = True

def test_admin_dashboard(client):
    # Generate a full user object with valid random data, overriding just the role
    admin_user = UserFactory.build(role=UserRole.ADMIN)

    response = client.post("/login", json={"user": admin_user.dict()})
    assert response.status_code == 200
```

## Mocking External Boundaries (RESPX)

Avoid patching `requests` directly. Use `respx` with `httpx` for robust, router-based HTTP mocking.

```python
import respx
import httpx
import pytest

@respx.mock
async def test_external_github_api_call():
    # Arrange: Define the mock behavior (Router style)
    my_route = respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"login": "test_user"})
    )

    # Act: Call function using httpx.AsyncClient
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user")

    # Assert
    assert response.json()["login"] == "test_user"
    assert my_route.called
```

## FastAPI Testing Patterns (Async)

Use `httpx.AsyncClient` with `ASGITransport` for modern FastAPI testing.

```python
from httpx import AsyncClient, ASGITransport
import pytest

@pytest.fixture
async def client(db_session):
    """Create async test client with DB overrides."""
    # Override dependency
    app.dependency_overrides[get_db] = lambda: db_session

    # Connect directly to the app (no network overhead)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()

async def test_create_user(client):
    user_data = UserFactory.build() # Generate data

    response = await client.post("/users", json=user_data.model_dump())

    assert response.status_code == 201
    assert response.json()["email"] == user_data.email
```

## Integration Testing (Testcontainers)

Do not use SQLite for Postgres tests. Use **Testcontainers** to spin up real, disposable Docker instances.

```python
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine

@pytest.fixture(scope="session")
def postgres_container():
    """Spin up a real Postgres container for the test session."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """Create engine connected to the container."""
    db_url = postgres_container.get_connection_url()
    engine = create_engine(db_url)

    # Run migrations (e.g., Alembic) here to set up schema
    Base.metadata.create_all(engine)

    yield engine
    engine.dispose()
```

## Table-Driven Tests (Parametrize)

```python
import pytest

@pytest.mark.parametrize("email, expected_error", [
    pytest.param("no-at-sign", "Invalid email", id="missing_at"),
    pytest.param("", "Field required", id="empty"),
    pytest.param("user@domain", "Missing TLD", id="missing_tld"),
])
def test_email_validation_errors(email, expected_error):
    with pytest.raises(ValueError, match=expected_error):
        validate_email(email)
```

## Tooling Quick Reference

| Tool               | Purpose         | Best For                           |
| ------------------ | --------------- | ---------------------------------- |
| **pytest**         | Test runner     | The industry standard              |
| **ruff**           | Linting         | Fast linting/formatting            |
| **polyfactory**    | Data generation | Modern replacement for factory_boy |
| **respx**          | HTTP Mocking    | Mocking `httpx` requests           |
| **testcontainers** | Infrastructure  | Real integration tests (Docker)    |
| **httpx**          | HTTP Client     | Async & Sync API testing           |
| **pytest-asyncio** | Async support   | `asyncio_mode="auto"`              |

## Property-Based Testing (Hypothesis)

For critical logic, generate thousands of edge cases automatically.

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_properties(x, y):
    # Commutative property
    assert add(x, y) == add(y, x)
```

## Refactor-safe Assertions for Mocked Kwargs
When validating kwargs passed to mocks, **do not access them via dictionary keys** (e.g. `kwargs["timeout"]`).  

String key access is brittle and not refactor-safe because IDE renaming tools will not update these strings.

Instead, assert the call using `assert_called_with` or compare the full kwargs dictionary.

#### ❌ Avoid

```python
kwargs = mock.call_args.kwargs
assert kwargs["timeout"] == 10
assert kwargs["retry_count"] == 3
```

#### ✅ Prefer

```python
mock.assert_called_once_with(timeout=10, retry_count=3)
```

or

```python
assert mock.call_args.kwargs == dict(timeout=10, retry_count=3)
```

These approaches are clearer, less brittle, and easier to maintain when function arguments change.

