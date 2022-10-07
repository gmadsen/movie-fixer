"""flask routing logic"""
from dataclasses import dataclass
import movie_db as mdb
import movie_interface as mi

############### routing logic ############################
def attempt_movie_update_from_form(movie_id, form):
    """ Update database with user defined info, will only be valid with an id"""
    new_movie = mi.Movie.from_form(form)
    if not new_movie.is_fully_defined():
        return False
    update_movie_to_valid(movie_id, new_movie)
    return True


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


############### SQL Commands ###############

GET_MOVIE_BY_ID = """SELECT * FROM movies WHERE id = ?;"""

GET_ALL_MOVIES = """SELECT * FROM movies;"""

GET_MOVIES_WITH_NO_IMDB_ID = """SELECT * FROM movies WHERE imdb_id IS NULL;"""

GET_INVALID_MOVIES = (""" SELECT * FROM Movies
                    LEFT OUTER JOIN Responses
                    ON Movies.id = Responses.from_movies_id
                    WHERE Responses.from_movies_id IS NULL
                    AND Movies.imdb_id = ''
                    AND Movies.tmdb_id = ''
                    """)

GET_VALID_MOVIES = (""" SELECT * FROM Movies
                    WHERE Movies.imdb_id != ''
                    OR Movies.tmdb_id != ''
                    """)

GET_MOVIES_WITH_VALID_SEARCHES = ("""
                    SELECT *
                    FROM Movies INNER JOIN Responses
                    ON Movies.id = Responses.from_movies_id
                    ORDER BY Movies.title
                    """)

GET_SEARCHES_BY_MOVIE_ID = ("""
                    SELECT * FROM Searches
                    WHERE from_responses_id
                    IN (SELECT id FROM Responses WHERE from_movies_id = ?)
                    """)

GET_MOVIES_WITH_CONFIDENT_MATCH = ("""
            SELECT Movies.id, Searches.title, Movies.year, Searches.imdb_id, Searches.tmdb_id
            FROM Movies
            INNER JOIN Responses ON
            Movies.id = Responses.from_movies_id
            INNER JOIN Searches ON
            Responses.id = Searches.from_responses_id
            WHERE UPPER(Movies.title) = UPPER(Searches.title)
            AND Movies.year = Searches.year
                    """)

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

# DB queries
get_movie = safe(make_query(GET_MOVIE_BY_ID))
get_all_movies = safe(make_query(GET_ALL_MOVIES))
get_searches_by_movie_id = safe(make_query(GET_SEARCHES_BY_MOVIE_ID))
get_movies_with_no_imdb_id = safe(make_query(GET_MOVIES_WITH_NO_IMDB_ID))
get_movies_with_valid_searches = safe(make_query(GET_MOVIES_WITH_VALID_SEARCHES))
get_invalid_movies = safe(make_query(GET_INVALID_MOVIES))
get_valid_movies = safe(make_query(GET_VALID_MOVIES))

###################################################################################################
################################### Main Functions #################################################

update_movie_to_valid = safe(mdb.MovieDB.update_movie_to_valid)
remove_associated_searches = safe(mdb.MovieDB.remove_associated_searches)
auto_match_movies = safe(mdb.MovieDB.auto_match_movies)
hard_db_reset = safe(mdb.MovieDB.hard_db_reset)
load_original_data = safe(mdb.MovieDB.load_original_data)
create_transaction_backup = safe(mdb.MovieDB.create_transaction_backup)
tmdb_search = safe(mdb.MovieDB.add_tmdb_movie_query_to_movie)


##################################################################################################
######################## Stats and Data Analysis Functions ########################################

TOTAL_MOVIE_COUNT = """SELECT COUNT(*) FROM Movies;"""
TOTAL_VALID_MOVIE_COUNT = """SELECT COUNT(*) FROM Movies WHERE imdb_id != '' OR tmdb_id != '';"""
MISSING_IMDB_ID_MOVIE_COUNT = """SELECT COUNT(*) FROM Movies WHERE imdb_id = '';"""
MISSING_TMDB_ID_MOVIE_COUNT = """SELECT COUNT(*) FROM Movies WHERE tmdb_id = '';"""

MISSING_BOTH_IDS_MOVIE_COUNT = """
                                select count(*) from movies where imdb_id = '' and tmdb_id = '';"""

TOTAL_RESPONSE_COUNT = """SELECT COUNT(*) FROM Responses;"""
TOTAL_SEARCH_COUNT = """SELECT COUNT(*) FROM Searches;"""
REVIEWABLE_MOVIE_COUNT = ("""
                        SELECT COUNT(*) FROM Movies
                        INNER JOIN Responses ON Movies.id = Responses.from_movies_id
                            """)

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
        stats.total_movies = database.query(TOTAL_MOVIE_COUNT)[0][0]
        stats.total_movies_missing_imdb_id = database.query(MISSING_IMDB_ID_MOVIE_COUNT)[0][0]
        stats.total_movies_missing_tmdb_id = database.query(MISSING_TMDB_ID_MOVIE_COUNT)[0][0]
        stats.total_movies_missing_both_ids = database.query(MISSING_BOTH_IDS_MOVIE_COUNT)[0][0]
        stats.total_responses = database.query(TOTAL_RESPONSE_COUNT)[0][0]
        stats.total_searches = database.query(TOTAL_SEARCH_COUNT)[0][0]
        stats.total_reviewable_movies = database.query(REVIEWABLE_MOVIE_COUNT)[0][0]
        stats.total_valid_movies = database.query(TOTAL_VALID_MOVIE_COUNT)[0][0]
        return stats


get_stats = safe(Stats.from_db)
