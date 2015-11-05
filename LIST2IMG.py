__author__ = 'rcktscnc'

import unicodedata
import os
import time
import urllib.request
import simplejson
import logging
import cfg

print("MAKE SURE YOU HAVE A FOLDER NAMED \"images\" AND A *.txt \n"
      "FILE NAMED \"list\" IN THE SAME FOLDER AS THE EXECUTABLE.\n"
      "\nby rcktscnc (2015)\n")

logging.basicConfig(filename='errlog.txt', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

if cfg.additionalParam in {'None', 'none', 'NONE', '0', ''}:
    additionalParam = input("ADDITIONAL SEARCH PARAMETERS: ")
else:
    additionalParam = cfg.additionalParam
    print('ADDITIONAL SEARCH PARAMETERS: ' + cfg.additionalParam)

additionalParam = additionalParam.replace(' ', '%20')
additionalParam = '%20' + additionalParam + '%20'

# Start FancyURLopener with defined version
class MyOpener(urllib.request.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'


# Start Request with overridden function
class HeadRequest(urllib.request.Request):
    def get_method(self):
        return 'HEAD'


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11'
                     ' (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Referer': 'testing.com',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

myopener = MyOpener()
DIR = os.getcwd() + "\\images\\"
TOTALIMGCOUNT = 0
searchTerm = "place_holder"
fname = "list.txt"
pageCount = 0

with open(fname) as f:
    listContent = f.read().splitlines()

for i in listContent:
    searchTerm = i
    IMGCOUNT = 0
    pageCount = 0
    print("\nSEARCHING IMAGES FOR " + "\"" + searchTerm + "\"")

    # Replace spaces ' ' in search term for '%20' in order to comply with request
    searchTerm = searchTerm.replace(' ', '%20')
    # Remove Accents (diatrics)
    searchTermNoAcc = remove_accents(searchTerm)
    additionalParamNoAcc = remove_accents(additionalParam)
    # Pretty file name with underscore
    searchTerm = searchTerm.replace('%20', '_')

    while IMGCOUNT < int(cfg.resultsPerItem):
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
               'v=1.0&q=' + additionalParamNoAcc + searchTermNoAcc + '&imgsz=' + cfg.imgSize +
               '&rsz=6&start=' + str(pageCount*6) + '&userip=MyIP')

        request = urllib.request.Request(url, None, {'Referer': 'testing'})

        try:
            response = urllib.request.urlopen(request)
        except:
            print("ERROR: BROKEN URL")
            logger.error("BROKEN URL: " + url)
            break

        # Get results using JSON
        results = simplejson.load(response)
        data = results['responseData']

        try:
            dataInfo = data['results']
        except:
            print("ERROR: LACK OF RESULTS")
            logger.error("LACK OF RESULTS: " + url)
            break

        # Set count to 0
        count = 0

        # Iterate for each result and get unescaped url
        for myUrl in dataInfo:
            if IMGCOUNT < int(cfg.resultsPerItem):
                count += 1
                imgResponse = None
                headrequest = HeadRequest(myUrl['unescapedUrl'], headers=hdr)

                try:
                    imgResponse = urllib.request.urlopen(headrequest)
                except:
                    print("ERROR: IMAGE REQUEST FAILED")
                    logger.error("REQUEST FAILED: " + myUrl['unescapedUrl'])
                finally:
                    if imgResponse is not None:
                        try:
                            maintype = imgResponse.headers['Content-Type'].split(';')[0].lower()
                        except:
                            print("ERROR: CAN'T READ HEADER")
                            logger.error("CAN'T READ HEADER: " + myUrl['unescapedUrl'])
                        finally:
                            if imgResponse.headers is not None:
                                if maintype not in ('image/png', 'image/jpeg', 'image/gif', 'image/jpg'):
                                    print('ERROR: INVALID FILE REJECTED')
                                    logger.error("FILE REJECTED: " + myUrl['unescapedUrl'])
                                else:
                                    IMGCOUNT += 1
                                    TOTALIMGCOUNT += 1
                                    print(myUrl['unescapedUrl'])
                                    myopener.retrieve(myUrl['unescapedUrl'], DIR + searchTerm + "_" +
                                                      str(IMGCOUNT) + '.jpg')
            else:
                break

        pageCount += 1

        # Sleep for one second to prevent IP blocking from Google
        time.sleep(1)

print("\nTHE SEARCH RETURNED " + str(TOTALIMGCOUNT) + " IMAGES")
input("PRESS ENTER TO EXIT...")
