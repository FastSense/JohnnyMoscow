import math
from rise.board.head import Head
from rise.board.motors import Motors
from rise.cannet.steppercontroller import StepperController
from rise.cannet.motorcontroller import MotorController


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

        self.speed = 20

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
        """ управление по вектору. x [-0.2, 0.2]; y [-0.2, 0.2] - мертвые зоны """
        x = min(max(-1.0, x), 1.0)
        y = min(max(-1.0, y), 1.0)
        if -0.2 < x < 0.2:
            x = 0.0
        if -0.2 < y < 0.2:
            y = 0.0
        if x >= 0.0:
            y = -y
        # convert to polar
        r = math.hypot(x, y)
        t = math.atan2(y, x)
        # rotate by 45 degrees
        t += math.pi / 4
        # back to cartesian
        left = r * math.cos(t)
        right = r * math.sin(t)
        # rescale the new coords
        left = left * math.sqrt(2)
        right = right * math.sqrt(2)
        # clamp to -1/+1
        left = max(-1.0, min(left, 1.0))
        right = max(-1.0, min(right, 1.0))

        left = int(left * self.speed)
        right = int(right * self.speed)

        self._motors.setSpeed(left, right)

    @property
    def voltage(self):
        return self._motors.voltage
