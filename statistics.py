def fetch_cookie_stats(cookies):
    stats = dict()
    
    for website in cookies.keys():

        tracker_count = 0
        third_party_count = 0

        # Parse frontpage
        for cookie in cookies[website]["frontpage"]:
            if cookie["third_party"]:
                tracker_count += 1
            if cookie["trackers_list"]:
                third_party_count += 1

        # Parse hops
        for cookie in cookies[website]["hopped"]:
            if cookie["third_party"]:
                tracker_count += 1
            if cookie["trackers_list"]:
                third_party_count += 1

        stats[website] = {"tracker_count": tracker_count, "third_party_count": third_party_count}

    return stats


def fetch_statistics(cookies):
    stats = fetch_cookie_stats(cookies)
    third_party_stats, tracker_stats = sort(stats)
    print(third_party_stats)
    print(tracker_stats)


def sort(stats):
    third_party_stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[0], reverse=True)}
    tracker_stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1], reverse=True)}
    return third_party_stats, tracker_stats
        