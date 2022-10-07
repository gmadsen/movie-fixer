import pytest
from .. movieapp import MOVIE_APP as app


@pytest.fixture(name='test_app')
def _test_app():
    return app

@pytest.asyncio
async def test_app(app):
    client = app.test_client()
    response = await client.get('/')
    assert response.status_code == 200
