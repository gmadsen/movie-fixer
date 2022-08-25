import json
from json import JSONDecoder
from io import StringIO
from datetime import datetime

class Movie:
    def __init__(self, title, year, imdb_id=None, tmdb_id=None, imdb_response=None, tmdb_response=None):
        self.title = title 
        self.year = year
        self.imdb_id = imdb_id 
        self.tmdb_id = tmdb_id
        self.imdb_response = imdb_response 
        self.tmdb_response = tmdb_response 

    @classmethod
    def from_tuple(cls, form):
        return cls(form['title'], form['year'], imdb_id=form['imdb_id'], tmdb_id=form['tmdb_id'])

    def isFullyDefined(self) -> bool:
        return self.title and self.year and (self.imdb_id or self.tmdb_id) 
        
    def __str__(self):
        return f"{self.title} ({self.year})"
    def __repr__(self):
        return f"{self.title} ({self.year})"
