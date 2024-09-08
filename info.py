from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from flask import Flask, request, redirect
import urllib.parse
from youtube_to_spotify import CreatePlaylist


load_dotenv()

AUTH_URL = "https://accounts.spotify.com/authorize"
redirect_uri = "http://localhost:1410/callback/"
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_id = os.getenv("USER_ID")
scopes = "playlist-modify-public playlist-modify-private"

app = Flask(__name__)


@app.route("/")
def login():
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scopes,
        'redirect_uri': redirect_uri,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route("/callback/")
def callback():
    # Get the authorization code from the callback URL
    auth_code = request.args.get("code")

    if auth_code:
        token = get_token(auth_code)
        create_playlist = CreatePlaylist(user_id, token)
        result = create_playlist.add_song_to_playlist()
        if token:
            return f"Authoriztion Successful, you may now close this window."
        else:
            return "Failed to get access token", 400
    else:
        return "Authorization code not found", 400

def get_token(auth_code):
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,  # This is the code you get from the callback
        "redirect_uri": redirect_uri
    }



    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)

    token = json_result["access_token"]
    return token


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=1410)


