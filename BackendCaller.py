import MoviesDB as mdb


def safe(func):
    def db_call(*args, **kwargs):
        db = mdb.MoviesDB()
        thing = func(db, *args, **kwargs)
        db.close()
        if thing is None:
            abort(404)
        return thing
    return db_call 

get_movie = safe(mdb.MoviesDB.getMovie)
get_all_movies = safe(mdb.MoviesDB.getAllMovies)
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