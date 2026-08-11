import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# need to match with app.py
CACHE_PATH = '/app/data/.cache'

auth_manager = SpotifyOAuth(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    redirect_uri = REDIRECT_URI,
    open_browser = False,
    scope = 'user-read-recently-played',
    cache_path = CACHE_PATH
)

auth_url = auth_manager.get_authorize_url()
print()
print(auth_url)

response_url = input("\nPaste the full redirect url").strip()
code = auth_manager.parse_response_code(response_url)
auth_manager.get_access_token(code, as_dict=False)

print("Reauth successful")