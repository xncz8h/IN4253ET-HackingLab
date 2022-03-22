import numpy as np
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from CrawlerManager import CrawlerManager

chrome_options = Options()
# The Google cookie seems to disappear when running headless.
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
# notifications
chrome_options.add_argument("disable-notifications")
chrome_options.add_argument("allow-running-insecure-content")

ALL_TRACKERS = {'adguarddns': np.loadtxt('3rd-party-trackers/adguarddns-justdomains-sorted.txt', dtype=str),
                'easylist': np.loadtxt('3rd-party-trackers/easylist-justdomains-sorted.txt', dtype=str),
                'easyprivacy': np.loadtxt('3rd-party-trackers/easyprivacy-justdomains-sorted.txt', dtype=str),
                'nocoin': np.loadtxt('3rd-party-trackers/nocoin-justdomains-sorted.txt', dtype=str)}


def is_tracker(domain_name: str, trackers_list):
    # Strip the domain name if some prefixes.
    if domain_name.startswith('.'):
        domain_name = domain_name.replace('.', '', 1)
    if domain_name.startswith('www.'):
        domain_name = domain_name.replace('www.', '', 1)

    # print(domain_name)
    # Binary search.
    index = np.searchsorted(trackers_list, domain_name)
    return trackers_list[index] == domain_name and index != len(trackers_list)


def check_trackers(domain_name):
    found_in = []
    for k, v in ALL_TRACKERS.items():
        if is_tracker(domain_name, v):
            found_in.append(k)

    return found_in


def get_parse_cookies(driver, url, website_name, fields):
    driver.get(url)
    # Empty dict for the input arguments.
    cookies = driver.execute_cdp_cmd('Network.getAllCookies', dict())['cookies']
    wanted_data = []
    for c in cookies:
        cookie_dict = {k: c[k] for k in fields}
        cookie_dict['third_party'] = website_name not in cookie_dict['domain']
        cookie_dict['trackers_list'] = check_trackers(cookie_dict['domain'])
        wanted_data.append(cookie_dict)

    print(url)
    return wanted_data


def crawl(websites):
    all_cookies = dict()
    fields = ['name', 'domain', 'expires']

    # TODO: check for https://www. and https:// both
    for w in websites:
        # Create new driver because it will otherwise return all the cookies.
        driver = webdriver.Chrome(options=chrome_options)
        website_name = w.rsplit('.', 1)[0].split('.', 1)[-1]
        try:
            target_url = f'https://{w}'
            all_cookies[w] = get_parse_cookies(driver, target_url, website_name, fields)

        # Try again but with www.
        except WebDriverException:
            try:
                target_url = f'https://www.{w}'
                all_cookies[w] = get_parse_cookies(driver, target_url, website_name, fields)

            except WebDriverException:
                print('Page Down')

    return all_cookies


def main_collect_cookies(input_file, output_file):
    # Multi-thread this cell.
    websites = np.loadtxt(input_file, delimiter='\n', dtype='str')
    all_cookies = crawl(websites)

    with open(output_file, 'w') as f:
        json.dump(all_cookies, f, indent=2)

def collectCookies():
    inFiles = ["health"]
    for file in inFiles:
        fileName = file + ".txt"
        print("Using: " + fileName)
        files = [fileName]

        crawlerManager = CrawlerManager(files, numThreads=10)
        crawlerManager.start()

        allCookies = crawlerManager.allCookies
        processCookies(allCookies)

def processCookies(cookies):
    for website in cookies:
        print("Processing cookies for: " + website)


if __name__ == '__main__':
    # Set-up parsing command line arguments
    #if len(sys.argv) < 3:
    #    print('No sufficient number of arguments given. Using default config.')
    #    main_collect_cookies('websites/overheid.txt', 'out/overheid.json')
    #    # main('websites/example.txt', 'out/example.json')

    # First argument is input file, second is output file.
    #else:
    #    main_collect_cookies(sys.argv[1], sys.argv[2])
    collectCookies()
