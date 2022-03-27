from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from Crawler import Crawler
import threading
import time


class CrawlerManager:

    websiteDir = "websites/"

    def __init__(self, websites, hops, numThreads=1):
        self.numThreads = min(len(websites), numThreads)
        self.hops = hops
        self.chromeOptions = Options()
        self.websites = websites

        self.crawlers = []
        self.threads = []
        self.drivers = []

        self.setup_options()
        self.init_drivers()

        self.allCookies = dict()

    # Sets up the chrome options.
    def setup_options(self):
        print("Setting up chrome options...")
        self.chromeOptions.add_argument("--headless")
        gl_spoofed_user_agent = ("Mozilla/5.0 (X11; Linux x86_64) "
                                 "AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/70.0.3538.77 "
                                 "Safari/537.36")
        self.chromeOptions.add_argument("--user-agent=%s" % gl_spoofed_user_agent)
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

    # def setup_urls(self, files):
    #     print("Initializing urls...")
    #     for file in files:
    #         file_stream = open(self.websiteDir + file, "r")
    #         line = file_stream.readline().replace("\n", "")
    #         while line != "":
    #             self.urls.append(line)
    #             line = file_stream.readline().replace("\n", "")

    def init_drivers(self):
        for _ in range(self.numThreads):
            self.drivers.append(webdriver.Chrome(options=self.chromeOptions))

    def init_crawlers(self):
        print("Initializing first wave of crawlers...")
        for x in range(self.numThreads):
            if len(self.websites) == 0:
                print("No more websites left")
                break
                                                                                        # was hopping
            self.crawlers.append(Crawler(self.drivers[x], self.websites.pop(), hops=self.hops))
            self.threads.append(threading.Thread(target=self.crawlers[x].start_crawl))

        # Start initial wave
        for thread in self.threads:
            thread.start()
            time.sleep(0.25)    # To not overload cpu during loading

    def start(self):
        self.init_crawlers()

        while self.websites:
            self.deploy_crawlers()  # Can be optimized by utilizing callbacks and assigning ids to crawlers...
            time.sleep(0.5)

        self.left_over_threads()
        print("All threads finished")

    # Checks which threads have died so new ones can be started
    def deploy_crawlers(self):
        for x in range(self.numThreads):
            if not self.websites:  # Checks if there are still websites left to visit
                break

            if not self.threads[x].is_alive():  # Starts a new thread
                finished_crawler = self.crawlers[x]
                self.extract_cookies(finished_crawler)

                # Create new drivers.
                self.drivers[x].close()
                self.drivers[x] = webdriver.Chrome(options=self.chromeOptions)

                # New crawler.
                self.crawlers[x] = Crawler(self.drivers[x], self.websites.pop(), hops=self.hops)
                self.threads[x] = threading.Thread(target=self.crawlers[x].start_crawl)
                self.threads[x].start()

            time.sleep(0.25)

    # Cleans up all threads that are still running when all websites have been visited
    def left_over_threads(self):
        while True:
            for x in range(self.numThreads):
                if self.threads[x] and not self.threads[x].is_alive():
                    finished_crawler = self.crawlers[x]
                    if finished_crawler.websiteUrl in self.allCookies:
                        self.threads[x] = None
                    else:
                        self.extract_cookies(finished_crawler)

            # Checks if all threads have been removed
            for t in self.threads:
                if t:
                    time.sleep(0.25)
                    continue
            break

    def extract_cookies(self, crawler):
        self.allCookies[crawler.websiteUrl] = dict.fromkeys({'frontpage', 'hopped'})
        self.allCookies[crawler.websiteUrl]['frontpage'] = crawler.frontpage_cookies
        if self.hops:
            self.allCookies[crawler.websiteUrl]['hopped'] = crawler.hopCookies
