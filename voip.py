import socket
import pyaudio

# Set up the audio stream parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
CHUNK = 1024

# Create a PyAudio instance
audio = pyaudio.PyAudio()

# Open a stream for audio playback
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, output=True,
                    frames_per_buffer=CHUNK)

# Set up the network socket
HOST = '192.168.1.10'  # The server's hostname or IP address
PORT = 1996  # The port used by the server

# Create a socket and connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Continuously receive data from the server and play it
    while True:
        data = s.recv(CHUNK)
        if not data:
            break
        stream.write(data)

# Clean up
stream.stop_stream()
stream.close()
audio.terminate()