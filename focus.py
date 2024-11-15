from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Spotipy OAuth with necessary scopes
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("REDIRECT_URI"),
    scope="playlist-read-private user-read-email"
)

# Step 1: Redirect to Spotify login
@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Step 2: Handle callback and obtain access token
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    
    if token_info:
        session['access_token'] = token_info['access_token']
        return redirect(url_for('focus'))
    else:
        return "Authentication failed", 400

# Focus Mode Page - Displays Focus Playlists
@app.route('/focus')
def focus():
    if 'access_token' in session:
        # Initialize Spotify client with the access token
        sp = Spotify(auth=session['access_token'])
        
        # Search for playlists with "focus" in the title
        search_results = sp.search(q="focus", type="playlist", limit=10)
        focus_playlists = search_results['playlists']['items']

        # Render the Focus Mode page with playlists
        return render_template("focus.html", playlists=focus_playlists, logged_in=True)
    else:
        # Render focus page with login prompt
        return render_template("focus.html", logged_in=False)

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=3000, debug=True)

