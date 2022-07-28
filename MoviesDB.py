import sqlite3

class MoviesDB:
    def __init__(self, db='data/movies.db'):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db)
            self.conn.row_factory = sqlite3.Row

        except Exception as e:
            print(e)
            self.conn.close()
            self.conn = None

        if self.conn is not None:
            self.createProjectTables()

    def __del__(self):
        if self.conn is not None:
            self.conn.close()


    def createProjectTables(self):
        if self.conn is None:
            return
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS Movies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year INTEGER,
            imdb_id TEXT,
            UNIQUE(name, year));
        """)
        cur.execute("""CREATE TABLE IF NOT EXISTS Responses (
            id INTEGER PRIMARY KEY,
            from_movies_id INTEGER NOT NULL,
            valid INTEGER NOT NULL,
            error TEXT,
            total_results INTEGER,
            FOREIGN KEY (from_movies_id) REFERENCES Movies(id));
        """)
        cur.execute(
            """CREATE TABLE IF NOT EXISTS Searches (
                id INTEGER PRIMARY KEY,
                from_responses_id INTEGER NOT NULL,  
                name TEXT,
                year INTEGER,
                imdb_id TEXT,
                type TEXT,
                poster TEXT,
                FOREIGN KEY (from_responses_id) REFERENCES Responses(id));
            """)
        self.conn.commit()

    def add_movie(self, movie):
        if self.conn is None:
            return
        cur = self.conn.cursor()
        try:

            cur.execute("""INSERT INTO Movies (name, year, imdb_id) VALUES (?, ?, ?)""", (movie.name, movie.year, movie.imdb_id))
            from_movie_id = cur.lastrowid

            #cur.execute("""SELECT id FROM Movies WHERE name = ? AND year = ?""", (movie.name, movie.year))
            #from_movie_id = cur.fetchone()[0]
            cur.execute("""INSERT INTO Responses (from_movies_id, valid, error, total_results) VALUES (?, ?, ?, ?)""", (from_movie_id, movie.imdb_response.valid, movie.imdb_response.error, movie.imdb_response.total_results))
            from_response_id = cur.lastrowid

            #cur.execute("""SELECT id FROM Responses WHERE from_movies_id = ?""", (from_movie_id,))
            #response_id = cur.fetchone()[0]
            for search in movie.imdb_response.results:
                cur.execute("""INSERT INTO Searches (from_responses_id, name, year, imdb_id, type, poster) VALUES (?, ?, ?, ?, ?, ?)""", (from_response_id, search.title, search.year, search.imdb_id, search.type, search.poster))

            self.conn.commit()

        except Exception as e:
            print(e)
            self.conn.rollback()

    def getMoviesWithNoImdbId(self):
        if self.conn is None:
            return
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM Movies WHERE imdb_id=''""")
        return cur.fetchall()