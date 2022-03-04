from importlib.resources import path
import os
from xml import dom
from cookie import Cookie

directory = "3rd-party-trackers"

def getPathToFiles():
    paths = [] 
    try:
        for filename in os.scandir(directory):
            if filename.is_file():
                paths.append(filename.path)
    except:
        pass
    return paths

def checkListAgainstList(f, cookie_list):

    for domain in f:
        for i, cookie in enumerate(cookie_list):
            if domain.rstrip() == cookie.domain[1:]:
                file_name = os.path.basename(f.name).split(".")[0]
                cookie_list[i].trackers.append(file_name)
    

def checkForTrackers(cookie_list):

    paths = getPathToFiles()

    for path in paths:
        with open(path, encoding='utf-8') as f:
            checkListAgainstList(f, cookie_list)