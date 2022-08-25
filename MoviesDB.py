import sqlite3
import MovieInterface as mi 
import tmdbAPI 

class Stats:
    def __init__(self):
        self.total_movies = 0 
        self.total_movies_missing_imdb_id = 0
        self.total_movies_missing_tmdb_id = 0
        self.total_movies_missing_both_ids = 0
        self.total_reviewable_movies = 0 
        self.total_movies_needing_queries = 0
        self.total_responses = 0
        self.total_searches = 0


class MoviesDB:
    def __init__(self, db='data/movies.db', build_tables=False):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db)

        except Exception as e:
            print(e)
            self.conn.close()
            self.conn = None

        if self.conn is not None and build_tables:
            self.createProjectTables()

    
    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def createProjectTables(self):
        if self.conn is None:
            return
        with open('moviedb_schema.sql') as f:
            self.conn.executescript(f.read()) 
        self.conn.commit()

    def addMovies(self, movies):
        if self.conn is None:
            return
        for movie in movies:
            self.addMovie(movie)

    def addMovie(self, movie):
        """
        movie is a Movie object from MovieInterface.py

        """
        if self.conn is None:
            return
        cur = self.conn.cursor()
        try:

            cur.execute("""INSERT INTO Movies (title, year, imdb_id, tmdb_id) VALUES (?, ?, ?, ?)""", (movie.title, movie.year, movie.imdb_id, movie.tmdb_id))
            from_movie_id = cur.lastrowid

            if movie.imdb_response is not None:
                cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?, ?)""", (from_movie_id, "imdb", movie.imdb_response.total_results))
                from_response_id = cur.lastrowid

                for search in movie.imdb_response.results:
                    cur.execute("""INSERT INTO Searches (from_responses_id, title, year, imdb_id, poster_path) VALUES (?, ?, ?, ?, ?, ?)""", (from_response_id, search.title, search.year, search.imdb_id, search.poster_path))

            if movie.tmdb_response is not None:
                cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?)""", (from_movie_id, "tmdb", movie.tmdb_response.total_results))
                from_response_id = cur.lastrowid
                
                for search in movie.tmdb_response.results:
                    cur.execute("""INSERT INTO Searches (from_responses_id, title, year, tmdb_id, type, poster_path) VALUES (?, ?, ?, ?, ?, ?)""",
                                (from_response_id, search.title, search.year, search.release_date, search.original_title, search.original_language, search.imdb_id, search.tmdb_id, search.poster_path))


            self.conn.commit()

        except Exception as e:
            print(e)
            self.conn.rollback()
   

    def updateMovieToValid(self, movie_id, movie):
        if self.conn is None:
            return
        cur = self.conn.cursor()
        try:
            cur.execute("""UPDATE Movies SET title = ?, year = ?, imdb_id = ?, tmdb_id = ? WHERE id = ?""", (movie.title, movie.year, movie.imdb_id, movie.tmdb_id, movie_id))
            cur.execute("""DELETE FROM Searches WHERE from_responses_id IN (SELECT id FROM Responses WHERE from_movies_id = ?)""", (movie_id,))
            cur.execute("""DELETE FROM Responses WHERE from_movies_id = ?""", (movie_id,)) 
            self.conn.commit()
            return True

        except Exception as e:
            print(e)
            self.conn.rollback()
            return False
            
    def addTmdbMovieQueryToMovie(self, movie_id, movie):
        if self.conn is None:
            return
        try:
            movie = tmdbAPI.updateMovieWithMovieQuery(movie)
        except Exception as e:
            print(e)
            return False

        cur = self.conn.cursor()
        try:
            cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?)""", (movie_id, "tmdb", movie.tmdb_response.total_results))
            from_response_id = cur.lastrowid
        
            for search in movie.tmdb_response.results:
                cur.execute("""INSERT INTO Searches (from_responses_id, title, year, tmdb_id, type, poster_path) VALUES (?, ?, ?, ?, ?, ?)""",
                        (from_response_id, search.title, search.year, search.release_date, search.original_title, search.original_language, search.imdb_id, search.tmdb_id, search.poster_path))
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False
        
    def getMovie(self, movie_id):
        if self.conn is None:
            print("DB is not connected")
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM Movies WHERE id=?""", (movie_id,))
        movie = cur.fetchone()
        return movie

    def getAllMovies(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM Movies""")
        return cur.fetchall()

    def getMoviesWithNoImdbId(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM Movies WHERE imdb_id=''""")
        return cur.fetchall()

    def getMoviesWithInvalidSearches(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(""" SELECT Movies.id, Movies.title, Movies.year, Movies.imdb_id, Responses.error
                    FROM Movies INNER JOIN Responses 
                    ON Movies.id = Responses.from_movies_id
                    WHERE Responses.valid = 0
                    """)
        return cur.fetchall()
        
        
        
    def getMoviesWithValidSearches(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT Movies.id, Movies.title, Movies.year, Movies.imdb_id 
                    FROM Movies INNER JOIN Responses 
                    ON Movies.id = Responses.from_movies_id
                    WHERE Responses.valid = 1
                    """)
        return cur.fetchall()

        
    def getSearchesByMovieId(self, movie_id):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM Searches WHERE from_responses_id IN (SELECT id FROM Responses WHERE from_movies_id = ?)""", (movie_id,))
        return cur.fetchall()

        
    def getStats(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        stats = Stats()
        cur = self.conn.cursor()

        cur.execute("""SELECT COUNT(*) FROM Movies""")
        stats.total_movies    = cur.fetchone()[0]
        
        cur.execute("""SELECT COUNT(*) FROM Movies WHERE imdb_id=''""")
        stats.total_movies_missing_imdb_id = cur.fetchone()[0]

        cur.execute("""SELECT COUNT(*) FROM Movies 
                    INNER JOIN Responses ON Movies.id = Responses.from_movies_id
                    WHERE Responses.valid = 0 """) 
        stats.total_movies_with_invalid_searches = cur.fetchone()[0]
 
        cur.execute("""SELECT COUNT(*) FROM Responses""")
        stats.total_responses = cur.fetchone()[0]
        
        cur.execute("""SELECT COUNT(*) FROM Searches""")
        stats.total_searches = cur.fetchone()[0]

        cur.execute("""
                SELECT COUNT(*) FROM Movies
                INNER JOIN Responses ON Movies.id = Responses.from_movies_id
                WHERE Responses.valid = 1
                """)
        stats.total_reviewable_movies = cur.fetchone()[0]
        return stats

    def getMoviesWithConfidentMatch(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT Movies.id, Movies.title, Movies.year, Movies.imdb_id 
                    FROM Movies
                    INNER JOIN Responses ON Movies.id = Responses.from_movies_id
                    WHERE Responses.valid = 1 AND Responses.total_results = 1
                    """)
        return cur.fetchall()

    def autoMatchMovies(self):
        if self.conn is None:
            return
        movies = self.getMoviesWithConfidentMatch()
        for movie in movies:
            searches = self.getSearchesByMovieId(movie['id'])
            mi_movie = mi.Movie(movie['title'], movie['year'], searches[0]['imdb_id'])
            self.updateMovieToValid(movie['id'], mi_movie)
        return True

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def cleanReset(self):
        if self.conn is None:
            return
        try:
            self.build_tables()
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()