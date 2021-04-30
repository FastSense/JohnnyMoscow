#!/usr/bin/env python3
# -*- coding:utf-8 vi:ts=4:noexpandtab
# Simple RTSP server. Run as-is or with a command-line to replace the default pipeline
#Прием: gst-launch-1.0 rtspsrc location=rtsp://192.168.42.162:8554/front latency=0 buffer-mode=auto ! application/x-rtp, encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec ! autovideosink



import sys
import gi
import RPi.GPIO as GPIO    
import os
import subprocess
import time
import os 
from PIL import Image       # библиотеки для рисования на дисплее
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_SSD1306 

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

loop = GLib.MainLoop()
#GLib.threads_init()
Gst.init(None)



class FrontCamFactory(GstRtspServer.RTSPMediaFactory):
        def __init__(self):
                GstRtspServer.RTSPMediaFactory.__init__(self)

        def do_create_element(self, url):
                pipeline_str = "( v4l2src do-timestamp=true ! image/jpeg, width=1280, height=480, framerate=30/1 ! jpegparse ! rtpjpegpay name=pay0 )"
                print(pipeline_str)
                return Gst.parse_launch(pipeline_str)




#Порт: 8554. Камера: front.
class FrontServer():
	def __init__(self):
		self.FrontServer = GstRtspServer.RTSPServer.new()
		self.FrontServer.set_service('8554')

		FrontCam = FrontCamFactory()
		FrontCam.set_shared(True)


		m = self.FrontServer.get_mount_points()
		m.add_factory("/front", FrontCam)

		self.FrontServer.attach(None)

		port_FrontServer = self.FrontServer.get_bound_port()
		print ('RTSP server started: rtsp://%s:%d/front' % (getIP(), port_FrontServer))
		print_display(line="Robot started",y=0, shutdown = 0)
		print_display(line="ip:"+ getIP(),y=8, shutdown = 0)
		print_display(line="RTSP server started",y=16, shutdown = 0)




###################
"""Возвращает ip"""
###################
def getIP():
    res = os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','') #получаем IP, удаляем \n
    return res


#######################################
"""Возвращает температуру процессора"""
#######################################
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return float(res.replace('temp=','').replace('\'C\n',''))


##################################
"""Вывод текста line на дисплей"""
##################################
def print_display(line, y, shutdown):
    if shutdown == 0: # Предыдущий текст остается
        draw.text((0,y), line, font=font, fill=255) # формируем текст
    if shutdown == 1:  # Предыдущий текст НЕ остается
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((0,y), line, font=font, fill=255) # формируем текст
        disp.image(image)       # записываем изображение в буффер
        disp.display()  # выводим его на экран



################################################
"""Выключение по единичному нажатию на кнопку"""
################################################
def Shutdown(channel):
    print("shutdown")
    print_display(line="Robot shutdown", y=0, shutdown=1)
    os.system("sudo shutdown -h now")



if __name__ == '__main__':

        disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        disp.begin()    # запускаем дисплей
        disp.clear()    # очищаем буффер изображения
        width, height = disp.width, disp.height  # получаем высоту и ширину дисплея
        image = Image.new('1', (width, height))     # создаем изображение из библиотеки PIL для вывода на экран. 1 = картинка черно-белая, далее размер изображения
        draw = ImageDraw.Draw(image)    # создаем объект, которым будем рисовать
        font = ImageFont.load_default()     # загружаем стандартный шрифт
        draw.rectangle((0, 0, width, height), outline=0, fill=0)        # прямоугольник, залитый черным - очищаем дисплей

        s1 = FrontServer()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(19, GPIO.RISING, callback = Shutdown, bouncetime = 2000)

        loop.run()
