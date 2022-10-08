""" Module of primary interface to movie database """
from pathlib import Path
import sqlite3
import io
from . import movie_interface as mi
from . import tmdb_api
from . import imdb_api
from . sql import readers as sqlr

PATH = Path(__file__).parent
class MovieDB:
    """ Primary class to construct, query, and modify movie database """
    def __init__(self, database=PATH/'data/movies.db', build_tables=False, debug_data=None):
        self.conn = None
        try:
            self.conn = sqlite3.connect(database)
        except Exception as booboo:
            print(booboo)
            self.conn.close()
            self.conn = None
        else:
            if self.conn is not None and build_tables:
                self.create_project_tables()
                if debug_data is not None:
                    self.load_debug_data(debug_data)
                else:
                    self.load_original_data()
    def __del__(self):
        if self.conn is not None:
            self.conn.close()
###########################################################################

########  Internal State and Maintenance ##################################

    def create_transaction_backup(self):
        """ make a sql cmd complete list as backup """
        if self.conn is None:
            return
        try:
            with io.open(PATH/'data/backupdatabase_dump.sql', 'w') as db_dump:
                for line in self.conn.iterdump():
                    db_dump.write(f'{line}\n')
            print(' Backup performed successfully!')
            print(' Data Saved as backupdatabase_dump.sql')
        except Exception as e:
            print(e, ' Backup Failed!')

    def create_project_tables(self):
        """ make tables """
        if self.conn is None:
            return
        with open(PATH/'moviedb_schema.sql') as dbfile:
            self.conn.executescript(dbfile.read())
        self.conn.commit()

    def close(self):
        """close database"""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def hard_db_reset(self):
        """ reset all data and reload tables"""
        if self.conn is None:
            return
        try:
            self.create_project_tables()
            self.load_original_data()
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def load_original_data(self):
        """load the original data in /data"""
        self.add_movies(imdb_api.convert_aggregate_imdb_response_file_to_movies(
            PATH/"data/top_1000_part_1_responded.json"
            )
        )
        # self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_2_responded.json"))
        # self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_3_responded.json"))
        # self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_4_responded.json"))
        # self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_5_responded.json"))
        # self.addMovies(ImdbAPI.convertAggregateImdbResponseFileToMovies("data/top_1000_part_6_responded.json"))

    def load_debug_data(self, path):
        """load the original data in /data"""
        self.add_movies(imdb_api.convert_aggregate_imdb_response_file_to_movies(path))
###########################################################################
###########################################################################



###########################################################################
##################### DB data  Functions ##################################

    def query(self, sql_string, *args):
        ''' Generic query function that takes a sql string and a tuple of arguments '''
        if self.conn is None:
            raise Exception("no connection to database")
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()

        try:
            cur.execute(sql_string, args)
            return cur.fetchall()
        except Exception as e:
            raise SyntaxError("bad query string") from e


    def update_movie_to_valid(self, movie_id, movie):
        """ attempt to update movie in database with user data"""
        if self.conn is None:
            raise Exception("no connection to database")
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

    def remove_associated_searches(self, movie_id):
        """remove attached search requests in database given movie_id"""
        if self.conn is None:
            raise Exception("no connection to database")
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


    def add_movies(self, movies):
        """add a list of movies to database"""
        if self.conn is None:
            raise Exception("no connection to database")
        for movie in movies:
            self.add_movie(movie)

    def add_movie(self, movie):
        """
        Movie is a Movie object from MovieInterface.py

        """
        if self.conn is None:
            raise Exception("no connection to database")
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
            print(e, f"error adding movie:{movie}")
            self.conn.rollback()




    def add_tmdb_movie_query_to_movie(self, movie_id):
        if self.conn is None:
            raise Exception("no connection to database")
        try:
            movie = mi.Movie.from_query(self.query(st.GET_MOVIE_BY_ID, movie_id)) #    getMovie(movie_id))
            movie = tmdb_api.update_movie_with_api_call(movie)
            print("now I have stuff, ", movie.tmdb_response.total_results)
        except Exception as e:
            print(e)
            return False
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


    def auto_match_movies(self):
        ''' Query the database for all movies that do not have a valid imdb_id and tmdb_id, and if they
            have a search result that matches the title and year, then update the movie with the search result
            and throw away the other search results.
        '''
        if self.conn is None:
            raise Exception("no connection to database")
        movies = self.query(st.GET_MOVIES_WITH_CONFIDENT_MATCH)
        for movie in movies:
            if (movie['imdb_id'] != '' or movie['tmdb_id'] != ''):
                mi_movie = mi.Movie(movie['title'], movie['year'], movie['imdb_id'], movie['tmdb_id'])
                self.update_movie_to_valid(movie['id'], mi_movie)
            else:
                return False
        return True

