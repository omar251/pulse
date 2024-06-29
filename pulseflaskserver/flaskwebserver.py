from flask import Flask, Response, render_template, request, jsonify
import pyaudio
import wave
import io
import threading
import configparser
import logging

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)

# Server settings
HOST = config.get('Server', 'host')
PORT = config.getint('Server', 'port')
DEBUG = config.getboolean('Server', 'debug')

# Audio settings
CHUNK = config.getint('Audio', 'chunk')
FORMAT = getattr(pyaudio, config.get('Audio', 'format'))
CHANNELS = config.getint('Audio', 'channels')
RATE = config.getint('Audio', 'rate')
DEVICE_INDEX = config.get('Audio', 'device_index')
DEVICE_INDEX = int(DEVICE_INDEX) if DEVICE_INDEX else None

# Logging setup
logging.basicConfig(filename=config.get('Logging', 'file'), 
                    level=getattr(logging, config.get('Logging', 'level')),
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Global variables
stream = None
is_streaming = False
stream_lock = threading.Lock()

def get_audio_devices():
    devices = []
    for i in range(audio.get_device_count()):
        dev_info = audio.get_device_info_by_index(i)
        if dev_info['maxInputChannels'] > 0:  # Only input devices
            devices.append({
                'index': i,
                'name': dev_info['name'],
                'channels': dev_info['maxInputChannels'],
                'sample_rate': int(dev_info['defaultSampleRate'])
            })
    return devices

def generate_wav_header(sample_rate, bits_per_sample, channels):
    datasize = 2000 * 10**6
    o = bytes("RIFF",'ascii')
    o += (datasize + 36).to_bytes(4,'little')
    o += bytes("WAVE",'ascii')
    o += bytes("fmt ",'ascii')
    o += (16).to_bytes(4,'little')
    o += (1).to_bytes(2,'little')
    o += (channels).to_bytes(2,'little')
    o += (sample_rate).to_bytes(4,'little')
    o += (sample_rate * channels * bits_per_sample // 8).to_bytes(4,'little')
    o += (channels * bits_per_sample // 8).to_bytes(2,'little')
    o += (bits_per_sample).to_bytes(2,'little')
    o += bytes("data",'ascii')
    o += (datasize).to_bytes(4,'little')
    return o

def audio_stream():
    global stream, is_streaming
    
    with stream_lock:
        if stream is None:
            stream = audio.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                input_device_index=DEVICE_INDEX,
                                frames_per_buffer=CHUNK)
    
    yield generate_wav_header(RATE, 16, CHANNELS)
    
    while is_streaming:
        try:
            data = stream.read(CHUNK)
            yield data
        except Exception as e:
            logging.error(f"Error reading stream: {e}")
            break

    with stream_lock:
        if stream:
            stream.stop_stream()
            stream.close()
            stream = None

@app.route('/audio')
def audio_feed():
    global is_streaming
    is_streaming = True
    logging.info("Started audio streaming")
    return Response(audio_stream(), mimetype='audio/wav')

@app.route('/stop')
def stop_stream():
    global is_streaming
    is_streaming = False
    logging.info("Stopped audio streaming")
    return jsonify({"status": "stopped"})

@app.route('/devices')
def list_devices():
    devices = get_audio_devices()
    logging.info(f"Listed {len(devices)} audio devices")
    return jsonify(devices)

@app.route('/set_device', methods=['POST'])
def set_device():
    global DEVICE_INDEX, CHANNELS, RATE, stream
    data = request.json
    DEVICE_INDEX = data.get('index')
    CHANNELS = data.get('channels', CHANNELS)
    RATE = data.get('sample_rate', RATE)
    
    with stream_lock:
        if stream:
            stream.stop_stream()
            stream.close()
            stream = None
    
    logging.info(f"Set audio device: index={DEVICE_INDEX}, channels={CHANNELS}, sample_rate={RATE}")
    return jsonify({"status": "device set", "index": DEVICE_INDEX, "channels": CHANNELS, "sample_rate": RATE})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    logging.info(f"Starting server on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)