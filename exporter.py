"""module to export database contents to a format websites like"""
from dataclasses import dataclass
import csv
import tempfile

def make_temp_csv_movie_list(movies, export_type):
    """construct a temporty csv file from a given list of movies and a format type"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as csvfile:
        fields = export_type.make_empty().__dict__.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for movie in movies:
            try:
                export_obj = export_type.from_movie_query(movie)
                writer.writerow(vars(export_obj))
            except Exception as e:
                print("Error in writing row: ", e)
    return csvfile

@dataclass
class Simkl:
    def __init__(self, title, year, imdb_id, tmdb_id):
        self.SIMKL_ID = ''
        self.Title = title
        self.Type = 'movie'
        self.Year = year
        self.Watchlist = 'false'
        self.LastEpWatched = ''
        self.WatchedDate = ''
        self.Rating = ''
        self.Memo = ''
        self.TVDB = ''
        self.TMDB = tmdb_id
        self.IMDB = imdb_id
    @classmethod
    def make_empty(cls):
        """make an empty struct"""
        return cls('', '', '', '')
    @classmethod
    def from_movie_query(cls, movie):
        """make a valid Simkl format type from movie_db movie type"""
        return cls(movie['title'], movie['year'], movie['imdb_id'], movie['tmdb_id'])
