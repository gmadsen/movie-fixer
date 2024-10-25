"""module to interface with public imdp api"""
from dataclasses import dataclass
import json
from io import StringIO
import requests
from .movie_interface import Movie

URL = "https://movie-database-alternative.p.rapidapi.com/"
HEADERS = {
    "X-RapidAPI-Key": "NEED TO ADD",
    "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
}


def make_query_string(req):
    """make query string"""
    return {"s": req.name, "y": req.year, "r": "json"}


def request(movie):
    """attempt request to api"""
    querystring = make_query_string(movie)
    response = requests.request("GET", url=URL, headers=HEADERS, params=querystring)
    return response.text

@dataclass
class ImdbValidSearchResult:
    """api get result as python data struct"""
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
        if response is None:
            self.valid = False
            self.error = "No response from IMDB"
            self.results = []
            self.total_results = 0
        if response["Response"] == "False":
            self.valid = False
            self.error = response["Error"]
            self.results = []
            self.total_results = 0
        elif response["Response"] == "True":
            self.valid = True
            self.error = None
            self.results = [ImdbValidSearchResult(
                x) for x in response["Search"]]
            self.total_results = int(response["totalResults"])

    def __str__(self):
        if self.valid:
            return f"{self.results}"
        return f"Invalid response. {self.error}"

    def __repr__(self):
        if self.valid:
            return f"{self.results}"
        return f"Invalid response. {self.error}"


def convert_aggregate_imdb_response_file_to_movies(aggregate_imdb_response_file):
    """convert old data with dumb function"""
    dumb_json_data = json.JSONDecoder().decode(
        open(aggregate_imdb_response_file).read())
    movies = []
    decoded_data = [x[1] for x in dumb_json_data.items()]

    for datum in decoded_data:
        resp = ImdbResponse(json.load(StringIO(datum['response'])))
        if resp.valid:
            movies.append(
                Movie(datum['name'], datum['year'], imdb_id="", imdb_response=resp))
        else:
            movies.append(Movie(datum['name'], datum['year'], imdb_id=""))
    return movies
