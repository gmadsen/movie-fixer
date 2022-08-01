import json
from json import JSONDecoder
from io import StringIO

class Movie:
    def __init__(self, title, year, imdb_id, imdb_response=None):
        self.title = title 
        self.year = year
        self.imdb_id = imdb_id 
        self.imdb_response = imdb_response 

    @classmethod
    def from_tuple(cls, form):
        return cls(form['title'], form['year'], form['imdb_id'])

    def isFullyDefined(self) -> bool:
        return self.title and self.year and self.imdb_id 
        
    def __str__(self):
        if self.imdb_response is None:
            return "Movie: {} ({})".format(self.title, self.year)
        else:
            return "Movie: {} ({}) \n\t Searches: {}".format(self.title, self.year, self.imdb_response)

    def __repr__(self):
        return f"{self.title} ({self.year})"

class ImdbValidSearchResult:
    def __init__(self, result):
        self.title = result["Title"]
        self.year = result["Year"]
        self.imdb_id = result["imdbID"]
        self.type = result["Type"]
        self.poster = result["Poster"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    def __repr__(self):
        return f"{self.title} ({self.year})"

    def __eq__(self, other):
        return self.imdb_id == other.imdb_id

class ImdbResponse:
    def __init__(self, response):
        if (response == None):
            self.valid = False
            self.error = "No response from IMDB"
            self.results = []
            self.total_results = 0
        if (response["Response"] == "False"):
            self.valid = False
            self.error = response["Error"]
            self.results = []
            self.total_results = 0
        elif (response["Response"] == "True"):
            self.valid = True
            self.error = None
            self.results = [ImdbValidSearchResult(x) for x in  response["Search"]]
            self.total_results = int(response["totalResults"])
    def __str__(self):
        if (self.valid):
            return f"{self.results}"
        else:
            return f"Invalid response. {self.error}"
    def __repr__(self):
        if (self.valid):
            return f"{self.results}"
        else:
            return f"Invalid response. {self.error}"


def convertAggregateImdbResponseFileToMovies(aggregate_imdb_response_file):
    dumb_json_data = JSONDecoder().decode(open(aggregate_imdb_response_file).read())
    movies = []
    decoded_data = [x[1] for x in dumb_json_data.items()]

    for object in decoded_data:
        resp =  ImdbResponse(json.load(StringIO(object['response'])))
        movies.append(Movie(object['name'], object['year'], imdb_id="", imdb_response=resp))
    return movies
    