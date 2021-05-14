#!/usr/bin/env python3

import pyaudio
import socket
import select
import redis
import time
import base64

import signal
import sys
import time
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

audio = pyaudio.PyAudio()

redis_connection = redis.Redis(host='192.168.118.96', port=6379, db=0, password='DTL@b2021')
pubsub = redis_connection.pubsub()

def callback(in_data, frame_count, time_info, status):
    # buffer = base64.b64encode(in_data)
    redis_connection.publish('audio', in_data)
    return (in_data, pyaudio.paContinue)

# start Recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

# read_list = [serversocket]
print("recording...")

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
forever = threading.Event()
forever.wait()

print("finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
