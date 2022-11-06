""" database tests"""
from pathlib import Path
from unittest.mock import AsyncMock
import pytest

import movie_fixer.movie_db as mdb
import movie_fixer.backend_caller as bc
import movie_fixer.sql_transactions.readers as sr
import movie_fixer.backend_caller

PATH = Path(__file__).parent
DB_PATH = PATH/"test.db"
DATA_PATH = PATH/"test_data.json"
DATA_PATHS = [DATA_PATH]

@pytest.fixture()
def test_db():
    """test data new db"""
    db = mdb.MovieDB(database=DB_PATH)
    db.create_project_tables()
    db.load_data_paths(DATA_PATHS)
    return db


def test_queries(test_db):
    """ test db with fake data"""
    test_all_movies = test_db.query(sr.GET_ALL_MOVIES)
    assert(len(test_all_movies)) == 5
    assert(test_all_movies[0]['title']) == '(500) Days of Summer'
