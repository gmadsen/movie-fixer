import csv
import re

with open('top_1000_aggregate.txt', 'r') as in_file:
    movies = []
    #lines = [line.strip('\n').replace('\t',' ') for line in in_file]
    lines = [line.strip('\n') for line in in_file]
    for line in lines:
        year = line.find('.') 
        movies.append(line[year + 2:])
    #print(movies)
    # for movie in movies:
    #     year = movie.rfind('(')
    #     print (movie[:year])
    # for line in movies:
    #     line.rstrip(" ")
    #     line.lstrip(" ")
    # print(movies)

    with open('top_1000.csv', 'w') as out_file:

        out_file.write('Title, Year, ID')
        out_file.write('\n')
        for i in movies:
            year = i.rfind("(") 
            out_file.write('"')
            out_file.write(i[:year -1])
            out_file.write('", ')
            out_file.write(i[year+1:year+5])
            out_file.write("\n")