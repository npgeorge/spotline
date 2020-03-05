import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import time
from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import lyricsgenius as genius
import pandas as pd
import numpy as np
#import os
#from dotenv import load_dotenv

#load_dotenv()

# flask app variable
app = Flask(__name__)

# setting market parameters for Spotify licensing issues
market = [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY", 
      "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU", 
      "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL", 
      "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW", 
      "US", "UY", "VN" ]

# spotipy keys, put in env file
SP_CLIENT_ID = "849709fe2afc44ec94af7527ce55999e"
SP_CLIENT_SECRET = "41b39f8cd0824289aebde74f22d853e3"

# genius keys
GENIUS_ACCESS_TOKEN = "ZV-wzEQ01W47OJSRBKTms7rwqvm4MrcGJV1FX1YV1l9R7q5RcSbE7ojT9rCtvAkt"
genius_api = genius.Genius(GENIUS_ACCESS_TOKEN)
genius.verbose = True                         # Keep status messages on
genius.remove_section_headers = False         # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title

# creds
credentials = SpotifyClientCredentials(client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET)

# token access
token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/output', methods=['POST'])
def output():
    # connecting html to request
    # user inputs song name here
    user_input_song = request.form['user_input_song']
    #spotify search params
    results = spotify.search(str(user_input_song), type="track", limit=1)

    # genius time parameter
    start = time.time()


    #if statements
    if len(results['tracks']['items']) > 0:
        #user_input_song = request.form['user_input_song']
        #results = spotify.search(str(user_input_song), type="track", limit=1)
        track = results['tracks']['items'][0]
        primary_artist = spotify.artist(str(track['album']['artists'][0]['uri']))
        
        #song info track artist duration
        track_name = str(track['name'])
        artist_name = str(track['artists'][0]['name'])

        # song features
        track_id = track['id']
        song_spotify_link = track['external_urls']['spotify']
        artist_id = track['artists'][0]['id']
        release_date = track['album']['release_date']
        release_date_precision = track['album']['release_date_precision']
        duration_ms = track['duration_ms']
        popularity = track['popularity']
        explicit_true_false = track['explicit']
        audio_preview = track['preview_url']
        cover_art_300x300_JFIF = track['album']['images'][1]['url']

        # audio features
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
        time_sig = audio_features['time_signature']

        # artist features
        num_artist_followers = primary_artist['followers']['total']
        artist_genres = primary_artist['genres']
        artist_popularity = primary_artist['popularity']
        artist_spotify_avatar = primary_artist['images'][1]['url']
        artist_spotify_link = primary_artist['external_urls']['spotify']

        # genius lyrics
        # passes in track and artist from spotify
        song = genius_api.search_song(track_name, artist_name)
        if song is None:
            delta = time.time() - start
            print("Lyrics not found. Other features retrieved in %.2f seconds" % (delta,))
            print()
        else:
            lyrics = song.lyrics
            delta = time.time() - start
            print("Lyrics found. All features retrieved in %.2f seconds" % (delta,))
            print() 

    else:
        print('Track not found')

    return jsonify(
        #str(results),
        # song features printout
        str('SONG FEATURES'),
        "track name             : " + str(track_name),
        "artist(s)              : " + str(artist_name),
        "track id               : " + str(track_id),
        "song spotify link      : " + str(song_spotify_link),
        "artist id              : " + str(artist_id),
        "release date           : " + str(release_date),
        "release date precision : " + str(release_date_precision),
        "duration (ms)          : " + str(duration_ms),
        "popularity             : " + str(popularity),
        "explicit (true/false)  : " + str(explicit_true_false),
        "audio preview url      : " + str(audio_preview),
        "cover art              : " + str(cover_art_300x300_JFIF),

        # audio features printout
        str('AUDIO FEATURES'),
        "danceability           : " + str(danceability),
        "energy                 : " + str(energy),
        "key                    : " + str(key),
        "loudness               : " + str(loudness),
        "mode                   : " + str(mode),
        "speechiness            : " + str(speechiness),
        "acousticness           : " + str(acousticness),
        "instrumentalness       : " + str(instrumentalness),
        "liveness               : " + str(liveness),
        "valence                : " + str(valence),
        "tempo                  : " + str(tempo),
        "time signature         : " + str(time_sig),

        # artist features printout
        str('ARTIST FEATURES'),
        "number of followers    : " + str(num_artist_followers),
        "artist genres          : " + str(artist_genres),
        "artist popularity      : " + str(artist_popularity),
        "artist spotify avatar  : " + str(artist_spotify_avatar),
        "artist spotify link    : " + str(artist_spotify_link),

        # genius lyrics
        str('LYRICS'),
        str(lyrics)

        )

# get all tracks data from an artist into a data frame or csv
@app.route('/artist_tracks', methods=['POST', 'GET'])
def artist_tracks():
    # connecting html to request
    # user inputs song name here
    artist_tracks = request.form['get_artist_tracks']
    #spotify search params
    result = spotify.search(artist_tracks) #search query

    #artist_name = result['tracks']['items'][0]['artists']

    #Extract Artist's uri
    artist_uri = result['tracks']['items'][0]['artists'][0]['uri']
    #Pull all of the artist's albums
    sp_albums = spotify.artist_albums(artist_uri, album_type='album')

    #Store artist's albums' names' and uris in separate lists
    album_names = []
    album_uris = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
        album_uris.append(sp_albums['items'][i]['uri'])

    #Keep names and uris in same order to keep track of duplicate albums
    #album_names
    #album_uris

    def albumSongs(uri):
        album = uri #assign album uri to a_name
        spotify_albums[album] = {} #Creates dictionary for that specific album
        
        # Create keys-values of empty lists inside nested dictionary for album
        spotify_albums[album]['album'] = [] #create empty list
        spotify_albums[album]['track_number'] = []
        spotify_albums[album]['id'] = []
        spotify_albums[album]['name'] = []
        spotify_albums[album]['uri'] = []

        #pull data on album tracks
        tracks = spotify.album_tracks(album) #pull data on album tracks

        for n in range(len(tracks['items'])): #for each song track
            spotify_albums[album]['album'].append(album_names[album_count]) #append album name tracked via album_count
            spotify_albums[album]['track_number'].append(tracks['items'][n]['track_number'])
            spotify_albums[album]['id'].append(tracks['items'][n]['id'])
            spotify_albums[album]['name'].append(tracks['items'][n]['name'])
            spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])

    spotify_albums = {}

    album_count = 0
    
    for i in album_uris: #each album
        albumSongs(i)
        print("Album " + str(album_names[album_count]) + " songs has been added to spotify_albums dictionary")
        album_count+=1 #Updates album count once all tracks have been added

    def audio_features(album):

        #Add new key-values to store audio features
        spotify_albums[album]['danceability'] = []
        spotify_albums[album]['energy'] = []
        spotify_albums[album]['key'] = []
        spotify_albums[album]['loudness'] = []
        spotify_albums[album]['mode'] = []
        spotify_albums[album]['speechiness'] = []
        spotify_albums[album]['acousticness'] = []
        spotify_albums[album]['instrumentalness'] = []
        spotify_albums[album]['liveness'] = []
        spotify_albums[album]['valence'] = []
        spotify_albums[album]['tempo'] = []
        spotify_albums[album]['time_signature'] = []
        spotify_albums[album]['popularity'] = []
            
        #create a track counter
        track_count = 0
        # for loop for track uri
        for track in spotify_albums[album]['uri']:
            #pull audio features per track
            features = spotify.audio_features(track)

            #Append to relevant key-value
            spotify_albums[album]['danceability'].append(features[0]['danceability'])
            spotify_albums[album]['energy'].append(features[0]['energy'])
            spotify_albums[album]['key'].append(features[0]['key']) #added
            spotify_albums[album]['loudness'].append(features[0]['loudness'])
            spotify_albums[album]['mode'].append(features[0]['mode'])
            spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
            spotify_albums[album]['acousticness'].append(features[0]['acousticness'])
            spotify_albums[album]['instrumentalness'].append(features[0]['instrumentalness'])
            spotify_albums[album]['liveness'].append(features[0]['liveness'])
            spotify_albums[album]['valence'].append(features[0]['valence'])
            spotify_albums[album]['tempo'].append(features[0]['tempo'])
            spotify_albums[album]['time_signature'].append(features[0]['time_signature'])
        
            #popularity is stored elsewhere
            pop = spotify.track(track)
            spotify_albums[album]['popularity'].append(pop['popularity'])
            track_count+=1


    sleep_min = 2
    sleep_max = 5
    start_time = time.time()
    request_count = 0
    for i in spotify_albums:
        audio_features(i)
        request_count+=1
        if request_count % 5 == 0:
            print(str(request_count) + " playlists completed")
            time.sleep(np.random.uniform(sleep_min, sleep_max))
            print('Loop #: {}'.format(request_count))
            print('Elapsed Time: {} seconds'.format(time.time() - start_time))

    # building dictionaries
    dic_df = {}
    dic_df['album'] = []
    dic_df['track_number'] = []
    dic_df['id'] = []
    dic_df['name'] = []
    dic_df['uri'] = []
    dic_df['danceability'] = []
    dic_df['energy'] = []
    dic_df['key'] = []
    dic_df['loudness'] = []
    dic_df['mode'] = []
    dic_df['speechiness'] = []
    dic_df['acousticness'] = []
    dic_df['instrumentalness'] = []
    dic_df['liveness'] = []
    dic_df['valence'] = []
    dic_df['tempo'] = []
    dic_df['time_signature'] = []
    dic_df['popularity'] = []
    
    for album in spotify_albums: 
        for feature in spotify_albums[album]:
            dic_df[feature].extend(spotify_albums[album][feature])

    df = pd.DataFrame.from_dict(dic_df)

    final_df = df.sort_values('popularity', ascending=False).drop_duplicates('name').sort_index()

    #renders data frame template
    #return render_template('output.html',  tables=[final_df.to_html(classes='data')], titles=final_df.columns.values)

    # prompts csv download
    csv = final_df
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=artist_tracks.csv"})


if __name__ == '__main__':
    app.debug = True #Uncomment to enable debugging
    app.run() #Run the Server
    .listen(process.env.PORT || 5000)
