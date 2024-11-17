from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, WindowOperations
import time
import numpy as np

from websocket_server import WebsocketServer
import threading
import json

# WebSocket server settings
HOST = 'localhost'
PORT = 8765

#List to keep track of connected clients
clients = []

def new_client(client, server):
    print(f"New client connected: {client['id']}")
    clients.append(client)

def client_left(client, server):
    print(f"Client disconnected: {client['id']}")
    clients.remove(client)

def send_eeg_data(data):
    # Convert the data dictionary to JSON string
    message = json.dumps(data)
    # Send the message to all connected clients
    server.send_message_to_all(message)

def run_websocket_server():
    global server
    server = WebsocketServer(host=HOST, port=PORT)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    print(f"WebSocket server started on ws://{HOST}:{PORT}")
    server.run_forever()

def compute_band_powers(data, sampling_rate):
    bands = {}
    eeg_channels = BoardShim.get_eeg_channels(board_id)

    for ch in eeg_channels:
        DataFilter.perform_bandpass(data[ch], sampling_rate, 1.0, 50.0, 4, 0, 0)

        data_length = len(data[ch])
        if data_length < 256:
            print(f"Data length ({data_length}) is too short for nfft=256. Adjust parameters.")

        psd, freq = DataFilter.get_psd_welch(
            data=data[ch],
            nfft=256,
            overlap=128,
            sampling_rate=sampling_rate,
            window=WindowOperations.BLACKMAN_HARRIS.value
        )
        bands[ch] = (psd, freq)

    alpha = []
    beta = []
    gamma = []
    delta = []
    theta = []

    for ch in eeg_channels:
        psd, freq = bands[ch]
        alpha.append(DataFilter.get_band_power((psd, freq), 8.0, 13.0))
        beta.append(DataFilter.get_band_power((psd, freq), 13.0, 30.0))
        gamma.append(DataFilter.get_band_power((psd, freq), 30.0, 50.0))
        delta.append(DataFilter.get_band_power((psd, freq), 1.0, 4.0))
        theta.append(DataFilter.get_band_power((psd, freq), 4.0, 8.0))

    band_powers = {
        'alpha': np.mean(alpha),
        'beta': np.mean(beta),
        'gamma': np.mean(gamma),
        'delta': np.mean(delta),
        'theta': np.mean(theta)
    }

    return band_powers
#Calm index (alpha+theta)/total_power
def compute_custom_calm(band_powers):
    total_power = sum(band_powers.values())
    if total_power == 0:
        return 0.0
    calm_score = (band_powers['alpha'] + band_powers['theta']) / total_power
    return calm_score

def compute_custom_concentration(band_powers):
    total_power = sum(band_powers.values())
    if total_power == 0:
        return 0.0
    # concentration_score = band_powers['beta'] / total_power
    concentration_score = (band_powers['beta'] + band_powers['alpha']) / total_power
    return concentration_score

def compute_custom_mindfulness(band_powers):
    total_power = sum(band_powers.values())
    if total_power == 0:
        return 0.0
    mindfulness_score = (band_powers['alpha'] + band_powers['theta']) / total_power
    return mindfulness_score

if __name__ == "__main__":
    # Start WebSocket server in a separate thread
    ws_thread = threading.Thread(target=run_websocket_server)
    ws_thread.daemon = True
    ws_thread.start()



    BoardShim.enable_board_logger()

    params = BrainFlowInputParams()
    params.mac_address = '61CA5961-72E1-290F-2FBC-144646B3D496'  # Replace with your device's MAC address
    # params.serial_port = 'COM5'


    board = BoardShim(BoardIds.MUSE_S_BOARD.value, params)
    board_id = board.get_board_id()
    sampling_rate = BoardShim.get_sampling_rate(board_id)
    eeg_channels = BoardShim.get_eeg_channels(board_id)

    try:
        board.prepare_session()
        board.start_stream()
        print('Starting data stream...')

        while True:
            time.sleep(2)
            data = board.get_current_board_data(256)
            print(f"EEG channels: {eeg_channels}")
            print(f"Data shape: {data.shape}")

            band_powers = compute_band_powers(data, sampling_rate)

            concentration_score = compute_custom_concentration(band_powers)
            mindfulness_score = compute_custom_mindfulness(band_powers)
            calm_score = compute_custom_calm(band_powers)
            


            print(f"Alpha: {band_powers['alpha']:.2f}, Beta: {band_powers['beta']:.2f}, "
                  f"Gamma: {band_powers['gamma']:.2f}, Delta: {band_powers['delta']:.2f}, "
                  f"Theta: {band_powers['theta']:.2f}")
            print(f"Concentration Score: {concentration_score:.2f}")
            print(f"Mindfulness Score: {mindfulness_score:.2f}")
            print(f"Calm Score: {mindfulness_score:.2f}")



            """ 3.4 SEND DATA VIA WEBSOCKET """
            eeg_data_dict = {
                "alpha": band_powers['alpha'],
                "beta": band_powers['beta'],
                "theta": band_powers['theta'],
                "delta":band_powers['delta'],
                "gamma":band_powers['gamma'],
                "concentration": concentration_score,
                "calm": calm_score
            }
            send_eeg_data(eeg_data_dict)


    except KeyboardInterrupt:
        print('Interrupted by user')

    finally:
        board.stop_stream()
        board.release_session()