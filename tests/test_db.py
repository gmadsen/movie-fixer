""" database tests"""
from pathlib import Path
from unittest.mock import AsyncMock
import pytest

import movie.fixer.movie_db as mdb
import movie.fixer.backend_caller as bc
import movie_fixer.sql_transactions.readers as sr
import movie_fixer.backend_caller

PATH = Path(__file__).parent

@pytest.fixture(name = test_db)
def _test_db():
     return mdb.MovieDB(db=PATH/test.db, )

@pytest
def test_safe(func):
    """ test wrap all backend"""
    def dbase_call(*args, **kwargs):
        dbase = mdb.MovieDB()
        thing = func(dbase, *args, **kwargs)
        dbase.close()
        return thing
    return dbase_call

# TODO: figure out if I can remove build_tables, just have a check if db and tables exists, build if no
def safe(db=None, func):
    """ wrap all db accesses with explicit db opening/closing and function validity checking """
    def dbase_call(*args, **kwargs):
        dbase = mdb.MovieDB()
        thing = func(dbase, *args, **kwargs)
        dbase.close()
        return thing
    return dbase_call


def test_queries(test_db):
    """ test db with fake data"""
    # a = get
    # local_db  = mdb.MovieDB(PATH/'test_db', build_tables=True, debug_data=PATH/'test_data.json')
    # return local_db
# class MovieDB:
    # """ Primary class to construct, query, and modify movie database """
    # def __init__(self, database=PATH/'data/movies.db', build_tables=False):
        # self.conn = None
