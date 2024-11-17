// Function to send the current song ID to the server
function logCurrentSong(songId, isPaused) {
    fetch('/log_song', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ song_id: songId, isPaused: isPaused })
    }).then(response => {
        if (!response.ok) {
            console.error('Failed to log song:', response.statusText);
        } else {
            console.log(`Logged song ID: ${songId}`);
        }
    }).catch(error => {
        console.error('Error logging song:', error);
    });
}

// Spotify IFrame API Ready function
window.onSpotifyIframeApiReady = (IFrameAPI) => {
    const iframes = document.querySelectorAll('.spotify-embed');
    iframes.forEach((iframe) => {
        const element = iframe;
        const options = {
            uri: iframe.getAttribute('data-uri'),
            songId: iframe.getAttribute('songID')
        };

        const callback = (EmbedController) => {
            // Add event listener for playback updates
            EmbedController.addListener('playback_update', (e) => {
                console.log(`heyyy ${e.data.isPaused}`);
                if (e.data.isPaused) {
                    console.log(`Paused song: ${options.uri}`);
                    console.log(e.data.isPaused);
                    // console.log(`Song ID: ${options.songId}`);
                    logCurrentSong(options.songId, e.data.isPaused);
                } else {
                    console.log(`Playing song: ${options.uri}`);
                    // console.log(`Song ID: ${options.songId}`);
                    logCurrentSong(options.songId);
                }
            });
        };

        // Create the controller for each iframe
        IFrameAPI.createController(element, options, callback);
    });
};