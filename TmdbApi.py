import asyncio
import aiohttp
import time
import MovieInterface as mi
import requests
from datetime import datetime

URL     = "https://api.themoviedb.org/3/search/movie/"
API_KEY = "4f8774170a53865294832e845594aee7"
AUTH    = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0Zjg3NzQxNzBhNTM4NjUyOTQ4MzJlODQ1NTk0YWVlNyIsInN1YiI6IjYyZTg3NjkxMWJmMjY2MDA1YTYxNTMwNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.J5fKMkgxJOZ40VqfA1tCnjfVDNcAYEGVIvXSRgfkqVU"
POSTER_PREFIX = "https://image.tmdb.org/t/p/w92"
    
class TmdbResponse:
    def __init__(self, response):
            self.page = int(response["page"])
            self.results = [TmdbSearchResult(x) for x in  response["results"]]
            self.total_pages = int(response["total_pages"])
            self.total_results = int(response["total_results"])
    def __str__(self):
        return f"{self.results}"
    def __repr__(self):
        return f"{self.results}"
        
class TmdbSearchResult:
    def __init__(self, result):
        self.title = result["title"]
        self.original_title = result["original_title"]
        self.release_date = result["release_date"]
        self.year = datetime.strptime(self.release_date, "%Y-%m-%d").year
        self.original_language = result["original_language"]
        self.tmdb_id = result["id"]
        self.poster_path = POSTER_PREFIX + result["poster_path"] if result["poster_path"] is not None else None
    def __str__(self):
        return f"{self.title} ({self.year})"
    def __repr__(self):
        return f"{self.title} ({self.year})"

def makeParamsFromMovieQuery(movie):
    return {"api_key":API_KEY, 
            "query":movie['title'],
            "year":movie['year'], 
            "language":"en-US", 
            "include_adult":True} 

def makeParamsFromMovie(req):
    return {"api_key":API_KEY, 
            "query":req.title,
            "year":req.year, 
            "language":"en-US", 
            "include_adult":True}

def updateMovieWithApiCall(movie):
        params = makeParamsFromMovie(movie)
        response = requests.get(URL, params=params)
        movie.tmdb_response = TmdbResponse(response.json()) 
        return movie    
    
############## Async Yo ####################
async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)
    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))

async def get_async(session, url, params, task_idx, results):
    async with session.get(url, params=params) as response:
        obj = await response.json()
        results[task_idx] = obj

async def batch_runner(max_conc_workers, tasks):
    conn = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
    session = aiohttp.ClientSession(connector=conn)
    results = {}
    #conc_req = 40
    now = time.time()
    await gather_with_concurrency(max_conc_workers, *[get_async(task, session, results) for task in tasks])
    time_taken = time.time() - now
    print(time_taken)
    await session.close()


# asyncio.run(batch_search_runner())