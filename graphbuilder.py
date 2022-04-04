import matplotlib.pyplot as plt
import json
import numpy as np

def process_cookies(filename):
    with open(filename) as jsonFile:
        allCookies = json.load(jsonFile)
        jsonFile.close()

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

def thirdparty_stats(filename):
    processedCookies = process_cookies(filename)

    cookieCount = 0
    thirdpartyCookies = 0
    websites_with_thirdparty_cookies = 0

    shouldCount = True
    for website in processedCookies:
        for cookie in processedCookies[website]["frontpage"]:
            cookieCount += 1
            if cookie["third_party"]:
                thirdpartyCookies += 1
                if shouldCount:
                    websites_with_thirdparty_cookies += 1
                    shouldCount = False

        for cookie in processedCookies[website]["hopped"]:
            cookieCount += 1
            if cookie["third_party"]:
                thirdpartyCookies += 1
                if shouldCount:
                    websites_with_thirdparty_cookies += 1
                    shouldCount = False

        shouldCount = True

    percentage_thirdparty_cookies = thirdpartyCookies / cookieCount
    avg_thirdparty_cookies =  thirdpartyCookies / len(processedCookies)
    percentage_with_thirdparty_cookies = websites_with_thirdparty_cookies / len(processedCookies)
    avg_thirdparty_cookies_for_present = thirdpartyCookies / websites_with_thirdparty_cookies
    print(filename)
    print("third party cookie percentage: " + str(percentage_thirdparty_cookies))
    print("Percentage of websites of third party cookies: " + str(percentage_with_thirdparty_cookies))
    print("Average amount of third party cookies: " + str(avg_thirdparty_cookies))
    print("Average amount of third party cookies for the amount of websites that have third party cookies: " + str(avg_thirdparty_cookies_for_present))

def tracker_stats(filename):
    processedCookies = process_cookies(filename)

    totalTrackers = 0
    websitesWithTrackers = 0

    shouldCount = True
    for website in processedCookies:
        totalCookies = processedCookies[website]["frontpage"] + processedCookies[website]["hopped"]
        for cookie in totalCookies:
            if len(cookie["trackers_list"]) > 0:
                totalTrackers += 1
                if shouldCount:
                    websitesWithTrackers += 1
                    shouldCount = False

        shouldCount = True


    percentage_websites_with_trackers = websitesWithTrackers / len(processedCookies)
    avg_trackers = totalTrackers / len(processedCookies)
    avg_trackers_for_tracker_website = totalTrackers / websitesWithTrackers

    print(filename)
    print("Total trackers: " + str(totalTrackers))
    print("Percentage of websites with trackers: " + str(percentage_websites_with_trackers))
    print("Average trackers for all websites: " + str(avg_trackers))
    print("Average trackers for all websites with trackers: " + str(avg_trackers_for_tracker_website))

def expiry_time_graph(filename, outfile):
    processedCookies = process_cookies(filename)

    data = {"session": [], "hour": [], "day": [], "month": [], "year": [], "greaterthanyear": []}  # Percentages
    sortedCookies = {"fp": [], "tp": [], "tpt": []}

    # Sort cookies based on their category
    for website in processedCookies:
        cookies = processedCookies[website]["frontpage"] + processedCookies[website]["hopped"]
        for cookie in cookies:
            if not cookie["third_party"]:
                sortedCookies["fp"].append(cookie)
            else:
                if len(cookie["trackers_list"]) > 0:
                    sortedCookies["tpt"].append(cookie)
                else:
                    sortedCookies["tp"].append(cookie)

    times = [3600, 86400, 2629743, 31536000]
    timeNames = ["hour", "day", "month", "year"]

    # Session & more than a year
    for cookieType in sortedCookies:
        cookies = sortedCookies[cookieType]
        count = {"session": 0, "hour": 0, "day": 0, "month": 0, "year": 0, "greaterthanyear": 0}

        for cookie in cookies:
            if cookie["time_to_live"] <= 0:
                count["session"] += 1
            elif cookie["time_to_live"] > 31536000:
                count["greaterthanyear"] += 1
            elif cookie["time_to_live"] < times[0]:
                count["hour"] += 1
            else:
                current_time_to_live = cookie["time_to_live"]
                # Find out between which times it is
                for x in range(4):
                    if times[x] <= current_time_to_live <= times[x + 1]:
                        if current_time_to_live - times[x] >= times[x + 1] - current_time_to_live:
                            count[timeNames[x+1]] += 1
                        else:
                            count[timeNames[x]] += 1
                        break

        # Calculate percentages
        for timespan in data:
            percentage = (count[timespan] / len(cookies)) * 100
            data[timespan].append(percentage)

    total = [0, 0, 0]
    for timespan in data:
        for x in range(len(data[timespan])):
            total[x] += data[timespan][x]
    print(total)
    # Making graph
    index = np.arange(3) + 0.3

    print(index)
    leftCoordinates = {"session":[0,0,0], "hour": [0,0,0], "day": [0,0,0], "month": [0,0,0], "year": [0,0,0], "greaterthanyear": [0,0,0]}
    allNames = ["session", "hour", "day", "month", "year", "greaterthanyear"]
    # offsets
    for x in range(1, len(allNames)):
        for y in range(len(leftCoordinates[allNames[x]])):
            leftCoordinates[allNames[x]][y] += leftCoordinates[allNames[x-1]][y] + data[allNames[x-1]][y]

    plt.figure(figsize=(5,4))
    plt.barh(index, width=data["session"], height=0.6, label="session")
    plt.barh(index, width=data["hour"], height=0.6, left=leftCoordinates["hour"], label="hour")
    plt.barh(index, width=data["day"], height=0.6, left=leftCoordinates["day"], label="day")
    plt.barh(index, width=data["month"], height=0.6, left=leftCoordinates["month"], label="month")
    plt.barh(index, width=data["year"], height=0.6, left=leftCoordinates["year"], label="year")
    plt.barh(index, width=data["greaterthanyear"], height=0.6, left=leftCoordinates["greaterthanyear"], label="More than a year")

    plt.yticks(index, ["FP" + "(" + str(len(sortedCookies["fp"])) + ")", "TP" + "(" + str(len(sortedCookies["tp"])) + ")", "TPT" + "(" + str(len(sortedCookies["tpt"])) + ")"])
    plt.xticks(np.arange(start=0, stop=100, step=20) + 20)
    plt.margins(x=0)
    plt.xlabel("Percentage %")

    plt.legend(loc='upper center', bbox_to_anchor=(0.5,-0.12), ncol=3)
    print("d")
    plt.savefig(outfile, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    frontpage_vs_hop_cookies("out/government-out.json", "graphs/government_frontpage_vs_hopped_cookies_bar.png")
    frontpage_vs_hop_cookies("out/health-out.json", "graphs/health_frontpage_vs_hopped_cookies_bar.png")
    frontpage_vs_hop_cookies("out/universities-out.json", "graphs/universities_frontpage_vs_hopped_cookies_bar.png")

    total_cookies_vs_thirdparty_cookies("out/government-out.json", "graphs/government_total_vs_thirdparty.png")
    total_cookies_vs_thirdparty_cookies("out/health-out.json", "graphs/health_total_vs_thirdparty.png")
    total_cookies_vs_thirdparty_cookies("out/universities-out.json", "graphs/universities_total_vs_thirdparty.png")

    #thirdparty_stats("out/government-out.json")
    #thirdparty_stats("out/health-out.json")
    #thirdparty_stats("out/universities-out.json")

    #tracker_stats("out/government-out.json")
    #tracker_stats("out/health-out.json")
    #tracker_stats("out/universities-out.json")

    expiry_time_graph("out/government-out.json", "graphs/gov-time-to-live-graph.png")
    expiry_time_graph("out/health-out.json", "graphs/health-time-to-live-graph.png")
    expiry_time_graph("out/universities-out.json", "graphs/universities-time-to-live-graph.png")
