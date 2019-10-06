# Boilerplate codes.
import os
import sys
import spotipy
import spotipy.util as util
import json

Spotify = spotipy.Spotify

os.environ['SPOTIPY_CLIENT_ID'] = '00b7317977ad4c0d971af8274f1aa790'
os.environ['SPOTIPY_CLIENT_SECRET'] = '6efbf45fe72d435f9739d0c0f4c26db5'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://360i.com/'
base_url = 'https://api.spotify.com'
scope = 'playlist-read-private'
# spotify:playlist:
rap_caviar = '5yolys8XG4q7YfjYGl5Lff'
token = util.prompt_for_user_token('Puffer Fish', scope=scope)
spotify_object = Spotify(auth=token)


# Getting data
results = spotify_object.search("Rap Caviar", limit=1, type='playlist')
# Getting playlist id and owner name of the playlist(spotify)
playlist_id = results['playlists']['items'][0]['id']
playlist_owner = results['playlists']['items'][0]['owner']['id']

# Getting a bit cleaned up.
results = spotify_object.user_playlist(playlist_owner, playlist_id)
results = results['tracks']['items']

# initializing some lists.
track_name = []
track_popularity = []
duration_ms = []
artist_name = []
track_id = []
album_name = []
release_date = []

# just going through the spotify object and retriving data.
for result in results:
    track_name.append(result['track']['name'])
    duration_ms.append(result['track']['duration_ms'])
    track_popularity.append(result['track']['popularity'])
    artist_name.append(result['track']['artists'][0]['name'])
    track_id.append(result['track']['id'])
    album_name.append(result['track']['album']['name'])
    release_date.append(result['track']['album']['release_date'])


# Creating Database
import sqlite3
from sqlite3 import Error

# write some functions to create batabase table and insert values


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn
# Creating table function


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        pass

# function to insert values


def insert_values(conn, sql_statement, values):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_statement, values)
    except Error as e:
        pass


# creating a connection with database
sqlite_db = '360i_db.sqlite'
conn = create_connection(sqlite_db)

# Table #1(tracks)
# Creating our first table "tracks"
sql_table = 'CREATE TABLE IF NOT EXISTS tracks(track_id CHAR(20) PRIMARY KEY, name TEXT, popularity INTEGER, duration_ms INTEGER, artist_name TEXT, album TEXT, release_date TEXT);'
create_table(conn, sql_table)

# looping through all the lists and inserting values.
for i, n, p, d, at, alb, dt in zip(track_id,
                                   track_name,
                                   track_popularity,
                                   duration_ms,
                                   artist_name,
                                   album_name,
                                   release_date):
    values = (i, n, p, d, at, alb, dt)
    insert_values(conn, 'INSERT INTO tracks VALUES (?,?,?,?,?,?,?)', values)
    conn.commit()

# Table #2(Artists)
# Initializing a dict to store unique artist id and name. This is to avoid duplicates.
artist_dict = {}
for result in results:
    for item in result['track']['artists']:
        if item['id'] in artist_dict:
            continue
        else:
            artist_dict[item['id']] = item['name']

# using the created dict above to get popularity and followers column.
for key, value in artist_dict.items():
    artist_dict[key] = (value, spotify_object.artist(key)['popularity'], spotify_object.artist(key)['followers']['total'])

# Creating 'artists' table
sql_statement = 'CREATE TABLE IF NOT EXISTS artists(artist_id CHAR(22) PRIMARY KEY, name TEXT, popularity INTEGER, followers INTEGER);'
create_table(conn, sql_statement)

# Inserting values.
for key, value in artist_dict.items():
    values = (key, value[0], value[1], value[2])
    insert_values(conn, 'INSERT INTO artists VALUES (?,?,?,?)', values)
    conn.commit()

# Analysis
import pandas as pd
from pandas.io import sql

# Writing a little function to make our life a bit easier.


def Q(input_string, db=conn):
    #     return sql.read_sql(input_string, db)
    return pd.read_sql(input_string, db)


# How many songs are there in the tracks table.
print(Q('SELECT COUNT(*) FROM tracks'))


# What are the top 5 tracks by artist follower count?
Q("""SELECT tracks."name"
FROM tracks
JOIN artists
ON tracks."artist_name" = artists."name"
ORDER BY artists."followers" DESC
LIMIT 5
""")
