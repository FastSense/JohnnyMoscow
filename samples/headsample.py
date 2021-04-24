""" При запуске робот должен поворачивать головой поочередно по каждой из осей """

import json
import socket
import time

serverIp = 'localhost'  # ip робота
serverPort = 9009   # порт робота
sendFreq = 15    # слать 15 пакетов в сек

package = {"yaw": 0, "pitch": 0, "roll": 0}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# на роботе должно урезаться до приемлимых голове углов
yawRange = list(range(0, 120, 1)) + list(range(120, 0, -1)) + list(range(0, -120, -1)) + list(range(-120, 0, 1))
pitchRange = list(range(0, 90, 1)) + list(range(90, 0, -1)) + list(range(0, -90, -1)) + list(range(-90, 0, 1))
rollRange = list(range(0, 140, 1)) + list(range(140, 0, -1)) + list(range(0, -140, -1)) + list(range(-140, 0, 1))


while True:
    for angle in yawRange:
        package["yaw"] = angle
        sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
        # json и отправляем его
        time.sleep(1/sendFreq)

    for angle in pitchRange:
        package["pitch"] = angle
        sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
        # json и отправляем его
        time.sleep(1/sendFreq)

    for angle in rollRange:
        package["roll"] = angle
        sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
        # json и отправляем его
        time.sleep(1/sendFreq)
