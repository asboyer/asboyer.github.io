import argparse
import requests
import shutil
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from secret import client_id, client_secret

from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Download an image and move it to a specific directory.')
parser.add_argument('link', type=str, help='The URL of the image to download.')
parser.add_argument('category', type=str, help='The category of the image.')
parser.add_argument('image_name', type=str, nargs='?', default='default.jpg', help='The name to give to the image.')

args = parser.parse_args()

title = "a favorite " + args.category
creator = "creator of the " + args.category
categories = args.category
link = args.link
extra_field = ""

if args.category in ['albums', 'songs', 'playlists', 'artists']:
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    link = args.link
    if args.category == 'albums':
        # differentiate song and album
        result = sp.album(args.link)
        artist_list = []
        for artist in result['artists']:
            artist_list.append(artist['name'])
        artists_string = ''
        for i in range(len(artist_list)):
            if i == len(artist_list) - 1:
                artists_string += artist_list[i]
            else:
                artists_string += f'{artist_list[i]}, '
        creator = artists_string
    elif args.category == 'songs':
        result = sp.track(args.link)
        artist_list = []
        for artist in result['artists']:
            artist_list.append(artist['name'])
        artists_string = ''
        for i in range(len(artist_list)):
            if i == len(artist_list) - 1:
                artists_string += artist_list[i]
            else:
                artists_string += f'{artist_list[i]}, '
        creator = artists_string
    elif args.category == 'playlists':
        result = sp.playlist(args.link)
        creator = result['owner']['display_name']
    elif args.category == 'artists':
        result = sp.artist(args.link)

    if args.category == 'songs':
        args.link = result['album']['images'][0]['url']
        extra_field = f'\nalbum_link: {result["album"]["external_urls"]["spotify"]}'
        extra_field += f'\nalbum: {result["album"]["name"]}'
    else:
        args.link = result['images'][0]['url']
    
    title = result['name'].replace(".", "").replace("(", "").replace(")", "").replace("/", "")
    args.image_name = title.lower().replace(" ", "_") + '.jpeg'

if args.category in ['movies', 'shows']:
    from bs4 import BeautifulSoup
    link = args.link
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    r = requests.get(args.link, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.find('meta', property='og:title')['content'].split(' (')[0].strip()
    args.link = soup.find('meta', property='og:image')['content']
    args.image_name = title.lower().replace(" ", "_") + '.jpg'
    director_tag = soup.find('meta', attrs={'name': 'description'})
    creator = director_tag['content'].split('Directed by ')[-1].split('.')[0].strip() if director_tag and 'Directed by' in director_tag.get('content', '') else 'Unknown'

# Download the image
response = requests.get(args.link, stream=True)
response.raise_for_status()

# Save the image to a temporary file
with open('/tmp/temp_image', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)

# Move the image to the specified directory with the specified name
destination_dir = f'./assets/img/favs/{args.category}'
os.makedirs(destination_dir, exist_ok=True)
shutil.move('/tmp/temp_image', f'{destination_dir}/{args.image_name}')

markdown_file_path = os.path.join("_favs", args.image_name.split('.')[0] + '.md')

# Create the markdown content
markdown_content = '''---
layout: fav
date: {date}
author: Andrew Boyer
title: {title}
creator: {creator}
img: assets/img/favs/{category}/{image_name}
categories: {category}
link: {link}{extra_field}
---
'''.format(date=today, title=title, creator=creator, image_name=args.image_name, link=link, category=args.category, extra_field=extra_field)

# Write the markdown content to the file
with open(markdown_file_path, 'w') as f:
    f.write(markdown_content)

markdown_content = '''---
layout: page
title: {category}s
permalink: /favs/{category}s/
description: list of {category} recommendations
---

{{% include archive_list.liquid category="{category}s" %}}
'''.format(category=args.category[:-1])

with open(f'_pages/{args.category}.md', 'w') as f:
    f.write(markdown_content)

markdown_content = '''---
layout: page
title: {year} {category} list
permalink: /favs/{year}/{category}/
description: favorite {category}s of {year}
---

{{% include archive_list.liquid category="{category}s" archive="{year}" %}}
'''.format(category=args.category[:-1], year=datetime.now().strftime('%Y'))

with open(f"_pages/{args.category}-{datetime.now().strftime('%Y')}.md", 'w') as f:
    f.write(markdown_content)