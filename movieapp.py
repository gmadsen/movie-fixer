import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import MovieInterface as mi
import MoviesDB as mdb



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'


def safe(func):
    def db_call(*args, **kwargs):
        db = mdb.MoviesDB()
        thing = func(db, *args, **kwargs)
        db.close()
        if thing is None:
            abort(404)
        return thing
    return db_call 

get_movie = safe(mdb.MoviesDB.getMovie)
get_all_movies = safe(mdb.MoviesDB.getAllMovies)
get_searches_by_movie_id = safe(mdb.MoviesDB.getSearchesByMovieId)
get_movies_with_valid_searches = safe(mdb.MoviesDB.getMoviesWithValidSearches)
get_movies_with_invalid_searches = safe(mdb.MoviesDB.getMoviesWithInvalidSearches)
get_stats = safe(mdb.MoviesDB.getStats)
update_movie = safe(mdb.MoviesDB.updateMovie)
auto_match_movies = safe(mdb.MoviesDB.autoMatchMovies)


## Routes ##
@app.route('/')
def index():
    return render_template('index.html', movies=get_all_movies()) 

@app.route('/review')
def review():
    return render_template('review.html', movies=get_movies_with_valid_searches())

@app.route('/invalid')
def invalid():
    return render_template('invalid.html', movies_with_errors=get_movies_with_invalid_searches())

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    return render_template('movie.html', movie=get_movie(movie_id))

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    if request.method == 'POST':
        print("we got a post")
        print(request.form)
        auto_match_movies()
        return redirect(url_for('stats'))
    return render_template('statistics.html', stats=get_stats())

@app.route('/fix/<int:movie_id>', methods=['GET', 'POST'])
def fix(movie_id):
    if request.method == 'POST':
        new_movie = mi.Movie.from_tuple(request.form)
        if not new_movie.isFullyDefined():
            flash('Please enter a title, year, and imdb_id ', 'danger')
        else:
            update_movie(movie_id, new_movie) 
            flash('Movie updated successfully', 'success')
            # seems a waste, but im not sure of a better way to get next movie id
            next_movie = get_movies_with_valid_searches()[0]
            return redirect(url_for('fix', movie_id=next_movie['id']))
            # return redirect(url_for('review'))

    return render_template('fix.html', movie=get_movie(movie_id), searches=get_searches_by_movie_id(movie_id))

@app.route('/search/<int:movie_id>', methods=['GET', 'POST'])
def search(movie_id):
    if request.method == 'POST':
        new_movie = mi.Movie.from_tuple(request.form)
        if not new_movie.isFullyDefined():
            flash('Please enter a title, year, and an id ', 'danger')
        else:
            update_movie(movie_id, new_movie) 
            flash('Movie updated successfully', 'success')
            return redirect(url_for('invalid'))
    ## temp test ##
    searches = [{'title': 'The Bandit', 'year': '1996', 'tmdb_id': '26900', 'poster_path': 'https://image.tmdb.org/t/p/w92/44KTRoayojxpzti2okBZGKmjEGM.jpg'}]
    return render_template('search.html', movie=get_movie(movie_id), searches=searches)