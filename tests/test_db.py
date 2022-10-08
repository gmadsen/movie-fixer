""" database tests"""
from pathlib import Path
from unittest.mock import AsyncMock
import pytest

# import movie_fixer.sql_transactions.readers as sr
# import backend_caller

# PATH = Path(__file__).parent

# @pytest.fixture(name = test_db)
# def _test_db():
    # return mdb

# def test_queries(test_db):
#     """ test db with fake data"""
    # a = get
    # local_db  = mdb.MovieDB(PATH/'test_db', build_tables=True, debug_data=PATH/'test_data.json')
    # return local_db
# class MovieDB:
    # """ Primary class to construct, query, and modify movie database """
    # def __init__(self, database=PATH/'data/movies.db', build_tables=False):
        # self.conn = None
