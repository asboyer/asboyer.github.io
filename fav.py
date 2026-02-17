import argparse
import requests
import shutil
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from secret import client_id, client_secret

from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')

# Separate key=value overrides from positional args before argparse
import sys
raw_args = sys.argv[1:]
positional = []
field_overrides = {}
for arg in raw_args:
    if '=' in arg and not arg.startswith('http'):
        key, value = arg.split('=', 1)
        field_overrides[key] = value
    else:
        positional.append(arg)

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Download an image and move it to a specific directory.')
parser.add_argument('link', type=str, help='The URL of the image to download.')
parser.add_argument('category', type=str, help='The category of the image.')
parser.add_argument('image_name', type=str, nargs='?', default='default.jpg', help='The name to give to the image.')

args = parser.parse_args(positional)

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
        release_date = result['album'].get('release_date', '')
    else:
        args.link = result['images'][0]['url']
        release_date = result.get('release_date', '')

    if release_date:
        extra_field += f'\nreleased: {release_date[:4]}'

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
    og_title = soup.find('meta', property='og:title')['content']
    title = og_title.split(' (')[0].strip()
    released = og_title.split('(')[-1].split(')')[0].strip() if '(' in og_title else ''
    args.link = soup.find('meta', property='og:image')['content']
    args.image_name = title.lower().replace(" ", "_") + '.jpg'
    director_tag = soup.find('meta', attrs={'name': 'description'})
    creator = director_tag['content'].split('Directed by ')[-1].split('.')[0].strip() if director_tag and 'Directed by' in director_tag.get('content', '') else 'Unknown'
    extra_field += f'\nreleased: {released}' if released else ''

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

# Build category-specific fields
fields = []
fields.append(f'layout: fav')
fields.append(f'date: {today}')
fields.append(f'author: Andrew Boyer')
fields.append(f'title: {title}')
fields.append(f'creator: {creator}')
fields.append(f'img: assets/img/favs/{args.category}/{args.image_name}')
fields.append(f'categories: {args.category}')
fields.append(f'link: {link}')

if args.category in ['movies', 'shows']:
    fields.append(f'released: {extra_field.split("released: ")[-1].strip()}' if 'released' in extra_field else 'released:')
    fields.append('started:')
    fields.append('finished:')
    fields.append('stars:')
    fields.append('star_link:')
    fields.append('imdb_link:')
    fields.append('perfect:')
    fields.append('opener: |')
elif args.category == 'books':
    fields.append('released:')
    fields.append('started:')
    fields.append('finished:')
    fields.append('stars:')
    fields.append('star_link:')
    fields.append('perfect:')
    fields.append('opener: |')
elif args.category == 'albums':
    fields.append(f'released: {extra_field.split("released: ")[-1].strip()}' if 'released' in extra_field else 'released:')
    fields.append('score:')
    fields.append('vinyl:')
    fields.append('vinyl_link:')
    fields.append('perfect:')
elif args.category == 'songs':
    if 'album_link' in extra_field:
        for line in extra_field.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('released:'):
                fields.append(line)
    else:
        fields.append('album:')
        fields.append('album_link:')
    fields.append(f'released: {extra_field.split("released: ")[-1].strip()}' if 'released' in extra_field else 'released:')
    fields.append('score:')
    fields.append('vinyl:')
    fields.append('perfect:')
elif args.category == 'playlists':
    fields.append('perfect:')
else:
    fields.append('perfect:')
    fields.append('opener: |')

# Apply field overrides
for i, field in enumerate(fields):
    key = field.split(':')[0]
    if key in field_overrides:
        fields[i] = f'{key}: {field_overrides[key]}'

# Auto-set perfect based on score/stars thresholds
perfect_thresholds = {
    'songs': ('score', 95),
    'albums': ('score', 9.5),
    'books': ('stars', 4.5),
    'movies': ('stars', 4.5),
    'shows': ('score', 9),
}
if args.category in perfect_thresholds:
    rating_field, threshold = perfect_thresholds[args.category]
    for field in fields:
        if field.startswith(f'{rating_field}:'):
            val = field.split(':', 1)[1].strip()
            if val:
                try:
                    if float(val) >= threshold:
                        for j, f in enumerate(fields):
                            if f.startswith('perfect:'):
                                fields[j] = 'perfect: true'
                except ValueError:
                    pass
            break

markdown_content = '---\n' + '\n'.join(fields) + '\n---\n'

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

year = datetime.now().strftime('%Y')
favs_year_path = f'_pages/favs_{year}.md'
if not os.path.exists(favs_year_path):
    markdown_content = '''---
layout: page
title: favs from {year}
permalink: /favs/{year}/
description: favorite things from {year}
year: "{year}"
---

{{% include archive_list.liquid archive="{year}" %}}
'''.format(year=year)
    with open(favs_year_path, 'w') as f:
        f.write(markdown_content)