import javascript, json, sys
from browser import aio, alert, console
from browser.local_storage import storage

javascript.import_js("ucuq.js", "ucuqjs")

LIB_VERSION = "0.0.1"

CONFIG_ITEM = "ucuq-config"
CONFIG_DEVICE_ENTRY = "Device"
CONFIG_DEVICE_TOKEN_ENTRY = "Token"
CONFIG_DEVICE_ID_ENTRY = "Id"

ITEMS_ = "i_"

device_ = None
uuid_ = 0

async def sleepAwait(time):
  await ucuqjs.sleep(1000 * time, lambda : None)

def GetUUID_():
  global uuid_

  uuid_ += 1

  return uuid_

def commit():
  getDevice_().commit()

async def commitAwait(expr):
  return await getDevice_().commitAwait(expr)

def sleep(secs):
  getDevice_().sleep(secs)

async def pingAwait():
  return await getDevice_().pingAwait()

async def handleATKAwait(dom):
  await dom.inner("", "<h3>Connecting…</h3>")

  try:
    label = await pingAwait()
  except Exception as err:
    await dom.inner("", f"<h5>Error: {err}</h5>")
    raise

  await dom.inner("", f"<h3>'{label}'</h3>")

  await sleepAwait(1.5)

  return label



class Lock_:
  def __init__(self):
    self.locked_ = False

  async def acquire(self):
    while self.locked_:
      await aio.sleep(0)
    self.locked_ = True

  def release(self):
    self.locked_ = False


def uploadCallback_(code, result):
  if code != 0:
    raise Exception(result)


def executeCallback_(data, code, result):
  print(f"Execute callback: '{result}'")
  if code != 0:
    raise Exception(result)

  try:
    jsonResult = json.loads(result) if result else None
  except:
    jsonResult = result

  if data:
    data["code"] = code
    data["result"] = jsonResult
    data["lock"].release()

def pingCallback_(data, code, result):
  if code != 0:
    raise Exception(result)

  if data:
    data["code"] = code
    data["result"] = result
    data["lock"].release()

def launchCallback_(lock):
  lock.release()

def displayMissingConfigMessage_():
  alert("Please launch the 'Config' app first to set the device to use!")
  console.error = javascript.UNDEFINED  # To avoid the displaying of an alert by below 'exit()'.
  sys.exit()

def handlingConfig_(token, id):
  if not CONFIG_ITEM in storage:
    displayMissingConfigMessage_()

  try:
    config = json.loads(storage[CONFIG_ITEM])
  except:
    displayMissingConfigMessage_()

  if CONFIG_DEVICE_ENTRY not in config:
    displayMissingConfigMessage_()

  device = config[CONFIG_DEVICE_ENTRY]

  if token == None:
    if CONFIG_DEVICE_TOKEN_ENTRY not in device:
      displayMissingConfigMessage_()

    token = device[CONFIG_DEVICE_TOKEN_ENTRY]

  if id == None:
    if CONFIG_DEVICE_ID_ENTRY not in device:
      displayMissingConfigMessage_()

    id = device[CONFIG_DEVICE_ID_ENTRY]

  return token, id


class Device:
  def __init__(self, /, id = None, token = None, now = True):
    if now:
      self.connect(id, token)

  def __del__(self):
    self.commit()

  def connect(self, id, token = None):
    self.pendingModules_ = ["Init-1"]
    self.handledModules_ = []
    self.commands_ = []

    if token == None or id == None:
      token, id = handlingConfig_(token, id)

    self.device_ = ucuqjs.launch(token, id, LIB_VERSION, lambda: None)

  
  def upload_(self, modules):
    ucuqjs.upload(self.device_, modules, lambda code, result: uploadCallback_(code, result))


  async def executeAwait_(self, script, expression):
    lock = Lock_()

    await lock.acquire()

    data = {
      "lock": lock
    }

    ucuqjs.execute(self.device_, script, expression, lambda code, result: executeCallback_(data, code, result))

    await lock.acquire()
    
    return data["result"]


  def execute_(self, script):
    ucuqjs.execute(self.device_, script, "", lambda code, result: executeCallback_(None, code, result))


  async def pingAwait(self):
    lock = Lock_()

    await lock.acquire()

    data = {
      "lock": lock
    }

    ucuqjs.ping(self.device_, lambda code, result: pingCallback_(data, code, result))

    await lock.acquire()
    
    return data["result"]

  def addModule(self, module):
    if not module in self.pendingModules_ and not module in self.handledModules_:
      self.pendingModules_.append(module)

  def addModules(self, modules):
    if isinstance( modules, str):
      self.addModule(modules)
    else:
      for module in modules:
        self.addModule(module)

  def addCommand(self, command):
    self.commands_.append(command)

  async def commitAwait(self, expression):
    result = ""

    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.extend(self.pendingModules_)
      self.pendingModules_ = []

    result = await self.executeAwait_('\n'.join(self.commands_) if self.commands_ else "", expression)
    self.commands_ = []

    return result
  
  def sleep(self, secs):
    self.addCommand(f"time.sleep({secs})")

  def commit(self):
    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.extend(self.pendingModules_)
      self.pendingModules_ = []

    if self.commands_:
      self.execute_('\n'.join(self.commands_))
    
    self.commands_ = []

###############
# UCUq COMMON #
###############

def getDevice_(device = None):
  if device == None:
    global device_

    if device_ == None:
      device_ = Device()
    
    return device_
  else:
    return device

def addCommand(command, /,device = None):
  getDevice_(device).addCommand(command)

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

  def addMethods(self, methods):
    self.addCommand(f"{self.getObject()}.{methods}")
                         

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
    return int(await self.executeAwait_("", f"{self.getObject()}.__len__()"))
               

  def setValue(self, index, val):
    self.addMethods(f"setitem({index}, {json.dumps(val)})")

    return self
                       
  async def getValueAwait(self, index):
    return await self.executeAwait_("", f"{self.getObject()}.__getitem__({index})")
                       
  def fill(self, val):
    self.addMethods(f"fill({json.dumps(val)})")
    return self

  def write(self):
    self.addMethods(f"write()")

class I2C(Core_):
  def __init__(self, sda = None, scl = None, /, device = None):
    super().__init__(device, "I2C-1")

    if bool(sda) != bool(scl):
      raise Exception("None or both of sda/scl must be given!")
    elif sda != None:
      self.init(sda, scl)

  def init(self, sda, scl):
    super().init(f"machine.I2C(0, sda=machine.Pin({sda}), scl=machine.Pin({scl}))")

  async def scanAwait(self):
    return (await commitAwait(f"{self.getObject()}.scan()"))
    

class HT16K33(Core_):
  def __init__(self, i2c = None, /, addr = None, device = None):
    super().__init__(device, "HT16K33-1")

    if i2c:
      self.init(i2c)


  def init(self, i2c, addr = None):
    super().init(f"HT16K33({i2c.getObject()}, {addr})")

    self.addMethods(f"set_brightness(0)")


  def setBlinkRate(self, rate):
    self.addMethods(f"set_blink_rate({rate})")

    return self

  def setBrightness(self, brightness):
    self.addMethods(f"set_brightness({brightness})")

    return self

  def clear(self):
    self.addMethods(f"clear()")

    return self

  def draw(self, motif):
    self.addMethods(f"clear().draw('{motif}').render()")

    return self

  def plot(self, x, y, ink=True):
    self.addMethods(f"plot({x}, {y}, ink={1 if ink else 0})")  

    return self

  def commit(self):
    self.addMethods(f"render()")

    return self


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
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_u16()"))


  def setU16(self, u16):
    self.addMethods(f"duty_u16({u16})")


  async def getNSAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_ns()"))


  def setNS(self, ns):
    self.addMethods(f"duty_ns({ns})")


  async def getFreqAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.freq()"))


  def setFreq(self, freq):
    self.addMethods(f"freq({freq})")


  def deinit(self):
    self.addMethods(f"deinit()")


class PCA9685(Core_):
  def __init__(self, i2c = None, freq = None,/, addr = None, device = None):
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

  async def getFreqAwait(self):
    return await self.executeAwait_("", f"{self.getObject()}.freq()")

  def setFreq(self, freq):
    return self.addMethods(f"freq({freq})")
  

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


  async def getNSAwait(self,):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_ns()"))

  def setNS(self, ns):
    self.addMethods(f"duty_ns({ns})")


  async def getU16Await(self, u16 = None):
    return int(await self.executeAwait_("",f"{self.getObject()}.duty_u16()"))
  
  def setU16(self, u16):
    self.addMethods(f"duty_u16({u16})")
  

  async def getFreqAwait(self):
    return int(await self.executeAwait_("",f"{self.getObject()}.freq()"))
  
  def setFreq(self, freq):
    self.addMethods(f"freq({freq})")


class LCD_PCF8574(Core_):
  def __init__(self, i2c, num_lines, num_columns,/,addr = None, device = None):
    super().__init__(device, "LCD_PCF8574-1")

    if i2c:
      self.init(i2c, num_lines, num_columns, addr = addr)
    elif addr != None:
      raise Exception("addr can not be given without i2c!")

  def init(self, i2c, num_lines, num_columns, addr = None):
    super().init(f"LCD_PCF8574({i2c.getObject()},{num_lines},{num_columns},{addr})")

  def moveTo(self, x, y):
    self.addMethods(f"move_to({x},{y})")

  def putString(self, string):
    self.addMethods(f"putstr(\"{string}\")")

  def clear(self):
    self.addMethods("clear()")

  def showCursor(self, value = True):
    self.addMethods("show_cursor()" if value else "hide_cursor()")

  def hideCursor(self):
    self.showCursor(False)

  def blinkCursorOn(self, value = True):
    self.addMethods("blink_cursor_on()" if value else "blink_cursor_off()")

  def blinkCursorOff(self):
    self.blinkCursorOn(False)

  def displayOn(self, value = True):
    self.addMethods("display_on()" if value else "display_off()")

  def displayOff(self):
    self.displayOn(False)

  def backlightOn(self, value = True):
    self.addMethods("backlight_on()" if value else "backlight_off()")

  def backlightOff(self):
    self.backlightOn(False)

  

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
    self.addMethods("show()")

  def powerOff(self):
    self.addMethods("poweroff()")

  def contrast(self, contrast):
    self.addMethods(f"contrast({contrast})")

  def invert(self, invert):
    self.addMethods(f"invert({invert})")

  def fill(self, col):
    self.addMethods(f"invert({col})")

  def pixel(self, x, y, col):
    self.addMethods(f"pixel({x},{y},{col})")

  def scroll(self, dx, dy, col):
    self.addMethods(f"scroll({dx},{dy})")

  def text(self, string, x, y, col=1):
    self.addMethods(f"text('{string}',{x}, {y}, {col})")

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



    
