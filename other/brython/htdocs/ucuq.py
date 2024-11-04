import javascript, json, sys
from browser import aio, alert, console
from browser.local_storage import storage

javascript.import_js("ucuq.js", "ucuqjs")

LIB_VERSION = "0.0.1"

CONFIG_ITEM = "ucuq-config"

ITEMS_ = "i_"

uuid_ = 0

async def sleepAwait(time):
  await ucuqjs.sleep(time, lambda : None)

def GetUUID_():
  global uuid_

  uuid_ += 1

  return uuid_


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

class Device:
  def connect_(self, deviceId, callback):
    if not CONFIG_ITEM in storage:
      alert("Please launch the 'Config' app first to set the device to use!")
      console.error = javascript.UNDEFINED  # To avoid the displaying of an alert by below 'exit()'.
      sys.exit()

    self.pendingModules_ = ["Init"]
    self.handledModules_ = []
    self.commands_ = []

    config = json.loads(storage[CONFIG_ITEM])

    device = config["Device"]

    self.device_ = ucuqjs.launch(device["Token"], deviceId if deviceId != None else device["Id"], LIB_VERSION, callback)

  def __init__(self):
    self.launch()


  def upload_(self, modules):
    print("Device: ", self.device_)
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


  async def launchSub_(function, lock):
    await lock.acquire()

    await function()


  # Does not handle an expression, otherwise it would need to be defined as 'async'.
  def launch(self, function = None,*,deviceId=None):
    lock = Lock_()

    if function:
      aio.run(lock.acquire())

    self.connect_(deviceId, lambda: launchCallback_(lock) if function else lambda: None)

    if function:
      aio.run(self.launchSub_(function, lock))


  def addModule(self, module):
    if not module in self.pendingModules_ and not module in self.handledModules_:
      self.pendingModules_.append(module)


  def addCommand(self, command):
    self.commands_.append(command)


  async def renderAwait(self, expression):
    result = ""

    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.self.extend(self.pendingModules_)
      self.pendingModules_ = []

    result = await self.executeAwait_('\n'.join(commands) if commands else "", expression)
    commands = []

    return result

  def render(self):
    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.extend(self.pendingModules_)
      self.pendingModules_ = []

    if self.commands_:
      self.execute_('\n'.join(self.commands_))
    
    self.commands_ = []


  def servoMoves(self, moves, speed = 1):
    self.addModule("ServoMoves")

    command = "servoMoves([\n"

    for move in moves:
      servo = move[0]

      step = speed * (servo.specs.max - servo.specs.min) / servo.specs.range

      command += f"\t[{move[0].pwm.getObject()},{move[0].angleToDuty(move[1])}],\n"

    command += f"], {int(step)})"

    self.addCommand(command)


class Core_:
  def __init__(self, device, module = ""):
    self.id = None
    self.device_ = device

    if module:
      self.device_.addModule(module)

  
  def __del__(self):
    if self.id:
      self.addCommand(f"del {ITEMS_}[{self.id}]")

  
  def init(self):
    self.id = GetUUID_()

  
  async def execute(self, script, expr = ""):
    return await self.device_.execute(script, expr)
    
    
  def getObject(self):
    return f"{ITEMS_}[{self.id}]"
  
  
  def addCommand(self, command):
    self.device_.addCommand(command)
                         
                         
  def render(self):
    self.render()
  

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
               

  def value(self, index, val):
    self.addCommand(f"{self.getObject()}.setitem({index}, {json.dumps(val)})")

    return self
                       
  async def valueAwait(self, index):
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
    self.execute_(f"{self.getObject()}.set_blink_rate({rate})")

  def setBrightness(self, brightness):
    self.execute_(f"{self.getObject()}.set_brightness({brightness})")

  def clear(self):
    self.addCommand(f"{self.getObject()}.clear()")
    self.render()

  def plot(self, x, y):
    self.addCommand(f"{self.getObject()}.plot({x},{y})")
    return self

  def draw(self, motif):
    self.addCommand(f"{self.getObject()}.clear().draw('{motif}').render()")
    self.render()

  def plot(self, x, y, ink=True):
    self.addCommand(f"{self.getObject()}.plot({x}, {y}, ink={1 if ink else 0})")  
    return self


  def render(self):
    self.addCommand(f"{self.getObject()}.render()")
    super().render()


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


  async def dutyU16Await(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_u16()"))


  def dutyU16(self, u16):
    self.addCommand(f"{self.getObject()}.duty_u16({u16})")


  async def dutyNSAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_ns()"))


  def dutyNS(self, ns):
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")


  async def freqAwait(self):
    return int(await self.executeAwait_("", f"{self.getObject()}.freq()"))


  def freq(self, freq):
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
    self.freq(freq if freq else 50)


  def deinit(self):
    self.addCommand(f"{self.getObject()}.reset()")
                    

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))

  async def freqAwait(self):
    return await self.executeAwait_("", f"{self.getObject()}.freq()")

  def freq(self, freq):
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


  async def dutyNSAwait(self,):
    return int(await self.executeAwait_("", f"{self.getObject()}.duty_ns()"))
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")

  def dutyNS(self, ns):
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")


  async def dutyU16Await(self, u16 = None):
    return int(await self.executeAwait_("",f"{self.getObject()}.duty_u16()"))
  
  def dutyU16(self, u16):
    self.addCommand(f"{self.getObject()}.duty_u16({u16})")
  

  async def freq(self):
    return int(await self.executeAwait_("",f"{self.getObject()}.freq()"))
  
  def freq(self, freq):
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
    self.angle(0)


  async def angleAwait(self):
    return self.dutyToAngle(await self.pwm.dutyU16Await())

  def angle(self, angle):
    return self.pwm.dutyU16(self.angleToDuty(angle))







