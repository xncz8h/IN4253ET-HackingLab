import numpy as np
import json
import sys
import requests
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from typing import List, Dict

from CrawlerManager import CrawlerManager

from post_processing import main_process

chrome_options = Options()
chrome_options.add_argument("--headless")
gl_SPOOFED_USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) "
                         "AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/70.0.3538.77 "
                         "Safari/537.36")
chrome_options.add_argument("--user-agent=%s" %
                            gl_SPOOFED_USER_AGENT)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("ignore-certificate-errors")
chrome_options.add_argument("incognito")
chrome_options.add_argument("disable-gpu")
chrome_options.add_argument("disable-xss-auditor")
# chrome_options.add_argument("disable-background-networking")
chrome_options.add_argument("mute-audio")
chrome_options.add_argument("disable-notifications")
chrome_options.add_argument("allow-running-insecure-content")

# Hardcoded, ugly, but the files won't change.
ALL_TRACKERS = {'adguarddns': np.loadtxt('3rd-party-trackers/adguarddns-justdomains-sorted.txt', dtype=str),
                'easylist': np.loadtxt('3rd-party-trackers/easylist-justdomains-sorted.txt', dtype=str),
                'easyprivacy': np.loadtxt('3rd-party-trackers/easyprivacy-justdomains-sorted.txt', dtype=str),
                'nocoin': np.loadtxt('3rd-party-trackers/nocoin-justdomains-sorted.txt', dtype=str)}


def get_website_name(url: str) -> str:
    return url.rsplit('.', 1)[0].split('.', 1)[-1]


# TODO: Implement this into the crawler.
def hop(base_url: str) -> List[str]:
    r = requests.get(base_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    a_tags = soup.find_all('a', href=True)
    # Create absolute URLs and remove the ones which are refs on the same page.
    w_name = get_website_name(base_url)
    refs = {full_url for x in a_tags if w_name == get_website_name(full_url := urljoin(base_url, x['href']))
            and not x['href'].startswith('#')}
    return random.sample([*refs], min(len(refs), 20))


# This function checks whether the given domain name is present in one of the trackers lists.
def is_tracker(domain_name: str, trackers_list: np.array) -> bool:
    # Strip the domain name if some prefixes.
    if domain_name.startswith('.'):
        domain_name = domain_name.replace('.', '', 1)
    if domain_name.startswith('www.'):
        domain_name = domain_name.replace('www.', '', 1)

    # Binary search.
    index = np.searchsorted(trackers_list, domain_name)
    return trackers_list[index] == domain_name and index != len(trackers_list)


# For each tracker list, check if the domain name is present and save the list name if that is the case.
def check_trackers(domain_name: str) -> List[str]:
    found_in = []
    for k, v in ALL_TRACKERS.items():
        if is_tracker(domain_name, v):
            found_in.append(k)

    return found_in


def get_parse_cookies(urls: List[str], website_name: str, fields: List[str]) -> List[Dict]:
    # Create new driver because it will otherwise return all the cookies.
    driver = webdriver.Chrome(options=chrome_options)
    for url in urls:
        try:
            driver.get(url)
        except WebDriverException:
            print(f'Could not reach {url}')

    # Empty dict for the input arguments.
    cookies = driver.execute_cdp_cmd('Network.getAllCookies', dict())['cookies']
    wanted_data = []
    for c in cookies:
        cookie_dict = {k: c[k] for k in fields}
        cookie_dict['third_party'] = website_name not in cookie_dict['domain']
        cookie_dict['trackers_list'] = check_trackers(cookie_dict['domain'])
        wanted_data.append(cookie_dict)

    return wanted_data


def crawl(websites: np.array) -> Dict:
    all_cookies = dict()
    fields = ['name', 'domain', 'expires']

    for w in websites:
        print(f'Getting {w}...')
        # Get just the website name.
        website_name = get_website_name(w)
        target_url = f'https://{w}'
        all_cookies[w] = dict.fromkeys({'frontpage', 'hopped'})
        # Try it with https:// only to keep it fair.
        frontpage_cookies = get_parse_cookies([target_url], website_name, fields)
        hopped_cookies = get_parse_cookies(hop(target_url), website_name, fields)

        # TODO: Refactor the json format to be website -> hopped -> cookie['name'] -> cookie info
        # TODO: Instead of website -> hopped -> [all cookie info]
        frontpage_cookie_names = [d['name'] for d in frontpage_cookies]
        hopped_cookies = [c for c in hopped_cookies if c['name'] not in frontpage_cookie_names]

        all_cookies[w]['frontpage'] = frontpage_cookies
        all_cookies[w]['hopped'] = hopped_cookies

    return all_cookies


# Loading input file, start crawling and write to output file.
def main_collect_cookies(input_file: str, output_file: str):
    # Multi-thread this cell.
    websites = np.loadtxt(input_file, delimiter='\n', dtype='str')
    all_cookies = crawl(websites)

    # Output.
    with open(output_file, 'w') as f:
        json.dump(all_cookies, f, indent=2)

# Calling this method takes care of everything
# Post processing needs to be fixed for the new file structure
def collectCookies(inFiles, numThreads, hopping):
    fields = ['name', 'domain', 'expires']
    for file in inFiles:
        fileName = file + ".txt"
        print("Using: " + fileName)
        files = [fileName]

        crawlerManager = CrawlerManager(files, numThreads=numThreads, hopping=hopping)  # Takes care of multithreading
        crawlerManager.start()  # Start crawling

        allCookies = crawlerManager.allCookies
        outputFile = file  # Output file
        processCookies(allCookies, fields, outputFile)  # Processing all the cookies

def processCookies(cookies, fields, outputFile):
    processedCookies = dict()

    # Pretty much copied this from what we had before
    for website in cookies:
        print("Processing cookies for: " + website)

        websiteName = website.rsplit('.', 1)[0].split('.', 1)[-1]
        url = f'https://{website}'
        websiteCookiesFrontpage = cookies[website]['frontpage']
        websiteCookiesHopping = cookies[website]['hopped']

        if len(websiteCookiesFrontpage) == 0:
            continue

        # Processes all the cookies
        processedCookies[website] = dict.fromkeys({'frontpage', 'hopped'})
        processedCookies[website]['frontpage'] = processWebsiteCookies(websiteName, websiteCookiesFrontpage, fields)

        if websiteCookiesHopping is not None:
            processedCookies[website]['hopped'] = processWebsiteCookies(websiteName, websiteCookiesHopping, fields)

    with open("out/" + outputFile + ".json", 'w') as f:
        json.dump(processedCookies, f, indent=2)

    # Post processing
    main_process(outputFile)

def processWebsiteCookies(websiteName, cookies, fields):
    wantedData = []
    for c in cookies:
        cookie_dict = {k: c[k] for k in fields}
        cookie_dict['third_party'] = websiteName not in cookie_dict['domain']
        cookie_dict['trackers_list'] = check_trackers(cookie_dict['domain'])
        wantedData.append(cookie_dict)

    return wantedData


if __name__ == '__main__':
    # TODO: Create argparser to decide whether to use the extra hop or not. And add the number of refs to take.
    # TODO: This way we can compare the frontpage vs frontpage + hoprefs (George's idea).
    #
    # Set-up parsing command line arguments
    #import time
    #start = time.time()
    #if len(sys.argv) < 3:
    #    print('No sufficient number of arguments given. Using default config.')
    #    main_collect_cookies('websites/example.txt', 'out/with_found_on.json')
    #
    # First argument is input file, second is output file.
    #else:
    #    main_collect_cookies(sys.argv[1], sys.argv[2])

    collectCookies(["overheid"], 10, True)
    #end = time.time() - start
    #print(f'Took{end:.3} seconds')
