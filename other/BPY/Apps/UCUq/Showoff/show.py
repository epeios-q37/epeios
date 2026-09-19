import base64  # noqa: I001
import collections
import random
import socket
import struct
import time
import types
import zlib

import ucuq

from shared import (
  RAINBOW as RAINBOW_,
  getRainbowColor as getRainbowColor_
)

W_COUNTDOWN_ = "ShowCountdown"

COMMIT_DELAY_ = 2/3

parts_ = None

def setParts_():
  parts = collections.OrderedDict((name, ucuq.Multi()) for name in ('buzzers', 'rings', 'panels', 'screens', 'uppers', 'lowers'))

  kits = ucuq.Multi()

  for device in ucuq.getDevice():
    kits.add(ucuq.ravel(device=device))

  for kit in kits:
    for (_, value), param in zip(parts.items(), kit.get("BRPSUL")):
      value.add(param)

  parts['kits'] = kits

  return types.SimpleNamespace(**parts)


def getParts():
  return parts_


def getNTPTime_(host="pool.ntp.org"):
  port = 123
  buf = 1024
  address = (host, port)
  msg = b'\x1b' + 47 * b'\0'

  NTP_DELTA = 2208988800

  try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)
    client.sendto(msg, address)
    data, _ = client.recvfrom(buf)
  except TimeoutError as e:
    raise RuntimeError("Erreur NTP : " + str(e))

  t = struct.unpack("!12I", data)[10]
  ntp_time = t - NTP_DELTA

  return ntp_time


ntpOffset_ = 0

  
def connect(deviceList):
  global ntpOffset_, parts_
  
  ntpOffset_ = time.time() - getNTPTime_()
  
  print(f"Décalage horaire : {ntpOffset_} s.")
  
  ucuq.setDevice(deviceList)

  parts_ = setParts_()

  ucuq.ntpSync()
  
  return ntpOffset_

lastCommitTimestamp_ = 0


def sleepUntil(timestamp, commitDelay):
  global lastCommitTimestamp_
  
  if commitDelay > 0:
    if lastCommitTimestamp_ == 0:
      lastCommitTimestamp_ = timestamp
    if timestamp - lastCommitTimestamp_ > commitDelay:
      lastCommitTimestamp_ = timestamp
      ucuq.commit()

  ucuq.ntpSleepUntil(timestamp - ntpOffset_)


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

def countdownIfRequested(dom, timestamp, parts):
  if dom.getValue(W_COUNTDOWN_) != "true":
      return timestamp

  ucuq.gcCollect()
  
  leds = [False] * ucuq.ravel.RING_SIZE
  timestamp += .5
  
  allEvents = []
  
  screenEvents = []
  ringEvents = []
  panelEvents = []

  parts.panels.uploadUpwardGaugeChars().backlightOn()
  
  for i in range(5, 0, -1):
    screenEvents.append((
      lambda digit=i:
        parts.screens.draw(DIGITS_[digit], 8, 48, 0, mul=9).show(),
      1))
    for c in range(2, 10):
      ringEvents.append((
        lambda
          led=c,
          color=(1,1,1) if leds[c % ucuq.ravel.RING_SIZE] else (0,0,0):
            parts.rings.setValue(led, color).write(), 1/8))
      leds[c%8] = not leds[c%8]

  gauge = ()

  for j in range(16):
    gauge = ((j,) + gauge)[:16]
    panelEvents.append((
      lambda gauge = gauge:
        parts.panels.moveTo(0,0).putUpwardGauges(0, gauge),
      5/48))

  for j in range(15, -1, -1):
    gauge = ((j,) + gauge)[:16]
    panelEvents.append((
      lambda gauge = gauge:
        parts.panels.moveTo(0,0).putUpwardGauges(0, gauge),
      5/48))
      
  for j in range(16):
    gauge = ((0,) + gauge)[:16]
    panelEvents.append((
      lambda gauge = gauge:
        parts.panels.moveTo(0,0).putUpwardGauges(0, gauge),
      5/48))


  allEvents += (ringEvents,)
  allEvents += (panelEvents,)
  allEvents += (screenEvents,)
  
  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)
  
  sleepUntil(timestamp, 0)
  parts.rings.flash()
  parts.rings.fill((1,1,1)).write()
  parts.panels.backlightOn()
  timestamp += ucuq.playEvents(allEvents, lambda tracking: sleepUntil(timestamp + tracking.cumul, COMMIT_DELAY_))
  parts.screens.fill(0).show()
  parts.rings.fill((0,0,0)).write()
  parts.panels.clear().backlightOff()
  
  ucuq.setCommitBehavior(cb)
  
  ucuq.gcCollect()
  
  return timestamp + 0.5


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def displayRingGauges(parts, addendum="  "):
  parts.kits.displayRingGauges(addendum=addendum)  


def turnOffAndScrollDown(timestamp, parts):
  offset = random.randrange(len(RAINBOW_))
  
  for i in range(offset, ucuq.ravel.RING_SIZE + offset):
    parts.rings.setValue(i, getRainbowColor_(i, 7))
    
  parts.rings.write()
  
  for i in range(64):
    parts.rings.setValue(i //ucuq.ravel.RING_SIZE + offset, (0,0,0)).write()
    parts.screens.scroll(0, 1).show()
    parts.kits.displayRingGauges()
    timestamp += 0.09
    sleepUntil(timestamp, 0) 
    
  return timestamp
    
def syncTest():
  parts = getParts()

  for i in range(3):  
    parts.screens[i].draw(DIGITS_[i+1], 8, 48, 0, mul=9).show(),
  
  timestamp = time.time() + 1.5
  
  sleepUntil(timestamp,0)
  
  parts.rings.flash()
  
  sleepUntil(timestamp + 1,0)
  
  parts.rings.flash()

  parts.screens.fill(0).show()
