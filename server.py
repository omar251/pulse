import pyaudio
import socket
import threading

# Set up the audio stream parameters for low latency
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000 
CHUNK = 50  # Or even 128, but test for stability

# Create a PyAudio instance
audio = pyaudio.PyAudio()

# Open a stream for audio capture with low latency settings
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=1,  # Adjust this based on your input device index for optimal performance
                    stream_callback=None)  # Using a callback can sometimes help reduce latency further

# Set up the network socket
HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 1996  # The port used by the server

# Create a socket and bind it to the address and port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle's algorithm for lower latency
s.bind((HOST, PORT))

# Listen for incoming connections
s.listen(1)
print("Server is listening...")

# Function to handle client connections
def handle_client(conn):
    print("Client connected")
    try:
        # Continuously send audio data to the client
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            if not data:
                break
            conn.sendall(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Client disconnected")
        conn.close()

# Continuously accept new client connections
def accept_connections():
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
        except Exception as e:
            print(f"Accept error: {e}")
            break

try:
    accept_connections()
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    # Close resources properly
    stream.stop_stream()
    stream.close()
    audio.terminate()
    s.close()
    print("Server closed")
