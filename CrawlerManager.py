from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import threading
import time

# Might need to be rewritten so that new tabs are opened instead of new instances
# When running a lot of drivers parallel it sometimes crashes, it is a known issue

class CrawlerManager:

    websiteDir = "websites/"

    def __init__(self, websiteFiles, numThreads=1):
        self.numThreads = numThreads
        self.chromeOptions = Options()
        self.urls = []

        self.crawlers = []
        self.threads = []
        self.drivers = []

        self.setupUrls(websiteFiles)
        self.setupOptions()
        self.initDrivers()

    def setupOptions(self):
        print("Setting up chrome options")
        self.chromeOptions.add_argument("--headless")
        self.chromeOptions.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")

    def setupUrls(self, files):
        print("Initializing urls...")
        for file in files:
            fileStream = open(self.websiteDir + file, "r")
            line = fileStream.readline().replace("\n", "")
            while line != "":
                self.urls.append(line)
                line = fileStream.readline().replace("\n", "")

    def initDrivers(self):
        for x in range(self.numThreads):
            self.drivers.append(webdriver.Chrome(options=self.chromeOptions))

    def initCrawlers(self):
        print("Initializing first wave of crawlers...")
        for x in range(self.numThreads):
            if len(self.urls) == 0:
                break

            self.crawlers.append(Crawler(self.drivers[x], self.urls.pop()))
            self.threads.append(threading.Thread(target=self.crawlers[x].startCrawl))

        # Start initial wave
        for thread in self.threads:
            thread.start()
            time.sleep(0.25)    # To not overload cpu during loading

    def start(self):
        self.initCrawlers()

        while len(self.urls) > 0:
            self.deployCrawlers()
            time.sleep(1)

    def deployCrawlers(self):
        for x in range(self.numThreads):
            if len(self.urls) == 0:
                break

            if not self.threads[x].is_alive():
                self.crawlers[x] = Crawler(self.drivers[x], self.urls.pop())
                self.threads[x] = threading.Thread(target=self.crawlers[x].startCrawl)
                self.threads[x].start()
            time.sleep(0.25)

class Crawler:

    prefixes = ["https://www.", "https://"]

    def __init__(self, driver, websiteUrl):
        self.driver = driver
        self.websiteUrl = websiteUrl


    def startCrawl(self):
        crawlSuccess = False
        for prefix in self.prefixes:
            currentUrl = prefix + self.websiteUrl
            print("crawling: " + currentUrl)
            try:
                self.driver.get(currentUrl)
                time.sleep(5)
            except:
                continue
            crawlSuccess = True
            break

        if crawlSuccess:
            self.cookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())  # Needs to be processed, can be done in multiple ways such as sending it to a processing thread, adding a method that returns it, callback
        else:
            print("ERROR: error while trying to crawl " + self.websiteUrl)

        # Close tab
