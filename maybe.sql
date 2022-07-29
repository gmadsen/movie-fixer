-- SQLite
    SELECT * 
    FROM Searches 
    WHERE 



    JOIN Responses ON Movies.id = Responses.from_movies_id 
    JOIN Searches ON Responses.id = Searches.from_responses_id
    WHERE Responses.valid = 1