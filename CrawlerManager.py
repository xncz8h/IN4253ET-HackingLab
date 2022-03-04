from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import threading
import time

class CrawlerManager:

    websiteDir = "websites/"

    def __init__(self, websiteFiles, numThreads=1):
        self.numThreads = numThreads
        self.chromeOptions = Options()
        self.urls = []

        self.crawlers = []
        self.threads = []
        self.setupUrls(websiteFiles)

    def setupUrls(self, files):
        print("Initializing urls...")
        for file in files:
            fileStream = open(self.websiteDir + file, "r")
            line = fileStream.readline().replace("\n", "")
            while line != "":
                self.urls.append(line)
                line = fileStream.readline().replace("\n", "")

    def initCrawlers(self):
        print("Initializing first wave of crawlers...")
        for x in range(self.numThreads):
            if len(self.urls) == 0:
                break

            self.crawlers.append(Crawler(self.chromeOptions, self.urls.pop()))
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
                self.crawlers[x] = Crawler(self.chromeOptions, self.urls.pop())
                self.threads[x] = threading.Thread(target=self.crawlers[x].startCrawl)
                self.threads[x].start()
            time.sleep(0.25)

class Crawler:

    prefixes = ["https://www.", "https://"]

    def __init__(self, chromeOptions, websiteUrl):
        self.chromeOptions = chromeOptions
        self.websiteUrl = websiteUrl

    def startCrawl(self):
        driver = webdriver.Chrome(options=self.chromeOptions)
        driver.minimize_window()

        crawlSuccess = False
        for prefix in self.prefixes:
            currentUrl = prefix + self.websiteUrl
            print("crawling: " + currentUrl)
            try:
                driver.get(currentUrl)
                time.sleep(5)
            except:
                continue
            crawlSuccess = True
            break

        if crawlSuccess:
            self.cookies = driver.execute_cdp_cmd('Network.getAllCookies', dict())
        else:
            print("ERROR: error while trying to crawl " + self.websiteUrl)

        driver.close()
        # Eventually might add error handling
