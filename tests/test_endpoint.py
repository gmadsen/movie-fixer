import pytest
from  movieapp.movieapp import MOVIE_APP as app


@pytest.fixture(name='test_app')
def _test_app():
    return app

@pytest.mark.asyncio
async def test_app(test_app):
    """ basic test """
    client = test_app.test_client()
    response = await client.get('/')
    assert response.status_code == 200
