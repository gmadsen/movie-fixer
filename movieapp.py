import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import MovieInteface as mi
import MoviesDB as mdb



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'


def get_movie(movie_id):
    db = mdb.MoviesDB()
    movie = db.getMovie(movie_id) 
    db.close()
    if movie is None:
        abort(404)
    return movie 

def get_searches_by_movie_id(movie_id):
    db = mdb.MoviesDB()
    searches = db.getSearchesByMovieId(movie_id) 
    db.close()
    if searches is None:
        abort(404)
    return searches 

@app.route('/')
def index():
    db = mdb.MoviesDB()
    movies = db.getMovies()
    db.close()
    return render_template('index.html', movies=movies) 

@app.route('/open_searches')
def open_searches():
    db = mdb.MoviesDB()
    movies = db.getMoviesWithValidSearches()
    db.close()
    return render_template('searches.html', searches=movies)


@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie = get_movie(movie_id)
    return render_template('movie.html', movie=movie)

@app.route('/fix/<int:movie_id>', methods=['GET', 'POST'])
def fix(movie_id):
    movie = get_movie(movie_id)
    searches = get_searches_by_movie_id(movie_id)
    if request.method == 'POST':
        new_title = request.form['title']
        new_year = request.form['year']
        new_imdb_id = request.form['imdb_id']
        if not new_title or not new_year or not new_imdb_id:
            flash('Please enter a title, year, and imdb_id ', 'danger')
        else:
            db = mdb.MoviesDB()
            db.update_movie(movie_id, mi.Movie(new_title, new_year, new_imdb_id))
            db.close()
            flash('Movie updated successfully', 'success')
            flash('"{}" associated searches were deleted successfully'.format(movie['title']), 'success')
            return redirect(url_for('open_searches'))

    return render_template('fix.html', movie=movie, searches=searches)

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    db = mdb.MoviesDB()
    stats = db.getStats()
    print("hi,", stats)
    db.close()
    return render_template('statistics.html', stats=stats)