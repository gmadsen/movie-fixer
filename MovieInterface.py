import json
from json import JSONDecoder
from io import StringIO
from datetime import datetime

class Movie:
    def __init__(self, title, year, imdb_id="", tmdb_id="", imdb_response=None, tmdb_response=None):
        self.title = title 
        self.year = year
        self.imdb_id = imdb_id if imdb_id is not None else "" 
        self.tmdb_id = tmdb_id if tmdb_id is not None else ""
        self.imdb_response = imdb_response 
        self.tmdb_response = tmdb_response 

    @classmethod
    def from_tuple(cls, form):
        tmdb_id = form['tmdb_id'] if form['tmdb_id'] is not None  else ""
        imdb_id = form['imdb_id'] if form['imdb_id'] is not None  else ""
        return cls(form['title'], form['year'], imdb_id, tmdb_id)

    def is_null_value(self, value):
        return value is None or value == "" or value == "None"

    def isFullyDefined(self) -> bool:
        is_title = not self.is_null_value(self.title) 
        is_year = not self.is_null_value(self.year) 
        is_imdb_id = not self.is_null_value(self.imdb_id) 
        is_tmdb_id = not self.is_null_value(self.tmdb_id) 
        print(f"is_title: {is_title}, is_year: {is_year}, is_imdb_id: {is_imdb_id}, is_tmdb_id: {is_tmdb_id}")
        print(f"imdb_id: {self.imdb_id}, tmdb_id: {self.tmdb_id}")
        print("tmdb type: ", type(self.tmdb_id), "is None: ", self.tmdb_id is None, "is empty: ", self.tmdb_id == "")

        return is_title and is_year and (is_imdb_id or is_tmdb_id) 
        
    def __str__(self):
        return f"{self.title} ({self.year})"
    def __repr__(self):
        return f"{self.title} ({self.year})"
