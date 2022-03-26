from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from urllib.parse import urljoin
from typing import List
from bs4 import BeautifulSoup

import threading
import time
import random
import requests

class CrawlerManager:

    websiteDir = "websites/"

    def __init__(self, websiteFiles, numThreads=1, hopping=False):
        self.numThreads = numThreads
        self.hopping = hopping
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
                print("No more websites left")
                break

            self.crawlers.append(Crawler(self.drivers[x], self.urls.pop(), hopping=self.hopping))
            self.threads.append(threading.Thread(target=self.crawlers[x].startCrawl))

        # Start initial wave
        for thread in self.threads:
            thread.start()
            time.sleep(0.25)    # To not overload cpu during loading

    def start(self):
        self.initCrawlers()

        while len(self.urls) > 0:
            self.deployCrawlers() # Can be optimized by utilizing callbacks and assigning ids to crawlers...
            time.sleep(0.5)

        self.leftOverThreads()
        print("All threads finished")

    # Checks which threads have died so new ones can be started
    def deployCrawlers(self):
        for x in range(self.numThreads):
            if len(self.urls) == 0:  # Checks if there are still websites left to visit
                break

            if not self.threads[x].is_alive():  # Starts a new thread
                finishedCrawler = self.crawlers[x]
                self.extractCookies(finishedCrawler)

                self.drivers[x].close()
                self.drivers[x] = webdriver.Chrome(options=self.chromeOptions)

                self.crawlers[x] = Crawler(self.drivers[x], self.urls.pop(), hopping=self.hopping)
                self.threads[x] = threading.Thread(target=self.crawlers[x].startCrawl)
                self.threads[x].start()
            time.sleep(0.25)

    # Cleans up all threads that are still running when all websites have been visited
    def leftOverThreads(self):
        while True:
            for x in range(self.numThreads):
                if self.threads[x] is not None and not self.threads[x].is_alive():
                    finishedCrawler = self.crawlers[x]
                    if finishedCrawler.websiteUrl in self.allCookies:
                        self.threads[x] = None
                    else:
                        self.extractCookies(finishedCrawler)

            count = 0
            # Checks if all threads have been removed
            for x in range(self.numThreads):
                if self.threads[x] is None:
                    count = count + 1

            # If all threads are dead, we can stop checking
            if count == self.numThreads:
                break

            time.sleep(0.25)

    def extractCookies(self, crawler):
        self.allCookies[crawler.websiteUrl] = dict.fromkeys({'frontpage', 'hopped'})
        self.allCookies[crawler.websiteUrl]['frontpage'] = crawler.frontpageCookies
        if self.hopping:
            self.allCookies[crawler.websiteUrl]['hopped'] = crawler.hopCookies

class Crawler:

    def __init__(self, driver, websiteUrl, hopping=False):
        self.driver = driver
        self.websiteUrl = websiteUrl
        self.hopping = hopping

        self.hopCookies = dict()

    # Crawls the initial url
    def startCrawl(self):
        url = "https://" + self.websiteUrl
        print("crawling: " + url)
        try:
            self.driver.get(url)
            time.sleep(5)  # Staying longer on a page results in more cookies
            self.frontpageCookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]

            if self.hopping:
                self.hop()
        except WebDriverException:
            print("Unreachable url: " + self.websiteUrl)
            self.frontpageCookies = dict()
            self.hopCookies = dict()

    # Hops pages found on the front page
    def hop(self):
        hopUrls = self.hopUrls("https://" + self.websiteUrl)
        # Visiting all of the urls
        for url in hopUrls:
            print("Hopping on " + self.websiteUrl + " to " + url)
            self.driver.get(url)
            time.sleep(5)

        unprocessedHopCookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]  # All the names of the frontpage cookies
        frontpageCookieNames = [c['name'] for c in self.frontpageCookies]
        self.hopCookies = [c for c in unprocessedHopCookies if c['name'] not in frontpageCookieNames]  # Cookies we found through hopping

    # Had to add these two methods here because otherwise it would complain about circular imports...
    def hopUrls(self, base_url: str) -> List[str]:
        r = requests.get(base_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        a_tags = soup.find_all('a', href=True)
        # Create absolute URLs and remove the ones which are refs on the same page.
        w_name = self.getWebsiteName(base_url)
        refs = {full_url for x in a_tags if w_name == self.getWebsiteName(full_url := urljoin(base_url, x['href']))
                and not x['href'].startswith('#')}
        return random.sample([*refs], min(len(refs), 20))

    def getWebsiteName(self, url: str) -> str:
        return url.rsplit('.', 1)[0].split('.', 1)[-1]
