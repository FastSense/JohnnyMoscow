""" Управление роботом с клавиатуры """

import json
import socket
import time

from pynput import keyboard

serverIp = 'localhost'
serverPort = 9009
sendFreq = 5    # слать 5 пакетов в сек
_exit = False   # переменная выхода из потоков

package = {"x": 0.0, "y": 0.0}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
speedAxisState = 0.9
turnAxisState = 0.7


def on_press(key):
    global package, speedAxisState, turnAxisState

    if key is keyboard.Key.up:
        package["x"] = speedAxisState
    if key is keyboard.Key.down:
        package["x"] = -speedAxisState
    if key is keyboard.Key.left:
        package["y"] = -turnAxisState
    if key is keyboard.Key.right:
        package["y"] = turnAxisState


def on_release(key):
    global package, speedAxisState, turnAxisState, _exit

    if key is keyboard.Key.up:
        package["x"] = 0
    if key is keyboard.Key.down:
        package["x"] = 0
    if key is keyboard.Key.left:
        package["y"] = 0
    if key is keyboard.Key.right:
        package["y"] = 0
    if key == keyboard.Key.esc:
        _exit = True
        # Stop listener
        return False


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

while not _exit:
    sock.sendto(json.dumps(package, ensure_ascii=False).encode("utf8"), (serverIp, serverPort))  # кодируем json и
    # отправляем его
    time.sleep(1/sendFreq)
