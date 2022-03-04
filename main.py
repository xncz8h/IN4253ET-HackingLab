from ThirdPartytracker import checkForTrackers
from cookie import Cookie

from CrawlerManager import CrawlerManager

def main():
    print("Started")
    cookie_list = []
    cookie_list.append(Cookie("test1", ".nytimes.com", ".nytimes.com", 12342))
    cookie_list.append(Cookie("test2", ".nytimes.com", ".nytimes.com", 12344322))
    cookie_list.append(Cookie("test3", ".nytimes.com", ".courierregistered.com", 12342))

    checkForTrackers(cookie_list)

    for cookie in cookie_list:
        if(len(cookie.trackers)) > 0:
            for tracker in cookie.trackers:
                print(tracker)


def startCrawling():
    print("Start crawling")

    # websiteFiles = ["overheid.txt", "universities.txt"]
    websiteFiles = ["example.txt"]
    crawlerManager = CrawlerManager(websiteFiles, numThreads=10)
    crawlerManager.start()

if __name__ == "__main__":
    startCrawling()