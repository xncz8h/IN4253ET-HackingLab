import requests
import random
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin


def hop(base_url: str, n_hops: int) -> List[str]:
    r = requests.get(base_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    a_tags = soup.find_all('a', href=True)
    # Create absolute URLs and remove the ones which are refs on the same page.
    w_name = get_website_name(base_url)
    refs = {full_url for x in a_tags if w_name == get_website_name(full_url := urljoin(base_url, x['href']))
            and not x['href'].startswith('#')}
    return random.sample([*refs], min(len(refs), n_hops))


def get_website_name(url: str) -> str:
    return url.rsplit('.', 1)[0].split('.', 1)[-1]
