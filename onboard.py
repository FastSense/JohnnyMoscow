#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
#import can
import socket
import time
#import RPi.GPIO as GPIO
#from rise.cannet.bot import Robot
#from rise.board.robothandle import JohnyHandle
import json
import logging
logging.basicConfig(filename='session.log', encoding='utf-8', format='%(asctime)s %(message)s')

configuration = {}
with open("robotConf.json", "r") as file:  # загружаем конфигурацию
    configuration = json.load(file)

udpPort = configuration["udpPort"]
udpBuffSize = configuration["udpBuffSize"]
recvTimeout = configuration["recvTimeout"]
canChannel = configuration["canInterface"]
headLimits = configuration["headOneSidedLimits"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', udpPort))


timer = time.time()    # счетчик задержки приема пакетов
def delayCountThread():
    global timer
    while True:
        if (time.time() - timer) > recvTimeout:
            print("timeout: robot stop")
            timer = time.time()
        time.sleep(0.01)


threading.Thread(daemon=True, target=delayCountThread).start()

while True:
    data, addr = sock.recvfrom(udpBuffSize)
    try:
        package = json.loads(data)

        if ("x" in package) and ("y" in package):
            x, y = package["x"], package["y"]
            x = min(max(-1.0, x), 1.0)
            y = min(max(-1.0, y), 1.0)
            timer = time.time()
            print("vector move: ", (x, y))
        if ("yaw" in package) and ("pitch" in package) and ("roll" in package):
            yaw, pitch, roll = package["yaw"], package["pitch"], package["roll"]
            yaw, pitch, roll = int(yaw), int(pitch), int(roll)
            timer = time.time()
            print("set head position: ", (yaw, pitch, roll))

    except Exception as e:
        logging.error("drop package: {data} from {addr}: {err}".format(data=data, addr=addr, err=e.__str__()))

"""
bus = can.interface.Bus(channel=configuration["can_interface"], bustype='socketcan_native')  # создаем can шину
# bus = seeedstudio.SeeedBus(channel=configuration["candevice"])
time.sleep(1)

robot = Robot(bus)  # создаем менеджера can-шины
robot.online = True  # флаг посылок онлайн меток

udpPort = configuration["udpPort"]

johnyHandler = JohnyHandle(robot)
onlineCount = 0


def th():
    global onlineCount
    while True:
        onlineCount += 1
        if onlineCount > 3:
            robot.online = False  # не шлем метки
        else:
            robot.online = True  # шлем метки
        time.sleep(1)


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)


def lamp():
    global onlineCount
    while True:
        if onlineCount > 3:
            GPIO.output(4, True)
            time.sleep(1)
            GPIO.output(4, False)
            time.sleep(1)
        else:
            GPIO.output(4, True)
            time.sleep(0.2)
            GPIO.output(4, False)
            time.sleep(0.2)


robot.start()
johnyHandler.start()
threading.Thread(daemon=True, target=th).start()
threading.Thread(daemon=True, target=lamp).start()

while True:
    pass
    del jh
    jh = None
    jh = JohnyHandle(robot)
    jh.start()
"""