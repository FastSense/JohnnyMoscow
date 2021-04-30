#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import can
import socket
import time
import RPi.GPIO as GPIO
from rise.cannet.bot import Robot
from rise.board.robothandle import JohnyHandle
import json
import logging

#logging.basicConfig(filename='session.log', encoding='utf-8', filemode='w',
#                    format="[%(levelname)8s] %(asctime)s %(message)s", level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('session.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter("[%(levelname)8s] %(asctime)s %(message)s"))
logger.addHandler(handler)
logging.info("start session")

configuration = {}
with open("robotConf.json", "r") as file:  # загружаем конфигурацию
    configuration = json.load(file)

udpPort = configuration["udpPort"]
udpBuffSize = configuration["udpBuffSize"]
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

logging.info("create udp server")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', udpPort))

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
    data, addr = sock.recvfrom(udpBuffSize)
    try:
        package = json.loads(data.decode('utf-8'))

        if ("x" in package) and ("y" in package):
            x, y = package["x"], package["y"]
            x = min(max(-1.0, x), 1.0)
            y = min(max(-1.0, y), 1.0)
            johnyHandler.vector(x, y)
            timer = time.time()

        if ("yaw" in package) and ("pitch" in package) and ("roll" in package):
            yaw, pitch, roll = package["yaw"], package["pitch"], package["roll"]
            yaw, pitch, roll = int(yaw), int(pitch), int(roll)
            johnyHandler.setHeadPosition(yaw, pitch, roll)

    except Exception as e:
        logging.error("drop package: {data} from {addr}: {err}".format(data=data, addr=addr, err=e.__str__()))
