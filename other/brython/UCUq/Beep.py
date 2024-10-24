import ucuq
from browser import aio

CMD = """
from machine import Pin, PWM
from time import sleep
import uos

def buzzer(buzzerPinObject,frequency,ratio):
    buzzerPinObject.duty_u16(int(65536*ratio))
    buzzerPinObject.freq(frequency)
    sleep(0.5)
    buzzerPinObject.duty_u16(int(65536*0))
    

buzzer(machine.PWM(machine.Pin(2)), 440, .5)
"""

ucuq.execute(CMD)


