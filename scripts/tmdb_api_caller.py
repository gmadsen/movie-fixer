import MovieInterface as mi
import requests
import json

URL     = "https://api.themoviedb.org/3/search/movie/"
API_KEY = "4f8774170a53865294832e845594aee7"
AUTH    = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0Zjg3NzQxNzBhNTM4NjUyOTQ4MzJlODQ1NTk0YWVlNyIsInN1YiI6IjYyZTg3NjkxMWJmMjY2MDA1YTYxNTMwNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.J5fKMkgxJOZ40VqfA1tCnjfVDNcAYEGVIvXSRgfkqVU"

def makeQueryString(req):
    return {"api_key":API_KEY, 
            "query":req.title,
            "year":req.year, 
            "language":"en-US", 
            "include_adult":True} 
    

def request(movie):
        querystring = makeQueryString(movie)
        response = requests.get(URL, params=querystring)
        return response