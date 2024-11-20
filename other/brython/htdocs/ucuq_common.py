def displayMissingConfigMessage_():
  displayExitMessage_("Please launch the 'Config' app first to set the device to use!")


def setDevice(id, token = None):
  getDevice_(id = id, token = token)


INFO_SCRIPT = """
def ucuqGetKitLabel(): 
  if "Kit" in CONFIG_:
    kit = CONFIG_["Kit"]

    id = getSelectorId_(SELECTOR_)

    if id in kit:
      return kit[id]
    else:
      return ""

def ucuqStructToDict(obj):
    return {attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__')}

def ucuqGetInfos():
  return {
    "kit": {
      "label": ucuqGetKitLabel()
    },
    "uname": ucuqStructToDict(uos.uname())
  }
"""

async def handleATKAwait(dom):
  await dom.inner("", "<h3>Connecting…</h3>")
  
  addCommand(INFO_SCRIPT)

  try:
    info = await commitAwait("ucuqGetInfos()")
  except Exception as err:
    await dom.inner("", f"<h5>Error: {err}</h5>")
    raise

  await dom.inner("", f"<h3>'{info['kit']['label']}'</h3>")

  await sleepAwait(1.5)

  return info

def getDevice_(device = None, *, id = None, token = None):

  if device  and ( token or id):
    displayExitMessage_("'device' can not be given together with 'token' or 'id'!")

  if device == None:
    global device_

    if token or id:
      device_ = Device(id = id, token = token)
    elif device_ == None:
      device_ = Device()
    
    return device_
  else:
    return device

def addCommand(command, /,device = None):
  getDevice_(device).addCommand(command)


class Core_:
  def __init__(self, device, modules = ""):
    self.id = None

    self.device_ = getDevice_(device)

    if modules:
      self.device_.addModules(modules)
  
  def __del__(self):
    if self.id:
      self.addCommand(f"del {ITEMS_}[{self.id}]")
  
  def init(self, instanciation):
    self.id = GetUUID_()
    if instanciation:
      self.addCommand(f"{self.getObject()} = {instanciation}")

  def getObject(self):
    return f"{ITEMS_}[{self.id}]"

  def addCommand(self, command):
    self.device_.addCommand(command)

    return self

  def addMethods(self, methods):
    return self.addCommand(f"{self.getObject()}.{methods}")

  def callMethodAwait(self, method):
    return self.device_.commitAwait(f"{self.getObject()}.{method}")
                         

class GPIO(Core_):
  def __init__(self, pin = None, device = None):
    super().__init__(device, "GPIO-1")

    if pin:
      self.init(pin)


  def init(self, pin):
    self.pin = f'"{pin}"' if isinstance(pin,str) else pin

    super().init(f"GPIO({self.pin})")


  def high(self, value = True):
    self.addMethods(f"high({value})")


  def low(self):
    self.high(False)


class WS2812(Core_):
  def __init__(self, pin = None, n = None, device = None):
    super().__init__(device, "WS2812-1")

    if (pin == None) != (n == None):
      raise Exception("Both or none of 'pin'/'n' must be given")

    if pin != None:
      self.init(pin, n)

  def init(self, pin, n):
    super().init(f"neopixel.NeoPixel(machine.Pin({pin}), {n})")

  async def lenAwait(self):
    return int(await self.callMethodAwait("__len__()"))
               

  def setValue(self, index, val):
    self.addMethods(f"__setitem__({index}, {json.dumps(val)})")

    return self
                       
  async def getValueAwait(self, index):
    return await self.callMethodAwait(f"__getitem__({index})")
                       
  def fill(self, val):
    self.addMethods(f"fill({json.dumps(val)})")
    return self

  def write(self):
    self.addMethods(f"write()")

class I2C_Core_(Core_):
  def __init__(self, sda = None, scl = None, /, device = None):
    super().__init__(device, "I2C-1")

    if sda == None != scl == None:
      raise Exception("None or both of sda/scl must be given!")
    elif sda != None:
      self.init(sda, scl)

  async def scanAwait(self):
    return (await commitAwait(f"{self.getObject()}.scan()"))


class I2C(I2C_Core_):
  def init(self, sda, scl):
    super().init(f"machine.I2C(0, sda=machine.Pin({sda}), scl=machine.Pin({scl}))")


class SoftI2C(I2C_Core_):
  def init(self, sda, scl):
    super().init(f"machine.SoftI2C(sda=machine.Pin({sda}), scl=machine.Pin({scl}))")
  

class HT16K33(Core_):
  def __init__(self, i2c = None, /, addr = None, device = None):
    super().__init__(device, "HT16K33-1")

    if i2c:
      self.init(i2c)


  def init(self, i2c, addr = None):
    super().init(f"HT16K33({i2c.getObject()}, {addr})")

    return self.addMethods(f"set_brightness(0)")


  def setBlinkRate(self, rate):
    return self.addMethods(f"set_blink_rate({rate})")


  def setBrightness(self, brightness):
    return self.addMethods(f"set_brightness({brightness})")

  def clear(self):
    return self.addMethods(f"clear()")

  def draw(self, motif):
    return self.addMethods(f"clear().draw('{motif}').render()")

  def plot(self, x, y, ink=True):
    return self.addMethods(f"plot({x}, {y}, ink={1 if ink else 0})")  

  def show(self):
    return self.addMethods(f"render()")



class PWM(Core_):
  def __init__(self, pin = None, freq = None, device = None):
    super().__init__(device, "PWM-1")

    if freq != None:
      if pin == None:
        raise Exception("'freq' cannot be given without 'pin'!")
      
    if pin != None:
      self.init(pin, freq)


  def init(self, pin, freq = None):
    super().init(f"machine.PWM(machine.Pin({pin}),freq={freq if freq else 50})")


  async def getU16Await(self):
    return int(await self.callMethodAwait("duty_u16()"))


  def setU16(self, u16):
    self.addMethods(f"duty_u16({u16})")


  async def getNSAwait(self):
    return int(await self.callMethodAwait("duty_ns()"))


  def setNS(self, ns):
    self.addMethods(f"duty_ns({ns})")


  async def getFreqAwait(self):
    return int(await self.callMethodAwait("freq()"))


  def setFreq(self, freq):
    self.addMethods(f"freq({freq})")


  def deinit(self):
    self.addMethods(f"deinit()")


class PCA9685(Core_):
  def __init__(self, i2c = None, freq = None, *, addr = None, device = None):
    super().__init__(device, "PCA9685-1")

    if i2c:
      self.init(i2c, freq = freq, addr = addr)
    elif freq:
      raise Exception("freq cannot be given without i2c!")
    elif addr:
      raise Exception("addr cannot be given without i2c!")


  def init(self, i2c, /, freq = None, addr = None):
    super().init(f"PCA9685({i2c.getObject()}, {addr})")

    self.setFreq(freq if freq else 50)


  def deinit(self):
    self.addMethods(f"reset()")
                    

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))

  async def setOffsetAwait(self):
    return int(await self.callMethodAwait("offset()"))

  def setOffset(self, offset):
    return self.addMethods(f"offset({offset})")

  async def getFreqAwait(self):
    return int(await self.callMethodAwait("freq()"))

  def setFreq(self, freq):
    return self.addMethods(f"freq({freq})")

  async def getPrescaleAwait(self):
    return int(await self.callMethodAwait("prescale()"))

  def setPrescale(self, value):
    return self.addMethods(f"prescale({value})")
  

class PWM_PCA9685(Core_):
  def __init__(self, pca = None, channel = None, device = None):
    super().__init__(device, "PWM_PCA9685-1")

    if bool(pca) != (channel != None):
      raise Exception("Both or none of 'pca' and 'channel' must be given!")
    
    if pca:
      self.init(pca, channel)

  def init(self, pca, channel):
    super().init(f"PWM_PCA9685({pca.getObject()}, {channel})")

    self.pca = pca # Not used inside this object, but to avoid pca being destroyed by GC, as it is used on the µc.

  def deinit(self):
    self.addMethods(f"deinit()")

  async def getOffset(self):
    return self.pca.offset()

  def setOffset(self, offset):
    self.pca.setOffset(offset)

  async def getNSAwait(self):
    return int(await self.callMethodAwait(f"duty_ns()"))

  def setNS(self, ns):
    self.addMethods(f"duty_ns({ns})")

  async def getU16Await(self, u16 = None):
    return int(await self.callMethodAwait("duty_u16()"))
  
  def setU16(self, u16):
    self.addMethods(f"duty_u16({u16})")
  
  async def getFreqAwait(self):
    return await self.pca.getFreqAwait()
  
  def setFreq(self, freq):
    self.pca.setFreq(freq)

  async def getPrescaleAwait(self):
    return await self.pca.getPrescaleAwait()
  
  def setPrescale(self, value):
    self.pca.setPrescale(value)
  

class LCD_PCF8574(Core_):
  def __init__(self, i2c, num_lines, num_columns,/,addr = None, device = None):
    super().__init__(device, "LCD_PCF8574-1")

    if i2c:
      self.init(i2c, num_lines, num_columns, addr = addr)
    elif addr != None:
      raise Exception("addr can not be given without i2c!")

  def init(self, i2c, num_lines, num_columns, addr = None):
    return super().init(f"LCD_PCF8574({i2c.getObject()},{num_lines},{num_columns},{addr})")

  def moveTo(self, x, y):
    return self.addMethods(f"move_to({x},{y})")

  def putString(self, string):
    return self.addMethods(f"putstr(\"{string}\")")

  def clear(self):
    return self.addMethods("clear()")

  def showCursor(self, value = True):
    return self.addMethods("show_cursor()" if value else "hide_cursor()")

  def hideCursor(self):
    return self.showCursor(False)

  def blinkCursorOn(self, value = True):
    return self.addMethods("blink_cursor_on()" if value else "blink_cursor_off()")

  def blinkCursorOff(self):
    return self.blinkCursorOn(False)

  def displayOn(self, value = True):
    return self.addMethods("display_on()" if value else "display_off()")

  def displayOff(self):
    return self.displayOn(False)

  def backlightOn(self, value = True):
    return self.addMethods("backlight_on()" if value else "backlight_off()")

  def backlightOff(self):
    return self.backlightOn(False)

  

class Servo(Core_):
  class Specs:
    def __init__(self, u16_min, u16_max, range):
      self.min = u16_min
      self.max = u16_max
      self.range = range
  
  class Tweak:
    def __init__(self, angle, u16_offset, invert):
      self.angle = angle
      self.offset = u16_offset
      self.invert = invert
  
  class Domain:
    def __init__(self, u16_min, u16_max):
      self.min = u16_min
      self.max = u16_max


  def test_(self, specs, tweak, domain):
    if tweak:
      if not specs:
        raise Exception("'tweak' can not be given without 'specs'!")

    if domain:
      if not specs:
        raise Exception("'domain' can not be given without 'specs'!")


  def __init__(self, pwm = None, specs = None, /, *, tweak = None, domain = None, device = None):
    super().__init__(device, "Servo-1")

    self.test_(specs, tweak, domain)

    if pwm:
      self.init(pwm, specs, tweak = tweak, domain = domain)


  def init(self, pwm, specs, tweak = None, domain = None):
    super().init("")

    self.test_(specs, tweak, domain)

    if not tweak:
      tweak = self.Tweak(specs.range/2, 0, False)

    if not domain:
      domain = self.Domain(specs.min, specs.max)

    self.specs = specs
    self.tweak = tweak
    self.domain = domain

    self.pwm = pwm

    self.reset()


  def angleToDuty(self, angle):
    if self.tweak.invert:
      angle = -angle

    u16 = self.specs.min + ( angle + self.tweak.angle ) * ( self.specs.max - self.specs.min ) / self.specs.range + self.tweak.offset

    if u16 > self.domain.max:
      u16 = self.domain.max
    elif u16 < self.domain.min:
      u16 = self.domain.min

    return int(u16)
  

  def dutyToAngle(self, duty):
    angle = self.specs.range * ( duty - self.tweak.offset - self.specs.min ) / ( self.specs.mas - self.specs.min )

    if self.tweak.invert:
      angle = -angle

    return angle - self.tweak.angle


  def reset(self):
    self.setAngle(0)


  async def getAngleAwait(self):
    return self.dutyToAngle(await self.pwm.getU16Await())

  def setAngle(self, angle):
    return self.pwm.setU16(self.angleToDuty(angle))
  

class SSD1306(Core_):
  def show(self):
    return self.addMethods("show()")

  def powerOff(self):
    return self.addMethods("poweroff()")

  def contrast(self, contrast):
    return self.addMethods(f"contrast({contrast})")

  def invert(self, invert):
    return self.addMethods(f"invert({invert})")

  def fill(self, col):
    return self.addMethods(f"fill({col})")

  def pixel(self, x, y, col):
    return self.addMethods(f"pixel({x},{y},{col})")

  def scroll(self, dx, dy):
    return self.addMethods(f"scroll({dx},{dy})")

  def text(self, string, x, y, col=1):
    return self.addMethods(f"text('{string}',{x}, {y}, {col})")

class SSD1306_I2C(SSD1306):
  def __init__(self, width = None, height = None, i2c = None, /, addr = None, external_vcc = False, device = None):
    super().__init__(device, ("SSD1306-1", "SSD1306_I2C-1"))

    if bool(width) != bool(height) != bool(i2c):
      raise Exception("All or none of width/height/i2c must be given!")
    elif width:
      self.init(width, height, i2c, external_vcc = external_vcc, addr= addr)
    elif addr:
      raise Exception("addr can not be given without i2c!")
      

  def init(self, width, height, i2c, /, external_vcc = False, addr = None):
    super().init(f"SSD1306_I2C({width}, {height}, {i2c.getObject()}, {addr}, {external_vcc})")


def servoMoves(moves, speed = 1,/,device = None):
  device = getDevice_(device)

  device.addModule("ServoMoves-1")

  command = "servoMoves([\n"

  for move in moves:
    servo = move[0]

    step = speed * (servo.specs.max - servo.specs.min) / servo.specs.range

    command += f"\t[{move[0].pwm.getObject()},{move[0].angleToDuty(move[1])}],\n"

  command += f"], {int(step)})"

  device.addCommand(command)


def rbShade(variant, i, max):
  match int(variant) % 6:
    case 0:
      return [max, i, 0]
    case 1:
      return [max - i, max, 0]
    case 2:
      return [0, max, i]
    case 3:
      return [0, max - i, max]
    case 4:
      return [i, 0, max]
    case 5:
      return [max, 0, max - i]
      
def rbFade(variant, i, max, inOut):
  if not inOut:
    i = max - i
  match variant % 6:
    case 0:
      return [i,0,0]
    case 1:
      return [i,i,0]
    case 2:
      return [0,i,0]
    case 3:
      return [0,i,i]
    case 4:
      return [0,0,i]
    case 5:
      return [i,0,i]
      

def rbShadeFade(variant, i, max):
  if i < max:
    return rbFade(variant, i, max, True)
  elif i > max * 6:
    return rbFade((variant + 5 ) % 6, i % max, max, False)
  else:
    return rbShade(variant + int( (i - max) / max ), i % max, max)
    
