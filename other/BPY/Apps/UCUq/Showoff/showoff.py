import atlastk  # noqa: F401
import ucuq # pyright: ignore[reportMissingImports]
import time
import pink
import trio
import colors
import shared

from shared import devices, sleep, connect

def atk(dom):
  dom.inner("", BODY)  # type: ignore # noqa: F821
  colors.fill(dom)
  colors.update(dom)
  connect()
  
  
def atkReconnect(dom):
  connect()
  
  
def atkSync(dom):
  ucuq.ntpSetTime()
  
  
def atkTest():
  timestamp = time.time() + 1
  
  sleep(timestamp)
  
  devices.rgbs.flash()
  
  sleep(timestamp + 1)
  
  devices.rgbs.flash()
  
  
def atkPink(dom):
  timestamp = shared.countdownIfSelected(dom, time.time() + 1)
  pink.launch(timestamp)
  
  
def atkFugue(dom):
  timestamp = shared.countdownIfSelected(dom, time.time() + 1)
  trio.launch(timestamp)


def atkColorUpdate(dom):
  colors.update(dom)


def atkColorOnce(dom):
  scheme, delay = dom.getValues((colors.W_SCHEMES, colors.W_DELAY)).values()
  timestamp = shared.countdownIfSelected(dom, time.time() + 1)
  colors.launch(int(scheme), timestamp, float(delay), 1)
  
  
def atkColorRepeat(dom):
  scheme, delay, repeat = dom.getValues((colors.W_SCHEMES, colors.W_DELAY, colors.W_REPEAT)).values()
  timestamp = shared.countdownIfSelected(dom, time.time() + 1)
  colors.launch(int(scheme), timestamp, float(delay), int(repeat))
