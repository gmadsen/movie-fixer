""" route endpoint tests"""
from unittest.mock import AsyncMock
import pytest
import pytest_asyncio
from movie_fixer.webapp import WEB_APP as app


@pytest_asyncio.fixture(name='test_app')
def _test_app():
    return app

@pytest.mark.asyncio
async def test_routes(test_app):
    """ basic test """
    client = test_app.test_client()
    response = await client.get('/')
    assert response.status_code == 200
