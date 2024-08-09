import asyncio

import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from rolf_common.schemas.auth import RequiredUser
from rolf_common.services import get_user

from backend.database import db_session
from backend.database import test_sessionmanager
from main import app
from rolf_common.models import Base


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function')
async def create_test_session():
    async with test_sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with test_sessionmanager.session() as session:
        yield session


@pytest_asyncio.fixture(scope='function', autouse=True)
def override_db_session(create_test_session):
    """
    Overrides the database session, in this case using test_sessionmanager.
    In session end it rolls back all database operations.
    """
    app.dependency_overrides[db_session] = lambda: create_test_session


def get_mock_user():
    return RequiredUser(
        user_id=uuid.uuid4(),
    )


@pytest_asyncio.fixture(scope='function', autouse=True)
def override_user_service():
    app.dependency_overrides[get_user] = get_mock_user


@pytest_asyncio.fixture(scope='function', autouse=True)
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
