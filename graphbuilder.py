import matplotlib.pyplot as plt
import json
import numpy as np

def process_cookies(filename):
    with open(filename) as jsonFile:
        allCookies = json.load(jsonFile)
        jsonFile.close()

    processedCookies = dict()

    for website in allCookies:
        allCookies[website]["website"] = website
        allCookies[website]["frontpage_cookies"] = len(allCookies[website]["frontpage"])
        allCookies[website]["hopped_cookies"] = len(allCookies[website]["hopped"])
        allCookies[website]["frontpage_thirdparty"] = 0
        allCookies[website]["hopped_thirdparty"] = 0

        for cookie in allCookies[website]["frontpage"]:
            if cookie["third_party"]:
                allCookies[website]["frontpage_thirdparty"] += 1

        for cookie in allCookies[website]["hopped"]:
            if cookie["third_party"]:
                allCookies[website]["hopped_thirdparty"] += 1

    return allCookies

def frontpage_vs_hop_cookies(filename, outfile):
    processedCookies = process_cookies(filename)

    cookieList = []
    for website in processedCookies:
        cookieList.append(processedCookies[website])

    cookieList.sort(key=lambda x: x["frontpage_cookies"] + x["hopped_cookies"], reverse=True)

    data = [[], [], []]
    for x in range(5):
        data[0].append(cookieList[x]["frontpage_cookies"])
        data[1].append(cookieList[x]["hopped_cookies"])
        data[2].append(cookieList[x]["frontpage_cookies"] + cookieList[x]["hopped_cookies"])

    columns = (cookieList[0]["website"], cookieList[1]["website"], cookieList[2]["website"], cookieList[3]["website"], cookieList[4]["website"])

    index = np.arange(5) + 0.3

    plt.bar(index, data[2], width=0.3, label="Hop cookies")
    plt.bar(index, data[0], width=0.3, label="Frontpage cookies")

    plt.xticks(index, columns, rotation=35, ha='right')
    plt.yticks(np.arange(data[0][0] + data[1][0], step=2) + 1)
    plt.tight_layout()
    plt.ylabel("#cookies")
    plt.legend()
    plt.subplots_adjust(left=0.08)
    plt.savefig(outfile)
    plt.close()

def total_cookies_vs_thirdparty_cookies(filename, outfile):
    processedCookies = process_cookies(filename)

    cookieList = []
    for website in processedCookies:
        cookieList.append(processedCookies[website])

    cookieList.sort(key=lambda x: x["frontpage_cookies"] + x["hopped_cookies"], reverse=True)

    data = [[], []]
    for x in range(5):
        data[0].append(cookieList[x]["frontpage_cookies"] + cookieList[x]["hopped_cookies"])
        data[1].append(cookieList[x]["frontpage_thirdparty"] + cookieList[x]["hopped_thirdparty"])

    columns = (cookieList[0]["website"], cookieList[1]["website"], cookieList[2]["website"], cookieList[3]["website"],
               cookieList[4]["website"])

    index = np.arange(5) + 0.3
    plt.bar(index, data[0], width=0.30, label="All")
    plt.bar(index, data[1], width=0.30, label="Third party")

    plt.xticks(index, columns, rotation=35, ha='right')
    plt.yticks(np.arange(data[0][0], step=2) + 1)
    plt.tight_layout()
    plt.ylabel("#cookies")
    plt.legend()
    plt.subplots_adjust(left=0.08)
    plt.savefig(outfile)
    plt.close()

def time_to_live_distribution(filename, outfile):
    processedCookies = process_cookies(filename)

    data = []
    for website in processedCookies:
        for cookie in processedCookies[website]["frontpage"]:
            data.append(cookie["time_to_live"])
        for cookie in processedCookies[website]["hopped"]:
            data.append(cookie["time_to_live"])

    data = [c for c in data if c >= 0]
    plt.hist(data, bins=100)
    plt.show()

if __name__ == "__main__":
    frontpage_vs_hop_cookies("out/government-out.json", "graphs/government_frontpage_vs_hopped_cookies_bar.png")
    frontpage_vs_hop_cookies("out/health-out.json", "graphs/health_frontpage_vs_hopped_cookies_bar.png")
    frontpage_vs_hop_cookies("out/universities-out.json", "graphs/universities_frontpage_vs_hopped_cookies_bar.png")

    total_cookies_vs_thirdparty_cookies("out/government-out.json", "graphs/government_total_vs_thirdparty.png")
    total_cookies_vs_thirdparty_cookies("out/health-out.json", "graphs/health_total_vs_thirdparty.png")
    total_cookies_vs_thirdparty_cookies("out/universities-out.json", "graphs/universities_total_vs_thirdparty.png")

    time_to_live_distribution("out/government-out.json", "graphs/government-time-to-live-distribution.png")