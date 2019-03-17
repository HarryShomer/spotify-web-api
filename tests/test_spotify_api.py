"""
Tests for the spotify_api.py file
"""
from spotify_web_api.spotify_api import Spotify
import os
import pytest


@pytest.fixture
def spy():
    return Spotify()

@pytest.fixture
def artists():
    return ["rolo tomassi", "converge"]

@pytest.fixture
def artist_ids():
    return ["3uHCTHxtg3IVAvhyrYsZvI", "7kHzfxMLtVHHb523s43rY1"]

@pytest.fixture
def albums():
    return ["the things we think we're missing", "in the aeroplane over the sea"]

@pytest.fixture
def album_ids():
    return ["7a4k5NMwt4L4vbuV9Qy1gL", "5COXoP5kj2DWfCDg0vxi4F"]

@pytest.fixture
def tracks():
    return ['beauty in falling leaves', 'me & my dog']

@pytest.fixture
def track_ids():
    return ['6e32JnkTy46WgO1waYifJo', '4q9w3UGW3utmeUruBLUoZZ']

@pytest.fixture
def category():
    return 'rock'


#################################################################
######################### General API ###########################
#################################################################

def test_spotify_credentials():
    """ 
    Test both methods of passing client id and secret work. Good as long as they don't throw errors
    """
    Spotify()
    Spotify(client_id=os.getenv("SPOTIFY_ID"), client_secret=os.getenv("SPOTIFY_SECRET"))


def test_access_token(spy):
    """Test we receive valid access token"""
    # It either includes or doesn't include 'scope'
    assert list(spy._access_token.keys()) == ['access_token', 'token_type', 'expires_in'] or\
           list(spy._access_token.keys()) == ['access_token', 'token_type', 'expires_in', 'scope']


def test_token_expired(spy):
    """Test it can correctly tell if expired"""
    assert not spy.token_expired()


def test_query(spy):
    """Test if a standard query works as intended"""
    query_type = "search"
    payload = {'q': "converge", 'type': "artist", 'limit': 3}

    assert len(spy.query(query_type, payload)['artists']['items']) > 0


#################################################################
##########################  Search API ##########################
#################################################################

def test_search(spy):
    """Test that the search works properly"""
    assert len(spy.search("time will die and love will bury it", "album")['albums']['items']) > 0


#################################################################
##########################  Browse API ##########################
#################################################################

def test_get_categories(spy):
    """Test getting all the categories"""
    assert len(spy.get_categories()) > 0


def test_get_category(spy, category):
    """Test getting information for a given category"""
    assert spy.get_category(category)['id'] == category


def test_get_category_playlists(spy, category):
    """Test getting the Spotify playlists for a given category"""
    assert len(spy.get_category_playlists(category)) > 0


def test_get_recommendations(spy, track_ids, artist_ids):
    """Test getting recommendations based on seed info"""
    genres = ['sad', 'metal']
    assert len(spy.get_recommendations(artist_ids, track_ids, genres)) > 0


def test_get_genre_seeds(spy):
    """Test getting the possible genre seeds for getting recommendations"""
    assert len(spy.get_genre_seeds()) > 0


def test_get_featured_playlists(spy):
    """Test getting the featured playlists"""
    assert len(spy.get_featured_playlists()) > 0


def test_get_new_releases(spy):
    """Test getting the new releases"""
    assert len(spy.get_new_releases()) > 0


#################################################################
##########################  Artist API ##########################
#################################################################

def test_get_artist_ids(spy, artists, artist_ids):
    """Test retrieving artist ids from their names"""
    query = spy.get_ids(artists, "artist")
    assert query[0] == artist_ids[0]
    assert query[1] == artist_ids[1]


def test_get_artists(spy, artists, artist_ids):
    """
    Test getting the artist info from both name and id
    """
    # From name
    assert len(spy.get_artists(artists)) == 2
    # From id
    assert len(spy.get_artists(artist_ids, artist_id=True)) == 2


def test_get_artist_albums(spy, artists, artist_ids):
    """Test getting the albums for an artist"""
    # From name
    assert len(spy.get_artist_albums(artists[1])) > 0
    # From id
    assert len(spy.get_artist_albums(artist_ids[1], artist_id=True)) > 0


def test_get_top_tracks(spy, artists, artist_ids):
    """Test getting the top tracks for an artist"""
    # From name
    assert len(spy.get_top_tracks(artists[0], "US")) > 0
    # From id
    assert len(spy.get_top_tracks(artist_ids[0], "US", artist_id=True)) > 0


def test_get_related_artists(spy, artists, artist_ids):
    """Test getting the related artist for an artist"""
    # From name
    assert len(spy.get_related_artists(artists[0])) > 0
    # From id
    assert len(spy.get_related_artists(artist_ids[0], artist_id=True)) > 0


#################################################################
##########################  Albums API ##########################
#################################################################

def test_get_album_ids(spy, albums, album_ids):
    """Test getting the album ids from and album names"""
    query = spy.get_ids(albums, "album")
    assert query[0] == album_ids[0]
    assert query[1] == album_ids[1]


def test_get_albums(spy, albums, album_ids):
    """Test getting albums from either name or id"""
    # From name
    assert len(spy.get_albums(albums)) > 0
    # From id
    assert len(spy.get_albums(album_ids, album_id=True)) > 0


def test_get_album_tracks(spy, albums, album_ids):
    """Test getting the tracks for an album"""
    # From name
    assert len(spy.get_album_tracks(albums[1])) == 11
    # From id
    assert len(spy.get_album_tracks(album_ids[1], album_id=True)) == 11


#################################################################
##########################  Tracks API ##########################
#################################################################

def test_get_track_ids(spy, tracks, track_ids):
    """Test getting the album ids from and album names"""
    query = spy.get_ids(tracks, "track")
    assert query[0] == track_ids[0]
    assert query[1] == track_ids[1]


def test_get_tracks(spy, tracks, track_ids):
    """Test getting the info for a number of tracks"""
    # From name
    assert len(spy.get_tracks(tracks)) == 2
    # From id
    assert len(spy.get_tracks(track_ids, track_id=True)) == 2


def test_get_audio_features(spy, tracks, track_ids):
    """Test getting the audio features for a number of tracks"""
    # From name
    assert len(spy.get_audio_features(tracks)) == 2
    # From id
    assert len(spy.get_audio_features(track_ids, track_id=True)) == 2


def test_get_audio_analysis(spy, tracks, track_ids):
    """Test getting the audio analysis for a track"""
    # From name
    assert "bars" in spy.get_audio_analysis(tracks[0])
    # From id
    assert "bars" in spy.get_audio_analysis(track_ids[0], track_id=True)


