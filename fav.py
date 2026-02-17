import argparse
import requests
import shutil
import os
import re
from urllib.parse import urlparse

from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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


def sanitize_title(t):
    """Strip special characters from a title."""
    return re.sub(r'[.()/\[\]{}<>:;!@#$%^&*~`|\\]', '', t).strip()


def detect_platform(url):
    """Detect the platform from a URL."""
    host = urlparse(url).hostname or ''
    if 'spotify' in host:
        return 'spotify'
    elif 'youtube' in host or 'youtu.be' in host:
        return 'youtube'
    elif 'soundcloud' in host:
        return 'soundcloud'
    else:
        return 'other'


def extract_youtube_video_id(url):
    """Extract the video/playlist ID from a YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be',):
        return parsed.path.lstrip('/')
    from urllib.parse import parse_qs
    qs = parse_qs(parsed.query)
    return qs.get('v', [None])[0] or qs.get('list', [None])[0]


def crop_to_square(image_path):
    """Crop an image to a square (center crop) if it isn't already square."""
    from PIL import Image
    img = Image.open(image_path)
    w, h = img.size
    if w == h:
        return
    fmt = img.format or 'JPEG'
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img.save(image_path, format=fmt)


title = "a favorite " + args.category
creator = "creator of the " + args.category
categories = args.category
link = args.link
extra_field = ""

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

if args.category in ['albums', 'songs', 'playlists', 'artists']:
    platform = detect_platform(args.link)

    if platform == 'spotify':
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        from secret import client_id, client_secret

        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        link = args.link
        if args.category == 'albums':
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

        title = sanitize_title(result['name'])
        args.image_name = title.lower().replace(" ", "_") + '.jpeg'

    elif platform == 'youtube':
        from bs4 import BeautifulSoup

        link = args.link
        r = requests.get(args.link, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        og_title_tag = soup.find('meta', property='og:title')
        title = og_title_tag['content'] if og_title_tag else 'Unknown'
        title = sanitize_title(title)

        og_image_tag = soup.find('meta', property='og:image')
        if og_image_tag:
            args.link = og_image_tag['content']
        else:
            video_id = extract_youtube_video_id(args.link)
            if video_id:
                args.link = f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg'

        # Try to get uploader/artist
        uploader_tag = soup.find('link', itemprop='name')
        if uploader_tag:
            creator = sanitize_title(uploader_tag.get('content', 'Unknown'))
        else:
            og_site = soup.find('meta', property='og:site_name')
            creator = sanitize_title(og_site['content']) if og_site else 'Unknown'

        args.image_name = title.lower().replace(" ", "_") + '.jpg'

    elif platform == 'soundcloud':
        from bs4 import BeautifulSoup

        link = args.link
        r = requests.get(args.link, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        og_title_tag = soup.find('meta', property='og:title')
        full_title = og_title_tag['content'] if og_title_tag else 'Unknown'
        # SoundCloud og:title is often "Track by Artist"
        if ' by ' in full_title:
            title, creator = full_title.rsplit(' by ', 1)
            creator = sanitize_title(creator)
        else:
            title = full_title
        title = sanitize_title(title)

        og_image_tag = soup.find('meta', property='og:image')
        if og_image_tag:
            args.link = og_image_tag['content']

        args.image_name = title.lower().replace(" ", "_") + '.jpg'

    elif platform == 'other':
        from bs4 import BeautifulSoup

        link = args.link
        # For 'other' platform, title and creator should be provided via overrides
        if 'title' in field_overrides:
            title = field_overrides['title']
        if 'creator' in field_overrides:
            creator = field_overrides['creator']

        # Try to scrape an image
        try:
            r = requests.get(args.link, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            og_image_tag = soup.find('meta', property='og:image')
            if og_image_tag:
                args.link = og_image_tag['content']
            elif 'img_url' in field_overrides:
                args.link = field_overrides['img_url']
            else:
                print("Warning: No image found. Provide img_url=<url> override.")
        except Exception:
            if 'img_url' in field_overrides:
                args.link = field_overrides['img_url']
            else:
                print("Warning: Could not scrape page. Provide img_url=<url> override.")

        title = sanitize_title(title)
        args.image_name = title.lower().replace(" ", "_") + '.jpg'

elif args.category in ['movies', 'shows']:
    from bs4 import BeautifulSoup
    link = args.link
    r = requests.get(args.link, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    og_title = soup.find('meta', property='og:title')['content']
    title = sanitize_title(og_title.split(' (')[0].strip())
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

# Crop to square if needed (e.g. YouTube thumbnails are 16:9)
if args.category in ['albums', 'songs', 'playlists', 'artists']:
    crop_to_square('/tmp/temp_image')

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
    fields.append('redirect:')
    fields.append('started:')
    fields.append('finished:')
    fields.append('stars:')
    fields.append('star_link:')
    fields.append('imdb_link:')
    fields.append('perfect:')
    fields.append('opener: |')
elif args.category == 'books':
    fields.append('released:')
    fields.append('redirect:')
    fields.append('started:')
    fields.append('finished:')
    fields.append('stars:')
    fields.append('star_link:')
    fields.append('perfect:')
    fields.append('opener: |')
elif args.category == 'albums':
    fields.append(f'released: {extra_field.split("released: ")[-1].strip()}' if 'released' in extra_field else 'released:')
    fields.append('redirect:')
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
    fields.append('redirect:')
    fields.append('score:')
    fields.append('vinyl:')
    fields.append('perfect:')
elif args.category == 'playlists':
    fields.append('redirect:')
    fields.append('perfect:')
else:
    fields.append('redirect:')
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
permalink: /favs/{year}/{categories}/
description: favorite {categories} of {year}
---

{{% include archive_list.liquid category="{categories}" archive="{year}" %}}
'''.format(category=args.category[:-1], categories=args.category, year=datetime.now().strftime('%Y'))

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
