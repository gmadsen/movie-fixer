def make_temp_csv_movie_list(movies, ExportType):
    import csv
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as csvfile:
        fields = ExportType.make_empty().__dict__.keys()
        #print(fields)
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for movie in movies:
            try:
                export_obj = ExportType.from_movie_query(movie)
                #print(vars(export_obj))
                writer.writerow(vars(export_obj))
            except Exception as e:
                print("Error in writing row: ", e)
    return csvfile

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
        return cls('', '', '', '')
    @classmethod
    def from_movie_query(cls, movie):
        return cls(movie['title'], movie['year'], movie['imdb_id'], movie['tmdb_id'])