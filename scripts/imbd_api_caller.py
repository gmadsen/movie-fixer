
import requests
import json

URL = "https://movie-database-alternative.p.rapidapi.com/"
HEADERS = {
	"X-RapidAPI-Key": "2afd199a52msh50040cd85d8d844p17f065jsnc8fd0db39230",
	"X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
}

def makeQueryString(req):
    return {"s":req.name,"y":req.year,"r":"json"} 
    

def request(movie):
        querystring = makeQueryString(movie)
        response = requests.request("GET", URL, HEADERS, params=querystring)
        return response.text