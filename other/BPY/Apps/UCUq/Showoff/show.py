import base64
import random
import types
import zlib

import ucuq

import shared

W_COUNTDOWN_ = "Countdown"

devices = types.SimpleNamespace()

indexes = [random.randrange(len(shared.RAINBOW)) for i in range(3)]

class Ring_(ucuq.Ravel.Ring):
  def setValue(self, index, color = None):
    if hasattr(self, "go") and not self.go:
      return self
    if hasattr(self, "turn") and color is None:
      color = shared.RAINBOW[indexes[self.turn] % len(shared.RAINBOW)]
    return super().setValue(index, color)


def connect(deviceList):
  ucuq.setDevice(tuple(shared.handleDevices(device) for device in deviceList))
  
  ucuq.ntpSetTime()
  
  devices.rings = Ring_()
  devices.buzzers = ucuq.Ravel.Buzzer()
  devices.lcds = ucuq.Ravel.LCD()
  devices.oleds = ucuq.Ravel.OLED()

  
def sleep(timestamp):
  ucuq.ntpSleepUntil(int(timestamp * 1_000_000))
  
  
DIGITS_ = (
  "708898A8C88870",
  "20602020202070",
  "708808304080f8",
  "f8081030088870",
  "10305090f81010",
  "f880f008088870",
  "708880f0888870",
  "f8081020404040",
  "70888870888870",
  "70888878088870",
)  
  
def countdownIfSelected(dom, timestamp):
  if dom.getValue(W_COUNTDOWN_) != "true":
    return timestamp
  
  sleep(timestamp)
  devices.rings.flash()
  
  leds_ = [False] * 8
  devices.rings.fill((1,1,1)).write()
  for counter in range(5, 0, -1):
    devices.oleds.draw(DIGITS_[counter], 8, 48, 0, mul=9).show()
    for c in range(2, 10):
      timestamp += 1 / 8
      sleep(timestamp)
      devices.rings.setValue(c, (1,1,1) if leds_[c % 8] else (0,0,0)).write()
      leds_[c%8] = not leds_[c%8]
    
  devices.oleds.fill(0).show()
  devices.rings.fill((0,0,0)).write()
  
  return timestamp


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def lcdDisplayRing():
  for i in range(len(devices.rings)):
    devices.lcds[i].moveTo(0,0).putString(devices.rings[i].getJaugesString(shared.RGB_MAX))

