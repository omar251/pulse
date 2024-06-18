import pyaudio
import socket
import wave
import threading

# Set up the audio stream parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
CHUNK = 1024

# Create a PyAudio instance
audio = pyaudio.PyAudio()

# Open a stream for audio capture
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

# Set up the network socket
HOST = '192.168.1.16'  # The server's hostname or IP address
PORT = 1996  # The port used by the server

# Create a socket and bind it to the address and port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

# Listen for incoming connections
s.listen(1)

print("Server is listening...")

# Function to handle client connections
def handle_client(conn):
    print("Client connected")

    # Continuously send audio data to the client
    while True:
        data = stream.read(CHUNK)
        if not data:
            break
        conn.sendall(data)

    print("Client disconnected")

# Continuously accept new client connections
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()
