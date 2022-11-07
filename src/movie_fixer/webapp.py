"""main file for movie database fixer web app"""

from quart import Quart, render_template, request, url_for, flash, redirect, send_file
from jinja2 import FileSystemLoader

from . import backend_caller as bc
from . import exporter


WEB_APP = Quart(__name__)
WEB_APP.config['SECRET_KEY'] = 'mysecretkey'

loader = FileSystemLoader("templates")

# Routes #
@WEB_APP.route('/')
async def index():
    """homepage"""
    return await render_template('index.html', movies=bc.get_all_movies())


@WEB_APP.route('/download')
async def download_file():
    """route to download csv file of movie list"""
    movies = bc.get_valid_movies()
    csvfile = exporter.make_temp_csv_movie_list(movies, exporter.Simkl)
    return await send_file(csvfile.name, attachment_filename='movies.csv', as_attachment=True, mimetype='text/csv')


@WEB_APP.route('/review')
async def review():
    """review route"""
    return await render_template('review.html', movies=bc.get_movies_with_valid_searches())


@WEB_APP.route('/invalid')
async def invalid():
    """invalid route"""
    return await render_template('invalid.html', invalid_movies=bc.get_invalid_movies())


@WEB_APP.route('/movie/<int:movie_id>')
async def movie(movie_id):
    """movie/id route"""
    return await render_template('movie.html', movie=bc.get_movie(movie_id)[0])


@WEB_APP.route('/stats', methods=['GET', 'POST'])
async def stats():
    """stats route"""
    if request.method == 'POST':
        form = await request.form
        try:
            await bc.user_power_button_handler(form['global_action'])
        except Exception as e:
            print(e)
        finally:
            return redirect(url_for('index'))
    return await render_template('statistics.html', stats=bc.get_stats())


@WEB_APP.route('/fix/<int:movie_id>', methods=['GET', 'POST'])
async def fix(movie_id):
    """fix route"""
    if request.method == 'POST':
        form = await request.form
        if 'local_action' in form.keys():
            if form['local_action'] == 'remove_search':
                bc.remove_associated_searches(movie_id)
                return redirect(url_for('fix', movie_id=bc.get_movies_with_valid_searches()[0]['id']))
        elif bc.update_movie_from_form(movie_id, form):
            bc.remove_associated_searches(movie_id)
            await flash('Movie updated!')
            return redirect(url_for('fix', movie_id=bc.get_movies_with_valid_searches()[0]['id']))
        else:
            await flash('Please enter a title, year, and imdb_id/tmdb_id', 'danger')
    return await render_template('fix.html', movie=bc.get_movie(movie_id)[0], searches=bc.get_searches_by_movie_id(movie_id))


@WEB_APP.route('/search/<int:movie_id>', methods=['GET', 'POST'])
async def search(movie_id):
    """route for search"""
    if request.method == 'POST':
        form = await request.form
        action = form['subject']
        if action == 'search':
            bc.update_movie_with_api_call(movie_id)
            return redirect(url_for('invalid'))
    return await render_template('search.html', movie=bc.get_movie(movie_id)[0])

if __name__ == "__main__":
    WEB_APP.run()
