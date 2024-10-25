"""module for tmdb api"""
from dataclasses import dataclass
import time
from datetime import datetime
import asyncio
import aiohttp
import requests

URL = "https://api.themoviedb.org/3/search/movie/"
MOVIE_URL = "https://api.themoviedb.org/3/movie/"
API_KEY = "NEED TO ADD env variable secure method"
AUTH = "env variable secure method"
POSTER_PREFIX = "https://image.tmdb.org/t/p/w92"


class TmdbResponse:
    """ takes a json get response from a movie query from tmdb """
    def __init__(self, response):
        self.page = int(response["page"])
        self.results = [TmdbSearchResult(x) for x in response["results"]]
        self.total_pages = int(response["total_pages"])
        self.total_results = int(response["total_results"])

    def __str__(self):
        return f"{self.results}"

    def __repr__(self):
        return f"{self.results}"


class TmdbSearchResult:
    """ takes a json get response from a movie query from tmdb"""
    def __init__(self, result):
        self.title = result["title"]
        self.original_title = result["original_title"]
        self.release_date = result["release_date"]
        if self.release_date != '':
            self.year = datetime.strptime(self.release_date, "%Y-%m-%d").year
        else:
            self.year = self.release_date
        self.original_language = result["original_language"]
        self.tmdb_id = result["id"]
        self.poster_path = POSTER_PREFIX + \
            result["poster_path"] if result["poster_path"] is not None else None

    def __str__(self):
        return f"{self.title} ({self.year})"

    def __repr__(self):
        return f"{self.title} ({self.year})"


def make_params_from_movie_query(movie):
    """ make get request params from a movie query or object"""
    return {"api_key": API_KEY,
            "query": movie['title'],
            "year": movie['year'],
            "language": "en-US",
            "include_adult": "true"}


def make_params_from_movie(movie):
    """ make get request params from a movie query or object"""
    return {"api_key": API_KEY,
            "query": movie.title,
            "year": movie.year,
            "language": "en-US",
            "include_adult": "true"}


def update_movie_with_api_call(movie):
    """ update movie reference with results of api query """
    params = make_params_from_movie(movie)
    response = requests.get(URL, params=params)
    movie.tmdb_response = TmdbResponse(response.json())
    return movie

############## Async Yo ####################
async def gather_with_concurrency(count, *tasks):
    """ asyncio gather with a specified semaphore count"""
    semaphore = asyncio.Semaphore(count)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def get_async(task, session, results) -> None:
    """ create an async get request job"""
    # async with session.get(url=URL, params=task.params) as response:
    async with session.get(task.url, params=task.params) as response:
        obj = await response.json()
        results[task.movie_id] = obj


async def batch_runner(max_conc_workers, tasks) -> dict:
    """ given tasks and a worker count, will run a async worker queue"""
    conn = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
    session = aiohttp.ClientSession(connector=conn)
    results = {}
    await gather_with_concurrency(max_conc_workers, *[get_async(task, session, results) for task in tasks])
    await session.close()
    return results


@dataclass
class Task:
    def __init__(self, movie_id: int, params: dict, url = URL):
        self.movie_id = movie_id
        self.params = params
        self.url = url