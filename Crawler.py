import time
import requests
from selenium.common.exceptions import WebDriverException
from helper import hop, get_website_name


class Crawler:
    def __init__(self, driver, websiteUrl, hops):
        self.driver = driver
        self.websiteUrl = websiteUrl
        self.hops = hops
        self.hopCookies = dict()

    # Crawls the initial url
    def start_crawl(self):
        url = "https://" + self.websiteUrl
        print("crawling: " + url)
        try:
            self.driver.get(url)
            time.sleep(5)  # Staying longer on a page results in more cookies
            self.frontpage_cookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]

            if self.hops:
                self.do_hop()
        except WebDriverException:
            print("Unreachable url: " + self.websiteUrl)
            self.frontpage_cookies = dict()
            self.hopCookies = dict()

    # Hop pages found on the front page.
    def do_hop(self):
        hop_urls = hop("https://" + self.websiteUrl, self.hops)
        # Visiting all the urls.
        for url in hop_urls:
            # print("Hopping on " + self.websiteUrl + " to " + url)
            self.driver.get(url)
            time.sleep(5)

        unprocessed_hop_cookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]  # All the names of the frontpage cookies
        frontpage_cookie_names = [c['name'] for c in self.frontpage_cookies]
        self.hopCookies = [c for c in unprocessed_hop_cookies if c['name'] not in frontpage_cookie_names]  # Cookies we found through hopping
