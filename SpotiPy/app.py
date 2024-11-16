from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import secret

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Spotipy OAuth with necessary scopes
sp_oauth = SpotifyOAuth(
    client_id=secret.client_id,
    client_secret=secret.client_secret,
    redirect_uri=secret.redirect_uri,
    scope="playlist-read-private playlist-modify-private playlist-modify-public user-library-read user-read-email"
)

# ---------------------------------------------
# General Website Routes
# ---------------------------------------------

@app.route('/')
def index():
    """Render the home page."""
    return render_template("index.html")


@app.route('/focus')
def focus_mode():
    """Render the Focus Mode page."""
    if 'access_token' not in session:
        return redirect(url_for('login'))

    try:
        sp = Spotify(auth=session['access_token'])
        # Check or create Focus Playlist
        focus_playlist = get_or_create_playlist(sp, "Focus Playlist", "A playlist for focus and productivity.")
        return render_template("focus.html", playlist_id=focus_playlist['id'])
    except Exception as e:
        app.logger.error(f"Error fetching Focus Playlist: {e}")
        return "Failed to load Focus Mode", 400



@app.route('/relax')
def relax_mode():
    """Render the Relax Mode page."""
    if 'access_token' not in session:
        return redirect(url_for('login'))

    try:
        sp = Spotify(auth=session['access_token'])
        # Check or create Relax Playlist
        relax_playlist = get_or_create_playlist(sp, "Relax Playlist", "A playlist for relaxation and unwinding.")
        return render_template("relax.html", playlist_id=relax_playlist['id'])
    except Exception as e:
        app.logger.error(f"Error fetching Relax Playlist: {e}")
        return "Failed to load Relax Mode", 400

@app.route('/saved')
def saved_songs():
    """Render the Saved Songs page."""
    return render_template("saved.html", message="Your favourite songs")



@app.route('/about')
def about():
    """Render the About Us page."""
    return render_template("about.html")


# ---------------------------------------------
# Spotify Integration Routes
# ---------------------------------------------

@app.route('/login')
def login():
    """Redirect the user to the Spotify login page."""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle Spotify authentication callback and save the access token."""
    code = request.args.get('code')
    try:
        token_info = sp_oauth.get_access_token(code)
        session['access_token'] = token_info['access_token']
        return redirect(url_for('index'))  # Redirect back to the home page
    except Exception as e:
        app.logger.error(f"Error during Spotify callback: {e}")
        return "Authentication failed", 400
    
@app.route('/dashboard')
def dashboard():
    """Render the Dashboard page."""
    try:
        # Any additional logic or data required for the dashboard can be added here
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error rendering dashboard: {e}")
        return "Failed to load dashboard", 500
@app.route('/recommended')
def recommended():
    """Render the Recommended page."""
    try:
        # Logic for fetching or generating recommendations can be added here.
        # For example, fetching recommended songs or playlists from Spotify.
        return render_template('recommended.html')
    except Exception as e:
        print(f"Error rendering recommended page: {e}")
        return "Failed to load recommended page", 500



# ---------------------------------------------
# Helper Functions
# ---------------------------------------------

def get_or_create_playlist(sp, playlist_name, description):
    """Fetch an existing playlist or create a new one."""
    playlists = sp.current_user_playlists(limit=50)
    for playlist in playlists['items']:
        if playlist['name'].lower() == playlist_name.lower():
            return playlist
    # If playlist not found, create it
    user_profile = sp.me()
    return sp.user_playlist_create(user=user_profile['id'], name=playlist_name, public=False, description=description)


# ---------------------------------------------
# Run Flask App
# ---------------------------------------------

if __name__ == "__main__":
    app.run(port=3000, debug=True)

