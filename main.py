from ThirdPartytracker import checkForTrackers
from collect_cookies import main_collect_cookies
from cookie import Cookie

from CrawlerManager import CrawlerManager
from post_processing import main_process

from CookieProcessing import processCookies

WEBSITES = ["example"]

#def main():
#    for website in WEBSITES:
#        main_collect_cookies(f"websites/{website}.txt", f"out/{website}.json")
#        main_process(website)

def startCrawling():
    print("Start crawling")

    websiteFiles = ["overheid.txt", "universities.txt"]
    crawlerManager = CrawlerManager(websiteFiles, numThreads=10)
    crawlerManager.start()

    allCookies = crawlerManager.allCookies
    processCookies(allCookies, ['name', 'domain', 'expires'])

if __name__ == "__main__":
    startCrawling()
    # main()