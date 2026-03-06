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
  
  devices.lcds.uploadJaugeChars()

  
def sleepUntil(timestamp):
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


def countdownCallback_(events, duration, helper):
  for event in events:
    if event[0] == 2:
      devices.oleds.draw(DIGITS_[event[1]], 8, 48, 0, mul=9).show()
    elif event[0] == 0:
      devices.rings.setValue(event[1][0], event[1][1]).write()
    elif event[0] == 1:
      devices.lcds.moveTo(0,0).putJauges(0, event[1])
      
  helper.timestamp += duration
      
  sleepUntil(helper.timestamp)


def countdownIfSelected(dom, timestamp):
  ucuq.gcCollect()
  
  if dom.getValue(W_COUNTDOWN_) != "true":
    return timestamp
  
  leds = [False] * 8
  helper = types.SimpleNamespace(timestamp = timestamp + .5)
  
  allEvents = []
  
  oledEvents = []
  ringEvents = []
  lcdEvents = []
  
  for i in range(5, 0, -1):
    oledEvents.append((i, 1))
    for c in range(2, 10):
      ringEvents.append(((c,(1,1,1) if leds[c % 8] else (0,0,0) ), 1/8))
      leds[c%8] = not leds[c%8]
      

  jauge = ()

  for j in range(16):
    jauge = ((j,) + jauge)[:16]
    lcdEvents.append((jauge, 5/48))

  for j in range(15, -1, -1):
    jauge = ((j,) + jauge)[:16]
    lcdEvents.append((jauge, 5/48))
      
  for j in range(16):
    jauge = ((0,) + jauge)[:16]
    lcdEvents.append((jauge, 5/48))


  allEvents += (ringEvents,)
  allEvents += (lcdEvents,)
  allEvents += (oledEvents,)
  
  sleepUntil(helper.timestamp)
  devices.rings.flash()
  devices.rings.fill((1,1,1)).write()
  devices.lcds.backlightOn()
  ucuq.playEvents(allEvents, countdownCallback_, helper)
  devices.oleds.fill(0).show()
  devices.rings.fill((0,0,0)).write()
  devices.lcds.clear().backlightOff()
  
  ucuq.gcCollect()
  
  return helper.timestamp + 1


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def lcdDisplayRing():
  for i in range(len(devices.rings)):
    ring = devices.rings[i]
    if not hasattr(ring, "go") or ring.go:
      devices.lcds[i].displayRing(ring, (shared.RGB_MAX))

