import numpy as np
import time
import json
from cookie import Cookie

from CrawlerManager import CrawlerManager
from typing import List, Dict
from post_processing import post_processing

import argparse

from statistics import fetch_statistics


def load_websites(path: str) -> List[str]:
    return list(np.loadtxt(path, delimiter='\n', dtype='str'))


def write_cookies(path: str, cookies: Dict, ext: str):
    out_path = 'out/' + path.split('/')[-1].split('.')[0] + ext
    with open(out_path, 'w') as f:
        json.dump(cookies, f, indent=2)


def startCrawling(num_of_threads, num_of_hops, path):

    websites = load_websites(path)
    print(websites)

    crawler_manager = CrawlerManager(websites, num_of_hops, numThreads=num_of_threads)
    crawler_manager.start()

    all_cookies = crawler_manager.allCookies
    write_cookies(path, all_cookies, ".json")

    c = post_processing(all_cookies)
    write_cookies(path, c, ".out")

    fetch_statistics(c)


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", help="input file path")
    parser.add_argument("-t", "--threads", type=int, default=10, help="number of threads to use")
    parser.add_argument("-n", "--num_hops", type=int, default=0, help="number of single depth hops on a website")
    args = parser.parse_args()

    startCrawling(args.threads, args.num_hops, args.input_path)
    end = time.time() - start
    print(f'Ran in {end:.3} seconds')
