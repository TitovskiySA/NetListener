import pyaudio
import socket
import threading
from threading import Thread
import wave

class ServerThread(threading.Thread):
    def __init__(self, comm, ip, port, filename, thread_id):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        self.filename = filename
        self.thread_id = thread_id
        print(
            "connecting to " + self.ip + ":" + str(self.port) +
            "\tID = " + str(self.thread_id))

    def run(self):
        wf = wave.open(self.filename, "rb")
        P = pyaudio.PyAudio()
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100

        stream = P.open(
            format = FORMAT, channels = CHANNELS, rate = RATE,
            output = True, frames_per_buffer = CHUNK)

        data = 1
        while data:
            data = wf.readframes(CHUNK)
            try:
                self.conn.send(data)
            except:
                break
        
print("end")
    
    
