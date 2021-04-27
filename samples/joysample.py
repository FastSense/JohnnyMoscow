""" Управление роботом со стика """

import json
import socket
import time
from joydepend import joystick

serverIp = 'localhost'
serverPort = 9009
sendFreq = 5    # слать 5 пакетов в сек
_exit = False   # переменная выхода из потоков

package = {"x": 0.0, "y": 0.0}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

J = joystick.Joystick()
J.open("/dev/input/js0")
J.start()
J.info()

try:
    while True:
        package["x"] = J.axis['x']  # могут быть другие оси, можно переназначить, но необходимо выяснить их название
        package["y"] = J.axis['y']
        sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем json и
        # отправляем его
        time.sleep(1/sendFreq)
except KeyboardInterrupt:
    J.exit()
    sock.close()
