from ThirdPartytracker import checkForTrackers
from collect_cookies import main_collect_cookies
from cookie import Cookie

from CrawlerManager import CrawlerManager
from post_processing import main_process

WEBSITES = ["health"]

def main():
    for website in WEBSITES:
        main_collect_cookies(f"websites/{website}.txt", f"out/{website}.json")
        main_process(website)

# def startCrawling():
#     print("Start crawling")

#     websiteFiles = ["overheid.txt", "universities.txt"]
#     # websiteFiles = ["example.txt"]
#     crawlerManager = CrawlerManager(websiteFiles, numThreads=10)
#     crawlerManager.start()

if __name__ == "__main__":
    # startCrawling()
    main()