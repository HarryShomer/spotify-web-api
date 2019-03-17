"""
This implements the client credentials flow explained here - 
https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow

Everything here refers to the current web api reference  - https://developer.spotify.com/documentation/web-api/reference/

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

# browse
# TODO: https://api.spotify.com/v1/browse/categories/{category_id}
# TODO: https://api.spotify.com/v1/browse/categories/{category_id}/playlists
# TODO: https://api.spotify.com/v1/artists/{id}/related-artists
# TODO: https://api.spotify.com/v1/recommendations
# TODO: https://api.spotify.com/v1/recommendations/available-genre-seeds
# TODO: https://api.spotify.com/v1/browse/featured-playlists
# artist
# TODO: https://api.spotify.com/v1/artists/{id}/related-artists

import json
import base64
import os
import time
import requests

TOKEN_URL = "https://accounts.spotify.com/api/token"
ACCESS_URL = "https://api.spotify.com/v1/me"
BASE_URL = "https://api.spotify.com/v1/"


class Spotify:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret

        # If none we assume defined in ENV
        if client_id is None:
            self.client_id = os.getenv('SPOTIFY_ID')
            self.client_secret = os.getenv('SPOTIFY_SECRET')

            if self.client_id is None:
                raise Exception("The SPOTIFY_ID or SPOTIFY_SECRET ENV variable don't exist")

        self.access_token = {}
        self.token_start_time = None
        self.get_access_token()


    def get_access_token(self):
        """
        Get the refresh token and use to exchange or exchange the authorization code for a token

        :param: refresh_token: Refresh to get auth token

        access_token = {access_token, token_type, expires_in (seconds)}
        """
        post_data = {"grant_type": "client_credentials"}

        auth_str = bytes('{}:{}'.format(self.client_id, self.client_secret), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

        # So we know when it expires
        self.token_start_time = time.time()

        headers = {"Authorization": "Basic {}".format(b64_auth_str)}
        post_request = requests.post(TOKEN_URL, data=post_data, headers=headers)

        self.access_token = json.loads(post_request.text)


    def token_expired(self):
        """
        If the current token has expired

        :return boolean - True if expired
        """
        return time.time() - self.token_start_time >= self.access_token['expires_in']


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
        headers = {"Authorization": "Bearer {}".format(self.access_token['access_token'])}

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


    #################################################################
    ##########################  Search API ##########################
    #################################################################


    def search(self, search_data, search_type, limit=3, market="US", offset=0):
        """
        Search for data

        https://api.spotify.com/v1/search

        :param search_data: Search input 
        :param search_type: Type of search you are conducting - - ['artist', 'album', 'playlist', 'track']
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
        path_params = ["browse", "categories"]

        return self.path_query("browse", payload, path_params)


    #################################################################
    ##########################  Artist API ##########################
    #################################################################


    def get_artists_ids(self, artists):
        """
        Get associated ids for a group of artists

        :param artists: List of names of artists

        :return ids -> List of corresponding artist ids
        """
        # Search artists one at a time
        ids = []
        for artist in artists:
            search_artist = self.search(artist, "artist")
            if len(search_artist['artists']['items']) > 0:
                ids.append(search_artist['artists']['items'][0]['id'])
            else:
                print(artist, "not found")

        return ids


    def get_artists(self, artists, artist_id=False):
        """
        Get the data for a given artists name or id

        https://api.spotify.com/v1/artists

        :param artists: Artist to query -> List, str, int
        :param artist_id: If supplying ids or names

        :return list of artist objects
        """
        # I only use the api endpoint that allows 1 or more artists
        if isinstance(artists, str):
            artists = [artists]

        if not artist_id:
            ids = self.get_artists_ids(artists)

        payload = {"ids": ids}
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
        if not artist_id:
            artist = self.get_artists_ids(artist)

        if artist:
            if include_groups is None:
                include_groups = ['album', 'single', 'appears_on', 'compilation']

            payload = {"include_groups": include_groups, "limit": limit}
            path_params = [artist[0], "albums"]

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
            artist = self.get_artists_ids(artist)

        if artist:
            payload = {"country": country}
            path_params = [artist, 'top-tracks']

            results = self.path_query("artists", payload, path_params)
            return results.get("tracks", [])


    #################################################################
    ##########################  Albums API ##########################
    #################################################################


    def get_albums_ids(self, albums):
        """
        Get associated ids for a group of albums

        :param albums: List of names of albums

        :return ids -> List of corresponding albums ids
        """
        # Search artists one at a time
        ids = []
        for album in albums:
            search_artist = self.search(album, "album")

            if len(search_artist['albums']['items']) > 0:
                ids.append(search_artist['albums']['items'][0]['id'])
            else:
                print(album, "not found")

        return ids


    def get_albums(self, albums, album_id=False, market="US"):
        """
        Get album info for # of albums

        https://api.spotify.com/v1/albums

        :param albums: Names or ids of albums - list, int, str
        :param album_id: If supplying ids
        :param market: Market to draw from

        :return list of album objects
        """
        # I only use the api endpoint that allows 1 or more artists
        if isinstance(albums, str):
            albums = [albums]

        if not album_id:
            ids = self.get_albums_ids(albums)

        payload = {"ids": ids, "market": market}
        results = self.query("albums", payload)

        return results.get("albums", [])


    def get_album_tracks(self, album, album_id, limit=20, market='US'):
        """
        Get the tracks for a given album

        https://api.spotify.com/v1/albums/{id}/tracks

        :param album: Name or id of album
        :param album_id: If supplying ids or name
        :param limit: # of items to return
        :param market: Market to take from

        :return list of album tracks
        """
        if not album_id:
            album = self.search(album, "album")

        if album:
            payload = {"limit": limit, "market": market}
            path_params = [album, "tracks"]

            results = self.path_query("albums", payload, path_params)
            return results.get("items", [])


    #################################################################
    ##########################  Tracks API ##########################
    #################################################################


    def get_tracks(self, track_ids, market="US"):
        """
        Get list of track information

        https://api.spotify.com/v1/tracks

        :param track_ids: IDs for tracks
        :param market: where to drawn info from

        :return list of tracks
        """
        payload = {"ids": track_ids, "market": market}

        results = self.query("tracks", payload)
        return results.get("tracks", [])


    def get_audio_features(self, track_ids):
        """
        Get audio features for multiple tracks

        https://api.spotify.com/v1/audio-features

        :param track_ids: IDs for tracks to get info for

        :return list of tracks
        """
        results = self.query("audio-features", {"ids": track_ids})
        return results.get("audio_features", [])


    def get_audio_analysis(self, track_id):
        """
        Get audio analysis for a single tracks

        https://api.spotify.com/v1/audio-analysis/{id}

        :param track_id: ID for track to get info for

        :return dict of info
        """
        return self.path_query("audio-analysis", {}, [track_id])

