        CREATE TABLE IF NOT EXISTS Movies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year INTEGER,
            imdb_id TEXT,
            UNIQUE(name, year)
        );

        CREATE TABLE IF NOT EXISTS Responses (
            id INTEGER PRIMARY KEY,
            from_movies_id INTEGER NOT NULL,
            valid INTEGER NOT NULL,
            error TEXT,
            total_results INTEGER,
            FOREIGN KEY (from_movies_id) REFERENCES Movies(id)
        );

        CREATE TABLE IF NOT EXISTS Searches (
            id INTEGER PRIMARY KEY,
            from_responses_id INTEGER NOT NULL,  
            name TEXT,
            year INTEGER,
            imdb_id TEXT,
            type TEXT,
            poster TEXT,
            FOREIGN KEY (from_responses_id) REFERENCES Responses(id)
        );