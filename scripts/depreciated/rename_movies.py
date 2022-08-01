

import os
import sys
import argparse
import subprocess
from ffprobe import FFProbe
from subprocess import call

from scripts.depreciated.xmllistconfig import XmlDictConfig
from xml.etree import ElementTree as ET

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder')
    args =parser.parse_args()
    res_list = []
    res_count = {}
    res_count["SDTV"] = 0
    res_count["Bluray-720p"] = 0
    res_count["Bluray-1080p"] = 0
    res_count["Bluray-2160p"] = 0

    root_dir  = args.input_folder

    for x in walk(root_dir, 2):
        # essentially trying to find a non subtitle file with the same name as the folder
        a = [video for video in x[2] if (
            video.lower().endswith('.avi') or
            video.lower().endswith('.mkv') or
            video.lower().endswith('.mp4') or
            video.lower().endswith('.mpg') or
            video.lower().endswith('.mpeg') or
            video.lower().endswith('.webm') or
            video.lower().endswith('.wmv') or
            video.lower().endswith('.mpg')) and not 
            (video.lower().endswith('.srt') or 
             video.lower().endswith('.idx') or
             video.lower().endswith('.sub') or
             video.lower().endswith('.smi'))]


        if (len(a) > 0):
            pairs = []
            for i in a:
                if x[0].endswith('/'):
                    x[0] = x[0][:-1]
                print('x0', x[0])
                fullpath = x[0] + '/' + i
                size = os.path.getsize(fullpath)
                pairs.append((size, fullpath))
            pairs.sort(key=lambda s: s[0])
            actual_movie = pairs[-1][1]
            print("old path", actual_movie)
            probe_file(actual_movie, res_list, res_count)
            name_itr = x[0].rfind('/', 0)
            container_itr = actual_movie.find('.', len(x[0]))
            new_name = x[0] + x[0][name_itr:] + ' [' + str(resolution_class(res_list[-1])) + ']' + actual_movie[container_itr:]
            print(new_name)
            print("")
            os.rename(actual_movie, new_name)
    
    res_list.sort()
    print(res_list) 
    print(len(res_list))
    print(res_count)








############# Helpers ##################################################
def probe_file(file, res_list,res_count):
    cmnd = ['ffprobe', '-v', 'error', '-hide_banner', '-print_format', 'xml',
             '-select_streams', 'v:0' , '-show_streams', file ]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    [out,err] =  p.communicate()
    root = ET.fromstring(out)
    #print(root)
    stream_dict = XmlDictConfig(root)
    res = int(stream_dict['streams']['stream']['height'])
    res_list.append(res)
    res_count[resolution_class(res)] += 1

    if err:
        print ("========= error ========")
        print (err)
        print ("========= end error ====")

def resolution_class(res):
    if (res >= 2000):
        return "Bluray-2160p"
    elif (res >= 1020):
        return "Bluray-1080p"
    elif (res >= 720):
        return "Bluray-720p"
    else:
        return "SDTV" 
def walk(top, maxdepth):
    dirs, nondirs = [], []
    for name in os.listdir(top):
        (dirs if os.path.isdir(os.path.join(top, name)) else nondirs).append(name)
    yield top, dirs, nondirs
    if maxdepth > 1:
        for name in dirs:
            for x in walk(os.path.join(top, name), maxdepth-1):
                yield x




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





if __name__ == '__main__':
    main()




