# coding: utf-8
from __future__ import unicode_literals

import re
import json

from .common import InfoExtractor

def embed_player_url(media_id):
    return "https://embeds.datpiff.com/mixtape/%s" % media_id

def fix_track(track_str, artist):
    new_track_str = track_str.replace("playerData.artist", '"%s"' % artist)
    new_track_str = new_track_str.replace('trackPrefix.concat( \'', '"')
    new_track_str = new_track_str.replace('\' ), "duration', '", "duration')
    return new_track_str

class DatPiffMixtapeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?datpiff\.com/.*?\.(?P<id>[0-9]+)\.html'
    _TEST = {
        'url': 'https://www.datpiff.com/Waka-Flocka-Flame-Salute-Me-Or-Shoot-Me-6-mixtape.933868.html',
        'info_dict': {
            'id': '933868',
            'title': 'Salute Me Or Shoot Me 6 Mixtape by Waka Flocka Flame',
        },
        'playlist_count': 11
    }

    def _real_extract(self, url):
        entries = []
        mixtape_id = self._match_id(url)
        embed_url = embed_player_url(mixtape_id)
        webpage = self._download_webpage(embed_url, mixtape_id)

        title = self._html_search_meta('og:title', webpage, 'title').strip()

        artist = self._html_search_regex(r'<div class="artist">(.+?)</div>', webpage, 'artist')
        album_title = self._html_search_regex(r'<div class="title">(.+?)</div>', webpage, 'album_title')

        tp_regex = r"var trackPrefix = '(.+?)';"
        track_prefix = self._html_search_regex(tp_regex, webpage, 'track_prefix')

        tracks_regex = r"playerData.tracks.push\((.+?)\);"
        tracks = [json.loads(fix_track(x.strip(), artist)) for x in re.findall(tracks_regex, webpage) if x.strip()]

        for track in tracks:
            entry = {
                "id": str(track['id']),
                "title": track['title'],
                "url": '%s%s' % (track_prefix, track['mfile'])
            }
            entries.append(entry)

        return self.playlist_result(entries, mixtape_id, title)
