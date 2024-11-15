// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

function App() {
    // State variables
    const [mood, setMood] = useState(''); // Current mode: 'focus' or 'relax'
    const [playlist, setPlaylist] = useState([]); // List of songs in the playlist
    const [savedSongs, setSavedSongs] = useState([]); // List of saved songs for later listening

    // Function to fetch playlist based on selected mood
    const fetchPlaylist = async (selectedMood) => {
        try {
            const response = await axios.get(`/get_playlist?mood=${selectedMood}`);
            setPlaylist(response.data.tracks.items);
        } catch (error) {
            console.error("Error fetching playlist:", error);
        }
    };

    // Function to save a song to the saved songs list
    const saveSong = (song) => {
        setSavedSongs((prev) => [...prev, song]);
    };

    // Effect to fetch playlist when mood changes
    useEffect(() => {
        if (mood) fetchPlaylist(mood);
    }, [mood]);

    // Sample data for focus level graph (replace with real-time data later)
    const data = {
        labels: ['Time 1', 'Time 2', 'Time 3', 'Time 4', 'Time 5'],
        datasets: [
            {
                label: 'Focus Level',
                data: [12, 19, 3, 5, 2], // Sample data points
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
            },
        ],
    };

    const options = {
        responsive: true,
        scales: {
            y: { beginAtZero: true },
        },
    };

    return (
        <div className="App" style={{ padding: '20px' }}>
            <h1>Focus & Relax Music App</h1>
            <div style={{ margin: '20px 0' }}>
                <button onClick={() => setMood('focus')}>Focus Mode</button>
                <button onClick={() => setMood('relax')}>Relax Mode</button>
            </div>

            <div>
                <h2>Playlist ({mood ? mood.charAt(0).toUpperCase() + mood.slice(1) : 'Select a Mode'})</h2>
                {playlist.length ? (
                    playlist.map((track) => (
                        <div key={track.id} style={{ margin: '10px 0' }}>
                            <p>{track.name} by {track.artists[0].name}</p>
                            <button onClick={() => saveSong(track)}>Save Song</button>
                        </div>
                    ))
                ) : (
                    <p>Select a mode to view the playlist</p>
                )}
            </div>

            <div style={{ margin: '20px 0' }}>
                <h2>Saved Songs</h2>
                {savedSongs.length ? (
                    savedSongs.map((track) => (
                        <div key={track.id} style={{ margin: '10px 0' }}>
                            <p>{track.name} by {track.artists[0].name}</p>
                        </div>
                    ))
                ) : (
                    <p>No saved songs yet.</p>
                )}
            </div>

            <div style={{ margin: '20px 0' }}>
                <h2>Dashboard - Focus Level</h2>
                <Line data={data} options={options} />
            </div>
        </div>
    );
}

export default App;
