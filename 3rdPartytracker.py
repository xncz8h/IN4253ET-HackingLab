from importlib.resources import path
import os

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
    print()

def checkForTrackers(cookie_list):

    paths = getPathToFiles()

    for path in paths:
        with open(path, encoding='utf-8') as f:
            checkListAgainstList(f, cookie_list)
    
