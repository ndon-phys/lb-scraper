import requests
from cookiestxt import MozillaCookieJar
import json
import math
from PIL import Image
import os

print('Enter book id:')
book_id = input()
print('Enter jwt-Authorization token')
token = input()

# Start a persistent browsing session
s = requests.Session()

# Load cookies
cookies = MozillaCookieJar('cookies.txt')
cookies.load()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language' : 'de,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding' : 'gzip, deflate, br',
    'PSPDFKit-Platform': 'web',
    # You may need to periodically update the client info
    'PSPDFKit-Version': 'protocol=5, client=2024.4.0, client-git=ffbc8fcc48',
    'Origin': 'https://ebook.cornelsen.de',
    'Referer': 'https://ebook.cornelsen.de',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'TE': 'trailers',
}

# Get authorization tokens
url = "https://pspdfkit.prod.cornelsen.de/i/d/" + book_id + "/auth"
auth_req = {'jwt': token, "origin":"https://unterrichtsmanager.cornelsen.de/" + book_id + "/start"}
r = s.post(url, json=auth_req, headers=headers)
auth = json.loads(r.text)
pspdf_token = auth['token']
image_token = auth['imageToken']
layer_handle = auth['layerHandle']
# Get the highest resolution allowed
scale = auth['allowedTileScales'][-1]
# Scale is given as a factor of the area, we need factor of length, so we take the squareroot
scale = math.sqrt(int(scale))

# Get picture urls
url = "https://pspdfkit.prod.cornelsen.de/i/d/" + book_id + "/h/" + layer_handle + "/document.json"
headers['X-PSPDFKit-Token'] = pspdf_token
headers['X-PSPDFKit-Image-Token'] = image_token
r = s.get(url, headers=headers)
index = json.loads(r.text)['data']

# Loop through pages
pagenr = 0
for page in index['pages']:
    # Get width and height of picture respecting max scale
    height = int(page['height'] * scale) + 1
    width = int(page['width'] * scale) + 1
    # Calculate table of individual tiles
    slice_x = 0
    stripe_names = []
    for x in range(0, width, 507):
        slice_y = 0
        image_names = []
        for y in range(0, height, 507):
            tileurl = "https://pspdfkit.prod.cornelsen.de/i/d/" \
                    + str(book_id) \
                    + "/h/" + layer_handle \
                    + "/page-" + str(pagenr) \
                    + "-dimensions-" + str(width) + "-" + str(height) \
                    + "-tile-" + str(x) + "-" + str(y) + "-512-512"
            r = s.get(tileurl, headers=headers)
            fname = str(pagenr) + "-" + str(slice_x) + "-" + str(slice_y) + ".png"
            open(fname, 'wb').write(r.content)
            image_names.append(fname)
            slice_y = slice_y + 1
        images = [Image.open(x) for x in image_names]
        widths, heights = zip(*(i.size for i in images))
        total_width = max(widths)
        total_height = sum(heights)
        new_im = Image.new('RGB', (total_width, total_height))
        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += 507
        sname = str(pagenr) + '-' + str(slice_x) + '.png'
        new_im.save(sname)
        stripe_names.append(sname)
        for tile in image_names:
            os.remove(tile)
        slice_x = slice_x + 1
    images = [Image.open(x) for x in stripe_names]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += 507
    new_im.crop((0, 0, width, height)).save(str(pagenr).zfill(4) + '.png')
    for tile in stripe_names:
        os.remove(tile)
    pagenr = pagenr + 1
