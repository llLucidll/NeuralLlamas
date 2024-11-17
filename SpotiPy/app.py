from flask import Flask, redirect, request, session, url_for, render_template, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import secret
import threading
import time
import websocket
from pymongo import MongoClient
import random
import wave
import os
from flask import Flask, render_template
import gridfs

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Spotipy OAuth with necessary scopes
sp_oauth = SpotifyOAuth(
    client_id=secret.client_id,
    client_secret=secret.client_secret,
    redirect_uri=secret.redirect_uri,
    scope="playlist-read-private playlist-modify-private playlist-modify-public user-library-read user-read-email user-top-read"
)

# Global variables to manage concentration and calm data collection
current_song_id = None
concentration_data = []
calm_data = []
data_collection_thread = None
data_collection_stop_event = threading.Event()

def collect_concentration_data(stop_event):
    ws = websocket.WebSocket()
    try:
        ws.connect("ws://localhost:8765")
        while not stop_event.is_set():
            result = ws.recv()
            data = json.loads(result)
            concentration = data.get('concentration')
            if concentration is not None:
                concentration_data.append(concentration)

            # Collect calm data
            calm = data.get('calm')
            if calm is not None:
                calm_data.append(calm)

            time.sleep(0.1)  # Adjust based on your data frequency
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        ws.close()

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

        link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'
        cluster = MongoClient(link)
        db = cluster['NeuralLlama']
        collection = db['concentration']

        # Query to find songs with average_concentration > 0.4
        query = { 'average_concentration': { '$gt': 0.4 } }

        # Projection to include only songID and exclude _id
        projection = { 'songID': 1, '_id': 0 }

        # Execute the query
        results = collection.find(query, projection)

        # Extract song IDs into a list
        song_ids = [doc['songID'] for doc in results]

        # Close the database connection
        cluster.close()

        # Output the list of song IDs
        print("Songs with average_concentration > 0.4:")
        print(song_ids)

        recommended_track_id = get_recommendations(sp, ','.join(song_ids))
        # recommended_track_id = get_recommendations(sp, '3ZgZ9NDAhTT0CnE3rTReqf')
        return render_template("focus.html", track_id=recommended_track_id)
    except Exception as e:
        app.logger.error(f"Error fetching Focus track: {e}")
        return "Failed to load Focus Mode", 400


@app.route('/relax')
def relax_mode():
    """Render the Focus Mode page."""
    if 'access_token' not in session:
        return redirect(url_for('login'))

    try:
        sp = Spotify(auth=session['access_token'])
        # Check or create Focus Playlist

        link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'
        cluster = MongoClient(link)
        db = cluster['NeuralLlama']
        collection = db['concentration']

        # Query to find songs with average_concentration > 0.4
        query = { 'average_calm': { '$lt': 0.2 } }

        # Projection to include only songID and exclude _id
        projection = { 'songID': 1, '_id': 0 }

        # Execute the query
        results = collection.find(query, projection)

        # Extract song IDs into a list
        song_ids = [doc['songID'] for doc in results]

        # Close the database connection
        cluster.close()

        # Output the list of song IDs
        print("Songs with average_calm < 0.2:")
        print(song_ids)
        print(','.join(song_ids))

        # recommended_track_id = get_recommendations(sp, ','.join(song_ids))
        recommended_track_id = get_recommendations(sp, '3ZgZ9NDAhTT0CnE3rTReqf')

        return render_template("relax.html", track_id=recommended_track_id)
    except Exception as e:
        app.logger.error(f"Error fetching Relax track: {e}")
        return "Failed to load Relax Mode", 400


@app.route('/saved')
def saved_songs():
    """Render the Saved Songs page."""
    print(session)
    print(session.get('access_token'))
    if 'access_token' not in session:
        return redirect(url_for('login'))

    try:
        sp = Spotify(auth=session['access_token'])
        # Get the top 25 tracks
        top25 = sp.current_user_top_tracks(limit=25)
        track_ids = [track['id'] for track in top25['items']][:5]

        print(track_ids)  # Debugging print statement

        return render_template("saved.html", track_ids=track_ids)
    
    except Exception as e:
        app.logger.error(f"Error fetching Saved Songs: {e}")
        return "Failed to load Saved Song", 400



@app.route('/about')
def about():
    """Render the About Us page."""
    return render_template("about.html")


@app.route('/dashboard')
def dashboard():
    """Render the Dashboard page."""
    try:
        # Any additional logic or data required for the dashboard can be added here
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error rendering dashboard: {e}")
        return "Failed to load dashboard", 500

@app.route('/generate', methods=['POST'])
def send_focus():
    # Retrieve the "focus" value from the form
    state = request.form.get('focus_value')
    print(f"Received value: {state}")  # For debugging or further processing
    generate_button(state)
    # Redirect to the recommended.html page
    return redirect(url_for('recommended'))


# recommended_songs = ["demo_song.mp3", "another_song.mp3", "example_song.mp3"]

@app.route('/recommended')
def recommended():
    """Render the Recommended page."""
    try:
        # Dynamically select a random song from the list
        # selected_song = random.choice(recommended_songs)
        # Retrieve .wav file from MongoDB by filename

        link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'

        client = MongoClient(link)
        db = client['NeuralLlama']  # Replace with your database name
        fs = gridfs.GridFS(db)

        output_path = "SpotiPy/static/new.wav"
        file = fs.find_one({"filename": "song.wav"})  # Replace with your file's name

        if file:
            with open(output_path, "wb") as output_file:
                output_file.write(file.read())
            print(f"File retrieved and saved as: {output_path}")

            output_path = 'new.wav'
            # Pass the selected song to the template
            return render_template('recommended.html', song_file=output_path)
        else:
            print("File not found.")

    except Exception as e:
        print(f"Error rendering recommended page: {e}")
        return "Failed to load recommended page", 500

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    feedback_data = request.json  # Parse JSON data from request
    print('Feedback received:', feedback_data)
    print('Feedback loudness received:', feedback_data['loudness'])
    link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'
    cluster = MongoClient(link)
    db = cluster['NeuralLlama']
    collection = db['feedback']
    query = {"randomID": 1}
    update = {
        "$set": {
            "tempo": feedback_data['tempo'],
            "loudness": feedback_data['loudness'],
            "energy": feedback_data['energy'],
            "overall_sat": feedback_data['satisfaction'],
            "processed": False
        }
    }
    collection.update_one(query, update)
    # Process the feedback here, e.g., save to a database or log file
    return jsonify({'message': 'Feedback received successfully!'}), 200

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


##################
# GET CONSOLE LOG
##################

@app.route('/log_song', methods=['POST'])
def log_song():
    global current_song_id, concentration_data, calm_data, data_collection_thread, data_collection_stop_event

    song_id = request.json.get('song_id')
    isPaused = request.json.get('isPaused')
    print(f"song_id: {song_id}, isPlayed: {isPaused}")

    if song_id:
        # Initialize Spotipy client with access token
        sp = Spotify(auth=session.get('access_token'))

        try:
            if isPaused is None:
                # Song is playing
                if current_song_id != song_id:
                    # New song started, reset data
                    current_song_id = song_id
                    concentration_data = []
                    calm_data = []
                    data_collection_stop_event.clear()
                    data_collection_thread = threading.Thread(target=collect_concentration_data, args=(data_collection_stop_event,))
                    data_collection_thread.start()
                    print(f"Started collecting data for song ID {song_id}")
                else:
                    # Same song continues playing
                    pass
                return "Started collecting data", 200

            elif isPaused is True:
                print("paused")
                # Song is paused
                if current_song_id == song_id:

                    print(f"Paused collecting data for song ID {current_song_id}")
                    # Stop data collection
                    data_collection_stop_event.set()
                    data_collection_thread.join()

                    print(f"Concentration Data: {concentration_data}")
                    print(f"Calm Data: {calm_data}")

                    if concentration_data or calm_data:
                        # Compute averages
                        average_concentration = sum(concentration_data) / len(concentration_data) if concentration_data else 0
                        average_calm = sum(calm_data) / len(calm_data) if calm_data else 0

                        print(f"Average Concentration: {average_concentration}")
                        print(f"Average Calm: {average_calm}")

                        # Store in database
                        try:
                            link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'
                            cluster = MongoClient(link)
                            db = cluster['NeuralLlama']
                            collection = db['concentration']

                            # Check if the songID already exists in the collection
                            existing_entry = collection.find_one({'songID': current_song_id})

                            if existing_entry:
                                # If the songID exists, calculate the new averages
                                existing_avg_conc = existing_entry.get('average_concentration', 0)
                                existing_avg_calm = existing_entry.get('average_calm', 0)

                                new_avg_conc = (existing_avg_conc + average_concentration) / 2
                                new_avg_calm = (existing_avg_calm + average_calm) / 2

                                # Update the database entry
                                collection.update_one(
                                    {'songID': current_song_id},
                                    {'$set': {
                                        'average_concentration': new_avg_conc,
                                        'average_calm': new_avg_calm
                                    }}
                                )
                                print(f"Updated averages for song ID {current_song_id}: Concentration={new_avg_conc}, Calm={new_avg_calm}")
                            else:
                                # If the songID does not exist, insert a new entry
                                collection.insert_one({
                                    'songID': current_song_id,
                                    'average_concentration': average_concentration,
                                    'average_calm': average_calm
                                })
                                print(f"Inserted new entry for song ID {current_song_id} with averages: Concentration={average_concentration}, Calm={average_calm}")
                        except Exception as db_error:
                            print(f"Database operation failed: {db_error}")
                        finally:
                            cluster.close()

                    else:
                        print("No data collected")
                    # Reset variables
                    current_song_id = None
                    concentration_data = []
                    calm_data = []
                    data_collection_thread = None
                    return "Stopped collecting data", 200
                else:
                    print(current_song_id)
                    print(song_id)
                    # Song paused but IDs don't match
                    print("Paused song does not match current song ID")
                    return "Paused song does not match current song ID", 400

            else:
                # isPaused is something else
                print("Invalid isPaused value")
                return "Invalid isPaused value", 400

        except Exception as e:
            print(f"Error in log_song: {e}")
            return "Failed to process song log", 400
    else:
        return "No song ID provided", 400



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

def get_recommendations(sp, song_id, num_tracks=50):
    recommended_tracks = sp.recommendations(seed_tracks=[song_id], limit=num_tracks)
    recommended_track = recommended_tracks['tracks'][random.randint(0, num_tracks-1)]['id']
    print(recommended_track)
    return recommended_track

def generate_button(which_button):
        link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'
        cluster = MongoClient(link)
        db = cluster['NeuralLlama']
        collection = db['state']
        query = {"randomID": 1}
        update = {
            "$set": {
                "generate": True,
                "state": which_button
            }
        }
        collection.update_one(query, update)
    
# ---------------------------------------------
# Run Flask App
# ---------------------------------------------

if __name__ == "__main__":
    app.run(port=3000, debug=True)

