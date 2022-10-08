"""SQL non modifying reads"""

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


