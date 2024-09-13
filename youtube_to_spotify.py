 #Youtube to Spotify Converter
    #a. Follow the YouTube tutorial first.
    #b. Change instead of liked videos, use created playlists instead
    #c. Convert to Google Extension

#Step 1: Log into YouTube
#Step 2: Get Liked Videos
#Step 3: Create a New Playlist
#Step 4: Search for song
#Step 5: Add song into the new Playlisy

import json
import requests
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import yt_dlp as youtube_dl
# from info import client_id, get_auth_header, get_token, user_id

class CreatePlaylist:
    
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

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
        validPlaylist = False
        playlist_name = input("Enter playlist link (Example: https://www.youtube.com/playlist?list=playlistid): ")
        # if playlist_name[12:19] != "youtube" or playlist_name[24:37] != "playlist?list":

        get_id = playlist_name.split("=")

        request = self.youtube_client.playlistItems().list(
            part = "snippet,contentDetails",
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
        playlist_name = input("Enter playlist name: ")
        playlist_description = input("Enter playlist description: ")
        request_body = json.dumps({
            "name": playlist_name,
            "description": playlist_description,
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
        query = "https://api.spotify.com/v1/search?query=track%3a{}+artist%3a{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    def add_song_to_playlist(self):
        self.get_liked_videos()

        uri = []
        for song,info in self.all_song_info.items():
            uri.append(info["spotify_url"])
        
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


