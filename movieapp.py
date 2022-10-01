#from re import A
import sqlite3
# from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from quart import Quart, render_template, request, url_for, flash, redirect, send_file
from werkzeug.exceptions import abort
import MovieInterface as mi
from BackendCaller import *
import Exporter
from jinja2 import FileSystemLoader, Environment, select_autoescape, PackageLoader
env = Environment(PackageLoader("movieapp"), autoescape=select_autoescape(
    enabled_extensions=('html', 'xml'),
    default_for_string=True,
))


app = Quart(__name__)
#app.config['SECRET_KEY'] = 'mysecretkey'

loader = FileSystemLoader("templates")

## Routes ##
@app.route('/')
async def index():
    return await render_template('index.html', movies=get_all_movies()) 

@app.route('/download')
async def download_file():
    movies = get_valid_movies()
    csvfile = Exporter.make_temp_csv_movie_list(movies, Exporter.Simkl)
    return await send_file(csvfile.name, download_name='movies.csv', as_attachment=True, mimetype='text/csv')

@app.route('/review')
async def review():
    return await render_template('review.html', movies=get_movies_with_valid_searches())

@app.route('/invalid')
async def invalid():
    return await render_template('invalid.html', invalid_movies=get_invalid_movies())

@app.route('/movie/<int:movie_id>')
async def movie(movie_id):
    return await render_template('movie.html', movie=get_movie(movie_id)[0])

@app.route('/stats', methods=['GET', 'POST'])
async def stats():
    if request.method == 'POST':
        form = await request.form
        try:
            user_power_button_handler(form['global_action'])
        except:
            pass
        finally:
            return redirect(url_for('index'))
    return await render_template('statistics.html', stats=get_stats())

@app.route('/fix/<int:movie_id>', methods=['GET', 'POST'])
async def fix(movie_id):
    if request.method == 'POST':
        form = await request.form
        if 'local_action' in form.keys():
            if form['local_action'] == 'remove_search':
                remove_associated_searches(movie_id)
                return redirect(url_for('index'))
        elif attempt_movie_update_from_form(movie_id, form):
            flash('Movie updated!')
            return redirect(url_for('fix', movie_id=get_movies_with_valid_searches()[0]['id']))
        else:
            flash('Please enter a title, year, and imdb_id/tmdb_id', 'danger')
    return await render_template('fix.html', movie=get_movie(movie_id)[0], searches=get_searches_by_movie_id(movie_id))


@app.route('/search/<int:movie_id>', methods=['GET', 'POST'])
async def search(movie_id): 
    if request.method == 'POST':
        form = await request.form
        action = form['subject']
        if action == 'search':
            tmdb_search(movie_id)
            return redirect(url_for('invalid'))
    return await render_template('search.html', movie=get_movie(movie_id)[0])

if __name__ == "__main__":
    app.run(debug=True)