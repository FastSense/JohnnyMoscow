""" Управление роботом со стика """

import json
import socket
import time
from src import joystick, glass

serverIp = 'localhost'  # необходимо указать ip робота
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
    while True:
        try:
            angle = glasses.angleHead
            head_package["yaw"] = angle[0]
            head_package["pitch"] = angle[1]
            head_package["roll"] = angle[2]
            sock.sendto(json.dumps(head_package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем
            # json и отправляем его
        except BrokenPipeError:
            print("Ошибка при отправке пакета с данными углов головы робота")
        except Exception as e:
            print("Ошибка при отправке пакета с данными углов головы робота: " + e.__repr__())

        try:
            joy_package["x"] = J.axis['x']  # могут быть другие оси, можно переназначить, но необходимо выяснить их название
            joy_package["y"] = -J.axis['y']
            sock.sendto(json.dumps(joy_package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем json и
        except BrokenPipeError:
            print("Ошибка при отправке пакета с данными движения робота")
        except Exception as e:
            print("Ошибка при отправке пакета с данными движения робота: " + e.__repr__())
    time.sleep(0.05)
except KeyboardInterrupt:
    J.exit()
    sock.close()
