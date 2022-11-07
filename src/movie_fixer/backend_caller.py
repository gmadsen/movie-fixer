"""flask routing logic"""
from dataclasses import dataclass
from pathlib import Path
from .sql_transactions import readers as sr
from .sql_transactions import writers as sw
from . import movie_db as mdb
from . import movie_interface as mi
from . import tmdb_api

##################################################################################################
######################## Stats and Data Analysis Functions ########################################
@dataclass
class Stats:
    def __init__(self):
        self.total_movies = 0
        self.total_movies_missing_imdb_id = 0
        self.total_movies_missing_tmdb_id = 0
        self.total_movies_missing_both_ids = 0
        self.total_reviewable_movies = 0
        self.total_valid_movies = 0
        self.total_responses = 0
        self.total_searches = 0

    @classmethod
    def from_db(cls, database):
        """construct stats struct with queries to database"""
        stats = cls()
        stats.total_movies = database.query(sr.TOTAL_MOVIE_COUNT)[0][0]
        stats.total_movies_missing_imdb_id = database.query(sr.MISSING_IMDB_ID_MOVIE_COUNT)[0][0]
        stats.total_movies_missing_tmdb_id = database.query(sr.MISSING_TMDB_ID_MOVIE_COUNT)[0][0]
        stats.total_movies_missing_both_ids = database.query(sr.MISSING_BOTH_IDS_MOVIE_COUNT)[0][0]
        stats.total_responses = database.query(sr.TOTAL_RESPONSE_COUNT)[0][0]
        stats.total_searches = database.query(sr.TOTAL_SEARCH_COUNT)[0][0]
        stats.total_reviewable_movies = database.query(sr.REVIEWABLE_MOVIE_COUNT)[0][0]
        stats.total_valid_movies = database.query(sr.TOTAL_VALID_MOVIE_COUNT)[0][0]
        return stats


############### routing logic ############################
def update_movie_from_form(movie_id, form):
    """ Update database with user defined info, will only be valid with an id"""
    new_movie = mi.Movie.from_form(form)
    if not new_movie.is_fully_defined():
        return False
    update_movie(movie_id, new_movie)
    remove_associated_searches(movie_id)
    return True

def update_movie_with_api_call(movie_id):
    """update movie record with a api get response"""
    try:
        movie = mi.Movie.from_query(get_movie(movie_id))
        movie = tmdb_api.update_movie_with_api_call(movie)
        add_search(movie_id, movie)
        return True
    except Exception as e:
        print(e)
        return False

async def update_invalid_movies_async():
    """update a list of movies asynchronously"""
    movies_query = get_invalid_movies()
    tasks = [tmdb_api.Task(movie['id'], tmdb_api.make_params_from_movie_query(movie)) for movie in movies_query]
    return await tmdb_api.batch_runner(20, tasks[:5])

def user_power_button_handler(action):
    """ handles all put requests from power buttons"""
    if action == 'match':
        auto_match_movies()
    elif action == 'query':
        print("not implemented")
        # query_all_invalids()
    elif action == 'export':
        print("not implemented")
        # export_all_valids()
    elif action == 'backup':
        create_transaction_backup()
    elif action == 'reset':
        hard_db_reset()
    else:
        print("go fuck yourself")


def hard_db_reset():
    """reset all tables, fill with normal data"""
    create_project_tables()
    load_data_paths()


#######################################################################################
########################### Database Commands and Queries #############################

def safe(func):
    """ wrap all db accesses with explicit db opening/closing and function validity checking """
    def dbase_call(*args, **kwargs):
        dbase = mdb.MovieDB()
        thing = func(dbase, *args, **kwargs)
        dbase.close()
        return thing
    return dbase_call


def make_query(sql_string):
    """ make a query func of arbitrary args from its sql command """
    def query_wrapper(dbase, *args):
        return dbase.query(sql_string, *args)
    return query_wrapper

def make_update(sql_string):
    """make an update of arbitary args from its sql command"""
    def update_wrapper(dbase, *args):
        return dbase.update(sql_string, *args)
    return update_wrapper


# DB Updates
def update_movie(movie_id, movie):
    """update a movie record from movie interface object"""
    func = safe(make_update(sw.UPDATE_MOVIE_BY_ID))
    return func(movie.title, movie.year, movie.imdb_id, movie.tmdb_id, movie_id)

# DB queries
get_movie = safe(make_query(sr.GET_MOVIE_BY_ID))
get_all_movies = safe(make_query(sr.GET_ALL_MOVIES))
get_searches_by_movie_id = safe(make_query(sr.GET_SEARCHES_BY_MOVIE_ID))
get_movies_with_no_imdb_id = safe(make_query(sr.GET_MOVIES_WITH_NO_IMDB_ID))
get_movies_with_valid_searches = safe(make_query(sr.GET_MOVIES_WITH_VALID_SEARCHES))
get_invalid_movies = safe(make_query(sr.GET_INVALID_MOVIES))
get_valid_movies = safe(make_query(sr.GET_VALID_MOVIES))

###################################################################################################
################################### Main Functions #################################################

#update_movie = safe(mdb.MovieDB.update_movie)
remove_associated_searches = safe(mdb.MovieDB.remove_associated_searches)
add_search = safe(mdb.MovieDB.add_search)
auto_match_movies = safe(mdb.MovieDB.auto_match_movies)
create_transaction_backup = safe(mdb.MovieDB.create_transaction_backup)
create_project_tables = safe(mdb.MovieDB.create_project_tables)
load_data_paths = safe(mdb.MovieDB.load_data_paths)
#tmdb_search = safe(mdb.MovieDB.add_tmdb_movie_query_to_movie)
get_stats = safe(Stats.from_db)


