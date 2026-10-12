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
import subprocess
API = 'https://www.googleapis.com/youtube/v3/'
HANDLE = '@RendertoResults'
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


def is_portrait(vid):
    """Verify video dimensions rather than guessing Shorts from duration."""
    try:
        proc = subprocess.run(
            ['yt-dlp', '--dump-single-json', '--skip-download', '--no-playlist',
             f'https://www.youtube.com/watch?v={vid}'],
            text=True, capture_output=True, timeout=40, check=True)
        data = json.loads(proc.stdout)
        width, height = data.get('width'), data.get('height')
        if not width or not height:
            variants = data.get('formats') or []
            portrait = [(x.get('width'), x.get('height')) for x in variants
                        if x.get('width') and x.get('height') and x.get('vcodec') != 'none']
            if portrait:
                width, height = max(portrait, key=lambda pair: pair[0] * pair[1])
        return bool(width and height and height > width)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        print(f'Unable to verify orientation for {vid}: {str(exc)[:140]}')
        return False


def latest_shorts():
    channel = youtube('channels', part='contentDetails', forHandle=HANDLE)
    items = channel.get('items', [])
    if not items:
        raise RuntimeError(f'Could not find channel {HANDLE}')
    uploads = items[0]['contentDetails']['relatedPlaylists']['uploads']

    # The uploads playlist preserves publishing order. Fetch up to 100 recent items.
    ids = []
    token = None
    for _ in range(2):
        options = dict(part='contentDetails', playlistId=uploads, maxResults=50)
        if token:
            options['pageToken'] = token
        batch = youtube('playlistItems', **options)
        ids.extend(x['contentDetails']['videoId'] for x in batch.get('items', []))
        token = batch.get('nextPageToken')
        if not token:
            break

    details = {}
    for start in range(0, len(ids), 50):
        batch = youtube('videos', part='snippet,contentDetails,status', id=','.join(ids[start:start + 50]))
        details.update((v['id'], v) for v in batch.get('items', []))

    shorts = []
    for vid in ids:
        video = details.get(vid)
        if not video or video.get('status', {}).get('privacyStatus') != 'public':
            continue
        runtime = seconds(video['contentDetails'].get('duration', ''))
        # YouTube supports Shorts up to 3 minutes; its API does not expose a
        # definitive Shorts flag, so duration is used as a best-effort filter.
        if runtime is None or runtime > 180 or runtime == 0:
            continue
        if not is_portrait(vid):
            print(f'Skipping {vid}: portrait dimensions not verified')
            continue
        thumbs = video['snippet'].get('thumbnails', {})
        thumb = next((thumbs[k]['url'] for k in ('maxres','standard','high','medium','default') if k in thumbs), None)
        if not thumb:
            continue
        shorts.append((vid, video['snippet']['title'], thumb))
        if len(shorts) == 4:
            break
    return shorts


def update_html(shorts):
    if len(shorts) < 4:
        raise RuntimeError('Fewer than four confirmed portrait videos; leaving existing gallery unchanged')
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
