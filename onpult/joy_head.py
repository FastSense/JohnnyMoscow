""" Управление роботом со стика """

import json
import socket
import time
from src import joystick, glass

serverIp = '192.168.118.125'  # необходимо указать ip робота
serverPort = 9009
sendFreq = 0.05    # слать 5 пакетов в сек
_exit = False   # переменная выхода из потоков

joy_package = {"x": 0.0, "y": 0.0}
head_package = {"yaw": 0, "pitch": 0, "roll": 0}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

glasses = glass.Glass("/dev/ttyUSB0")
glasses.connect("READ", lambda y, p, r: None)
glasses.start()

J = joystick.Joystick()
J.open("/dev/input/js0")
J.start()
J.info()

try:
    i = 0
    while True:
        try:
            angle = glasses.angleHead
            head_package["yaw"] = round(angle[0], 3)
            head_package["pitch"] = round(angle[1], 3)
            head_package["roll"] = -round(angle[2], 3)
            sock.sendto(json.dumps(head_package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
            # json и отправляем его
        except BrokenPipeError:
            print("Ошибка при отправке пакета с данными углов головы робота")
        except Exception as e:
            print("Ошибка при отправке пакета с данными углов головы робота: " + e.__repr__())

        try:
            joy_package["x"] = -round(J.axis['x'], 3)  # могут быть другие оси, можно переназначить, но необходимо выяснить их название
            joy_package["y"] = -round(J.axis['y'], 3)
            sock.sendto(json.dumps(joy_package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем json и
        except BrokenPipeError:
            print("Ошибка при отправке пакета с данными движения робота")
        except Exception as e:
            print("Ошибка при отправке пакета с данными движения робота: " + e.__repr__())
        time.sleep(0.08)
except KeyboardInterrupt:
    J.exit()
    sock.close()
