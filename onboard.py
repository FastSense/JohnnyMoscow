#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import can
import time
import RPi.GPIO as GPIO
from rise.cannet.bot import Robot
from rise.board.robothandle import JohnyHandle
import json
import logging
import redis
import math

redis_connection = redis.Redis(host='192.168.118.96', port=6379, db=0, password='DTL@b2021')
pubsub = redis_connection.pubsub()
pubsub.subscribe('command')

#logging.basicConfig(filename='session.log', encoding='utf-8', filemode='w',
#                    format="[%(levelname)8s] %(asctime)s %(message)s", level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/home/pi/session.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter("[%(levelname)8s] %(asctime)s %(message)s"))
logger.addHandler(handler)
logging.info("start session")

configuration = {}
with open("/home/pi/johnny_dev/JohnnyMoscow/robotConf.json", "r") as file:  # загружаем конфигурацию
    configuration = json.load(file)

recvTimeout = configuration["recvTimeout"]
canChannel = configuration["canInterface"]
headLimits = configuration["headOneSidedLimits"]

logging.info("open can bus")
bus = can.interface.Bus(channel=canChannel, bustype='socketcan_native')  # создаем can шину
# bus = seeedstudio.SeeedBus(channel=configuration["candevice"])
time.sleep(1)

logging.info("create can bus manager")
robot = Robot(bus)  # создаем менеджера can-шины
robot.online = True  # флаг посылок онлайн меток

logging.info("create robot handler")
johnyHandler = JohnyHandle(robot, headLimits)   # обработчик команд

timer = time.time()    # счетчик задержки приема пакетов

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)


def delayCountThread():
    global timer
    while True:
        if (time.time() - timer) > recvTimeout:
            johnyHandler.vector(0.0, 0.0)
            time.sleep(recvTimeout)
        time.sleep(0.01)


def lamp():
    global timer
    while True:
        if (time.time() - timer) > recvTimeout:
            GPIO.output(4, True)
            time.sleep(1)
            GPIO.output(4, False)
            time.sleep(1)
        else:
            GPIO.output(4, True)
            time.sleep(0.2)
            GPIO.output(4, False)
            time.sleep(0.2)


logging.info("start can bus manager")
robot.start()
logging.info("start robot handler")
johnyHandler.start()
logging.info("start timeout threads")
threading.Thread(daemon=True, target=lamp).start()
threading.Thread(daemon=True, target=delayCountThread).start()
logging.info("start calibrate head")
johnyHandler.calibrateHead()

logging.info("start receive packages")
while True:
    msg = pubsub.get_message()

    #time.sleep(0.1)
    if msg is not None:
        if msg['data'] != 1:
            data = msg['data']
        else:
            continue
    else:
        continue

    try:
        package = json.loads(data.decode('utf-8'))
        if package["command"] == "WHEELS":
            x, y = package["data"]["x"], package["data"]["y"]
            x = min(max(-1.0, x), 1.0)
            y = -min(max(-1.0, y), 1.0)

            # Exponential scaling for input
            kl = 1
            ka = 1
            if y < 0:
                y = abs(y)
                kl = -1
            if x < 0:
                x = abs(x)
                ka = -1

            # Exponential scaling for inputs
            y = kl * (math.exp(y) - 1) / (math.e - 1)
            x = ka * (math.exp(x) - 1) / (math.e - 1)

            johnyHandler.vector(x, y)
            timer = time.time()

        if package["command"] == "HEAD":
            yaw, pitch, roll = package["data"]["rot"]["y"], package["data"]["rot"]["p"], package["data"]["rot"]["r"]
            yaw, pitch, roll = int(yaw), int(pitch), int(-roll)
            if yaw > 180:
                yaw = -1 * (360 - yaw)
            if pitch > 180:
                pitch = -1 * (360 - pitch)
            if roll > 180:
                roll = -1 * (360 - roll)

            pitch = int(pitch * 1.8)

            if pitch > 130:
                pitch = 130
            if pitch < -130:
                pitch = -130

            if yaw > 110:
                yaw = 110
            if yaw < - 110:
                yaw = -110

            johnyHandler.setHeadPosition(-yaw, pitch, -roll)

            print(-yaw, pitch, roll)

    except Exception as e:
        logging.error("drop package: {data} from {addr}: {err}".format(data=data, addr=addr, err=e.__str__()))

