import MovieInterface as mi
import requests
import json
from datetime import datetime

URL     = "https://api.themoviedb.org/3/search/movie/"
API_KEY = "4f8774170a53865294832e845594aee7"
AUTH    = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0Zjg3NzQxNzBhNTM4NjUyOTQ4MzJlODQ1NTk0YWVlNyIsInN1YiI6IjYyZTg3NjkxMWJmMjY2MDA1YTYxNTMwNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.J5fKMkgxJOZ40VqfA1tCnjfVDNcAYEGVIvXSRgfkqVU"
POSTER_PREFIX = "https://image.tmdb.org/t/p/w92"


class TmdbResponse:
    def __init__(self, response):
            self.page = int(response["page"])
            self.results = [TmdbSearchResult(x) for x in  response["results"]]
            self.total_pages = int(response["total_pages"])
            self.total_results = int(response["total_results"])
    def __str__(self):
        return f"{self.results}"
    def __repr__(self):
        return f"{self.results}"

        
class TmdbSearchResult:
    def __init__(self, result):
        self.title = result["title"]
        self.original_title = result["original_title"]
        self.release_date = result["release_date"]
        self.year = datetime.strptime(self.release_date, "%Y-%m-%d").year
        self.original_language = result["original_language"]
        self.tmdb_id = result["id"]
        self.poster_path = result["poster_path"]
    def __str__(self):
        return f"{self.title} ({self.year})"
    def __repr__(self):
        return f"{self.title} ({self.year})"

def makeQueryString(req):
    return {"api_key":API_KEY, 
            "query":req.title,
            "year":req.year, 
            "language":"en-US", 
            "include_adult":True} 
    

def updateMovieWithMovieQuery(movie):
        querystring = makeQueryString(movie)
        response = requests.get(URL, params=querystring)
        movie.tmdb_response = TmdbResponse(response.json()) 
        return movie

