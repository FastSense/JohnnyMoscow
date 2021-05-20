import math
from rise.board.head import Head
from rise.board.motors import Motors
from rise.cannet.steppercontroller import StepperController
from rise.cannet.motorcontroller import MotorController

# Reduser for angle velocity
ANGLE_VELOCITY_MULTIPLYER = 0.3
# Linear part of angle velocity - we want to steer more during linear movement
LINEAR_VELOCITY_MULTIPLYER = 0.5


class JohnyHandle:
    """ Класс, обрабатывающий сообщения и управляющий роботом на самом роботе """

    def __init__(self, robotHandle, headLimits):
        self._robot = robotHandle
        self._step = StepperController(self._robot, 0x230)
        self._mot = MotorController(self._robot, 0x200)
        self._robot.addDevice(self._step)
        self._robot.addDevice(self._mot)
        self._head = Head(self._step, headLimits)
        self._motors = Motors(self._mot)

        self.max_speed = 100

    def start(self):
        self._head.start()
        self._motors.start()

    def setHeadPosition(self, yaw, pitch, roll):
        """ Установка позиции головы робота """
        self._head.setAllPosition(yaw, pitch, roll)

    def calibrateHead(self):
        """ калибровка головы робота """
        self._head.calibrate()

    def move(self, speed):
        """ движение вперед/назад """
        self._motors.move(speed)

    def rotate(self, speed):
        """ поворот на месте """
        self._motors.rotate(speed)

    def vector(self, x, y):
        x = x * ANGLE_VELOCITY_MULTIPLYER + (x * abs(y) * LINEAR_VELOCITY_MULTIPLYER)
        left = (y - x) * self.max_speed
        right = (y + x) * self.max_speed
        self._motors.setSpeed(-int(right), int(left))

    @property
    def voltage(self):
        return self._motors.voltage
