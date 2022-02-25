# IN4253ET-HackingLab
## About
### Why
Cooooookiiies
### How
This project only focusses on the websites owned by the Dutch government. The domains used for this project were fetched from the Dutch goverrnment [website](https://www.overheid.nl/english/dutch-government-websites). Using the script in this repository it is possible to fetch all the domain names automatically.

TODO: add univeristies, hospitals, police & banks to the list

## Setup
This project makes use of Python3. In order to run this repository the dependencies of the [Pythia](https://bitbucket.org/srdjanmatic/pythia/src/master/) library are required. Run the following command to install all dependencies:

```console
$ pip3 install --upgrade ipwhois tldextract wordsegment selenium bs4 dnspython intervaltree netaddr nltk psutil
```

Google Chrome aswell as the corresponding [Chrome Driver](https://chromedriver.chromium.org/downloads) should be installed on the OS aswell. Make sure to download the correct driver version. This should match the version of the install Google Chrome browser. The Chrome Driver should be located in the Pythia folder and chrome path should be the following: 
C:\Program Files\Google\Chrome\Application\chrome.exe