
import requests
from json import JSONDecoder
from datetime import datetime
from io import StringIO
from MovieInterface import Movie

URL = "https://movie-database-alternative.p.rapidapi.com/"
HEADERS = {
	"X-RapidAPI-Key": "2afd199a52msh50040cd85d8d844p17f065jsnc8fd0db39230",
	"X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
}

def makeQueryString(req):
    return {"s":req.name,"y":req.year,"r":"json"} 
    

def request(movie):
        querystring = makeQueryString(movie)
        response = requests.request("GET", URL, HEADERS, params=querystring)
        return response.text

        
class ImdbValidSearchResult:
    def __init__(self, result):
        self.title = result["Title"]
        self.year = result["Year"]
        self.imdb_id = result["imdbID"]
        self.type = result["Type"]
        self.poster_path = result["Poster"]

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
        if (resp.valid):
            movies.append(Movie(object['name'], object['year'], imdb_id="", imdb_response=resp))
        else:
            movies.append(Movie(object['name'], object['year'], imdb_id=""))
    return movies
    