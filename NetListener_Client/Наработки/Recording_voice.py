import pyaudio
import wave


CHUNK = 1024
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
FILENAME = "output.wav"

p = pyaudio.PyAudio()
stream = p.open(
    format = FORMAT, channels = CHANNELS, rate = RATE,
    input = True, frames_per_buffer = CHUNK)

print("recording started")
frames = []
for i in range (0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("recording stopped")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(FILENAME, "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print("end of script")
