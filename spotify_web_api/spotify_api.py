"""
This implements the client credentials flow explained here - 
https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow

Everything here refers to the current web api reference - https://developer.spotify.com/documentation/web-api/reference/

Sections of API covered:
    - Browse
    - Artists
    - Tracks
    - Albums
    - Search
    
Sections of API not covered:
    - Follow
    - Library
    - Personalization
    - Player
    - Playlists
    - User Profile
"""

import json
import base64
import os
import time
import requests
from datetime import datetime

TOKEN_URL = "https://accounts.spotify.com/api/token"
ACCESS_URL = "https://api.spotify.com/v1/me"
BASE_URL = "https://api.spotify.com/v1/"

# All possible Category IDs
CAT_IDS = ['toplists', 'pop', 'hiphop', 'mood', 'workout', 'decades', 'country', 'focus', 'latin', 'chill', 'edm_dance',
           'rnb', 'rock', 'indie_alt', 'roots', 'party', 'sleep', 'classical', 'jazz', 'inspirational']



class Spotify:
    def __init__(self, client_id=None, client_secret=None):
        self._client_id = client_id
        self._client_secret = client_secret

        # If none we assume defined in ENV
        if client_id is None:
            self._client_id = os.getenv('SPOTIFY_ID')
            self._client_secret = os.getenv('SPOTIFY_SECRET')

            if self._client_id is None:
                raise Exception("The SPOTIFY_ID or SPOTIFY_SECRET ENV variable don't exist")

        self._access_token = {}
        self._token_start_time = None
        self.get_access_token()


    def get_access_token(self):
        """
        Get the refresh token and use to exchange or exchange the authorization code for a token

        :param: refresh_token: Refresh to get auth token

        access_token = {access_token, token_type, expires_in (seconds)}
        """
        post_data = {"grant_type": "client_credentials"}

        auth_str = bytes('{}:{}'.format(self._client_id, self._client_secret), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

        # So we know when it expires
        self._token_start_time = time.time()

        headers = {"Authorization": "Basic {}".format(b64_auth_str)}
        post_request = requests.post(TOKEN_URL, data=post_data, headers=headers)

        self._access_token = json.loads(post_request.text)


    def token_expired(self):
        """
        If the current token has expired

        :return boolean - True if expired
        """
        return time.time() - self._token_start_time >= self._access_token['expires_in']


    def query(self, query_type, payload):
        """
        Query the specified data

        :param query_type: Query to make
        :param payload: Associated parameters

        :return response json
        """
        if self.token_expired():
            self.get_access_token()

        url = f"{BASE_URL}{query_type}"
        headers = {"Authorization": "Bearer {}".format(self._access_token['access_token'])}

        response = requests.get(url, headers=headers, params=payload)
        time.sleep(3)

        return json.loads(response.content)


    def path_query(self, query_type, payload, path_params):
        """
        When making a query with a modified path

        :param query_type: Query to make
        :param payload: Associated parameters
        :param path_params: Parameters to add to path -> must be in correct order

        :return: response json
        """
        query_type = "/".join([query_type, *path_params])
        return self.query(query_type, payload)


    def get_ids(self, search_vals, search_type):
        """
        Get associated ids for a group of searched items

        :param search_vals: What you are searching for
        :param search_type: Type of item you are searching for

        :return ids -> List of corresponding ids
        """
        # I only use the api endpoint that allows 1 or more artists
        # So we come here whenever there exist the single and multiple options
        # So for ease just convert to a list
        if isinstance(search_vals, str):
            search_vals = [search_vals]

        # Search one at a time
        ids = []
        for search_val in search_vals:
            search_items = self.search(search_val, search_type).get(f"{search_type}s", [])

            if search_items and len(search_items['items']) > 0:
                ids.append(search_items['items'][0]['id'])
            else:
                print(search_val, "not found")

        return ids

    def get_id(self, search_val, search_type):
        """
        Get associated id for a one searched item

        :param search_val: What you are searching for
        :param search_type: Type of item you are searching for

        :return id or None
        """
        response = self.get_ids([search_val], search_type)
        if response:
            return response[0]


    #################################################################
    ##########################  Search API ##########################
    #################################################################


    def search(self, search_data, search_type, limit=3, market="US", offset=0):
        """
        Search for data

        https://api.spotify.com/v1/search

        :param search_data: Search input 
        :param search_type: Type of search you are conducting - ['artist', 'album', 'playlist', 'track']
        :param limit: Number of albums to return 
        :param market: Only get from specific market where playable
        :param offset: index of first result to return

        :return response data
        """
        if not search_type in ['artist', 'album', 'playlist', 'track'] and isinstance(search_data, str):
            print("Not a valid search type")
        else:
            payload = {
                'q': search_data,
                'type': search_type,
                'limit': limit,
                'market': market,
                'offset': offset
            }
            return self.query("search", payload)


    #################################################################
    ##########################  Browse API ##########################
    #################################################################


    def get_categories(self, country="US", locale="US", limit=20, offset=0):
        """
        Get all the music categories available 
        
        https://api.spotify.com/v1/browse/categories
        
        :param country: Where content is playable
        :param locale: language
        :param limit: results to return
        :param offset: index of first result to return
        
        :return: response data
        """
        payload = {"country": country, "limit": limit, "locale": locale, "offset": offset}
        path_params = ["categories"]

        return self.path_query("browse", payload, path_params)['categories']['items']


    def get_category(self, category, country="US", locale="US"):
        """
        Get the info for a given category
        
        https://api.spotify.com/v1/browse/categories/{category_id}
        
        :param category: id of category
        :param country: exists for supplied country
        :param locale: language
        
        :return: dict of info
        """
        if category.lower() not in CAT_IDS:
            raise ValueError(f"{category} is not one of the possible category ids")

        payload = {"country": country, "locale": locale}
        path_params = ["categories", category.lower()]

        return self.path_query("browse", payload, path_params)


    def get_category_playlists(self, category, country="US", limit=20, offset=0):
        """
        Get the info for a given category

        https://api.spotify.com/v1/browse/categories/{category_id}/playlists

        :param category: id of category
        :param country: country to get for
        :param limit: # of items to return
        :param offset: index of first item to return

        :return: list of info
        """
        if category.lower() not in CAT_IDS:
            raise ValueError(f"{category} is not one of the possible category ids")

        if not 51 > limit > 0:
            raise ValueError("Limit must be between 0 and 50")

        payload = {"country": country, "limit": limit, "offset": offset}
        path_params = ["categories", category.lower(), "playlists"]

        results = self.path_query("browse", payload, path_params)
        return results['playlists']['items'] if 'playlists' in results else []


    def get_genre_seeds(self):
        """
        Get all the possible genres
        
        https://api.spotify.com/v1/recommendations/available-genre-seeds
        
        :return: List of genres
        """
        return self.path_query("recommendations", {}, ["available-genre-seeds"]).get("genres", [])

    # TODO: Get this took work
    # TODO: Add min, max, and target params for tunable track attributes
    def get_recommendations(self, seed_artists, seed_tracks, seed_genres, limit=20, market="US"):
        """
        Get recommendations for new music
        
        https://api.spotify.com/v1/recommendations
        
        :param seed_artists: Up to 5 artists -> Must be IDs
        :param seed_tracks: Up to 5 tracks -> Must be IDs
        :param seed_genres: Up to 5 genres 
        :param limit: # to return
        :param market: country
        
        :return: 
        """
        if not 101 > limit > 0:
            raise ValueError("Limit must be between 0 and 100")

        # If supply strings for any of the seeds then convert to a list
        if isinstance(seed_artists, str):
            seed_artists = [seed_artists]
        if isinstance(seed_genres, str):
            seed_genres = [seed_genres]
        if isinstance(seed_tracks, str):
            seed_tracks = [seed_tracks]

        payload = {
            "seed_artists": ",".join(seed_artists),
            "seed_genres": ",".join(seed_genres),
            "seed_tracks": ",".join(seed_tracks),
            "limit": limit,
            "market": market
        }

        return self.query("recommendations", payload).get("tracks", [])


    def get_featured_playlists(self, timestamp=None, country="US", locale="US", limit=20, offset=0):
        """
        Get all featured playlists
        
        # TODO: https://api.spotify.com/v1/browse/featured-playlists
        
        :param timestamp: ISO-8601 format
        :param country: market
        :param locale: language
        :param limit: results to return
        :param offset: index to begin at
        
        :return: list of featured playlists
        """
        # Needs to be ISO-8601 format
        if timestamp is None:
            iso = datetime.now().isoformat()
            timestamp = iso[0:iso.find(".")]
        else:
            try:
                datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError("The timestamp isn't in the correct format should be %Y-%m-%dT%H:%M:%S")

        if not 51 > limit > 0:
            raise ValueError("Limit must be between 0 and 50")

        payload = {
            "timestamp": timestamp,
            "country": country,
            "locale": locale,
            "limit": limit,
            "offset": offset
        }
        path_params = ['featured-playlists']

        results = self.path_query("browse", payload, path_params)
        return results['playlists']['items'] if 'playlists' in results else []


    def get_new_releases(self, country="US", limit=20, offset=0):
        """
        Get the new album releases on spotify
        
        https://api.spotify.com/v1/browse/new-releases
        
        :param country: country to get for
        :param limit: # of items to return
        :param offset: index of first item to return
        
        :return: list of album objects
        """
        if not 51 > limit > 0:
            raise ValueError("Limit must be between 0 and 50")

        payload = {"country": country, "limit": limit, "offset": offset}
        path_params = ['new-releases']

        return self.path_query("browse", payload, path_params).get("albums", [])


    #################################################################
    ##########################  Artist API ##########################
    #################################################################


    def get_artists(self, artists, artist_id=False):
        """
        Get the data for a given artists name or id

        https://api.spotify.com/v1/artists

        :param artists: Artist to query -> List, str, int
        :param artist_id: If supplying ids or names

        :return list of artist objects
        """
        if len(artists) > 50:
            raise ValueError("Can only retrieve a maximum of 50 artists")

        if not artist_id:
            artists = self.get_ids(artists, "artist")

        if artists:
            payload = {"ids": ",".join(artists)}
            results = self.query("artists", payload)

            return results.get("artists", [])


    def get_artist_albums(self, artist, artist_id=False, include_groups=None, limit=20):
        """
        Get the albums for an artist

        https://api.spotify.com/v1/artists/{id}/albums

        :param artist: Name or id of artist
        :param artist_id: If supplying ids or names
        :param include_groups: str, list, None
        :param limit: Number to return

        :return list of album objects
        """
        if not 51 > limit > 0:
            raise ValueError("Limit must be between 0 and 50")

        if not artist_id:
            artist = self.get_id(artist, "artist")

        if artist is not None:
            if include_groups is None:
                include_groups = ['album', 'single', 'appears_on', 'compilation']

            payload = {"include_groups": include_groups, "limit": limit}
            path_params = [artist, "albums"]

            results = self.path_query("artists", payload, path_params)
            return results.get("items", [])


    def get_top_tracks(self, artist, country, artist_id=False):
        """
        Get the top tracks for an artist

        https://api.spotify.com/v1/artists/{id}/top-tracks

        :param artist: name or id of artist
        :param country: Country to get shift from
        :param artist_id: If providing id

        :return list of track objects
        """
        if not artist_id:
            artist = self.get_id(artist, "artist")

        if artist is not None:
            payload = {"country": country}
            path_params = [artist, 'top-tracks']

            results = self.path_query("artists", payload, path_params)
            return results.get("tracks", [])


    def get_related_artists(self, artist, artist_id=False):
        """
        Get the related artist for a given artist 
        
        https://api.spotify.com/v1/artists/{id}/related-artists
        
        :param artist: ID or name of artist
        :param artist_id: If supplied id
        
        :return: List of related artist objects
        """
        if not artist_id:
            artist = self.get_id(artist, "artist")

        if artist is not None:
            path_params = [artist, 'related-artists']
            results = self.path_query("artists", {}, path_params)

            return results.get("artists", [])


    #################################################################
    ##########################  Albums API ##########################
    #################################################################


    def get_albums(self, albums, album_id=False, market="US"):
        """
        Get album info for # of albums

        https://api.spotify.com/v1/albums

        :param albums: Names or ids of albums - list, int, str
        :param album_id: If supplying ids
        :param market: Market to draw from

        :return list of album objects
        """
        if isinstance(albums, list) and len(albums) > 20:
            raise ValueError("Can only request a maximum of 20 albums")

        if not album_id:
            albums = self.get_ids(albums, "album")

        if albums:
            payload = {"ids": ",".join(albums), "market": market}
            results = self.query("albums", payload)

            return results.get("albums", [])


    def get_album_tracks(self, album, album_id=False, limit=20, market='US'):
        """
        Get the tracks for a given album

        https://api.spotify.com/v1/albums/{id}/tracks

        :param album: Name or id of album
        :param album_id: If supplying ids or name
        :param limit: # of items to return
        :param market: Market to take from

        :return list of album tracks
        """
        if not 51 > limit > 0:
            raise ValueError("Limit must be between 0 and 50")

        if not album_id:
            album = self.get_id(album, "album")

        if album is not None:
            payload = {"limit": limit, "market": market}
            path_params = [album, "tracks"]

            results = self.path_query("albums", payload, path_params)
            return results.get("items", [])


    #################################################################
    ##########################  Tracks API ##########################
    #################################################################


    def get_tracks(self, tracks, track_id=False, market="US"):
        """
        Get list of track information

        https://api.spotify.com/v1/tracks

        :param tracks: IDs or names of tracks
        :param track_id: If supplied ids or name
        :param market: where to drawn info from

        :return list of tracks
        """
        if isinstance(tracks, list) and len(tracks) > 50:
            raise ValueError("Can only request a maximum of 50 tracks")

        if not track_id:
            tracks = self.get_ids(tracks, "track")

        if tracks:
            payload = {"ids": ",".join(tracks), "market": market}
            results = self.query("tracks", payload)

            return results.get("tracks", [])


    def get_audio_features(self, tracks, track_id=False):
        """
        Get audio features for multiple tracks

        https://api.spotify.com/v1/audio-features

        :param tracks: IDs or names of tracks
        :param track_id: If supplied ids or name

        :return list of tracks
        """
        if not track_id:
            tracks = self.get_ids(tracks, "track")

        if tracks:
            results = self.query("audio-features", {"ids": ",".join(tracks)})
            return results.get("audio_features", [])


    def get_audio_analysis(self, track, track_id=False):
        """
        Get audio analysis for a single tracks

        https://api.spotify.com/v1/audio-analysis/{id}

        :param track: ID or names of track
        :param track_id: If supplied ids or name

        :return dict of info
        """
        if not track_id:
            track = self.get_id(track, "track")

        if track is not None:
            return self.path_query("audio-analysis", {}, [track])

