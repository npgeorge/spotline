import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import time
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy


# flask app variable
APP = Flask(__name__)

# setting market parameters for Spotify licensing issues
market = [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY", 
      "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU", 
      "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL", 
      "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW", 
      "US", "UY", "VN" ]

# keys, put in env file
CLIENT_ID = "849709fe2afc44ec94af7527ce55999e"
CLIENT_SECRET = "41b39f8cd0824289aebde74f22d853e3"

# creds
credentials = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# token access
token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)


def print_statement():
    results = spotify.search("Thriller", type="track", limit=1)
    
    if len(results['tracks']['items']) > 0:
        track = results['tracks']['items'][0]
        audio_features = spotify.audio_features(str(track['uri']))[0]
        danceability = audio_features['danceability']
        energy = audio_features['energy']
        key = audio_features['key']
        loudness = audio_features['loudness']
        mode = audio_features['mode']
        speechiness = audio_features['speechiness']
        acousticness = audio_features['acousticness']
        instrumentalness =audio_features['instrumentalness']
        liveness = audio_features['liveness']
        valence = audio_features['valence']
        tempo = audio_features['tempo']
        primary_artist = spotify.artist(str(track['album']['artists'][0]['uri']))
        track_name = str(track['name'])
        artist_name = str(track['artists'][0]['name'])
    return (
        print('-----------------------'),
        print('***TRACK FEATURES***'),
        print('-----------------------'),
        #print('track : ', track_name),
        #print('primary artist : ', primary_artist),
        print('track name : ', track_name),
        print('artist name : ', artist_name),

        print('-----------------------'),
        print('***AUDIO FEATURES***'),
        print('-----------------------'),
        print('danceability : ', danceability),
        print('energy : ', energy),
        print('key : ', key),
        print('loudness : ', loudness),
        print('mode : ', mode),
        print('speechiness : ', speechiness),
        print('acousticness : ', acousticness),
        print('instrumentalness : ', instrumentalness),
        print('liveness : ', liveness),
        print('valence : ', valence),
    )

print_statement()