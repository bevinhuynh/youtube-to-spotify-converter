import json
import requests
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import yt_dlp as youtube_dl
import urllib.parse
import re
from thefuzz import fuzz, process

class CreatePlaylist:
    
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        self.playlist_link = ""
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    def normalize_song_title(self, title):
        # Remove 'feat.' and other common feature indicators from the title
        return re.sub(r'\s*\(feat\..*\)', '', title, flags=re.IGNORECASE).strip()
    

    def get_youtube_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secret_files = "client_secret.json"

        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secret_files, scopes)
        credentials = flow.run_local_server(port=8080)

        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

        return youtube_client
    
    def get_liked_videos(self):
        self.all_song_info = {}
        get_id = self.playlist_link.split("=")

        request = self.youtube_client.playlistItems().list(
            part = "snippet,contentDetails",
            maxResults=50,
            playlistId = get_id[1]
        )

        response = request.execute()


        for item in response["items"]:

            video_title = item["snippet"]["title"]
            
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["contentDetails"]["videoId"])

            ydl = youtube_dl.YoutubeDL()

            try:

                video = ydl.extract_info(youtube_url, download=False)
             
    
                song_name = video["track"]
                artist = video["artist"]


                self.all_song_info[video_title]={
                    "youtube_url":youtube_url,
                    "song_name":song_name,
                    "artist":artist,

                    "spotify_url":self.get_spotify_url(song_name, artist)
                }

                print(f"Added {song_name} by {artist}")

            except KeyError:
                print("Track not found")
    

    def create_playlist(self): 
        request_body = json.dumps({
            "name": "New Playlist",
            "description": "Converted Youtube Playlist",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type":"application/json",
                "Authorization": 'Bearer ' + self.token
            }
        )
        
        response_json = response.json()

        return response_json["id"]

    def get_spotify_url(self, song_name, artist):
        song_name_encoded = urllib.parse.quote(song_name)
        artist_encoded = urllib.parse.quote(artist)

        query = f"https://api.spotify.com/v1/search?query=track:{song_name_encoded}+artist:{artist_encoded}&type=track&offset=0&limit=20"

        response = requests.get(
            query,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        explicit_songs = []
        for song in songs:
            if song['explicit'] == True:
                explicit_songs.append(song)

        if len(explicit_songs) > 0:
            songs = explicit_songs
        
        spotify_songs = []
        # for song in songs: #organizes found spotify songs by Title - Artist Name
        #     completed_name = song["name"] + " - " + song["artists"][0]["name"]
        #     spotify_songs.append(completed_name)
        # print(spotify_songs)
        full_song_name = song_name + " - " + artist
        song_ratios = {}
        for song in songs:
            completed_name = song["name"] + " - " + song["artists"][0]["name"]
            ratio = fuzz.ratio(full_song_name, completed_name)
            song_ratios[song["uri"]] = ratio
            # spotify_song_name = self.normalize_song_title(song['name'])
            # normalized_song_name = self.normalize_song_title(song_name)

            # spotify_artists = [a['name'].lower() for a in song['artists']]
            # spotify_artists = (', ').join(spotify_artists)

            # if spotify_artists == artist.lower() and normalized_song_name.lower() == spotify_song_name.lower():
            #     return song["uri"]
        if len(song_ratios) > 0:
            return max(song_ratios, key=song_ratios.get)
        return None

    def add_song_to_playlist(self):
        self.get_liked_videos()

        uri = []
        for song,info in self.all_song_info.items():
            uri.append(info["spotify_url"])

        uri = [uri for uri in uri if uri is not None]
        
        playlist_id = self.create_playlist()

        request_data = json.dumps(uri)
        
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.token)
            }
        )
        response_json = response.json()
        return response_json


