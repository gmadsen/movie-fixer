""" interface between movie objects and database queries"""
class Movie:
    """
        main python movie object
        will probably be replaced when switching to sqlalchemy
    """
    def __init__(self, title, year, imdb_id="", tmdb_id="", imdb_response=None, tmdb_response=None):
        self.title = title
        self.year = year
        self.imdb_id = imdb_id if imdb_id is not None else ""
        self.tmdb_id = tmdb_id if tmdb_id is not None else ""
        self.imdb_response = imdb_response
        self.tmdb_response = tmdb_response

    @classmethod
    def from_query(cls, row_list):
        """constructs movie from a sqlite3 query"""
        form = row_list[0]
        tmdb_id = form['tmdb_id'] if form['tmdb_id'] is not None else ""
        imdb_id = form['imdb_id'] if form['imdb_id'] is not None else ""
        return cls(form['title'], form['year'], imdb_id, tmdb_id)

    @classmethod
    def from_form(cls, form):
        """ construct movie from flask jinja2 form"""
        tmdb_id = form['tmdb_id'] if form['tmdb_id'] is not None else ""
        imdb_id = form['imdb_id'] if form['imdb_id'] is not None else ""
        return cls(form['title'], form['year'], imdb_id, tmdb_id)

    def is_null_value(self, value):
        """ is value ill defined"""
        return value is None or value == "" or value == "None"

    def is_fully_defined(self) -> bool:
        """is movie object fully defined ,i.e. title,year, atleast one db id"""
        is_title = not self.is_null_value(self.title)
        is_year = not self.is_null_value(self.year)
        is_imdb_id = not self.is_null_value(self.imdb_id)
        is_tmdb_id = not self.is_null_value(self.tmdb_id)

        return is_title and is_year and (is_imdb_id or is_tmdb_id)

    def __str__(self):
        return f"{self.title} ({self.year})"

    def __repr__(self):
        return f"{self.title} ({self.year})"
