import json
import numpy as np
from typing import List

# Hardcoded, ugly, but the files won't change.
ALL_TRACKERS = {'adguarddns': np.loadtxt('3rd-party-trackers/adguarddns-justdomains-sorted.txt', dtype=str),
                'easylist': np.loadtxt('3rd-party-trackers/easylist-justdomains-sorted.txt', dtype=str),
                'easyprivacy': np.loadtxt('3rd-party-trackers/easyprivacy-justdomains-sorted.txt', dtype=str),
                'nocoin': np.loadtxt('3rd-party-trackers/nocoin-justdomains-sorted.txt', dtype=str)}

FIELDS = ["name", "domain", "expires"]


def parse_cookie(cookie, website):
    trackers = check_trackers(cookie["domain"])
    # Copy only selected fields
    c = {k: cookie[k] for k in FIELDS}
    c['third_party'] = website not in c['domain']
    c["trackers_list"] = trackers

    return c


def post_processing(cookies):
    out = dict()

    for website in cookies.keys():
        out[website] = {"frontpage": [], "hopped": []}
        # Parse frontpage
        for cookie in cookies[website]["frontpage"]:
            # Select field and add trackers
            c = parse_cookie(cookie, website)
            out[website]["frontpage"].append(c)

        # Parse hops
        for cookie in cookies[website]["hopped"]:
            # Select field and add trackers
            c = parse_cookie(cookie, website)
            out[website]["hopped"].append(c)

    return out


# For each tracker list, check if the domain name is present and save the list name if that is the case.
def check_trackers(domain_name: str) -> List[str]:
    found_in = []
    for k, v in ALL_TRACKERS.items():
        if is_tracker(domain_name, v):
            found_in.append(k)

    return found_in


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
