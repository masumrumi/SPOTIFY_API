# Boilerplate code


```python
# Boilerplate codes. 
import os
import sys
import spotipy
import spotipy.util as util
import json

Spotify = spotipy.Spotify

## spotify account details
## you can save those in your .bash_profile file and access it from there..

## this way
# os.environ['SPOTIPY_CLIENT_ID'] = 'your-spotify-client-id'
# os.environ['SPOTIPY_CLIENT_SECRET'] = 'your-spotify-client-secret'
# os.environ['SPOTIPY_REDIRECT_URI'] = 'your-app-redirect-url'

## or this way. 
token = os.environ['SPOTIPY_CLIENT_TOKEN']
base_url = 'https://api.spotify.com'
scope = 'playlist-read-private'

# spotify:playlist:
token = util.prompt_for_user_token( token,scope=scope)
spotify_object = Spotify(auth=token)


```

# Creating database functions


```python
# Creating DataBase functions
import sqlite3
from sqlite3 import Error

## write some functions to create batabase table and insert values
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
## Creating table function
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

## function to insert values        
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
```


```python
def getting_playlist_data_to_database(playlist_id, playlist_owner, db, sql_table_statement, sql_value_statement):
    
    ## Getting a bit cleaned up. 
    results = spotify_object.user_playlist(playlist_owner, playlist_id)
    results = results['tracks']['items']
    
    ## initializing some lists.
    track_name = []
    track_popularity = []
    duration_ms = []
    artist_name = []
    track_id = []
    album_name = []
    release_date = []
    
    ## just going through the spotify object and retriving data. 
    for result in results:
        track_name.append(result['track']['name'])
        duration_ms.append(result['track']['duration_ms'])
        track_popularity.append(result['track']['popularity'])
        artist_name.append(result['track']['artists'][0]['name'])
        track_id.append(result['track']['id'])
        album_name.append(result['track']['album']['name'])
        release_date.append(result['track']['album']['release_date'])
        
    ## creating a connection with database
    conn = create_connection(db)
    create_table(conn, sql_table_statement)
    
    ## looping through all the lists and inserting values. 
    for i, n, p, d, at, alb, dt in zip(track_id, 
                                   track_name, 
                                   track_popularity, 
                                   duration_ms, 
                                   artist_name, 
                                   album_name, 
                                   release_date):
        values = (i, n, p, d, at, alb, dt)
        insert_values(conn, sql_value_statement, values)
        conn.commit()


```

# Table#1(tracks)


```python
results = spotify_object.search("Rap Caviar", limit = 1, type='playlist')
```


```python
# used this to have print readable spotify_object
# print (json.dumps(artist, sort_keys=True, indent=4))
```


```python
playlist_id =  results['playlists']['items'][0]['id']
playlist_owner = results['playlists']['items'][0]['owner']['id']
```


```python
sqlite_db = '360i_db.sqlite'

## Getting playlist id and owner name of the playlist(spotify)
playlist_id =  results['playlists']['items'][0]['id']
playlist_owner = results['playlists']['items'][0]['owner']['id']

## sql_command for creating table. 
sql_table = 'CREATE TABLE IF NOT EXISTS tracks(track_id CHAR(20) PRIMARY KEY, name TEXT, popularity INTEGER, duration_ms INTEGER, artist_name TEXT, album TEXT, release_date TEXT);'

## sql command for inserting values
value_statement = 'INSERT INTO tracks VALUES (?,?,?,?,?,?,?)'
```


```python
## this function creates database and inserts values. 
getting_playlist_data_to_database(playlist_id, playlist_owner, sqlite_db,sql_table, value_statement)
```

## Table#2 (Artists)


```python
results = spotify_object.user_playlist(playlist_owner, playlist_id)
results = results['tracks']['items']
```


```python
## Initializing a dict to store unique artist id and name. This is to avoid duplicates.  
artist_dict = {}
for result in results:
    for item in result['track']['artists']:
        if item['id'] in artist_dict:
            continue
        else:
            artist_dict[item['id']] = item['name']

## using the created dict above to get popularity and followers column. 
for key,value in artist_dict.items():
    try:
        artist_dict[key] = (value, spotify_object.artist(key)['popularity'], spotify_object.artist(key)['followers']['total'])
    except:
        artist_dict[key] = (value, 'NA', 'NA')

```


```python
## getting rid of values that are NA. 
artist_dict = {i: v for i, v in artist_dict.items() if v[1] != 'NA'}
```


```python
## Creating 'artists' table
conn = sqlite3.connect(sqlite_db)
sql_statement = 'CREATE TABLE IF NOT EXISTS artists(artist_id CHAR(22) PRIMARY KEY, name TEXT, popularity INTEGER, followers INTEGER);'
create_table(conn, sql_statement)
```


```python
## Inserting values. 
for key, value in artist_dict.items():
    values = (key, value[0], value[1], value[2])
    insert_values(conn, 'INSERT INTO artists VALUES (?,?,?,?)', values)
    conn.commit()
```

## Analysis


```python
import pandas as pd
from pandas.io import sql

## Writing a little function to make our life a bit easier. 
def Q(input_string, db = conn):
#     return sql.read_sql(input_string, db)
    return pd.read_sql(input_string, db)


## How many songs are there in the tracks table. 
Q('SELECT COUNT(*) FROM tracks')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>COUNT(*)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>54</td>
    </tr>
  </tbody>
</table>
</div>




```python
## What are the top 5 tracks by artist follower count?
Q("""SELECT tracks."name" 
FROM tracks 
JOIN artists
ON tracks."artist_name" = artists."name"
ORDER BY artists."followers" DESC
LIMIT 5
""")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NorthStar - Remix</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Follow God</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Futsal Shuffle 2020</td>
    </tr>
    <tr>
      <th>3</th>
      <td>HIGHEST IN THE ROOM</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Immortal</td>
    </tr>
  </tbody>
</table>
</div>




```python
## What are the top 5 tracks by artist follower count?
Q("""SELECT tracks."name", artists."name", artists."followers" 
FROM tracks 
JOIN artists
ON tracks."artist_name" = artists."name"
ORDER BY artists."followers" DESC
LIMIT 5
""")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>name</th>
      <th>followers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NorthStar - Remix</td>
      <td>XXXTENTACION</td>
      <td>16760146</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Follow God</td>
      <td>Kanye West</td>
      <td>10840912</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Futsal Shuffle 2020</td>
      <td>Lil Uzi Vert</td>
      <td>7382041</td>
    </tr>
    <tr>
      <th>3</th>
      <td>HIGHEST IN THE ROOM</td>
      <td>Travis Scott</td>
      <td>7329878</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Immortal</td>
      <td>21 Savage</td>
      <td>7107211</td>
    </tr>
  </tbody>
</table>
</div>




```python
## Which song is the longest?
Q("""SELECT name, MAX(duration_ms) FROM tracks
""")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>MAX(duration_ms)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Hot (Remix) [feat. Gunna and Travis Scott]</td>
      <td>279906</td>
    </tr>
  </tbody>
</table>
</div>




```python
## What is the relationship between track and artist popularity?
## Let's do a little analysis, 
df = Q("""SELECT tracks."popularity" as 'tracks_popularity', 
tracks."duration_ms", 
tracks."artist_name", 
artists."popularity" as 'artist_popularity',
artists."followers"
FROM tracks
JOIN artists
ON tracks."artist_name"= artists."name"
""")
```


```python
df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tracks_popularity</th>
      <th>duration_ms</th>
      <th>artist_name</th>
      <th>artist_popularity</th>
      <th>followers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>84</td>
      <td>198912</td>
      <td>Lil Uzi Vert</td>
      <td>90</td>
      <td>7382041</td>
    </tr>
    <tr>
      <th>1</th>
      <td>92</td>
      <td>159714</td>
      <td>DaBaby</td>
      <td>94</td>
      <td>1492998</td>
    </tr>
    <tr>
      <th>2</th>
      <td>97</td>
      <td>175720</td>
      <td>Travis Scott</td>
      <td>97</td>
      <td>7329878</td>
    </tr>
    <tr>
      <th>3</th>
      <td>82</td>
      <td>196652</td>
      <td>Roddy Ricch</td>
      <td>89</td>
      <td>890667</td>
    </tr>
    <tr>
      <th>4</th>
      <td>82</td>
      <td>215380</td>
      <td>Juice WRLD</td>
      <td>98</td>
      <td>6796358</td>
    </tr>
  </tbody>
</table>
</div>




```python
import matplotlib.pyplot as plt
import seaborn as sns
plt.subplots(figsize = (15,12))
sns.scatterplot(x = 'tracks_popularity', y = 'artist_popularity',size = 'followers', data = df);
```

As you can see there is a positive correlation between tracks and artists popularity. It seems as if popular artists tend to produce popular tracks. However, sometimes things  as you can see the top left data point

# Bonus Analysis


```python
sns.pairplot(df);
```


![png](spotify_api_files/spotify_api_27_0.png)


It looks like there are a couple of datapoint in the followers column, that are outliers. If we get rid off those couple of points we might be able to get a better look at the data. Let's find out those artist with top followers. 


```python
df.sort_values(by = 'followers', ascending = False).head(8)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tracks_popularity</th>
      <th>duration_ms</th>
      <th>artist_name</th>
      <th>artist_popularity</th>
      <th>followers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>44</th>
      <td>75</td>
      <td>166406</td>
      <td>XXXTENTACION</td>
      <td>95</td>
      <td>16760146</td>
    </tr>
    <tr>
      <th>40</th>
      <td>90</td>
      <td>104591</td>
      <td>Kanye West</td>
      <td>95</td>
      <td>10840912</td>
    </tr>
    <tr>
      <th>0</th>
      <td>84</td>
      <td>198912</td>
      <td>Lil Uzi Vert</td>
      <td>90</td>
      <td>7382041</td>
    </tr>
    <tr>
      <th>2</th>
      <td>97</td>
      <td>175720</td>
      <td>Travis Scott</td>
      <td>97</td>
      <td>7329878</td>
    </tr>
    <tr>
      <th>12</th>
      <td>85</td>
      <td>254723</td>
      <td>21 Savage</td>
      <td>89</td>
      <td>7107211</td>
    </tr>
    <tr>
      <th>4</th>
      <td>82</td>
      <td>215380</td>
      <td>Juice WRLD</td>
      <td>98</td>
      <td>6796358</td>
    </tr>
    <tr>
      <th>10</th>
      <td>94</td>
      <td>189322</td>
      <td>Juice WRLD</td>
      <td>98</td>
      <td>6796358</td>
    </tr>
    <tr>
      <th>6</th>
      <td>89</td>
      <td>279906</td>
      <td>Young Thug</td>
      <td>93</td>
      <td>4638713</td>
    </tr>
  </tbody>
</table>
</div>



So, Drake and Post Malone are so far above and away from others that interms of followers that we may be better off leaving them out of the dataset. 


```python
df_followers = df[df.followers <17356258]

sns.pairplot(df_followers);
```


![png](spotify_api_files/spotify_api_31_0.png)


Well, If we look at the top right plot,we see that there are a cluster of datapoints where tracks_popularity is fairly high eventhough there isn't enough followers. However, the relationship between artist_popularity and tracks_popularity is quite significant as we have discussed earlier. May be if we have more data we can reveal something more significant.

# Bonus Data


```python
# results = spotify_object.search("biggest playlist ever.", limit = 10, type='playlist')
# results['playlists']['items']
```


```python
sqlite_db = '360i_db.sqlite'
## Getting playlist id and owner name of the playlist(spotify)
playlist_owner = 'maxmoroz07'
playlist_id = '7htu5ftbLBRFAwiuHVcUAg'

## sql_command for creating table. 
sql_table = 'CREATE TABLE IF NOT EXISTS tracks_100(track_id CHAR(20) PRIMARY KEY, name TEXT, popularity INTEGER, duration_ms INTEGER, artist_name TEXT, album TEXT, release_date TEXT);'

## sql command for inserting values
value_statement = 'INSERT INTO tracks_100 VALUES (?,?,?,?,?,?,?)'
```


```python
## this function creates database and inserts values. 
getting_playlist_data_to_database(playlist_id, playlist_owner, sqlite_db,sql_table, value_statement)
```

# Resources used
#### https://www.sqlitetutorial.net/sqlite-python/create-tables/ 
#### https://spotipy.readthedocs.io/en/latest/
 


```python

```
