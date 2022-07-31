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

def get_all_movies():
    db = mdb.MoviesDB()
    movies = db.getAllMovies() 
    db.close()
    if movies is None:
        abort(404)
    return movies

def get_searches_by_movie_id(movie_id):
    db = mdb.MoviesDB()
    searches = db.getSearchesByMovieId(movie_id) 
    db.close()
    if searches is None:
        abort(404)
    return searches 

def get_movies_with_valid_searches():
    db = mdb.MoviesDB()
    movies = db.getMoviesWithValidSearches() 
    db.close()
    if movies is None:
        abort(404)
    return movies

def get_stats():
    db = mdb.MoviesDB()
    stats = db.getStats() 
    db.close()
    if stats is None:
        abort(404)
    return stats

def update_movie(movie_id, movie):
    db = mdb.MoviesDB()
    db.updateMovie(movie_id, movie)
    db.close()
    return 


## Routes ##
@app.route('/')
def index():
    return render_template('index.html', movies=get_all_movies()) 

@app.route('/review')
def review():
    return render_template('review.html', movies=get_movies_with_valid_searches())

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    return render_template('movie.html', movie=get_movie(movie_id))

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    return render_template('statistics.html', stats=get_stats())

@app.route('/fix/<int:movie_id>', methods=['GET', 'POST'])
def fix(movie_id):
    if request.method == 'POST':
        print(request.form)
        new_title = request.form['title']
        new_year = request.form['year']
        new_imdb_id = request.form['imdb_id']
        if not new_title or not new_year or not new_imdb_id:
            flash('Please enter a title, year, and imdb_id ', 'danger')
        else:
            update_movie(movie_id, mi.Movie(new_title, new_year, new_imdb_id))
            flash('Movie updated successfully', 'success')
            return redirect(url_for('review'))

    return render_template('fix.html', movie=get_movie(movie_id), searches=get_searches_by_movie_id(movie_id))