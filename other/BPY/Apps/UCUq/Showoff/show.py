import base64
import random
import types
import zlib

import ucuq

import shared

from shared import RGB_MAX as RGB_MAX_, RAINBOW as RAINBOW_, getRainbowColor as getRainbowColor_

W_COUNTDOWN_ = "Countdown"

devices = types.SimpleNamespace()

indexes = [random.randrange(len(RAINBOW_)) for i in range(3)]

class Ring_(ucuq.Ravel.Ring):
  def setValue(self, index, color = None):
    if hasattr(self, "go") and not self.go:
      return self
    if hasattr(self, "turn") and color is None:
      color = getRainbowColor_(indexes[self.turn])
    return super().setValue(index, color)


def connect(deviceList):
  ucuq.setDevice(tuple(shared.handleDeviceInput(device) for device in deviceList))
  
  ucuq.ntpSetTime()
  
  devices.rings = Ring_()
  devices.buzzers = ucuq.Ravel.Buzzer()
  devices.lcds = ucuq.Ravel.LCD()
  devices.oleds = ucuq.Ravel.OLED()
  devices.ravel = ucuq.Ravel(ring=devices.rings, buzzer=devices.buzzers, oled = devices.oleds, lcd=devices.lcds)
  
  devices.lcds.uploadGaugeChars()

prevLocalTimeStamp_ = 0
  
  
def sleepUntil(timestamp):
  global prevLocalTimeStamp_
  
  if timestamp - prevLocalTimeStamp_ > 0.66:
    prevLocalTimeStamp_ = timestamp
    ucuq.commit()

  ucuq.ntpSleepUntil(timestamp)


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
  
def countdownIfSelected_(dom, timestamp):
  if dom.getValue(W_COUNTDOWN_) != "true":
    return timestamp
  
  sleepUntil(timestamp)
  devices.rings.flash()
  
  leds_ = [False] * 8
  devices.rings.fill((1,1,1)).write()
  for counter in range(5, 0, -1):
    devices.oleds.draw(DIGITS_[counter], 8, 48, 0, mul=9).show()
    for c in range(2, 10):
      timestamp += 1 / 8
      sleepUntil(timestamp)
      devices.rings.setValue(c, (1,1,1) if leds_[c % 8] else (0,0,0)).write()
      leds_[c%8] = not leds_[c%8]
    
  devices.oleds.fill(0).show()
  devices.rings.fill((0,0,0)).write()
  
  return timestamp


def countdownIfSelected(dom, timestamp):
  ucuq.gcCollect()
  
  if dom.getValue(W_COUNTDOWN_) != "true":
    return timestamp
  
  leds = [False] * 8
  timestamp += .5
  
  allEvents = []
  
  oledEvents = []
  ringEvents = []
  lcdEvents = []
  
  for i in range(5, 0, -1):
    oledEvents.append((
      lambda digit=i:
        devices.oleds.draw(DIGITS_[digit], 8, 48, 0, mul=9).show(),
      1))
    for c in range(2, 10):
      ringEvents.append((
        lambda
          led=c,
          color=(1,1,1) if leds[c % 8] else (0,0,0):
            devices.rings.setValue(led, color).write(), 1/8))
      leds[c%8] = not leds[c%8]
      

  gauge = ()

  for j in range(16):
    gauge = ((j,) + gauge)[:16]
    lcdEvents.append((
      lambda gauge = gauge:
        devices.lcds.moveTo(0,0).putGauges(0, gauge),
      5/48))

  for j in range(15, -1, -1):
    gauge = ((j,) + gauge)[:16]
    lcdEvents.append((
      lambda gauge = gauge:
        devices.lcds.moveTo(0,0).putGauges(0, gauge),
      5/48))
      
  for j in range(16):
    gauge = ((0,) + gauge)[:16]
    lcdEvents.append((
      lambda gauge = gauge:
        devices.lcds.moveTo(0,0).putGauges(0, gauge),
      5/48))


  allEvents += (ringEvents,)
  allEvents += (lcdEvents,)
  allEvents += (oledEvents,)
  
  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)
  
  sleepUntil(timestamp)
  devices.rings.flash()
  devices.rings.fill((1,1,1)).write()
  devices.lcds.backlightOn()
  timestamp += ucuq.playEvents(allEvents, lambda _, cumul: sleepUntil(timestamp + cumul))
  devices.oleds.fill(0).show()
  devices.rings.fill((0,0,0)).write()
  devices.lcds.clear().backlightOff()
  
  ucuq.setCommitBehavior(cb)
  
  ucuq.gcCollect()
  
  return timestamp + 1


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def displayRingGauges():
  devices.ravel.displayRingGauges(RGB_MAX_)  

def turnOffAndScrollDown(timestamp):
  offset = random.randrange(len(RAINBOW_))
  
  for i in range(offset, 8 + offset):
    devices.rings.setValue(i, getRainbowColor_(i, 7))
    
  devices.rings.write()
  
  for i in range(64):
    devices.rings.setValue(i // 8 + offset, (0,0,0)).write()
    devices.oleds.scroll(0, 1).show()
    devices.ravel.displayRingGauges(RGB_MAX_)
    timestamp += 0.09
    sleepUntil(timestamp) 
    
  return timestamp
    
  
def flood(timestamp):
  gauges = (0,) * 16 + tuple(15 - abs(i) for i in range(-15, 16))
    
  for i in range(len(gauges)):
    sleepUntil(timestamp)
    devices.lcds.putGauges(0, gauges[len(gauges) - i - 1:][:16], True)
    timestamp += 0.1
    
  return timestamp

