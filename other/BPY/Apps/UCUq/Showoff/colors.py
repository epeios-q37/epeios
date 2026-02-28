import ucuq

from shared import RAINBOW as RAINBOW_, RGB_MAX as RGB_MAX_
from show import devices as devices_, sleep as sleep_

W_SCHEMES = "ColorSchemes"
W_DELAY = "ColorDelay"
W_DELAY_DISPLAY = "ColorDelayDisplay"
W_REPEAT = "ColorRepeat"
W_REPEAT_DISPLAY = "ColorRepeatDisplay"

class Colors_:
  def set(self, x, y, col):
    x = x % 15
    index = x // 5
    x = x % 5
    devices_.rgbs[index].setValue((1 - y) * x + y * (8 - x) * (x != 0), col)
    
    return self
    
  def fill(self, col):
    devices_.rgbs.fill(col)

    return self
    
  def write(self):
    devices_.rgbs.write()
    
    for i in range(len(devices_.rgbs)):
      devices_.lcds[i].moveTo(0,0).putString(devices_.rgbs[i].getJaugesString(RGB_MAX_))

    return self
  
SCHEMES_ = []


def oledRGB(oled,color):
  return oled.fill(0)\
    .rect(0, 63 - color[0] * 63 // RGB_MAX_, 42, 64, 1, True)\
    .rect(43, 63 - color[1] * 63 // RGB_MAX_, 42, 64, 1, True)\
    .rect(86, 63 - color[2] * 63 // RGB_MAX_, 42, 64, 1, True)


def _(timestamp, delay):
  delay /= 1.5
  
  # oleds = devices_.oleds  # Too slow, reintroduced when framebuffer implemented directly in ucuq.
  oleds = ucuq.Nothing()

  for color in RAINBOW_:
    sleep_(timestamp)
    timestamp += delay
    colors_.fill(color)
    colors_.write()
    oledRGB(oleds, color).show()

  colors_.fill((0,0,0))
  oleds.fill(0).show()
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  delay /= 1.5
  
  rgbs = devices_.rgbs
  # oleds = devices_.oleds  # Too slow, reintroduced when framebuffer implemented directly in ucuq.
  oleds = ucuq.Nothing()
  
  for r in range(len(RAINBOW_)):
    sleep_(timestamp)
    timestamp += delay
    for i in range(len(rgbs)):
      color = RAINBOW_[(r + i * len(RAINBOW_) // len(rgbs)) % len(RAINBOW_)]
      rgbs[i].fill(color)
      oledRGB(oleds[i], color)
    colors_.write()
    oleds.show()

  colors_.fill((0,0,0))
  oleds.fill(0).show()
  
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for i in range(15):
    sleep_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * i // 15]
    colors_.set(i, (i // 5) % 2, col)
    colors_.write()
    
  for i in range(13, 0, -1):
    sleep_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * i // 15]
    colors_.set(i, (i // 5 + 1) % 2, col)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for i in range(15):
    sleep_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    colors_.set(i, (i // 5) % 2, (10,0,0))
    colors_.set((14 - i), ((14 - i) // 5 + 1) % 2, (0,0,10))
    colors_.write()
    
  for i in range(13, 0, -1):
    sleep_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    colors_.set(i, (i // 5 + 1) % 2, (10,0,0))
    colors_.set((14 - i), ((14 - i) // 5) % 2, (0,0,10))
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  
  
SCHEMES_.append(_)


def _(timestamp, delay):
  for i in range(15):
    sleep_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * i // 15]
    colors_.set(i, 0, col).set(i, 1, col)
    colors_.write()

  for i in range(13, 0, -1):
    sleep_(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW_[len(RAINBOW_) * i // 15]
    colors_.set(i, 0, col).set(i, 1, col)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp
  
SCHEMES_.append(_)


def _(timestamp, delay):
  for _ in range(2):
    for i in range(15):
      sleep_(timestamp)
      timestamp += delay
      colors_.fill((0,0,0))
      col = RAINBOW_[len(RAINBOW_) * i // 15]
      colors_.set(i, 0, col).set(i, 1, col)
      colors_.set(14 - i, 0, col).set(14 - i, 1, col)
      colors_.write()
    
  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for _ in range(2):
    for i in range(15):
      sleep_(timestamp)
      timestamp += delay
      colors_.fill((0,0,0))
      col = RAINBOW_[len(RAINBOW_) * i // 15]
      colors_.set(i, 0, col).set(i, 1, col)
      colors_.set(7 - i, 0, col).set(7 - i, 1, col)
      colors_.set(7 + i, 0, col).set(7 + i, 1, col)
      colors_.set(14 - i, 0, col).set(14 - i, 1, col)
      colors_.write()
    
  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for i in range(8):
    sleep_(timestamp)
    timestamp += delay
    col = RAINBOW_[len(RAINBOW_) * (7 - i) // 8]
    colors_.set(i, 0, col).set(14 - i, 0, col).set(i, 1, col).set(14 - i, 1, col)
    colors_.write()
    
  for i in range(7, -1, -1):
    sleep_(timestamp)
    timestamp += delay
    col = (0,0,0)
    colors_.set(i, 0, col).set(14 - i, 0, col).set(i, 1, col).set(14 - i, 1, col)
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


def lcdSetJaugeChars_():
  lcds = devices_.lcds
  charmap = [0] * 8
  
  for i in range(8):
    charmap[7-i] = 0b11111
    lcds.createChar(i, charmap)
    
  lcds.backlightOn()

  
def launch(scheme, timestamp, delay, repeat):
  timestamp += 1 
  lcdSetJaugeChars_()
  
  if scheme == 0:
    for scheme in SCHEMES_:
      for _ in range(repeat):
        timestamp = scheme(timestamp, delay)
  else:
    for _ in range(repeat):
      timestamp = SCHEMES_[scheme-1](timestamp, delay)
    
  colors_.fill((0,0,0)).write()
  
  return timestamp

colors_ = Colors_()
