
class JohnySimHandle:
    """ Класс симулятора """

    def __init__(self, robotHandle):
        pass

    def __del__(self):
        pass

    def start(self):
        pass

    def setHeadPosition(self, yaw, pitch, roll):
        """ Установка позиции головы робота """
        pass

    def setVideoState(self, dev, host, state):
        """ включение/выключение видео """
        pass

    def calibrateHead(self):
        """ калибровка головы робота """
        pass

    def move(self, speed):
        """ движение вперед/назад """
        pass

    def rotate(self, speed):
        """ поворот на месте """
        pass

    @property
    def voltage(self):
        pass