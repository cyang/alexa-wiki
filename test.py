from bs4 import BeautifulSoup
from urllib2 import Request, urlopen, URLError, HTTPError

WIKI_URL = "https://en.wikipedia.org/wiki/"

topic = "Net Neutrality"
req = WIKI_URL + topic.replace(" ", "_")
try:
    response = urlopen(req)
except HTTPError as e:
    print 'The server couldn\'t fulfill the request.'
    print 'Error code: ', e.code
except URLError as e:
    print 'We failed to reach a server.'
    print 'Reason: ', e.reason
else:
    # everything is fine
    soup = BeautifulSoup(response, 'html.parser')
    print(soup.find("div", {"class" : 'mw-parser-output'}).\
            find("p", recursive=False).get_text())


