import argparse
import requests
import shutil
import os
import re
from urllib.parse import urlparse

from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Separate key=value overrides from positional args before argparse
import sys

raw_args = sys.argv[1:]
positional = []
field_overrides = {}
for arg in raw_args:
    if "=" in arg and not arg.startswith("http"):
        key, value = arg.split("=", 1)
        field_overrides[key] = value
    else:
        positional.append(arg)

# Set up command-line argument parsing
parser = argparse.ArgumentParser(
    description="Download an image and move it to a specific directory."
)
parser.add_argument("link", type=str, help="The URL of the image to download.")
parser.add_argument("category", type=str, help="The category of the image.")
parser.add_argument(
    "image_name",
    type=str,
    nargs="?",
    default="default.jpg",
    help="The name to give to the image.",
)

args = parser.parse_args(positional)

# ─── Category Configuration ──────────────────────────────────────────────────
# Each category lists its extra frontmatter fields (beyond the common ones).
# To add a new category, just add an entry here.
CATEGORY_FIELDS = {
    "movies": [
        "released",
        "redirect",
        "started",
        "finished",
        "stars",
        "star_link",
        "imdb_link",
        "perfect",
        "opener: |",
    ],
    "shows": [
        "released",
        "redirect",
        "started",
        "finished",
        "stars",
        "star_link",
        "imdb_link",
        "perfect",
        "opener: |",
    ],
    "episodes": [
        "season",
        "episode",
        "show",
        "show_link",
        "released",
        "redirect",
        "score",
        "imdb_link",
        "perfect",
        "opener: |",
    ],
    "books": [
        "released",
        "redirect",
        "started",
        "finished",
        "stars",
        "star_link",
        "perfect",
        "opener: |",
    ],
    "albums": ["released", "redirect", "score", "vinyl", "vinyl_link", "perfect"],
    "songs": [
        "album",
        "album_link",
        "released",
        "redirect",
        "score",
        "vinyl",
        "perfect",
    ],
    "playlists": ["redirect", "perfect"],
    "artists": ["redirect", "perfect"],
    "articles": ["published", "publication", "redirect", "perfect", "opener: |"],
    "videos": ["redirect", "perfect", "opener: |"],
    "podcasts": ["published", "publication", "redirect", "perfect", "opener: |"],
}

# Default fields for any category not listed above
DEFAULT_FIELDS = ["redirect", "perfect", "opener: |"]

# Categories that should have square-cropped images
SQUARE_CROP_CATEGORIES = ["albums", "songs", "playlists", "artists"]

# Categories that use Spotify API
SPOTIFY_CATEGORIES = ["albums", "songs", "playlists", "artists"]

# Categories that use IMDB scraping
IMDB_CATEGORIES = ["movies", "shows", "episodes"]

# Categories that use Goodreads scraping
GOODREADS_CATEGORIES = ["books"]

# Categories that use generic og: scraping
OG_SCRAPE_CATEGORIES = ["articles", "videos", "podcasts"]

# Perfect score thresholds
PERFECT_THRESHOLDS = {
    "songs": ("score", 95),
    "albums": ("score", 9.5),
    "books": ("stars", 4.5),
    "movies": ("stars", 4.5),
    "shows": ("score", 9),
    "episodes": ("score", 9.5),
}

# ─── Helpers ─────────────────────────────────────────────────────────────────


def sanitize_title(t):
    """Strip special characters from a title."""
    # Replace common unicode quotes/dashes with ASCII equivalents
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", "").replace("\u201d", "")
    t = t.replace("\u2013", "-").replace("\u2014", "-")
    # Strip special characters
    t = re.sub(r"[.()/\[\]{}<>:;!@#$%^&*~`|\\,\'\"\u00e2\u0080\u0099]", "", t)
    # Collapse multiple spaces
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def clean_author(s):
    """Strip photographer credits and other noise from author strings."""
    # Cut at common suffixes
    for sep in [
        "Photographs by",
        "Photography by",
        "Photos by",
        "Illustration by",
        "Illustrated by",
        "Video by",
    ]:
        if sep in s:
            s = s.split(sep)[0]
    # Clean up trailing separators
    s = re.sub(r"[\s,;|/]+$", "", s)
    return s.strip()


def detect_platform(url):
    """Detect the platform from a URL."""
    host = urlparse(url).hostname or ""
    if "spotify" in host:
        return "spotify"
    elif "youtube" in host or "youtu.be" in host:
        return "youtube"
    elif "soundcloud" in host:
        return "soundcloud"
    else:
        return "other"


def extract_youtube_video_id(url):
    """Extract the video/playlist ID from a YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    from urllib.parse import parse_qs

    qs = parse_qs(parsed.query)
    return qs.get("v", [None])[0] or qs.get("list", [None])[0]


def crop_to_square(image_path):
    """Crop an image to a square (center crop) if it isn't already square."""
    from PIL import Image

    img = Image.open(image_path)
    w, h = img.size
    if w == h:
        return
    fmt = img.format or "JPEG"
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img.save(image_path, format=fmt)


def scrape_og(url, headers):
    """Scrape og:title, og:image, og:site_name, and meta description from a URL."""
    from bs4 import BeautifulSoup

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    og_title_tag = soup.find("meta", property="og:title")
    og_image_tag = soup.find("meta", property="og:image")
    og_site_tag = soup.find("meta", property="og:site_name")
    og_desc_tag = soup.find("meta", property="og:description")
    desc_tag = soup.find("meta", attrs={"name": "description"})

    # Try multiple common author meta tags
    author = None
    for tag in [
        soup.find("meta", attrs={"name": "author"}),
        soup.find("meta", property="article:author"),
        soup.find("meta", attrs={"name": "sailthru.author"}),
        soup.find("meta", property="og:article:author"),
    ]:
        if tag and tag.get("content"):
            author = tag["content"]
            break

    # Try to get published date
    published = None
    for tag in [
        soup.find("meta", property="article:published_time"),
        soup.find("meta", attrs={"name": "date"}),
        soup.find("meta", property="og:article:published_time"),
        soup.find("meta", attrs={"name": "publish-date"}),
    ]:
        if tag and tag.get("content"):
            published = tag["content"][:10]  # YYYY-MM-DD
            break

    return {
        "soup": soup,
        "title": og_title_tag["content"] if og_title_tag else None,
        "image": og_image_tag["content"] if og_image_tag else None,
        "site_name": og_site_tag["content"] if og_site_tag else None,
        "description": desc_tag["content"] if desc_tag else None,
        "og_description": og_desc_tag["content"] if og_desc_tag else None,
        "author": author,
        "published": published,
    }


# ─── Main Logic ──────────────────────────────────────────────────────────────

title = "a favorite " + args.category
creator = "creator of the " + args.category
categories = args.category
link = args.link
extra_field = ""

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

if args.category in SPOTIFY_CATEGORIES:
    platform = detect_platform(args.link)

    if platform == "spotify":
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        from secret import client_id, client_secret

        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        link = args.link
        if args.category == "albums":
            result = sp.album(args.link)
            artist_list = []
            for artist in result["artists"]:
                artist_list.append(artist["name"])
            artists_string = ""
            for i in range(len(artist_list)):
                if i == len(artist_list) - 1:
                    artists_string += artist_list[i]
                else:
                    artists_string += f"{artist_list[i]}, "
            creator = artists_string
        elif args.category == "songs":
            result = sp.track(args.link)
            artist_list = []
            for artist in result["artists"]:
                artist_list.append(artist["name"])
            artists_string = ""
            for i in range(len(artist_list)):
                if i == len(artist_list) - 1:
                    artists_string += artist_list[i]
                else:
                    artists_string += f"{artist_list[i]}, "
            creator = artists_string
        elif args.category == "playlists":
            result = sp.playlist(args.link)
            creator = result["owner"]["display_name"]
        elif args.category == "artists":
            result = sp.artist(args.link)

        if args.category == "songs":
            args.link = result["album"]["images"][0]["url"]
            extra_field = f'\nalbum_link: {result["album"]["external_urls"]["spotify"]}'
            extra_field += f'\nalbum: {result["album"]["name"]}'
            release_date = result["album"].get("release_date", "")
        else:
            args.link = result["images"][0]["url"]
            release_date = result.get("release_date", "")

        if release_date:
            extra_field += f"\nreleased: {release_date[:4]}"

        title = sanitize_title(result["name"])
        args.image_name = title.lower().replace(" ", "_") + ".jpeg"

    elif platform == "youtube":
        link = args.link
        og = scrape_og(args.link, headers)

        title = sanitize_title(og["title"] or "Unknown")

        if og["image"]:
            args.link = og["image"]
        else:
            video_id = extract_youtube_video_id(args.link)
            if video_id:
                args.link = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

        uploader_tag = og["soup"].find("link", itemprop="name")
        if uploader_tag:
            creator = sanitize_title(uploader_tag.get("content", "Unknown"))
        else:
            creator = sanitize_title(og["site_name"] or "Unknown")

        args.image_name = title.lower().replace(" ", "_") + ".jpg"

    elif platform == "soundcloud":
        link = args.link
        og = scrape_og(args.link, headers)

        full_title = og["title"] or "Unknown"
        if " by " in full_title:
            title, creator = full_title.rsplit(" by ", 1)
            creator = sanitize_title(creator)
        else:
            title = full_title
        title = sanitize_title(title)

        if og["image"]:
            args.link = og["image"]

        args.image_name = title.lower().replace(" ", "_") + ".jpg"

    elif platform == "other":
        link = args.link
        if "title" in field_overrides:
            title = field_overrides["title"]
        if "creator" in field_overrides:
            creator = field_overrides["creator"]

        try:
            og = scrape_og(args.link, headers)
            if og["image"]:
                args.link = og["image"]
            elif "img_url" in field_overrides:
                args.link = field_overrides["img_url"]
            else:
                print("Warning: No image found. Provide img_url=<url> override.")
        except Exception:
            if "img_url" in field_overrides:
                args.link = field_overrides["img_url"]
            else:
                print("Warning: Could not scrape page. Provide img_url=<url> override.")

        title = sanitize_title(title)
        args.image_name = title.lower().replace(" ", "_") + ".jpg"

elif args.category in GOODREADS_CATEGORIES:
    import json as _json

    link = args.link
    og = scrape_og(args.link, headers)

    # Parse JSON-LD for structured book data
    book_data = {}
    for script in og["soup"].find_all("script", type="application/ld+json"):
        try:
            data = _json.loads(script.string)
            if data.get("@type") == "Book":
                book_data = data
                break
        except (ValueError, TypeError):
            pass

    if book_data:
        raw_name = book_data.get("name", "")
        # Unescape HTML entities
        from html import unescape

        raw_name = unescape(raw_name)
        title = sanitize_title(raw_name)
        authors = book_data.get("author", [])
        if isinstance(authors, list):
            creator = ", ".join(sanitize_title(a.get("name", "")) for a in authors)
        elif isinstance(authors, dict):
            creator = sanitize_title(authors.get("name", "Unknown"))
    else:
        title = sanitize_title(og["title"] or "Unknown")
        creator = sanitize_title(og["author"] or "Unknown")

    # Get publication year from page
    pub_info = og["soup"].find("p", attrs={"data-testid": "publicationInfo"})
    if pub_info:
        import re as _re

        year_match = _re.search(r"(\d{4})", pub_info.text)
        if year_match:
            extra_field += f"\nreleased: {year_match.group(1)}"

    if og["image"]:
        args.link = og["image"]
    elif "img_url" in field_overrides:
        args.link = field_overrides["img_url"]

    args.image_name = title.lower().replace(" ", "_") + ".jpg"

elif args.category in IMDB_CATEGORIES:
    import json as _json

    link = args.link
    og = scrape_og(args.link, headers)
    og_title = og["title"]
    desc = og["description"] or ""

    if args.category == "episodes":
        # Parse JSON-LD for episode data
        ep_data = {}
        for script in og["soup"].find_all("script", type="application/ld+json"):
            try:
                data = _json.loads(script.string)
                if data.get("@type") == "TVEpisode":
                    ep_data = data
                    break
            except (ValueError, TypeError):
                pass

        # Episode title from JSON-LD
        title = sanitize_title(
            ep_data.get("name", "") or og_title.split(" (")[0].strip()
        )

        # Director as creator
        directors = ep_data.get("director", [])
        if isinstance(directors, list) and directors:
            creator = ", ".join(
                sanitize_title(d.get("name", "")) for d in directors if d.get("name")
            )
        elif isinstance(directors, dict):
            creator = sanitize_title(directors.get("name", "Unknown"))
        else:
            creator = (
                desc.split("Directed by ")[-1].split(".")[0].strip()
                if "Directed by" in desc
                else "Unknown"
            )

        # Air date
        date_published = ep_data.get("datePublished", "")
        if date_published:
            extra_field += f"\nreleased: {date_published[:4]}"

        # Season and episode from page (S5.E14 format)
        import re as _re

        for el in og["soup"].find_all(
            attrs={"data-testid": _re.compile("hero-subnav")}
        ):
            se_match = _re.search(r"S(\d+)\.E(\d+)", el.text)
            if se_match:
                extra_field += f"\nseason: {se_match.group(1)}"
                extra_field += f"\nepisode: {se_match.group(2)}"
                break

        # Show name from og:title: "Show Name" Episode Title (TV Episode YYYY)
        show_name = ""
        show_match = _re.match(r'"([^"]+)"', og_title)
        if show_match:
            show_name = show_match.group(1)

        # Find parent show link
        show_link = ""
        for a in og["soup"].find_all("a", href=_re.compile(r"/title/tt\d+")):
            if a.text.strip() == show_name:
                href = a["href"].split("?")[0]
                if not href.endswith("/"):
                    href += "/"
                show_link = f"https://www.imdb.com{href}"
                break

        if show_name:
            extra_field += f"\nshow: {show_name}"
        if show_link:
            extra_field += f"\nshow_link: {show_link}"

        # Use the parent show's image instead of episode image
        if show_link:
            show_og = scrape_og(show_link, headers)
            if show_og["image"]:
                args.link = show_og["image"]
            else:
                args.link = og["image"]
        else:
            args.link = og["image"]

        args.image_name = title.lower().replace(" ", "_") + ".jpg"
    else:
        # Movies and shows
        title = sanitize_title(og_title.split(" (")[0].strip())
        released = (
            og_title.split("(")[-1].split(")")[0].strip() if "(" in og_title else ""
        )
        args.link = og["image"]
        args.image_name = title.lower().replace(" ", "_") + ".jpg"
        creator = (
            desc.split("Directed by ")[-1].split(".")[0].strip()
            if "Directed by" in desc
            else "Unknown"
        )
        extra_field += f"\nreleased: {released}" if released else ""

elif args.category in OG_SCRAPE_CATEGORIES:
    link = args.link
    og = scrape_og(args.link, headers)

    title = sanitize_title(og["title"] or "Unknown")

    # For Apple Podcasts, og:description has "Podcast Episode · ShowName · date · duration"
    og_desc = og.get("og_description") or ""
    host = urlparse(args.link).hostname or ""
    # Normalize middle dot separators (Â· is mojibake for ·)
    og_desc = og_desc.replace("\u00c2\u00b7", "\u00b7").replace("Â·", "·")
    if "podcasts.apple.com" in host and "·" in og_desc:
        parts = [p.strip() for p in og_desc.split("·")]
        # parts: ["Podcast Episode", "ShowName", "MM/DD/YYYY", "duration"]
        if len(parts) >= 2:
            creator = sanitize_title(parts[1])
        if len(parts) >= 3:
            # Parse date from MM/DD/YYYY to YYYY-MM-DD
            date_str = parts[2].strip()
            try:
                from datetime import datetime as dt

                parsed_date = dt.strptime(date_str, "%m/%d/%Y")
                extra_field += f'\npublished: {parsed_date.strftime("%Y-%m-%d")}'
            except ValueError:
                pass
        publication = sanitize_title(og["site_name"] or "")
    else:
        raw_author = og["author"] or ""
        creator = (
            sanitize_title(clean_author(raw_author))
            if raw_author
            else sanitize_title(og["site_name"] or "Unknown")
        )
        publication = sanitize_title(og["site_name"] or "")
        if og["published"]:
            extra_field += f'\npublished: {og["published"]}'

    if publication:
        extra_field += f"\npublication: {publication}"

    if og["image"]:
        args.link = og["image"]
    elif "img_url" in field_overrides:
        args.link = field_overrides["img_url"]
    else:
        print("Warning: No image found. Provide img_url=<url> override.")

    args.image_name = title.lower().replace(" ", "_") + ".jpg"

else:
    # Unknown category — try og: scraping, fall back to overrides
    link = args.link
    if "title" in field_overrides:
        title = field_overrides["title"]
    if "creator" in field_overrides:
        creator = field_overrides["creator"]

    try:
        og = scrape_og(args.link, headers)
        if og["title"] and "title" not in field_overrides:
            title = sanitize_title(og["title"])
        if og["site_name"] and "creator" not in field_overrides:
            creator = sanitize_title(og["site_name"])
        if og["image"]:
            args.link = og["image"]
        elif "img_url" in field_overrides:
            args.link = field_overrides["img_url"]
        else:
            print("Warning: No image found. Provide img_url=<url> override.")
    except Exception:
        if "img_url" in field_overrides:
            args.link = field_overrides["img_url"]
        else:
            print("Warning: Could not scrape page. Provide img_url=<url> override.")

    title = sanitize_title(title)
    args.image_name = title.lower().replace(" ", "_") + ".jpg"

# Download the image
response = requests.get(args.link, stream=True)
response.raise_for_status()

# Save the image to a temporary file
with open("/tmp/temp_image", "wb") as out_file:
    shutil.copyfileobj(response.raw, out_file)

# Crop to square if needed (e.g. YouTube thumbnails are 16:9)
if args.category in SQUARE_CROP_CATEGORIES:
    crop_to_square("/tmp/temp_image")

# Move the image to the specified directory with the specified name
destination_dir = f"./assets/img/favs/{args.category}"
os.makedirs(destination_dir, exist_ok=True)
shutil.move("/tmp/temp_image", f"{destination_dir}/{args.image_name}")

markdown_file_path = os.path.join("_favs", args.image_name.split(".")[0] + ".md")

# Build common fields
fields = []
fields.append(f"layout: fav")
fields.append(f"date: {today}")
fields.append(f"author: Andrew Boyer")
fields.append(f"title: {title}")
fields.append(f"creator: {creator}")
fields.append(f"img: assets/img/favs/{args.category}/{args.image_name}")
fields.append(f"categories: {args.category}")
fields.append(f"link: {link}")

# Build category-specific fields from config
category_fields = CATEGORY_FIELDS.get(args.category, DEFAULT_FIELDS)

# Special handling: songs with Spotify album info
if args.category == "songs" and "album_link" in extra_field:
    for line in extra_field.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("released:"):
            fields.append(line)
    # Skip album/album_link from the template since we just added them
    category_fields = [f for f in category_fields if f not in ("album", "album_link")]

for field_entry in category_fields:
    if ": " in field_entry:
        # Field with default value (e.g. 'opener: |')
        key = field_entry.split(":")[0]
    else:
        key = field_entry
        field_entry = f"{key}:"

    # Fill in values from extra_field if available
    if (
        key
        in (
            "released",
            "publication",
            "published",
            "season",
            "episode",
            "show",
            "show_link",
            "imdb_link",
        )
        and f"\n{key}: " in extra_field
    ):
        val = extra_field.split(f"{key}: ")[-1].split(chr(10))[0].strip()
        field_entry = f"{key}: {val}"

    fields.append(field_entry)

# Apply field overrides
for i, field in enumerate(fields):
    key = field.split(":")[0]
    if key in field_overrides:
        fields[i] = f"{key}: {field_overrides[key]}"

# Auto-set perfect based on score/stars thresholds
if args.category in PERFECT_THRESHOLDS:
    rating_field, threshold = PERFECT_THRESHOLDS[args.category]
    for field in fields:
        if field.startswith(f"{rating_field}:"):
            val = field.split(":", 1)[1].strip()
            if val:
                try:
                    if float(val) >= threshold:
                        for j, f in enumerate(fields):
                            if f.startswith("perfect:"):
                                fields[j] = "perfect: true"
                except ValueError:
                    pass
            break

markdown_content = "---\n" + "\n".join(fields) + "\n---\n"

# Write the markdown content to the file
with open(markdown_file_path, "w") as f:
    f.write(markdown_content)

markdown_content = """---
layout: page
title: {category}s
permalink: /favs/{category}s/
description: list of {category} recommendations
---

{{% include archive_list.liquid category="{category}s" %}}
""".format(
    category=args.category[:-1]
)

with open(f"_pages/{args.category}.md", "w") as f:
    f.write(markdown_content)

markdown_content = """---
layout: page
title: {year} {category} list
permalink: /favs/{year}/{categories}/
description: favorite {categories} of {year}
---

{{% include archive_list.liquid category="{categories}" archive="{year}" %}}
""".format(
    category=args.category[:-1],
    categories=args.category,
    year=datetime.now().strftime("%Y"),
)

with open(f"_pages/{args.category}-{datetime.now().strftime('%Y')}.md", "w") as f:
    f.write(markdown_content)

year = datetime.now().strftime("%Y")
favs_year_path = f"_pages/favs_{year}.md"
if not os.path.exists(favs_year_path):
    markdown_content = """---
layout: page
title: favs from {year}
permalink: /favs/{year}/
description: favorite things from {year}
year: "{year}"
---

{{% include archive_list.liquid archive="{year}" %}}
""".format(
        year=year
    )
    with open(favs_year_path, "w") as f:
        f.write(markdown_content)
