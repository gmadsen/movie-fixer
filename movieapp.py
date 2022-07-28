import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import MovieInteface as mi
import MoviesDB as mdb



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

def get_movie(movie_id):
    cur = mdb.MoviesDB().conn.cursor()
    cur.execute("SELECT * FROM Movies WHERE id = ?", (movie_id,))
    movie = cur.fetchone()
    if movie is None:
        abort(404)
    return movie 

@app.route('/')
def index():
    open_issues = mdb.MoviesDB().getMoviesWithNoImdbId()
    return render_template('index.html', movies=open_issues) 




@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie = get_movie(movie_id)
    return render_template('movie.html', movie=movie)


