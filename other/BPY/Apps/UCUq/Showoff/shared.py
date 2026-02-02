import base64
import zlib
import ucuq # type: ignore
import random

from types import SimpleNamespace

W_COUNTDOWN_ = "Countdown"

DEVICES = ("Alpha", "India", "Lima")

RGB_MAX_ = 10

devices = SimpleNamespace()

def rainbowGradient_(n, max):
  colors = []
  
  for i in range(n):
    h = (i * 6) / n
    x = int((1 - abs((h % 2) - 1)) * max)

    if 0 <= h < 1:
      r, g, b = max, x, 0
    elif 1 <= h < 2:
      r, g, b = x, max, 0
    elif 2 <= h < 3:
      r, g, b = 0, max, x
    elif 3 <= h < 4:
      r, g, b = 0, x, max
    elif 4 <= h < 5:
      r, g, b = x, 0, max
    else:
      r, g, b = max, 0, x

    colors.append((r, g, b))
  return colors

RAINBOW = rainbowGradient_(50, RGB_MAX_)

indexes = [random.randrange(len(RAINBOW)) for i in range(3)]


class RGB_(ucuq.WS2812):
  def setValue(self, index, color = None):
    if hasattr(self, "go") and not self.go:
      return self
    if hasattr(self, "turn") and color is None:
      color = RAINBOW[indexes[self.turn] % len(RAINBOW)]
    return super().setValue(index, color)


def connect():
  ucuq.setDevice(DEVICES)
  
  ucuq.ntpSetTime()
  
  devices.rgbs = RGB_(8, 20)
  devices.buzzers = ucuq.Buzzer(ucuq.PWM(5))
  devices.lcds = ucuq.HD44780_I2C(16, 2, ucuq.SoftI2C(6, 7))
  devices.oleds = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(8, 9))

  
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
  devices.rgbs.flash()
  
  leds_ = [False] * 8
  devices.rgbs.fill((1,1,1)).write()
  for counter in range(5, 0, -1):
    devices.oleds.draw(DIGITS_[counter], 8, 48, 0, mul=9).show()
    for c in range(3, 11):
      timestamp += 1 / 8
      sleep(timestamp)
      devices.rgbs.setValue(c, (1,1,1) if leds_[c % 8] else (0,0,0)).write()
      leds_[c%8] = not leds_[c%8]
    
  devices.oleds.fill(0).show()
  devices.rgbs.fill((0,0,0)).write()
  
  return timestamp


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def polyphonicPlay(voices, tempo, userObject, callback):
#  ucuq.addCommand("__import__('gc').disable()")
  ucuq.polyphonicPlay(voices, tempo, userObject, callback)
#  ucuq.addCommand("__import__('gc').enable()")
