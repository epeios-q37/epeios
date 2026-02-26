from show import devices, sleep
from shared import RAINBOW

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
    devices.rgbs[index].setValue((1 - y) * x + y * (8 - x) * (x != 0), col)
    
    return self
    
  def fill(self, col):
    devices.rgbs.fill(col)

    return self
    
  def write(self):
    devices.rgbs.write()

    return self
  
SCHEMES_ = []  


def _(timestamp, delay):
  delay /= 1.5

  for color in RAINBOW:
    sleep(timestamp)
    timestamp += delay
    colors_.fill(color)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  delay /= 1.5
  
  rgbs = devices.rgbs
  
  for r in range(len(RAINBOW)):
    sleep(timestamp)
    timestamp += delay
    for rgb in rgbs:
      rgb.fill(RAINBOW[(r + rgbs.index(rgb) * len(RAINBOW) // len(rgbs)) % len(RAINBOW)])
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for i in range(15):
    sleep(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW[len(RAINBOW) * i // 15]
    colors_.set(i, (i // 5) % 2, col)
    colors_.write()
    
  for i in range(13, 0, -1):
    sleep(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW[len(RAINBOW) * i // 15]
    colors_.set(i, (i // 5 + 1) % 2, col)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for i in range(15):
    sleep(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    colors_.set(i, (i // 5) % 2, (10,0,0))
    colors_.set((14 - i), ((14 - i) // 5 + 1) % 2, (0,0,10))
    colors_.write()
    
  for i in range(13, 0, -1):
    sleep(timestamp)
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
    sleep(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW[len(RAINBOW) * i // 15]
    colors_.set(i, 0, col).set(i, 1, col)
    colors_.write()

  for i in range(13, 0, -1):
    sleep(timestamp)
    timestamp += delay
    colors_.fill((0,0,0))
    col = RAINBOW[len(RAINBOW) * i // 15]
    colors_.set(i, 0, col).set(i, 1, col)
    colors_.write()

  colors_.fill((0,0,0))
  return timestamp
  
SCHEMES_.append(_)


def _(timestamp, delay):
  for _ in range(2):
    for i in range(15):
      sleep(timestamp)
      timestamp += delay
      colors_.fill((0,0,0))
      col = RAINBOW[len(RAINBOW) * i // 15]
      colors_.set(i, 0, col).set(i, 1, col)
      colors_.set(14 - i, 0, col).set(14 - i, 1, col)
      colors_.write()
    
  colors_.fill((0,0,0))
  return timestamp  

SCHEMES_.append(_)


def _(timestamp, delay):
  for _ in range(2):
    for i in range(15):
      sleep(timestamp)
      timestamp += delay
      colors_.fill((0,0,0))
      col = RAINBOW[len(RAINBOW) * i // 15]
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
    sleep(timestamp)
    timestamp += delay
    col = RAINBOW[len(RAINBOW) * (7 - i) // 8]
    colors_.set(i, 0, col).set(14 - i, 0, col).set(i, 1, col).set(14 - i, 1, col)
    colors_.write()
    
  for i in range(7, -1, -1):
    sleep(timestamp)
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

  
def launch(scheme, timestamp, delay, repeat):
  timestamp += 1 
  
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
