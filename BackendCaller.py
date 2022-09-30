import MoviesDB as mdb
import MovieInterface as mi



## SQL Commands ##

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




# wrap all db accesses with explicit db opening/closing and function validity checking
def safe(func):
    def db_call(*args, **kwargs):
        db = mdb.MoviesDB()
        thing = func(db, *args, **kwargs)
        db.close()
        if thing is None:
            raise Exception("DB function returned None") 
        return thing
    return db_call 


def make_query(sql_string):
    def query_wrapper(db, *args):
        return db.query(sql_string, *args)
    return query_wrapper 

## for all queries
#query = safe(mdb.MoviesDB.query)
get_movie = safe(make_query(GET_MOVIE_BY_ID))
get_all_movies = safe(make_query(GET_ALL_MOVIES))
#get_movie = safe(mdb.MoviesDB.getMovie)
#get_all_movies = safe(mdb.MoviesDB.getAllMovies)
get_searches_by_movie_id = safe(mdb.MoviesDB.getSearchesByMovieId)
get_movies_with_valid_searches = safe(mdb.MoviesDB.getMoviesWithValidSearches)
get_invalid_movies = safe(mdb.MoviesDB.getInvalidMovies)
get_stats = safe(mdb.MoviesDB.getStats)
update_movie_to_valid = safe(mdb.MoviesDB.updateMovieToValid)
auto_match_movies = safe(mdb.MoviesDB.autoMatchMovies)
hard_db_reset = safe(mdb.MoviesDB.hardDBReset)
load_original_data = safe(mdb.MoviesDB.loadOriginalData)
tmdb_search = safe(mdb.MoviesDB.addTmdbMovieQueryToMovie)
get_valid_movies = safe(mdb.MoviesDB.getValidMovies)

## helpers
def attempt_movie_update_from_form(movie_id, form):
    new_movie = mi.Movie.from_form(form)
    if not new_movie.isFullyDefined():
        return False
    update_movie_to_valid(movie_id, new_movie) 
    return True

def user_power_button_handler(action):
    if action == 'match' :
        auto_match_movies()
    elif action == 'query':
        print("not implemented") 
        #query_all_invalids()
    elif action == 'reset':
        hard_db_reset()


