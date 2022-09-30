#from re import A
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from werkzeug.exceptions import abort
import MovieInterface as mi
from BackendCaller import *
import Exporter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'


## Routes ##
@app.route('/')
def index():
    return render_template('index.html', movies=get_all_movies()) 

@app.route('/download')
def download_file():
    movies = export_valid_movies()
    csvfile = Exporter.make_temp_csv_movie_list(movies, Exporter.Simkl)
    return send_file(csvfile.name, download_name='movies.csv', as_attachment=True, mimetype='text/csv')

@app.route('/review')
def review():
    return render_template('review.html', movies=get_movies_with_valid_searches())

@app.route('/invalid')
def invalid():
    return render_template('invalid.html', invalid_movies=get_invalid_movies())

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    return render_template('movie.html', movie=get_movie(movie_id))

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    if request.method == 'POST':
        action = request.form.getlist('subject')[0]
        if action == 'match':
            auto_match_movies()
        elif action == 'query':
            query_all_invalids() 
        elif action == 'export':
            export_valid_movies()
        elif action == 'reset':
            print("attempting to reset")
            hard_db_reset()
        return redirect(url_for('stats'))
    return render_template('statistics.html', stats=get_stats())

@app.route('/fix/<int:movie_id>', methods=['GET', 'POST'])
def fix(movie_id):
    if request.method == 'POST':
        new_movie = mi.Movie.from_tuple(request.form)
        if not new_movie.isFullyDefined():
            flash('Please enter a title, year, and imdb_id/tmdb_id', 'danger')
        else:
            update_movie_to_valid(movie_id, new_movie) 
            flash('Movie updated successfully', 'success')
            # seems a waste, but im not sure of a better way to get next movie id
            next_movie = get_movies_with_valid_searches()[0]
            return redirect(url_for('fix', movie_id=next_movie['id']))
    return render_template('fix.html', movie=get_movie(movie_id), searches=get_searches_by_movie_id(movie_id))

@app.route('/search/<int:movie_id>', methods=['GET', 'POST'])
def search(movie_id): 
    if request.method == 'POST':
        action = request.form.getlist('subject')[0]
        if action == 'search':
            tmdb_search(movie_id)
            return redirect(url_for('invalid'))
    return render_template('search.html', movie=get_movie(movie_id))