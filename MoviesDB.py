import sqlite3
import io
import MovieInterface as mi 
import TmdbAPI
import ImdbAPI
import BackendCaller as bc

class MoviesDB:
    def __init__(self, db='data/movies.db', build_tables=False):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db)
        except Exception as e:
            print(e)
            self.conn.close()
            self.conn = None
        else:
            if self.conn is not None and build_tables:
                self.createProjectTables()
                self.loadOriginalData()
    def __del__(self):
        if self.conn is not None:
            self.conn.close()    
###########################################################################

########  Internal State and Maintenance ##################################

    def createTransactionBackup(self):
        if self.conn is None:
            return
        try:
            with io.open('data/backupdatabase_dump.sql', 'w') as p: 
                for line in self.conn.iterdump(): 
                    p.write('%s\n' % line)
            print(' Backup performed successfully!')
            print(' Data Saved as backupdatabase_dump.sql')
        except Exception as e: 
            print(e, ' Backup Failed!')

    def createProjectTables(self):
        if self.conn is None:
            return
        with open('moviedb_schema.sql') as f:
            self.conn.executescript(f.read()) 
        self.conn.commit()

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
        self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_2_responded.json"))
        self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_3_responded.json"))
        self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_4_responded.json"))
        self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_5_responded.json"))
        self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_6_responded.json"))
###########################################################################
###########################################################################
        

        
###########################################################################
##################### DB data  Functions ##################################

    def query(self, sql_string, *args):
        ''' Generic query function that takes a sql string and a tuple of arguments '''
        if self.conn is None:
            return
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(sql_string, args) 
        return cur.fetchall()

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

    def removeAssociatedSearches(self, movie_id):
        if self.conn is None:
            return
        cur = self.conn.cursor()
        try:
            cur.execute("""DELETE FROM Searches WHERE from_responses_id IN (SELECT id FROM Responses WHERE from_movies_id = ?)""", (movie_id,))
            cur.execute("""DELETE FROM Responses WHERE from_movies_id = ?""", (movie_id,)) 
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False


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
   


            
    def addTmdbMovieQueryToMovie(self, movie_id):
        if self.conn is None:
            return
        try:
            movie = mi.Movie.from_query(self.query(bc.GET_MOVIE_BY_ID, movie_id)) #    getMovie(movie_id))
            movie = TmdbAPI.updateMovieWithMovieQuery(movie)
            print("now I have stuff, ", movie.tmdb_response.total_results)
        except Exception as e:
            print(e)
            return False
# TODO this needs to all be under the same transaction, which fallback

        cur = self.conn.cursor()
        try:
            cur.execute("""INSERT INTO Responses (from_movies_id, source, total_results) VALUES (?, ?, ?)""", (movie_id, "tmdb", movie.tmdb_response.total_results))
            from_response_id = cur.lastrowid
        
            for search in movie.tmdb_response.results:
                cur.execute("""INSERT INTO Searches (from_responses_id, title, year, release_date, original_title, original_language, tmdb_id, poster_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (from_response_id, search.title, search.year, search.release_date, search.original_title, search.original_language, search.tmdb_id, search.poster_path))
            self.conn.commit()
            print("success")
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False
      
      
    def autoMatchMovies(self):
        ''' Query the database for all movies that do not have a valid imdb_id and tmdb_id, and if they 
            have a search result that matches the title and year, then update the movie with the search result
            and throw away the other search results.
        '''
        if self.conn is None:
            return False
        movies = self.query(bc.GET_MOVIES_WITH_CONFIDENT_MATCH)
        print("i am trying to auto match")
        print(len(movies), "len of movies")
        for movie in movies:
            if (movie['imdb_id'] != '' or movie['tmdb_id'] != ''):
                mi_movie = mi.Movie(movie['title'], movie['year'], movie['imdb_id'], movie['tmdb_id'])
                self.updateMovieToValid(movie['id'], mi_movie)
            else:
                return False
        return True
       