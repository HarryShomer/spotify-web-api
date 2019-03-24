# Spotify Web API

A extremely minimal client library for some portions of the spotify [web api](https://developer.spotify.com/documentation/web-api/)  which only implements the [clients credentials](https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow)  flow.


## Install

It's currently not on pip. Therefore to install it on your machine either clone or download the repository and run either:

```
pip setup.py install
```

or if you are interested in modifying it

```
pip setup.py develop
```

## Supported APIs

As of right now only the following sections of the API are supported:

* [Browse](https://developer.spotify.com/documentation/web-api/reference/browse/)
* [Artists](https://developer.spotify.com/documentation/web-api/reference/artists/)
* [Tracks](https://developer.spotify.com/documentation/web-api/reference/tracks/)
* [Albums](https://developer.spotify.com/documentation/web-api/reference/albums/)
* [Search](https://developer.spotify.com/documentation/web-api/reference/search/search/)

The following sections of the API aren't covered:

* [Follow](https://developer.spotify.com/documentation/web-api/reference/follow/)
* [Library](https://developer.spotify.com/documentation/web-api/reference/library/)
* [Personalization](https://developer.spotify.com/documentation/web-api/reference/personalization/)
* [Player](https://developer.spotify.com/documentation/web-api/reference/player/)
* [Playlists](https://developer.spotify.com/documentation/web-api/reference/playlists/)
* [User Profile](https://developer.spotify.com/documentation/web-api/reference/users-profile/)


## Usage

As of right now only the client credentials flow is supported. To use this you must have a spotify Client ID and Client Secret. You can get those by registering [here](https://developer.spotify.com/dashboard/).

I recommend setting these two as environment variables on your computer which will cause the the library to automatically
find them. You will need to set them equal to SPOTIFY\_ID and SPOTIFY\_SECRET. This can be done by modifying your
.bash_profile and adding

```
export SPOTIFY_ID="Your ID"
export SPOTIFY_SECRET="Your Secret key"
```

You can then just do:

```python
from spotify_web_api import Spotify

spy = Spotify()
```

You can also pass the two through the constructor when you create a Spotify object:

```python
from spotify_web_api import Spotify

SPOTIFY_ID = "Your Client Id"
SPOTIFY_SECRET = "Your secret key"

spy = Spotify(client_id=SPOTIFY_ID, client_secret=SPOTIFY_SECRET)
```

### Examples

Get the all tracks for an album

```python
spy.get_album_tracks("time will die and love will bury it")
```

Get all the albums (only LPs) for a specific artist

```python
spy.get_artist_albums("converge", include_groups="album")
```

Get all the spotify playlists for a specific category

```python
spy.get_category_playlists("rock")
```

Get the audio features for several tracks

```python
tracks = ['beauty in falling leaves', 'me & my dog']
spy.get_audio_features(tracks)
```

Search for a specific track, album, artist, or playlist

```python
spy.search("deathspell omega", "artist")
```

## Tests

To run the tests you will need to have pytest installed. Once you do, go over to the tests directory and run

```
pytest -v
```

## Contribute

Please feel free to fork this or submit a pull request. There are obviously quite a lot of parts of the api this is missing  so implement it if you want. If you do choose to submit a pull request please write the appropriate tests for the added  features.
