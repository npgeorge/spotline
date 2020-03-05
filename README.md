# spotline
flask app for gathering data from spotify API spotipy

#old procfile
web: gunicorn spotline:app --preload -b 0.0.0.0:5000 