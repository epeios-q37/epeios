import ucuq

import shared
import show

from shared import RAINBOW as RAINBOW_, RGB_MAX as RGB_MAX_
from show import devices as devices_, sleepUntil as sleepUntil_

W_SCHEMES = "ColorSchemes"
W_DELAY = "ColorDelay"
W_DELAY_DISPLAY = "ColorDelayDisplay"
W_REPEAT = "ColorRepeat"
W_REPEAT_DISPLAY = "ColorRepeatDisplay"

class Colors_:
  def set(self, x, y, col):
    x = x % 12
    index = x // 4
    x = x % 4
    devices_.rings[index].setValue(x if y == 0 else -x - 1, col)
    
    return self
    
  def fill(self, col):
    devices_.rings.fill(col)

    return self
    
  def write(self):
    devices_.rings.write()
    show.lcdDisplayRing()
    
    return self
  

SCHEMES_ = []


def oledRGB(oled,color):
  return oled.fill(0)\
    .rect(0, 63 - color[0] * 63 // RGB_MAX_, 42, 64, 1, True)\
    .rect(43, 63 - color[1] * 63 // RGB_MAX_, 42, 64, 1, True)\
    .rect(86, 63 - color[2] * 63 // RGB_MAX_, 42, 64, 1, True)

# 1
def _(timestamp, delay):
  delay /= 1.5
  
  # oleds = devices_.oleds  # Too slow, reintroduced when framebuffer implemented directly in ucuq.
  oleds = ucuq.Nothing()

  for color in RAINBOW_:
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill(color)
    colors_.write()
    oledRGB(oleds, color).show()

  colors_.fill((0,0,0))
  oleds.fill(0).show()
  return timestamp  

SCHEMES_.append(_)

# 2
def _(timestamp, delay):
  delay /= 1.5
  
  rings = devices_.rings
  # oleds = devices_.oleds  # Too slow, reintroduced when framebuffer implemented directly in ucuq.
  oleds = ucuq.Nothing()
  
  for r in range(len(RAINBOW_)):
    sleepUntil_(timestamp)
    timestamp += delay
    for i in range(len(rings)):
      color = RAINBOW_[(r + i * len(RAINBOW_) // len(rings)) % len(RAINBOW_)]
      rings[i].fill(color)
      oledRGB(oleds[i], color)
    colors_.write()
    oleds.show()

  colors_.fill((0,0,0))
  oleds.fill(0).show()
  
  return timestamp  

SCHEMES_.append(_)

# 3
def _(timestamp, delay):
  for x in range(12):
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * x // 12]
    colors_.set(x, (x // 4) % 2, col)
    colors_.write()
    
  for x in range(11, -1, -1):
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * x // 12]
    colors_.set(x, (x // 4 + 1) % 2, col)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)

# 4
def _(timestamp, delay):
  for i in range(12):
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    colors_.set(i, (i // 4) % 2, (10,0,0))
    colors_.set((11 - i), ((11 - i) // 4 + 1) % 2, (0,0,10))
    colors_.write()
    
  for i in range(11, -1, -1):
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    colors_.set(i, (i // 4 + 1) % 2, (10,0,0))
    colors_.set((11 - i), ((11 - i) // 4) % 2, (0,0,10))
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  
  
SCHEMES_.append(_)

# 5
def _(timestamp, delay):
  for i in range(12):
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * i // 12]
    colors_.set(i, 0, col).set(i, 1, col)
    colors_.write()

  for i in range(10, -1, -1):
    sleepUntil_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * i // 12]
    colors_.set(i, 0, col).set(i, 1, col)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp
  
SCHEMES_.append(_)

# 6
def _(timestamp, delay):
  for _ in range(2):
    for i in range(12):
      sleepUntil_(timestamp)
      timestamp += delay
      colors_.fill((0,0,0))
      col = RAINBOW_[len(RAINBOW_) * i // 12]
      colors_.set(i, 0, col).set(i, 1, col)
      colors_.set(11 - i, 0, col).set(11 - i, 1, col)
      colors_.write()
    
  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)

## 7
def _(timestamp, delay):
  for _ in range(2):
    for i in range(12):
      sleepUntil_(timestamp)
      timestamp += delay
      colors_.fill((0,0,0))
      col = RAINBOW_[len(RAINBOW_) * i // 12]
      colors_.set(i, 0, col).set(i, 1, col)
      colors_.set(6 - i, 0, col).set(6 - i, 1, col)
      colors_.set(6 + i, 0, col).set(6 + i, 1, col)
      colors_.set(12 - i, 0, col).set(12 - i, 1, col)
      colors_.write()
    
  colors_.fill((0,0,0))
  return timestamp  

# SCHEMES_.append(_)

# 7
def _(timestamp, delay):
  for i in range(6):
    sleepUntil_(timestamp)
    timestamp += delay
    col = RAINBOW_[len(RAINBOW_) * (5 - i) // 6]
    colors_.set(i, 0, col).set(11 - i, 0, col).set(i, 1, col).set(11 - i, 1, col)
    colors_.write()
    
  for i in range(5, -1, -1):
    sleepUntil_(timestamp)
    timestamp += delay
    col = (0,0,0)
    colors_.set(i, 0, col).set(11 - i, 0, col).set(i, 1, col).set(11 - i, 1, col)
    colors_.write()
    
  colors_.fill((0,0,0))
  return timestamp

SCHEMES_.append(_)
    

def fill(dom):
  html = '\n<option value="0">All</option>'
  
  for i in range(1, len(SCHEMES_) + 1):
    html += f'\n<option value="{i}">{i}</option>'
    
  dom.inner(W_SCHEMES, html)
  
  
def update(dom):
  delay, repeat = dom.getValues((W_DELAY, W_REPEAT)).values()
  dom.setValues({W_DELAY_DISPLAY: float(delay), W_REPEAT_DISPLAY: int(repeat)})


def launch(scheme, timestamp, delay, repeat):
  timestamp += 1 
  
  sleepUntil_(timestamp)
  devices_.lcds.backlightOn()
  
  if scheme == 0:
    for scheme in SCHEMES_:
      for _ in range(repeat):
        timestamp = scheme(timestamp, delay)
  else:
    for _ in range(repeat):
      timestamp = SCHEMES_[scheme-1](timestamp, delay)
    
  colors_.fill((0,0,0)).write()
  devices_.lcds.clear().backlightOff()
  
  return timestamp

colors_ = Colors_()
