import pyaudio
import wave
from flask import Flask, Response, render_template

app = Flask(__name__)

# List audio devices to confirm the correct index
def list_audio_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']}")

# list_audio_devices()

# Set up audio stream
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    input_device_index=1,  # Replace with correct index
                    frames_per_buffer=128)

def generate_wav_header(sample_rate, bits_per_sample, channels):
    # WAV file header format
    datasize = 2000*10**6
    o = bytes("RIFF", 'ascii')  # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4, 'little')  # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE", 'ascii')  # (4byte) File type
    o += bytes("fmt ", 'ascii')  # (4byte) Format Chunk Marker
    o += (16).to_bytes(4, 'little')  # (4byte) Length of above format data
    o += (1).to_bytes(2, 'little')  # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2, 'little')  # (2byte)
    o += (sample_rate).to_bytes(4, 'little')  # (4byte)
    o += (sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little')  # (4byte)
    o += (channels * bits_per_sample // 8).to_bytes(2, 'little')  # (2byte)
    o += (bits_per_sample).to_bytes(2, 'little')  # (2byte)
    o += bytes("data", 'ascii')  # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4, 'little')  # (4byte) Data size in bytes
    return o

def generate():
    wav_header = generate_wav_header(44100, 16, 1)
    yield wav_header
    while True:
        try:
            data = stream.read(1024)
            yield data
        except Exception as e:
            print(f"Error reading stream: {e}")
            break

@app.route('/audio')
def audio_feed():
    print("Streaming audio...")
    return Response(generate(), mimetype='audio/wav')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
