import requests
from cookiestxt import MozillaCookieJar
import json

print('Enter book id:')
book_id = input()
print('Enter Authorization token')
token = input()

# Helper function for download
def download_file(url, session):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
    return local_filename

# Start a persistent browsing session
s = requests.Session()

# Load cookies
cookies = MozillaCookieJar('cookies.txt')
cookies.load()

# Headers to imitate browser, might have to adjust
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language' : 'de,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Authorization' : token,
    'Origin': 'https://bibox2.westermann.de',
    'Referer': 'https://bibox2.westermann.de',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'TE': 'trailers',
}

# Get index json with all .jpg links
url = "https://backend.bibox2.westermann.de/v1/api/sync/" + book_id
params = {'materialtypes[]': 'default', 'materialtypes[]': 'addon'}
r = s.get(url, headers=headers)

# Empty list for page urls
jpg_urls = []

# Load as json
index = json.loads(r.text)

for page in index['pages']:
    # Last listed image is always the highest res
    jpg_urls.append(page['images'][-1]['url'])


# Local filenames for later processing
fnames = []
for jpg in jpg_urls:
    download_file(jpg, s)

# Add your own post-processing (maybe convert to pdf and join?)
# use fnames as a list
