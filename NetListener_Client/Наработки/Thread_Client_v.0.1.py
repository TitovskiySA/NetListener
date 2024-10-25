import pyaudio
import socket


P = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

stream = P.open(
    format = FORMAT, channels = CHANNELS, rate = RATE,
    output = True, frames_per_buffer = CHUNK)

while True:
    res = self.ClientSocket.recv(1024).decode()
    sys.stdout.flush()
    data = "|"
    while data != "":
        audio_bytes = self.ClientSocket.recv(1024)
        stream.write(audiobytes)

stream.stop_stream()
stream.close()
p.terminate()
