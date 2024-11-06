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
  await ucuqjs.sleep(time, lambda : None)

def GetUUID_():
  global uuid_

  uuid_ += 1

  return uuid_

def render():
  getDevice_().render()

async def renderAwait(expr):
  return await getDevice_().renderAwait()

def sleep(secs):
  getDevice_.sleep(secs)


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
    self.render()

  def connect(self, id, token = None):
    self.pendingModules_ = ["Init"]
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


  def addModule(self, module):
    if not module in self.pendingModules_ and not module in self.handledModules_:
      self.pendingModules_.append(module)


  def addCommand(self, command):
    self.commands_.append(command)


  async def renderAwait(self, expression):
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

  def render(self):
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

def servoMoves(self, moves, speed = 1,/,device = None):
  device = getDevice_(device)

  device.addModule("ServoMoves")

  command = "servoMoves([\n"

  for move in moves:
    servo = move[0]

    step = speed * (servo.specs.max - servo.specs.min) / servo.specs.range

    command += f"\t[{move[0].pwm.getObject()},{move[0].angleToDuty(move[1])}],\n"

  command += f"], {int(step)})"

  device.addCommand(command)


class Core_:
  def __init__(self, device, module = ""):
    self.id = None

    self.device_ = getDevice_(device)

    if module:
      self.device_.addModule(module)
  
  def __del__(self):
    if self.id:
      self.device_.execute_(f"del {ITEMS_}[{self.id}]")
  
  def init(self):
    self.id = GetUUID_()

  def getObject(self):
    return f"{ITEMS_}[{self.id}]"

  def addCommand(self, command):
    self.device_.addCommand(command)
                         
  def render(self):
    self.device_.render()
  

class GPIO(Core_):
  def __init__(self, pin = None, device = None):
    super().__init__(device, "GPIO")

    if pin:
      self.init(pin)


  def init(self, pin):
    super().init()
    self.pin = f'"{pin}"' if isinstance(pin,str) else pin

    self.addCommand(f"{self.getObject()} = GPIO({self.pin})")


  def on(self, state = True):
    self.addCommand(f"{self.getObject()}.on({state})")


  def off(self):
    self.on(False)


class WS2812(Core_):
  def __init__(self, pin = None, n = None, device = None):
    super().__init__(device, "WS2812")

    if (pin == None) != (n == None):
      raise Exception("Both or none of 'pin'/'n' must be defined")

    if pin != None:
      self.init(pin, n)

  def init(self, pin, n):
    super().init()

    self.addCommand(f"{self.getObject()} = neopixel.NeoPixel(machine.Pin({pin}), {n})")


  async def lenAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.__len__()"))
               

  def setValue(self, index, val):
    self.addCommand(f"{self.getObject()}.setitem({index}, {json.dumps(val)})")

    return self
                       
  async def getValueAwait(self, index):
    return await self.executeAwait_("", f"{self.getObject()}.__getitem__({index})")
                       
  def fill(self, val):
    self.addCommand(f"{self.getObject()}.fill({json.dumps(val)})")
    return self

  def write(self):
    self.addCommand(f"{self.getObject()}.write()")
    self.render()
    

class HT16K33(Core_):
  def __init__(self, sda = None, scl = None, device = None):
    super().__init__(device, "HT16K33")

    if bool(sda) != bool(scl):
      raise Exception("None or both of sda/scl must be defined!")
    elif sda:
      self.init(sda, scl)


  def init(self, sda, scl):
    super().init()

    self.addCommand(f"{self.getObject()} = HT16K33(machine.I2C(0, sda=machine.Pin({sda}), scl=machine.Pin({scl})))")
    self.addCommand(f"{self.getObject()}.set_brightness(0)")


  def setBlinkRate(self, rate):
    self.addCommand(f"{self.getObject()}.set_blink_rate({rate})")

    return self

  def setBrightness(self, brightness):
    self.addCommand(f"{self.getObject()}.set_brightness({brightness})")

    return self

  def clear(self):
    self.addCommand(f"{self.getObject()}.clear()")

    return self

  def draw(self, motif):
    self.addCommand(f"{self.getObject()}.clear().draw('{motif}').render()")

    return self

  def plot(self, x, y, ink=True):
    self.addCommand(f"{self.getObject()}.plot({x}, {y}, ink={1 if ink else 0})")  

    return self

  def render(self):
    self.addCommand(f"{self.getObject()}.render()")

    return self


class PWM(Core_):
  def __init__(self, pin = None, freq = None, device = None):
    super().__init__(device, "PWM")

    if freq != None:
      if pin == None:
        raise Exception("'freq' cannot be defined without 'pin'!")
      
    if pin != None:
      self.init(pin, freq)


  def init(self, pin, freq = None):
    super().init()

    self.addCommand(f"{self.getObject()} = machine.PWM(machine.Pin({pin}),freq={freq if freq else 50})")


  async def getU16Await(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_u16()"))


  def setU16(self, u16):
    self.addCommand(f"{self.getObject()}.duty_u16({u16})")


  async def getNSAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_ns()"))


  def setNS(self, ns):
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")


  async def getFreqAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.freq()"))


  def setFreq(self, freq):
    self.addCommand(f"{self.getObject()}.freq({freq})")


  def deinit(self):
    self.addCommand(f"{self.getObject()}.deinit()")


class PCA9685(Core_):
  def __init__(self, sda = None, scl = None, freq = None, addr = None, device = None):
    super().__init__(device, "PCA9685")

    if (sda != None) != bool(scl != None) :
      raise Exception("None or both of 'sda'/'scl' must be defined!")
    
    if sda:
      self.init(sda, scl, freq = freq, addr = addr)
    elif freq:
      raise Exception("'freq' cannot be defined without 'sda' and 'scl'!")
    elif addr:
      raise Exception("'addr' cannot be defined without 'sda' and 'scl'!")


  def init(self, sda, scl, *, freq = None, addr = None):
    super().init()

    self.addCommand(f"{self.getObject()} = PCA9685({sda}, {scl}, {addr if addr else 0x40})")
    self.setFreq(freq if freq else 50)


  def deinit(self):
    self.addCommand(f"{self.getObject()}.reset()")
                    

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))

  async def getFreqAwait(self):
    return await self.executeAwait_("", f"{self.getObject()}.freq()")

  def setFreq(self, freq):
    return self.addCommand(f"{self.getObject()}.freq({freq})")
  

class PCA9685Channel(Core_):
  def __init__(self, pca = None, channel = None, device = None):
    super().__init__(device, "PCA9685Channel")

    if bool(pca) != (channel != None):
      raise Exception("Both or none of 'pca' and 'channel' must be defined!")
    
    if pca:
      self.init(pca, channel)


  def init(self, pca, channel):
    super().init()

    self.pca = pca # Not used inside this object, but to avoid pca being destroyed by GC, as it is used on the µc.
    self.addCommand(f"{self.getObject()} = PCA9685Channel({pca.getObject()}, {channel})")

  def deinit(self):
    self.addCommand(f"{self.getObject()}.deinit()")


  async def getNSAwait(self,):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_ns()"))
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")

  def setNS(self, ns):
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")


  async def getU16Await(self, u16 = None):
    return int(await self.executeAwait_("",f"{self.getObject()}.duty_u16()"))
  
  def setU16(self, u16):
    self.addCommand(f"{self.getObject()}.duty_u16({u16})")
  

  async def getFreqAwait(self):
    return int(await self.executeAwait_("",f"{self.getObject()}.freq()"))
  
  def setFreq(self, freq):
    self.addCommand(f"{self.getObject()}.freq({freq})")
  


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


  def test_(self, pwm, specs, tweak, domain):
    if tweak:
      if not specs:
        raise Exception("'tweak' can not be defined without 'specs'!")

    if domain:
      if not specs:
        raise Exception("'domain' can not be defined without 'specs'!")


  def __init__(self, pwm = None, specs = None, /, *, tweak = None, domain = None, device = None):
    super().__init__(device, "Servo")

    self.test_(pwm, specs, tweak, domain)

    if pwm:
      self.init(pwm, specs, tweak = tweak, domain = domain)


  def init(self, pwm, specs, tweak = None, domain = None):
    super().init()

    self.test_(pwm, specs, tweak, domain)

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
