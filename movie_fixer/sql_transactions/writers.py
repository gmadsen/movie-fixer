""""SQL modifying updates"""

############### SQL Commands ###############

UPDATE_MOVIE_BY_ID = ("""UPDATE Movies
                    SET title = ?, year = ?, imdb_id = ?, tmdb_id = ? WHERE id = ?;""")


#, (movie.title, movie.year, movie.imdb_id, movie.tmdb_id, movie_id))
