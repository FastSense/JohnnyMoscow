""" Управление роботом со стика """

import json
import socket
import time
from src import joystick

serverIp = 'localhost'  # необходимо указать ip робота
serverPort = 9009
sendFreq = 0.05    # слать 5 пакетов в сек
_exit = False   # переменная выхода из потоков

joy_package = {"x": 0.0, "y": 0.0}
head_package = {"yaw": 0, "pitch": 0, "roll": 0}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

glasses = Glass("/dev/ttyUSB0")
glasses.connect("READ", lambda y, p, r: None)
glasses.start()

J = joystick.Joystick()
J.open("/dev/input/js0")
J.start()
J.info()

try:
    while True:
        try:
            angle = self._helmet.angleHead
            for angle[0] in yawRange:
                package["yaw"] = angle
                sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
                # json и отправляем его

            for angle[1] in pitchRange:
                package["pitch"] = angle
                sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
                # json и отправляем его

            for angle[2] in rollRange:
                package["roll"] = angle
                sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
                # json и отправляем его
        except BrokenPipeError:
            print("Ошибка при отправке пакета с данными углов головы робота")
        except Exception as e:
            print("Ошибка при отправке пакета с данными углов головы робота: " + e.__repr__())

        try:
            if i > 4:
                package["x"] = J.axis['x']  # могут быть другие оси, можно переназначить, но необходимо выяснить их название
                package["y"] = J.axis['y']
                sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем json и
                i = 0
            i += 1
        except BrokenPipeError:
            print("Ошибка при отправке пакета с данными движения робота")
        except Exception as e:
            print("Ошибка при отправке пакета с данными движения робота: " + e.__repr__())
    time.sleep(0.1)
except KeyboardInterrupt:
    J.exit()
    sock.close()


# на роботе должно урезаться до приемлимых голове углов
yawRange = list(range(0, 120, 1)) + list(range(120, 0, -1)) + list(range(0, -120, -1)) + list(range(-120, 0, 1))
pitchRange = list(range(0, 90, 1)) + list(range(90, 0, -1)) + list(range(0, -90, -1)) + list(range(-90, 0, 1))
rollRange = list(range(0, 140, 1)) + list(range(140, 0, -1)) + list(range(0, -140, -1)) + list(range(-140, 0, 1))


while True:
