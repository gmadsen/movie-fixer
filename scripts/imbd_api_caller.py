
import requests
import json

URL = "https://movie-database-imdb-alternative.p.rapidapi.com/"
HEADERS = {
        'x-rapidapi-key': "2afd199a52msh50040cd85d8d844p17f065jsnc8fd0db39230",
        'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com"
        }

## return type dic {#id: {name: "", year: ""}}
def importMovieList(file):
    with open(file, 'r') as in_file:
        movies = {}
        next(in_file)
        list_id = 0
        lines = [line.strip('\n') for line in in_file]
        for line in lines:
            year_pos = line.rfind(',')
            _name = line[1:year_pos - 1]
            _year = line[year_pos + 2 :] 
            movies[list_id] ={"name":_name, "year":_year}
            list_id += 1
        return movies

## req must by of form {name: "", year: ""}
def makeQueryString(req):
    return {"s":req["name"],"y":req["year"],"type":"movie","r":"json"} 
    

def main():
    ## variables
    url = URL
    headers = HEADERS
    in_file = 'data/top_1000_part_6.csv'
    out_file = 'data/top_1000_part_6_responded.txt'

    ## get movie list and get ids from api
    query_dic = importMovieList(in_file)
    for id in query_dic:
        querystring = makeQueryString(query_dic[id])
        response = requests.request("GET", url, headers=headers, params=querystring)
        #print(response.text)
        query_dic[id]["response"] = response.text
        #print()

    # convert to json and write out
    with open(out_file, 'w') as file:
        file.write(json.dumps(query_dic))
    #temp_dic = json.loads(temp_s)





if __name__ == '__main__':
    main()

