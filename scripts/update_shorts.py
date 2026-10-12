#!/usr/bin/env python3
"""Refresh the website's latest four YouTube Shorts using the YouTube Data API.

Requires YOUTUBE_API_KEY environment variable. Does not print or persist the key.
"""
import html
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request
import urllib.error
API = 'https://www.googleapis.com/youtube/v3/'
PLAYLIST_ID = 'PLEwKIxLkJ-tw'
HTML_FILE = Path('index.html')


def youtube(endpoint, **params):
    params['key'] = os.environ['YOUTUBE_API_KEY']
    url = API + endpoint + '?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print("YouTube API error:", e.read().decode("utf-8"))
        raise

def seconds(iso):
    # Standard YouTube durations such as PT1M5S, PT59S, PT2M.
    match = re.fullmatch(r'P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not match:
        return None
    h, m, s = (int(x or 0) for x in match.groups())
    return h * 3600 + m * 60 + s


def latest_shorts():
    """Use the curated public Shorts playlist, newest video publication first."""
    ids = []
    token = None
    for _ in range(2):
        options = dict(part='snippet,contentDetails', playlistId=PLAYLIST_ID, maxResults=50)
        if token:
            options['pageToken'] = token
        batch = youtube('playlistItems', **options)
        # Collect IDs; playlist addition dates are not video publication dates.
        for item in batch.get('items', []):
            vid = item.get('contentDetails', {}).get('videoId')
            if vid:
                ids.append((item.get('snippet', {}).get('publishedAt', ''), vid))
        token = batch.get('nextPageToken')
        if not token:
            break

    ordered_ids = list(dict.fromkeys(vid for _, vid in ids))
    details = {}
    for start in range(0, len(ordered_ids), 50):
        batch = youtube('videos', part='snippet,status', id=','.join(ordered_ids[start:start + 50]))
        details.update((v['id'], v) for v in batch.get('items', []))

    ordered_ids.sort(key=lambda vid: (details.get(vid, {}).get('snippet', {}).get('publishedAt', ''), vid), reverse=True)
    shorts = []
    for vid in ordered_ids:
        video = details.get(vid)
        if not video or video.get('status', {}).get('privacyStatus') != 'public':
            continue
        thumbs = video['snippet'].get('thumbnails', {})
        thumb = next((thumbs[k]['url'] for k in ('maxres', 'standard', 'high', 'medium', 'default') if k in thumbs), None)
        if not thumb:
            continue
        shorts.append((vid, video['snippet']['title'], thumb))
        if len(shorts) == 4:
            break
    return shorts


def update_html(shorts):
    if len(shorts) < 4:
        raise RuntimeError('Fewer than four videos in Shorts playlist; leaving existing gallery unchanged')
    page = HTML_FILE.read_text(encoding='utf-8')
    left = '<div class="shorts-grid">'
    right = '</div><a class="youtube-link"'
    start = page.find(left)
    end = page.find(right, start + len(left))
    if start < 0 or end < 0:
        raise RuntimeError('Could not locate Shorts grid; leaving homepage unchanged')
    parts = []
    for vid, title, thumb in shorts:
        safe_title = html.escape(title, quote=True)
        safe_thumb = html.escape(thumb, quote=True)
        parts.append(f'<article class="short-card"><div class="short-frame"><button type="button" class="short-launch" data-video-id="{vid}" aria-label="Play {safe_title}"><img src="{safe_thumb}" alt="{safe_title} thumbnail" loading="lazy"><span class="short-play" aria-hidden="true">▶</span></button></div><h3>{safe_title}</h3></article>')
    updated = page[:start] + left + ''.join(parts) + page[end:]
    if updated != page:
        HTML_FILE.write_text(updated, encoding='utf-8')
        print('Updated homepage with:', ', '.join(vid for vid, _, _ in shorts))
    else:
        print('Already up to date; no changes')


if __name__ == '__main__':
    if not os.environ.get('YOUTUBE_API_KEY'):
        raise RuntimeError('YOUTUBE_API_KEY secret is missing')
    update_html(latest_shorts())
