from ThirdPartytracker import checkForTrackers
from collect_cookies import main_collect_cookies
from cookie import Cookie

from CrawlerManager import CrawlerManager
from post_processing import main_process

import argparse

WEBSITES = ["example.txt"]

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threads", type=int, default=10, help="number of threads to use")
parser.add_argument("-n", "--numHops", type=int, default=20, help="number of single depth hops on a website")

#def main():
#    for website in WEBSITES:
#        main_collect_cookies(f"websites/{website}.txt", f"out/{website}.json")
#        main_process(website)

def startCrawling(num_of_threads, num_of_hops):

    crawlerManager = CrawlerManager(WEBSITES, numThreads=num_of_threads)
    crawlerManager.start()

    allCookies = crawlerManager.allCookies
    processCookies(allCookies, ['name', 'domain', 'expires'])

if __name__ == "__main__":
    args = parser.parse_args()

    num_of_threads = args.threads
    num_of_hops = args.numHops

    startCrawling(num_of_threads, num_of_hops)