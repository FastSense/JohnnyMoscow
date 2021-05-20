#!/usr/bin/env python3

import pyaudio
import socket
import sys
import time
import redis

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

redis_connection = redis.Redis(host='192.168.118.96', port=6379, db=0, password='DTL@b2021')
pubsub = redis_connection.pubsub()

pubsub.subscribe('audio')

try:
    while True:
        msg = pubsub.get_message()
        if msg is not None:
            if msg['data'] != 1:
                stream.write(msg["data"])
except KeyboardInterrupt:
    pass

print('Shutting down')
stream.close()
audio.terminate()
