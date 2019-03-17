"""
Tests for the spotify_api.py file
"""
from spotify_web_api.spotify_api import Spotify
import os
import pytest


@pytest.fixture
def spy():
    return Spotify()


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
    assert list(spy.access_token.keys()) == ['access_token', 'token_type', 'expires_in'] or\
           list(spy.access_token.keys()) == ['access_token', 'token_type', 'expires_in', 'scope']


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
    pass

def test_get_cateogry(spy):
    """Test getting information for a given category"""
    pass

def test_get_category_playlists(spy):
    """Test getting the Spotify playlists for a given category"""
    pass

def test_get_recommendations(spy):
    """Test getting recommendations based on seed info"""
    pass

def test_get_genre_seeds(spy):
    """Test getting the possible genre seeds for getting recommendations"""
    pass

def test_get_featured_playlists(spy):
    """Test getting the featured playlists"""
    pass


#################################################################
##########################  Artist API ##########################
#################################################################


def test_get_artists_ids(spy):
    """Test retrieving artist ids from their names"""
    pass


def get_get_artists(spy):
    """
    Test getting the artist from both name and id
    """
    pass


def test_get_artist_albums(spy):
    """Test getting the albums for an artist"""
    pass


def test_get_top_tracks(spy):
    """Test getting the top tracks for an artist"""
    pass


def test_get_related_artists(spy):
    """Test getting the related artist for an artist"""
    pass


#################################################################
##########################  Albums API ##########################
#################################################################


def test_get_albums_ids(spy):
    """Test getting the album ids from and album names"""
    pass


def test_get_albums(spy):
    """Test getting albums from either name or id"""
    pass


#################################################################
##########################  Tracks API ##########################
#################################################################


def get_album_tracks(spy):
    """Test getting the tracks for an album"""
    pass


def get_tracks(spy):
    """Test getting the info for a number of tracks"""
    pass


def get_audio_features(spy):
    """Test getting the audio features for a number of tracks"""
    pass

def get_audio_analysis(spy):
    """Test getting the audio analysis for a track"""
    pass


