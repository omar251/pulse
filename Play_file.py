import pyaudio
import wave

filename = 'myfile.wav'

# Set chunk size of 1024 samples per data frame
CHUNK = 1024

# Open the sound file 
wf = wave.open(filename, 'rb')
FORMAT = pyaudio.paInt16 #p.get_format_from_width(wf.getsampwidth()
CHANNELS = 1 #wf.getnchannels()
RATE = 16000 # wf.getframerate()
# Create an interface to PortAudio
p = pyaudio.PyAudio()

# Open a .Stream object to write the WAV file to
# 'output = True' indicates that the sound will be played rather than recorded
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                output = True)

# # Read data in chunks
# data = wf.readframes(CHUNK)

# # Play the sound by writing the audio data to the stream
# while data != b'':
#     stream.write(data)
#     data = wf.readframes(CHUNK)

# Play the sound by writing the audio data to the stream
with open(filename, 'rb') as f:
   stream.write(f.read())

# Close and terminate the stream
stream.close()
p.terminate()


