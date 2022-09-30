import sqlite3
import MovieInterface as mi 
import TmdbAPI
import ImdbAPI

class Stats:
    def __init__(self):
        self.total_movies = 0 
        self.total_movies_missing_imdb_id = 0
        self.total_movies_missing_tmdb_id = 0
        self.total_movies_missing_both_ids = 0
        self.total_reviewable_movies = 0 
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
            self.loadOriginalData()

    
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
                cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?)""", (from_movie_id, "imdb", movie.imdb_response.total_results))
                from_response_id = cur.lastrowid

                for search in movie.imdb_response.results:
                    cur.execute("""INSERT INTO Searches (from_responses_id, title, year, imdb_id, poster_path) VALUES (?, ?, ?, ?, ?)""", (from_response_id, search.title, search.year, search.imdb_id, search.poster_path))

            if movie.tmdb_response is not None:
                cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?)""", (from_movie_id, "tmdb", movie.tmdb_response.total_results))
                from_response_id = cur.lastrowid
                
                for search in movie.tmdb_response.results:
                    cur.execute("""INSERT INTO Searches (from_responses_id, title, year, tmdb_id,
                                original_title, release_date, original_language, poster_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (from_response_id, search.title, search.year, search.tmdb_id,
                                 search.original_title, search.release_date, search.original_language, search.poster_path))


            self.conn.commit()

        except Exception as e:
            print(e)
            self.conn.rollback()
   

    def updateMovieToValid(self, movie_id, movie):
        if self.conn is None:
            return
        cur = self.conn.cursor()
        try:
            print(movie.title, "  ", movie.imdb_id, "  ", movie.tmdb_id)
            cur.execute("""UPDATE Movies SET title = ?, year = ?, imdb_id = ?, tmdb_id = ? WHERE id = ?""", (movie.title, movie.year, movie.imdb_id, movie.tmdb_id, movie_id))
            cur.execute("""DELETE FROM Searches WHERE from_responses_id IN (SELECT id FROM Responses WHERE from_movies_id = ?)""", (movie_id,))
            cur.execute("""DELETE FROM Responses WHERE from_movies_id = ?""", (movie_id,)) 
            self.conn.commit()
            return True

        except Exception as e:
            print(e)
            self.conn.rollback()
            return False
            
    def addTmdbMovieQueryToMovie(self, movie_id):
        if self.conn is None:
            return
        try:
            movie = mi.Movie.from_query(self.getMovie(movie_id))
            movie = TmdbAPI.updateMovieWithMovieQuery(movie)
            print("now I have stuff, ", movie.tmdb_response.total_results)
        except Exception as e:
            print(e)
            return False

        cur = self.conn.cursor()
        try:
            cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?)""", (movie_id, "tmdb", movie.tmdb_response.total_results))
            from_response_id = cur.lastrowid
        
            for search in movie.tmdb_response.results:
                print(search.title)
                cur.execute("""INSERT INTO Searches (from_responses_id, title, year, release_date, original_title, original_language, tmdb_id, poster_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (from_response_id, search.title, search.year, search.release_date, search.original_title, search.original_language, search.tmdb_id, search.poster_path))
            self.conn.commit()
            print("success")
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False
       
       
    def query(self, sql_string, *args):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(sql_string, args) 
        return cur.fetchall()

    # def make_query(self, sql_string):
    #     def query_wrapper(self, *args):
    #         return self.query(self, sql_string, *args)
    #     return query_wrapper 

 
    def getMovie(self, movie_id):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM Movies WHERE id=?""", (movie_id,))
        return cur.fetchall()

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
        cur.execute("""SELECT Movies.* FROM Movies WHERE imdb_id=''""")
        return cur.fetchall()

    def getInvalidMovies(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(""" SELECT * FROM Movies 
                    LEFT OUTER JOIN Responses
                    ON Movies.id = Responses.from_movies_id
                    WHERE Responses.from_movies_id IS NULL
                    AND Movies.imdb_id = ''
                    AND Movies.tmdb_id = ''
                    """)
        return cur.fetchall()

    def getValidMovies(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(""" SELECT * FROM Movies 
                    WHERE Movies.imdb_id != ''
                    OR Movies.tmdb_id != ''
                    """)
        return cur.fetchall()
        
        
        
    def getMoviesWithValidSearches(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT * 
                    FROM Movies INNER JOIN Responses 
                    ON Movies.id = Responses.from_movies_id
                    ORDER BY Movies.title
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
        cur = self.conn.cursor()

        stats = Stats()

        cur.execute("""SELECT COUNT(*) FROM Movies""")
        stats.total_movies    = cur.fetchone()[0]
        
        cur.execute("""SELECT COUNT(*) FROM Movies WHERE imdb_id='' """)
        stats.total_movies_missing_imdb_id = cur.fetchone()[0]

        cur.execute("""SELECT COUNT(*) FROM Movies WHERE tmdb_id='' """)
        stats.total_movies_missing_tmdb_id = cur.fetchone()[0]

        cur.execute("""SELECT COUNT(*) FROM Movies 
                    WHERE imdb_id='' AND tmdb_id='' """)
        stats.total_movies_missing_both_ids = cur.fetchone()[0]

        cur.execute("""SELECT COUNT(*) FROM Responses""")
        stats.total_responses = cur.fetchone()[0]
        
        cur.execute("""SELECT COUNT(*) FROM Searches""")
        stats.total_searches = cur.fetchone()[0]

        cur.execute("""
                SELECT COUNT(*) FROM Movies
                INNER JOIN Responses ON Movies.id = Responses.from_movies_id
                """)
        stats.total_reviewable_movies = cur.fetchone()[0]
        return stats

    def getMoviesWithConfidentMatch(self):
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()

        cur.execute("""
            SELECT Movies.id, Searches.title, Movies.year, Searches.imdb_id, Searches.tmdb_id  
            FROM Movies
            INNER JOIN Responses ON 
            Movies.id = Responses.from_movies_id
            INNER JOIN Searches ON 
            Responses.id = Searches.from_responses_id
            WHERE UPPER(Movies.title) = UPPER(Searches.title)
            AND Movies.year = Searches.year
                    """)
        return cur.fetchall()

    def autoMatchMovies(self):
        if self.conn is None:
            return False

        movies = self.getMoviesWithConfidentMatch()
        for movie in movies:
            #searches = self.getSearchesByMovieId(movie['id'])
            if (movie['imdb_id'] != '' or movie['tmdb_id'] != ''):
                mi_movie = mi.Movie(movie['title'], movie['year'], movie['imdb_id'], movie['tmdb_id'])
                self.updateMovieToValid(movie['id'], mi_movie)
            else:
                return False
        return True

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def hardDBReset(self):
        if self.conn is None:
            return
        try:
            self.createProjectTables()
            self.loadOriginalData()
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def loadOriginalData(self):
        self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_1_responded.json"))