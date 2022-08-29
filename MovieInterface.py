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
        print("made from tuple")
        print ("imdb_id: ")
        print(form['imdb_id'])
        print ("tmdb_id: ")
        print(form['tmdb_id'])
        tmdb_id = form['tmdb_id'] if form['tmdb_id'] != None else ""
        imdb_id = form['imdb_id'] if form['imdb_id'] != None else ""
        return cls(form['title'], form['year'], imdb_id, tmdb_id)

    def isFullyDefined(self) -> bool:
        is_title = self.title is not None and self.title != ""
        is_year = self.year is not None and self.year != ""
        is_imdb_id = self.imdb_id is not None and self.imdb_id != ""
        is_tmdb_id = self.tmdb_id is not None and self.tmdb_id != ""


        return self.title and self.year and (self.imdb_id or self.tmdb_id) 
        
    def __str__(self):
        return f"{self.title} ({self.year})"
    def __repr__(self):
        return f"{self.title} ({self.year})"
