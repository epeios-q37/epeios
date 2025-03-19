import zlib, base64

ITEMS_ = "i_"

# Keys
K_DEVICE = "Device"
K_DEVICE_TOKEN = "Token"
K_DEVICE_ID = "Id"

ONE_DEVICE_VTOKEN = "%ONE_DEVICE_VTOKEN%"
ALL_DEVICES_VTOKEN = "%ALL_DEVICES_VTOKEN%"

uuid_ = 0
device_ = None

unpak_ = lambda data : zlib.decompress(base64.b64decode(data)).decode()

def GetUUID_():
  global uuid_

  uuid_ += 1

  return uuid_


def displayMissingConfigMessage_():
  displayExitMessage_("Please launch the 'Config' app first to set the device to use!")


def handlingConfig_(token, id):
  if not CONFIG_:
    displayMissingConfigMessage_()

  if K_DEVICE not in CONFIG_:
    displayMissingConfigMessage_()

  device = CONFIG_[K_DEVICE]

  if not token:
    if K_DEVICE_TOKEN not in device:
      displayMissingConfigMessage_()

    token = device[K_DEVICE_TOKEN]

  if not id:
    if K_DEVICE_ID not in device:
      displayMissingConfigMessage_()

    id = device[K_DEVICE_ID]

  return token, id


def setDevice(id = None, *, device = None, token = None):
  if device != None:
    global device_
    if id or token:
      raise Exception("'device' can not be given together with 'id' or 'token'!")
    device_ = device
  else:    
    getDevice_(id = id, token = token)


# Infos keys and subkeys
IK_DEVICE_ID_ = "DeviceId"
IK_DEVICE_UNAME_ = "uname"
IK_HARDWARE = "Hardware"
IK_KIT_LABEL = "KitLabel"

# Kits keys
IK_BRAND_ = "brand"
IK_MODEL_ = "model"
IK_VARIANT_ = "variant"


INFO_SCRIPT_ = f"""
def ucuqStructToDict(obj):
    return {{attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__')}}

def ucuqGetInfos():
  return {{
    "{IK_DEVICE_ID_}": getIdentificationId_(IDENTIFICATION_),
    "{IK_DEVICE_UNAME_}": ucuqStructToDict(uos.uname())
  }}
"""

ATK_BODY_ = """
<style>
  .ucuq {
    max-height: 200px;
    overflow: hidden;
    opacity: 1;
    animation: ucuqFadeOut 2s forwards;
   }

  @keyframes ucuqFadeOut {
    0% {
      max-height: 200px;
     }
    100% {
      max-height: 0;
     }
   }
</style>
<div style="display: flex; justify-content: center;" class="ucuq">
  <h3>'BRACES' (<em>BRACES</em>)</h3>
</div>
<div id="ucuq_body">
</div>
""".replace("{", "{{").replace("}", "}}").replace("BRACES", "{}")


CB_AUTO = 0
CB_MANUAL = 1

defaultCommitBehavior_ = CB_AUTO

def testCommit_(behavior = None):
  if behavior == None:
    behavior = defaultCommitBehavior_

  return behavior == CB_AUTO

class Device(Device_):
  def __init__(self, *, id = None, token = None, callback = None):
    self.pendingModules_ = ["Init-1"]
    self.handledModules_ = []
    self.commands_ = []
    self.commitBehavior = None

    super().__init__(id=id, token = token, callback = callback)
  
  def __del__(self):
    self.commit()

  def testCommit_(self):
    return testCommit_(self.commitBehavior)

  def addModule(self, module):
    if not module in self.pendingModules_ and not module in self.handledModules_:
      self.pendingModules_.append(module)

  def addModules(self, modules):
    if isinstance( modules, str):
      self.addModule(modules)
    else:
      for module in modules:
        self.addModule(module)

  def addCommand(self, command, commit = False):
    self.commands_.append(command)

    if commit or self.testCommit_():
      self.commit()

    return self

  def sleep(self, secs):
    self.addCommand(f"time.sleep({secs})")


async def getBaseInfosAwait_(device = None):
  device = getDevice_(device)

  device.addCommand(INFO_SCRIPT_, False)

  return await device.commitAwait("ucuqGetInfos()")


def getKitFromDeviceId_(deviceId):
  for kit in KITS_:
    if deviceId in kit["devices"]:
      return kit
  else:
    return None
  

def getKitLabelFormDeviceId_(deviceId):
  kit = getKitFromDeviceId_(deviceId)

  if kit:
    return f"{kit[IK_BRAND_]}/{kit[IK_MODEL_]}/{kit[IK_VARIANT_]}"
  else:
    return "Undefined"  
  

def getKitFromLabel_(label):
  brand, model, variant = label.split('/')

  for kit in KITS_:
    if kit["brand"] == brand and kit["model"] == model and kit["variant"] == variant:
      return kit
  else:
    return None
  

def getKit_(infosOrLabel):
  if type(infosOrLabel) != str:
    infosOrLabel = getKitLabel(infosOrLabel)

  return getKitFromLabel_(infosOrLabel)


def getKitLabel(infos):
  return infos[IK_KIT_LABEL]
  

def getKitHardware(infosOrLabel):
  kit = getKit_(infosOrLabel)

  if kit:
    return kit["hardware"]
  else:
    return "Undefined"
  

getHardware_ = lambda hardware, key, index: hardware[key][index] if key in hardware and index < len(hardware[key]) else None


def getHardware(hardware, stringOrList, index = 0):
  if type(stringOrList) == str:
    return getHardware_(hardware, stringOrList, index)
  else:
    for key in stringOrList:
      if result := getHardware_(hardware, key, index):
        return result

  return None      
  

def getDeviceId(infos):
  return infos[IK_DEVICE_ID_]


async def getInfosAwait(device):
  infos = await getBaseInfosAwait_(device)

  infos[IK_KIT_LABEL] = getKitLabelFormDeviceId_(getDeviceId(infos))
  infos[IK_HARDWARE] = getKitHardware(infos)

  return infos


async def ATKConnectAwait(dom, body, *, device = None):
  if not KITS_:
    raise Exception("No kits defined!")

  await dom.inner("", "<h3>Connecting…</h3>")
  
  if device or CONFIG_:
    device = getDevice_(device)
  else:
    device = await getDemoDeviceAwait()

  if not device:
    await dom.inner("", "<h3>ERROR: Please launch the 'Config' application!</h3>")
    raise SystemExit("Unable to connect to a device!")
  
  setDevice(device = device)
  infos = await getInfosAwait(device)

  deviceId =  getDeviceId(infos)

  await dom.inner("", ATK_BODY_.format(getKitLabelFormDeviceId_(deviceId), deviceId))

  await dom.inner("ucuq_body", body)

  await sleepAwait(0.5)

  await sleepAwait(1.5)

  return infos


def getDevice_(device = None, *, id = None, token = None):
  if device and ( token or id ):
    displayExitMessage_("'device' can not be given together with 'token' or 'id'!")

  if device == None:
    global device_

    if token or id:
      device_ = Device(id = id, token = token)
    elif device_ == None:
      device_ = Device()
      device_.connect()
    return device_
  else:
    return device


def getDevice():
  return device_


def addCommand(command, /,device = None):
  getDevice_(device).addCommand(command)


# does absolutely nothing whichever method is called.
# 'if Nothing()' returns 'False'.
class Nothing:
  def __getattr__(self, name):
    def doNothing(*args, **kwargs):
      return self
    return doNothing
  
  def __bool__(self):
    return False


class Core_:
  def __init__(self, device = None):
    self.id = None
    self.device_ = device
  
  def __del__(self):
    if self.id:
      self.addCommand(f"del {ITEMS_}[{self.id}]")

  def getDevice(self):
    return self.device_
  
  def getId(self):
    return self.id
  
  def init(self, modules, instanciation, device,*,before=""):
    self.id = GetUUID_()

    if self.device_:
        if device and device != self.device_:
          raise Exception("'device' already given!")
    else:
      self.device_ = getDevice_(device)

    if modules:
      self.device_.addModules(modules)

    if before:
      self.addCommand(before)

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
    super().__init__(device)

    if pin:
      self.init(pin, device)

  def init(self, pin, device = None):
    self.pin = f'"{pin}"' if isinstance(pin,str) else pin

    super().init("GPIO-1", f"GPIO({self.pin})", device)


  def high(self, value = True):
    self.addMethods(f"high({value})")


  def low(self):
    self.high(False)


class WS2812(Core_):
  def __init__(self, pin = None, n = None, device = None):
    super().__init__(device)

    if (pin == None) != (n == None):
      raise Exception("Both or none of 'pin'/'n' must be given")

    if pin != None:
      self.init(pin, n)

  def init(self, pin, n, device = None):
    super().init("WS2812-1", f"neopixel.NeoPixel(machine.Pin({pin}), {n})", device)

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
    return self
  

class I2C_Core_(Core_):
  def __init__(self, sda = None, scl = None, *, device = None, soft = None):
    super().__init__(device)

    if sda == None != scl == None:
      raise Exception("None or both of sda/scl must be given!")
    elif sda != None:
      self.init(sda, scl, device = device, soft = soft)

  async def scanAwait(self):
    return (await commitAwait(f"{self.getObject()}.scan()"))


class I2C(I2C_Core_):
  def init(self, sda, scl, *, device = None, soft = False):
    if soft == None:
      soft = False

    super().init("I2C-1", f"machine.{'Soft' if soft else ''}I2C({'0,' if not soft else ''} sda=machine.Pin({sda}), scl=machine.Pin({scl}))", device = device)


class SoftI2C(I2C):
  def init(self, sda, scl, *, device = None, soft = True):
    if soft == None:
      soft = True

    super().init(sda, scl, device = device, soft = soft)


class HT16K33(Core_):
  def __init__(self, i2c = None, /, addr = None):
    super().__init__()

    if i2c:
      self.init(i2c)

  def init(self, i2c, addr = None):
    super().init("HT16K33-1", f"HT16K33({i2c.getObject()}, {addr})", i2c.getDevice())

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
  
  def rect(self, x0, y0, x1, y1, ink = True):
    return self.addMethods(f"rect({x0}, {y0}, {x1}, {y1}, ink={1 if ink else 0})")  


  def show(self):
    return self.addMethods(f"render()")


def getParam(label, value):
  if value:
    return f", {label} = {value}"
  else:
    return ""


class PWM(Core_):
  def __init__(self, pin = None, *, freq = None, ns = None, u16 = None, device = None):
    super().__init__(device)

    if pin != None:
      self.init(pin, freq = freq, u16 = u16, ns = ns, device = device)


  def init(self, pin, *, freq = None, u16 = None, ns = None, device = None):
    command = f"machine.PWM(machine.Pin({pin}, machine.Pin.OUT){getParam('freq', freq)}{getParam('duty_u16', u16)}{getParam('duty_ns', ns)})"
    super().init("PWM-1", command, device, before=f"{command}.deinit()")


  async def getU16Await(self):
    return int(await self.callMethodAwait("duty_u16()"))


  def setU16(self, u16):
    return self.addMethods(f"duty_u16({u16})")


  async def getNSAwait(self):
    return int(await self.callMethodAwait("duty_ns()"))


  def setNS(self, ns):
    return self.addMethods(f"duty_ns({ns})")


  async def getFreqAwait(self):
    return int(await self.callMethodAwait("freq()"))


  def setFreq(self, freq):
    return self.addMethods(f"freq({freq})")


  def deinit(self):
    return self.addMethods(f"deinit()")


class PCA9685(Core_):
  def __init__(self, i2c = None, *, addr = None):
    super().__init__()

    if i2c:
      self.init(i2c, addr = addr)

  def init(self, i2c, addr = None):
    super().init("PCA9685-1", f"PCA9685({i2c.getObject()}, {addr})", i2c.getDevice())

  def deinit(self):
    self.addMethods(f"reset()")

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))

  async def getOffsetAwait(self):
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
  def __init__(self, pca = None, channel = None):
    super().__init__()

    if bool(pca) != (channel != None):
      raise Exception("Both or none of 'pca' and 'channel' must be given!")
    
    if pca:
      self.init(pca, channel)

  def init(self, pca, channel):
    super().init("PWM_PCA9685-1", f"PWM_PCA9685({pca.getObject()}, {channel})", pca.getDevice())

    self.pca = pca # Not used inside this object, but to avoid pca being destroyed by GC, as it is used on the µc.

  def deinit(self):
    self.addMethods(f"deinit()")

  async def getOffsetAwait(self):
    return self.pca.getOffsetAwait()

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
  

class HD44780_I2C(Core_):
  def __init__(self, i2c, num_lines, num_columns,/,addr = None):
    super().__init__()

    if i2c:
      self.init(i2c, num_lines, num_columns, addr = addr)
    elif addr != None:
      raise Exception("addr can not be given without i2c!")

  def init(self, i2c, num_lines, num_columns, addr = None):
    return super().init("HD44780_I2C-1", f"HD44780_I2C({i2c.getObject()},{num_lines},{num_columns},{addr})", i2c.getDevice())

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


  def __init__(self, pwm = None, specs = None, /, *, tweak = None, domain = None):
    super().__init__()

    self.test_(specs, tweak, domain)

    if pwm:
      self.init(pwm, specs, tweak = tweak, domain = domain)


  def init(self, pwm, specs, tweak = None, domain = None):
    super().init("Servo-1", "", pwm.getDevice())

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

  def pixel(self, x, y, col = 1):
    return self.addMethods(f"pixel({x},{y},{col})")

  def scroll(self, dx, dy):
    return self.addMethods(f"scroll({dx},{dy})")

  def text(self, string, x, y, col=1):
    return self.addMethods(f"text('{string}',{x}, {y}, {col})")
  
  def rect(self, x, y, w, h, col, fill=True):
    return self.addMethods(f"rect({x},{y},{w},{h},{col},{fill})")

  def draw(self, pattern, width, ox = 0, oy = 0, mul = 1):
    if width % 4:
      raise Exception("'width' must be a multiple of 4!")
    return self.addMethods(f"draw('{pattern}',{width},{ox},{oy},{mul})")


class SSD1306_I2C(SSD1306):
  def __init__(self, width = None, height = None, i2c = None, /, addr = None, external_vcc = False):
    super().__init__()

    if bool(width) != bool(height) != bool(i2c):
      raise Exception("All or none of width/height/i2c must be given!")
    elif width:
      self.init(width, height, i2c, external_vcc = external_vcc, addr= addr)
    elif addr:
      raise Exception("addr can not be given without i2c!")
      
  def init(self, width, height, i2c, /, external_vcc = False, addr = None):
    super().init(("SSD1306-1", "SSD1306_I2C-1"), f"SSD1306_I2C({width}, {height}, {i2c.getObject()}, {addr}, {external_vcc})", i2c.getDevice())


def pwmJumps(jumps, step = 100, delay = 0.05):
  command = "pwmJumps([\n"

  for jump in jumps:
    command += f"\t[{jump[0].getObject()},{jump[1]}],\n"

  command += f"], {step}, {delay})"

  return command


def execute_(command, device):
    device.addModule("PWMJumps-1")
    device.addCommand(command)


def servoMoves(moves, step = 100, delay = 0.05):
  jumps = {}
  devices = {}
  commands = {}
  
  for move in moves:
    servo = move[0]
    key = id(servo.getDevice())

    if not key in devices:
      devices[key] = servo.getDevice()
      jumps[key] = []
      commands[key] = []

    jumps[key].append([servo.pwm, servo.angleToDuty(move[1])])

  for key in jumps:
    commands[key].append(pwmJumps(jumps[key], step, delay))

  for key in commands:
    for command in commands[key]:
      execute_(command, devices[key])

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
    
def setCommitBehavior(behavior):
  global defaultCommitBehavior_

  defaultCommitBehavior_ = behavior
  