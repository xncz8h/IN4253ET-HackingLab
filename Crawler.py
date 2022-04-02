import time
import requests
from selenium.common.exceptions import WebDriverException
from helper import hop, get_website_name


class Crawler:
    def __init__(self, driver, websiteUrl, hops):
        self.driver = driver
        self.websiteUrl = websiteUrl
        self.hops = hops
        self.hopCookies = []

    # Crawls the initial url
    def start_crawl(self):
        url = "https://" + self.websiteUrl
        print("crawling: " + url)
        try:
            self.driver.get(url)
            current_time = time.time()

            time.sleep(5)  # Staying longer on a page results in more cookies
            self.frontpage_cookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]

            # Add time to live to each cookie
            for cookie in self.frontpage_cookies:
                cookie["time_to_live"] = cookie["expires"] - current_time

            if self.hops:
                self.do_hop()
        except WebDriverException:
            print("Unreachable url: " + self.websiteUrl)
            self.frontpage_cookies = []
            self.hopCookies = []

    # Hop pages found on the front page.
    def do_hop(self):
        hop_urls = hop("https://" + self.websiteUrl, self.hops)
        frontpage_cookie_names = [c['name'] for c in self.frontpage_cookies]

        # Visiting all the urls.
        for url in hop_urls:
            self.driver.get(url)
            current_time = time.time()

            time.sleep(5)
            unprocessed_cookies = self.driver.execute_cdp_cmd('Network.getAllCookies', dict())["cookies"]
            hop_cookie_names = [c['name'] for c in self.hopCookies]

            filtered_cookies = [c for c in unprocessed_cookies if c['name'] not in hop_cookie_names and c['name'] not in frontpage_cookie_names]
            for cookie in filtered_cookies:
                cookie["time_to_live"] = cookie["expires"] - current_time
            self.hopCookies += filtered_cookies



