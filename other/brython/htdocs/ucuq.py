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


class Lock:
  def __init__(self):
    self.locked_ = False

  async def acquire(self):
    while self.locked_:
      await aio.sleep(0)
    self.locked_ = True

  def release(self):
    self.locked_ = False


def launch_(deviceId, callback):
  if not CONFIG_ITEM in storage:
    alert("Please launch the 'Config' app first to set the device to use!")
    console.error = javascript.UNDEFINED  # To avoid the displaying of an alert by below 'exit()'.
    sys.exit()

  config = json.loads(storage[CONFIG_ITEM])

  device = config["Device"]

  ucuqjs.launch(device["Token"], deviceId if deviceId != None else device["Id"], LIB_VERSION, callback)


def uploadCallback_(code, result):
  if code != 0:
    raise Exception(result)


def upload_(modules):
  ucuqjs.upload(modules, lambda code, result: uploadCallback_(code, result))


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


async def executeAwait_(script, expression):
  lock = Lock()

  await lock.acquire()

  data = {
    "lock": lock
  }

  ucuqjs.execute(script, expression, lambda code, result: executeCallback_(data, code, result))

  await lock.acquire()
  
  return data["result"]


def execute_(script):
  ucuqjs.execute(script, "", lambda code, result: executeCallback_(None, code, result))


async def launchSub_(function, lock):
  await lock.acquire()

  await function()


def launchCallback_(lock):
  lock.release()

# Does not handle an expression, otherwise it would need to be defined as 'async'.
def launch(function = None,*,deviceId=None):
  lock = Lock()

  if function:
    aio.run(lock.acquire())

  launch_(deviceId, lambda: launchCallback_(lock) if function else lambda: None)

  if function:
    aio.run(launchSub_(function, lock))


pendingModules = ["Init"]
handledModules = []
commands = []

def addModule(module):
  global pendingModules

  if not module in pendingModules and not module in handledModules:
    pendingModules.append(module)


def addCommand(command):
  global commands

  commands.append(command)


async def renderAwait(expression):
  global pendingModules, handledModules, commands

  result = ""

  if pendingModules:
    upload_(pendingModules)
    handledModules.extend(pendingModules)
    pendingModules = []

  result = await executeAwait_('\n'.join(commands) if commands else "", expression)
  commands = []

  return result

def render():
  global pendingModules, handledModules, commands

  if pendingModules:
    upload_(pendingModules)
    handledModules.extend(pendingModules)
    pendingModules = []

  if commands:
    execute_('\n'.join(commands))
  
  commands = []


def servoMoves( moves, speed = 1):
  addModule("ServoMoves")

  command = "servoMoves([\n"

  for move in moves:
    servo = move[0]

    step = speed * (servo.specs.max - servo.specs.min) / servo.specs.range

    command += f"\t[{move[0].pwm.getObject()},{move[0].angleToDuty(move[1])}],\n"

  command += f"], {int(step)})"

  addCommand(command)


class Core_:
  def __init__(self, module = ""):
    if module:
      addModule(module)
    self.id = None

  
  def __del__(self):
    if self.id:
      self.addCommand(f"del {ITEMS_}[{self.id}]")

  
  def init(self):
    self.id = GetUUID_()

  
  async def execute(self, script, expr = ""):
    return await execute(script, expr)
    
    
  def getObject(self):
    return f"{ITEMS_}[{self.id}]"
  
  
  def addCommand(self, command):
    addCommand(command)
                         
                         
  def render(self):
    render()
  

class GPIO(Core_):
  def __init__(self, pin = None):
    super().__init__("GPIO")

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
  def __init__(self, pin = None, n = None):
    super().__init__("WS2812")

    if (pin == None) != (n == None):
      raise Exception("Both or none of 'pin'/'n' must be defined")

    if pin != None:
      self.init(pin, n)

  def init(self, pin, n):
    super().init()

    self.addCommand(f"{self.getObject()} = neopixel.NeoPixel(machine.Pin({pin}), {n})")


  async def lenAwait(self):
    return int(await executeAwait_("", f"{self.getObject()}.__len__()"))
               

  def value(self, index, val):
    addCommand(f"{self.getObject()}.setitem({index}, {json.dumps(val)})")

    return self
                       
  async def valueAwait(self, index):
    return await executeAwait_("", f"{self.getObject()}.__getitem__({index})")
                       
  def fill(self, val):
    self.addCommand(f"{self.getObject()}.fill({json.dumps(val)})")
    return self

  def write(self):
    self.addCommand(f"{self.getObject()}.write()")
    self.render()
    

class HT16K33(Core_):
  def __init__(self, sda = None, scl = None):
    super().__init__("HT16K33")

    if bool(sda) != bool(scl):
      raise Exception("None or both of sda/scl must be defined!")
    elif sda:
      self.init(sda, scl)


  def init(self, sda, scl):
    super().init()

    addCommand(f"{self.getObject()} = HT16K33(machine.I2C(0, sda=machine.Pin({sda}), scl=machine.Pin({scl})))")
    addCommand(f"{self.getObject()}.set_brightness(0)")


  def setBlinkRate(self, rate):
    execute_(f"{self.getObject()}.set_blink_rate({rate})")

  def setBrightness(self, brightness):
    execute_(f"{self.getObject()}.set_brightness({brightness})")

  def clear(self):
    addCommand(f"{self.getObject()}.clear()")
    self.render()

  def plot(self, x, y):
    addCommand(f"{self.getObject()}.plot({x},{y})")

  def draw(self, motif):
    addCommand(f"{self.getObject()}.clear().draw('{motif}').render()")
    self.render()

  def render(self):
    addCommand(f"{self.getObject()}.render()")
    super().render()


class PWM(Core_):
  def __init__(self, pin = None, freq = None):
    super().__init__("PWM")

    if freq != None:
      if pin == None:
        raise Exception("'freq' cannot be defined without 'pin'!")
      
    if pin != None:
      self.init(pin, freq)


  def init(self, pin, freq = None):
    super().init()

    addCommand(f"{self.getObject()} = machine.PWM(machine.Pin({pin}),freq={freq if freq else 50})")


  async def dutyU16Await(self):
    return int(await executeAwait_("", f"{self.getObject()}.duty_u16()"))


  def dutyU16(self, u16):
    addCommand(f"{self.getObject()}.duty_u16({u16})")


  async def dutyNSAwait(self):
    return int(await executeAwait_("", f"{self.getObject()}.duty_ns()"))


  def dutyNS(self, ns):
    addCommand(f"{self.getObject()}.duty_ns({ns})")


  async def freqAwait(self):
    return int(await executeAwait_("", f"{self.getObject()}.freq()"))


  def freq(self, freq):
    addCommand(f"{self.getObject()}.freq({freq})")


  def deinit(self):
    addCommand(f"{self.getObject()}.deinit()")


class PCA9685(Core_):
  def __init__(self, sda = None, scl = None, freq = None, addr = None):
    super().__init__("PCA9685")

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

    addCommand(f"{self.getObject()} = PCA9685({sda}, {scl}, {addr if addr else 0x40})")
    self.freq(freq if freq else 50)


  def deinit(self):
    addCommand(f"{self.getObject()}.reset()")
                    

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))

  async def freqAwait(self):
    return await executeAwait_("", f"{self.getObject()}.freq()")

  def freq(self, freq):
    return addCommand(f"{self.getObject()}.freq({freq})")
  

class PCA9685Channel(Core_):
  def __init__(self, pca = None, channel = None, /):
    super().__init__("PCA9685Channel")

    if bool(pca) != (channel != None):
      raise Exception("Both or none of 'pca' and 'channel' must be defined!")
    
    if pca:
      self.init(pca, channel)


  def init(self, pca, channel):
    super().init()

    self.pca = pca # Not used inside this object, but to avoid pca being destroyed by GC, as it is used on the µc.
    addCommand(f"{self.getObject()} = PCA9685Channel({pca.getObject()}, {channel})")

  def deinit(self):
    addCommand(f"{self.getObject()}.deinit()")


  async def dutyNSAwait(self,):
    return int(await executeAwait_("", f"{self.getObject()}.duty_ns()"))
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")

  def dutyNS(self, ns):
    self.addCommand(f"{self.getObject()}.duty_ns({ns})")


  async def dutyU16Await(self, u16 = None):
    return int(await executeAwait_("",f"{self.getObject()}.duty_u16()"))
  
  def dutyU16(self, u16):
    addCommand(f"{self.getObject()}.duty_u16({u16})")
  

  async def freq(self):
    return int(await executeAwait_("",f"{self.getObject()}.freq()"))
  
  def freq(self, freq):
    addCommand(f"{self.getObject()}.freq({freq})")
  


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


  def __init__(self, pwm = None, specs = None, /, *, tweak = None, domain = None):
    super().__init__("Servo")

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







