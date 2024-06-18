import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']}")

list_audio_devices()
import pyaudio
import wave

def record_audio(device_index, duration=5):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024)
    
    frames = []
    
    try:
        print("Recording...")
        for _ in range(0, int(44100 / 1024 * duration)):  # Record for the specified duration
            data = stream.read(1024)
            frames.append(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Finished recording.")
        stream.stop_stream()
        stream.close()
        audio.terminate()
    
        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

# Replace <device_index> with the correct index of your audio device
record_audio(device_index=1, duration=5)
