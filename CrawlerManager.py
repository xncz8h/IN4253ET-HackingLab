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
        self.drivers = []

        self.setupUrls(websiteFiles)
        self.setupOptions()
        self.initDrivers()

        self.allCookies = dict()

    # Sets up the chrome options.
    def setupOptions(self):
        print("Setting up chrome options...")
        self.chromeOptions.add_argument("--headless")
        gl_SPOOFED_USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) "
                                 "AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/70.0.3538.77 "
                                 "Safari/537.36")
        self.chromeOptions.add_argument("--user-agent=%s" % gl_SPOOFED_USER_AGENT)
        self.chromeOptions.add_argument("--disable-extensions")
        self.chromeOptions.add_argument("ignore-certificate-errors")
        self.chromeOptions.add_argument("incognito")
        self.chromeOptions.add_argument("disable-gpu")
        self.chromeOptions.add_argument("disable-xss-auditor")
        # chrome_options.add_argument("disable-background-networking")
        self.chromeOptions.add_argument("mute-audio")
        # notifications
        self.chromeOptions.add_argument("disable-notifications")
        self.chromeOptions.add_argument("allow-running-insecure-content")

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
            self.deployCrawlers() # Can be optimized by utilizing callbacks and assigning ids to crawlers...
            time.sleep(1)

    def deployCrawlers(self):
        for x in range(self.numThreads):
            if len(self.urls) == 0:
                self.leftOverThreads()
                print("Finished everything")
                break

            if not self.threads[x].is_alive():
                finishedCrawler = self.crawlers[x]
                self.extractCookies(finishedCrawler)

                self.crawlers[x] = Crawler(self.drivers[x], self.urls.pop())
                self.threads[x] = threading.Thread(target=self.crawlers[x].startCrawl)
                self.threads[x].start()
            time.sleep(0.25)

    # Cleans up all threads that are still running when all websites have been visited
    def leftOverThreads(self):
        while True:
            for x in range(self.numThreads):
                if self.threads[x] is not None and not self.threads[x].is_alive():
                    currentCrawler = self.crawlers[x]
                    if currentCrawler.websiteUrl in self.allCookies:
                        self.threads[x] = None
                    else:
                        self.allCookies[currentCrawler.websiteUrl] = currentCrawler.cookies

            count = 0
            # Checks if all threads have been removed
            for x in range(self.numThreads):
                if self.threads[x] is None:
                    count = count + 1

            if count == self.numThreads:
                break

            time.sleep(0.25)

    def extractCookies(self, crawler):
        self.allCookies[crawler.websiteUrl] = crawler.cookies

class Crawler:

    prefixes = ["https://www.", "https://"]
    urlStack = []   # For the future when websites need to be crawled to a depth of n

    def __init__(self, driver, websiteUrl):
        self.driver = driver
        self.websiteUrl = websiteUrl

    def startCrawl(self):
        crawlSuccess = False
        for prefix in self.prefixes:  # Test out different prefixes
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
            self.cookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]
        else:
            print("ERROR: error while trying to crawl " + self.websiteUrl)

        self.prepareDriverForNext()

    def prepareDriverForNext(self):
        self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
