import pyaudio
import wave
import os

def ToLog(mess):
    global Log
    Log.append(mess)

def SaveLog():
    global Log
    file = open(os.getcwd() + "\\" + "log.txt", "w")
    for strings in Log:
        file.write(strings + "\n")
    file.close()

def TryDevices(output = True):
    for Chunk in CHUNK:
        for Format in range(0, len(FORMAT)):
            for Channels in CHANNELS:
                for Rate in RATE:
                    print("-" * (i+1))
                    try:
                        if p.is_format_supported(Rate,
                                                 input_device = DevicesBase[i]["index"],
                                                 input_channels = Channels,
                                                 input_format = FORMAT[Format]):
                            #ToLog(
                            #    "!!! Supported: device index = " + str(i) + " " +
                            #    "rate = " + str(Rate) + " input_channels = " + str(Channels) +
                            #    " input_format = " + str(Format) + " chunk = " + str(Chunk))

                            try:
                                if output == True:
                                    stream = p.open(
                                        format = FORMAT[Format],
                                        channels = Channels,
                                        rate = Rate,
                                        input_device_index = DevicesBase[i]["index"],
                                        output = True,
                                        frames_per_buffer = Chunk)
                                    ToLog("!!!!!!!!!!!!!!!!!!!!!!!!")
                                    ToLog("\t\tOUTPUT successed stream")
                                else:
                                    stream = p.open(
                                        format = Format,
                                        channels = FORMAT[Format],
                                        rate = Rate,
                                        input_device_index = DevicesBase[i]["index"],
                                        input = True,
                                        frames_per_buffer = Chunk)
                                    ToLog("!!!!!!!!!!!!!!!!!!!!!!!!")
                                    ToLog("\t\tINPUT successed stream")
                                ToLog(
                                    "!!! Supported: device index = " + str(i) + " " +
                                    "rate = " + str(Rate) + " input_channels = " + str(Channels) +
                                    " input_format = " + str(Format) + " chunk = " + str(Chunk))
                                    
                                stream.stop_stream()
                                stream.close()

                                

                            except Exception as Err:
                                ToLog("Errored with = " + str(Err))
                                
            
                        else:
                            ToLog("Not supported")
                    except Exception as e:
                        pass
                        #ToLog("index " + str(i) + " format nor supported" + str(e))
    
    
def TryOneDevice():
    try:
        stream = p.open(
            format = pyaudio.paInt16,
            channels = 2,
            rate = 44100,
            input_device_index = 5,
            input = True,
            frames_per_buffer = 1024)
        stream.stop_stream()
        stream.close()

        print("!!!!!!!!!!!!!!!!!!!!!!!!")
        print("successed stream")

    except Exception as Err:
        print("Errored with = " + str(Err))
    

global Log
Log = []
CHUNK = [512, 1024, 2048]
FORMAT = [pyaudio.paInt8, pyaudio.paInt16, pyaudio.paInt24, pyaudio.paInt32, pyaudio.paFloat32, pyaudio.paUInt8, pyaudio.paCustomFormat]
CHANNELS = [1, 2]
RATE = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 96000, 192000]
RECORD_SECONDS = 10
FILENAME = "output.wav"

p = pyaudio.PyAudio()

#print("format = " + str(p.get_format_from_width(1)))
#print("samplesize = " + str(p.get_sample_size(FORMAT)))
#print(str(p.get_device_count()))
#print("Input device info")
#print(str(p.get_default_input_device_info()))
#print(str(p.get_default_output_device_info()))
#
a = input("Введите 0 если проверить все устройства")
#a = "0"
DevicesBase = []
ToLog("\n\n\n\t\tALL DEVICES FINDED")
for i in range (0, p.get_device_count()):
    DevicesBase.append(p.get_device_info_by_index(i))
    ToLog("Device #" + str(i) + str(p.get_device_info_by_index(i)))
    print("Device #" + str(i) + str(p.get_device_info_by_index(i)))
    
if a == "0":
    ToLog("TESTING RESULTS")
    for i in range (0, p.get_device_count()):
        ToLog("\n\n\n\t\tFOR DEVICE = " + str(i))
        ToLog("\n\n\n\t\tINPUT TESTING")
        TryDevices(output = False)
        #ToLog("\n\n\n\t\tOUTPUT TESTING")
        #TryDevices()
else:
    TryOneDevice()



                         
print("\n\n\n\n\n\n")

#num = 1
#print("info about device " + str(num))
#print(str(p.get_device_info_by_index(num)))
#print("All devices")

#print("recording started")
#frames = []
#for i in range (0, int(RATE / CHUNK * RECORD_SECONDS)):
#    data = stream.read(CHUNK)
#    frames.append(data)

#print("recording stopped")

#stream.stop_stream()
#stream.close()
#p.terminate()

#wf = wave.open(FILENAME, "wb")
#wf.setnchannels(CHANNELS)
#wf.setsampwidth(p.get_sample_size(FORMAT))
#wf.setframerate(RATE)
#wf.writeframes(b''.join(frames))
#wf.close()

SaveLog()
print("end of script")
