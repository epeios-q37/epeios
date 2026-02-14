import zlib, base64, atlastk, re, copy, time

ITEMS_ = "i_"

# Keys
K_DEVICE = "Device"
K_DEVICE_TOKEN = "Token"
K_DEVICE_ID = "Id"

DEMO_VTOKEN = "%DEMO_VTOKEN%"

FLASH_DELAY_ = 0

objectCounter_ = 0
device_ = None

unpack_ = lambda data: zlib.decompress(base64.b64decode(data)).decode()


def getObjectIndice():
  global objectCounter_

  objectCounter_ += 1

  return objectCounter_


def getObject_(id):
  return f"{ITEMS_}[{id}]"


def displayMissingConfigMessage_():
  displayExitMessage_(
    "Please launch the 'Config' app first to set the device to use!"
  )


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


def getConfigToken_():
  try:
    return CONFIG_[K_DEVICE][K_DEVICE_TOKEN]
  except:
    return ""


def setDevice(id=None, *, device=None, token=None):
  if device != None:
    global device_
    if id or token:
      raise Exception("'device' can not be given together with 'id' or 'token'!")
    device_ = device
  else:
    getDevice(id=id, token=token)


# Infos keys and subkeys
IK_DEVICE_ID_ = "DeviceId"
IK_DEVICE_UNAME_ = "uname"
IK_HARDWARE = "Hardware"
IK_FEATURES = "Features"
IK_KIT_LABEL = "KitLabel"

# Kits keys
IK_BRAND_ = "brand"
IK_MODEL_ = "model"
IK_VARIANT_ = "variant"


INFO_SCRIPT_ = f"""
def ucuqStructToDict(obj):
  return {{attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__')}}

def ucuqGetInfos():
  infos = {{
  "{IK_DEVICE_ID_}": ucuq.settings.getDeviceId(),
  "{IK_DEVICE_UNAME_}": ucuqStructToDict(__import__('uos').uname())
  }}

  if kit := ucuq.settings.getKitLabel():
    infos["{IK_KIT_LABEL}"] = kit

  return infos
"""

ATK_BODY_ = (
  """
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
<div id="ucuq_body" style_="display: flex; justify-content: center;">
</div>
""".replace(
    "{", "{{"
  )
  .replace("}", "}}")
  .replace("BRACES", "{}")
)


ATK_XDEVICE_ = """
<dialog id="ucuq_xdevice" style="width: min-content;">
  <fieldset>
    <legend>Device</legend>
    <label style="display: flex; justify-content: space-between; margin: 5px;">
      <span>Token:&nbsp;</span>
      <input id="ucuq_xdevice_token">
    </label>
    <label style="display: flex; justify-content: space-between; margin: 5px;">
      <span>Id:&nbsp;</span>
      <input id="ucuq_xdevice_id">
    </label>
  </fieldset>
  <div style="display: flex; justify-content: space-around; margin: 5px;">
    <button xdh:onevent="ucuq_xdevice_ok"/>{}</button>
    <button xdh:onevent="ucuq_xdevice_cancel">{}</button>
  </div>
  <fieldset>{}</fieldset>
</dialog>
"""

UCUQ_XDEVICE_ACTION_ = "UCUqXDevice"


async def handleXDevice_(dom, response):
  await dom.executeVoid("document.getElementById('ucuq_xdevice').close();")

  if response:
    await atlastk.getUserGlobals()["UCUqXDevice"](
      dom,
      Device(
        id=await dom.getValue("ucuq_xdevice_id"),
        token=await dom.getValue("ucuq_xdevice_token"),
      ),
    )

  await dom.executeVoid("element = document.getElementById('ucuq_xdevice').remove();")


def getDOM_(dom1, dom2):
  if isinstance(dom1, atlastk.DOM):
    return dom1
  else:
    return dom2


UCUQ_XDEVICE_I10N = (
  ("OK", "Cancel", "Click on ‘Cancel’ unless you know exactly what you're doing!"),
  (
    "OK",
    "Annuler",
    "Cliquez sur 'Annuler' à moins que vous ne sachiez exactement ce que vous faites !",
  ),
)


async def handleXDeviceRetrieving_(dom1, dom2):
  dom = getDOM_(dom1, dom2)

  language = dom.language

  i10n = UCUQ_XDEVICE_I10N[
    1 if (language[:2].upper() if len(language) >= 2 else "") == "FR" else 0
  ]

  await dom.end("", ATK_XDEVICE_.format(*i10n))

  atlastk.setCallback("ucuq_xdevice_ok", handleXDeviceOK_)
  atlastk.setCallback("ucuq_xdevice_cancel", handleXDeviceCancel_)

  await dom.executeVoid(f"document.getElementById('ucuq_xdevice').showModal();")


async def handleXDeviceOK_(dom1, dom2):
  await handleXDevice_(getDOM_(dom1, dom2), True)


async def handleXDeviceCancel_(dom1, dom2):
  await handleXDevice_(getDOM_(dom1, dom2), False)


CB_AUTO = 0
CB_MANUAL = 1

defaultCommitBehavior_ = CB_AUTO


def testCommit_(commit, behavior=None):
  if commit == None:
    if behavior == None:
      behavior = defaultCommitBehavior_

    return behavior == CB_AUTO
  else:
    return commit


def sleepStart():
  return getDevice().sleepStart()


def sleepWait(secs):
  return getDevice().sleepWait(secs)


def sleep(secs):
  return getDevice().sleep(secs)


patchKeys_ = lambda keys: keys if keys else []

B_LCD = "LCD"
B_OLED = "OLED"
B_BUZZER = "Buzzer"
B_LOUDSPEAKER = "Loudspeaker"
B_SMART_RGB = "SmartRGB"
B_MATRIX = "Matrix"
B_TFT = "TFT"


class Auto:
  def __new__(cls, bit, infos, item, hardwareKeys, featuresKeys, **kwargs):
    hardware = getKitHardware_(infos)
    features = getKitFeatures_(infos)

    if not hasHardware_(hardware, item) and not hasFeatures_(features, item):
      return Nothing()

    hardwareKeys = patchKeys_(hardwareKeys)
    featuresKeys = patchKeys_(featuresKeys)

    return bit(
      *getDescItems_(features, item, featuresKeys),
      *getDescItems_(hardware, item, hardwareKeys),
      **kwargs,
    )


def getBits(infos, *bitLabels, device=None):
  bits = [getDevice(device)]

  for label in bitLabels:
    match label:
      case "LCD":
        bits.append(
          Auto(
            HD44780_I2C,
            infos,
            label,
            None,
            ["Width", "Height"],
            i2c=Auto(
              I2C,
              infos,
              label,
              ["SDA", "SCL", "Soft"],
              None,
              device=device,
            ),
          )
        )
      case "OLED":
        bits.append(
          Auto(
            OLED_I2C,
            infos,
            label,
            None,
            ["Driver", "Width", "Height"],
            i2c=Auto(
              I2C,
              infos,
              label,
              ["SDA", "SCL", "Soft"],
              None,
              device=device,
            ),
          )
        )
      case "Buzzer" | "Loudspeaker":
        bits.append(Auto(PWM, infos, label, ["Pin"], None, device=device))
      case "SmartRGB":
        bits.append(
          Auto(WS2812, infos, label, ["Pin"], ["Count"], device=device)
        )
      case "Matrix":
        bits.append(
          Auto(
            HT16K33,
            infos,
            label,
            None,
            None,
            i2c=Auto(
              I2C,
              infos,
              "Matrix",
              ["SDA", "SCL", "Soft"],
              None,
              device=device,
            ),
          )
        )
      case "TFT":
        bits.append(
          Auto(
            ILI9341,
            infos,
            label,
            ["DC", "CS", "RST"],
            ["Width", "Height", "Rotation"],
            spi=Auto(
              SPI,
              infos,
              label,
              ["Id", "SCK", "MOSI", "MISO", "Baudrate"],
              None,
              device=device,
            ),
          )
        )
      case _:
        raise Exception(f"Unknown bit label: {label}")

  return bits


class Multi:
  def __init__(self, object = None):
    self.objects_ = []

    if object is not None:
      self.add(object)

  def add(self, object):
    self.objects_.append(object)
    
  def __len__(self):
    return len(self.objects_)

  def __getattr__(self, methodName):
    def wrapper(*args, **kwargs):
      for object in self.objects_:
        if hasattr(object, "__getattr__"):
          object.__getattr__(methodName)(*args, **kwargs)
        else:
          getattr(object, methodName)(*args, **kwargs)
      return self

    return wrapper

  def __getitem__(self, index):
    if index < len(self.objects_):
      return self.objects_[index]
    else:
      raise IndexError("Index out of range for Multi object.")
    
  def index(self, object):
    return self.objects_.index(object)
    
  def getObjects(self):
    return self.objects_

  # Workaround for Brython (https://github.com/brython-dev/brython/issues/2590)
  def __bool__(self):
    return True


class Device(Device_):
  def __new__(cls, id=None, token=None, callback=None):
    if type(id) in (list, tuple):
      ids = id
      
      if type(token) not in (list, tuple):
        tokens = (token,) * len(ids)
        
      if len(tokens) != len(ids):
        raise Exception("'ids' and (tokens' must be of same amounr!)")
      
      multi = Multi()
      
      for i in range(len(ids)):
        multi.add(Device(id=ids[i], token=tokens[i], callback=callback))
        
      return multi
    else:
      return super().__new__(Device)
        
  def __init__(self, *, id=None, token=None, callback=None):  # If id == "", using id and token from config.
    self.pendingModules_ = ["Init-1"]
    self.handledModules_ = []
    self.commands_ = [
"""
def sleepWait(start, us):
  elapsed = time.ticks_us() - start
            
  if elapsed < us:
    time.sleep_us(int(us - elapsed))
""",
      NTP_SCRIPT_
    ]
    self.commitBehavior_ = None
    self.timer_ = None

    super().__init__(id=id, token=token, callback=callback)
    
    if id == "":
      self.connect(id=None, token=token)

  def __del__(self):
    try:
      self.commit()
    except:
      pass

  def testCommit_(self, commit):
    return testCommit_(commit, self.commitBehavior_)

  def addModule(self, module):
    if module not in self.pendingModules_ and module not in self.handledModules_:
      self.pendingModules_.append(module)

    return self

  def addModules(self, modules):
    if isinstance(modules, str):
      self.addModule(modules)
    else:
      for module in modules:
        self.addModule(module)

    return self

  def addCommand(self, command, commit=None):
    self.commands_.append(command)

    if self.testCommit_(commit):
      self.commit()

    return self

  def sleepStart(self):
    if self.timer_ is None:
      self.timer_ = getObjectIndice()

    self.addCommand(f"{getObject_(self.timer_)} = time.ticks_us()")

    return id

  def sleepWait(self, secs):
    if self.timer_ is None:
      raise Exception("'sleepWait' called before 'sleepStart'!")
      
    self.addCommand(f"sleepWait({getObject_(self.timer_)}, {secs * 1000000})")

  def sleep(self, secs):
    self.addCommand(f"time.sleep_us({int(secs * 1000000)})")
    
  def ntpSetTime(self):
    self.addCommand("ntp_set_time()")
    
  def ntpSleepUntil(self, timestamp):
    # self.addCommand(f"sleep_until_us({timestamp})")
    self.addCommand(f"time.sleep_us({timestamp} - precise_time_us())")
    
  def ntpSleep(self, delay):
    self.addCommand(f"time.sleep_us({delay})")
    
  async def ntpTimeAwait(self):
    return self.commitAwait("precise_time_us()")
    


async def getBaseInfosAwait_(device=None):
  device = getDevice(device)

  device.addCommand(INFO_SCRIPT_, False)

  return await device.commitAwait("ucuqGetInfos()")


def getKitFromDeviceId_(deviceId):
  for kit in KITS_:
    if "devices" in kit and deviceId in kit["devices"]:
      return kit
  else:
    return None


buildKitLabel_ = lambda brand, model, variant: f"{brand}/{model}/{variant}"


def getKitLabelFromDeviceId_(deviceId):
  kit = getKitFromDeviceId_(deviceId)

  if kit:
    return buildKitLabel_(kit[IK_BRAND_], kit[IK_MODEL_], kit[IK_VARIANT_])
  else:
    return "Undefined"


def getKitFromLabel_(label):
  brand, model, variant = label.split("/")

  for kit in KITS_:
    if (
      kit["brand"] == brand
      and kit["model"] == model
      and kit["variant"] == variant
    ):
      return kit
  else:
    return None


def getKitLabel(infos):
  return infos[IK_KIT_LABEL]


def getKit_(infosOrLabel):
  if type(infosOrLabel) != str:
    infosOrLabel = getKitLabel(infosOrLabel)

  return getKitFromLabel_(infosOrLabel)


def getKitDesc_(infosOrLabel, descLabel):
  kit = getKit_(infosOrLabel)

  if kit:
    return kit[descLabel]
  else:
    return "Undefined"


def getKitHardware_(infosOrLabel):
  return getKitDesc_(infosOrLabel, "hardware")


def getKitFeatures_(infosOrLabel):
  return getKitDesc_(infosOrLabel, "features")


subGetDescItems_ = lambda desc, key, index: (
  desc[key][index] if key in desc and index < len(desc[key]) else None
)


def getDescItems_(kitDesc, stringOrList, keys=None, *, index=0):
  if type(stringOrList) == str:
    items = subGetDescItems_(kitDesc, stringOrList, index)
  else:
    for key in stringOrList:
      if items := subGetDescItems_(kitDesc, key, index):
        break

  if items and (keys or keys == []):
    result = tuple(
      items[keys] if type(keys) == str else (items[key] for key in keys)
    )
  elif items:
    result = items
  else:
    result = ()

  return result


def hasHardware_(kitHardware, item):
  return bool(getDescItems_(kitHardware, item))


def hasFeatures_(kitFeatures, item):
  return bool(getDescItems_(kitFeatures, item))


def getFeatures(infosOrLabel, item, keys=None, *, index=0):
  kitFeatures = getKitFeatures_(infosOrLabel)

  if not kitFeatures:
    return ()

  return getDescItems_(kitFeatures, item, keys, index=index)


def getHardware(infosOrLabel, item, keys=None, *, index=0):
  kitHardware = getKitHardware_(infosOrLabel)

  if not kitHardware:
    return ()

  return getDescItems_(kitHardware, item, keys, index=index)


def getDeviceId(infos):
  return infos[IK_DEVICE_ID_]


async def getInfosAwait(device):
  infos = await getBaseInfosAwait_(device)

  if not IK_KIT_LABEL in infos:
    infos[IK_KIT_LABEL] = getKitLabelFromDeviceId_(getDeviceId(infos))
  infos[IK_HARDWARE] = getKitDesc_(infos, "hardware")
  infos[IK_FEATURES] = getKitDesc_(infos, "features")

  return infos


async def ATKConnectAwait(dom, body, *, target="", device=None):
  await getKitsAwait()

  if not KITS_:
    raise Exception("No kits defined!")

  await dom.inner(
    target,
    """
  <style>
  .ucuq-connection {
    display: inline-block;
    /* Pour éviter les retours à la ligne */
    white-space: nowrap;
    /* Pour que le texte ne déborde pas */
    overflow: hidden;
    /* Animation en continu */
    animation: ucuq-connection 1s linear infinite;
    /* Masque linéaire horizontal */
    -webkit-mask-image: linear-gradient(to right, transparent 0%, black 50%, transparent 100%);
    mask-image: linear-gradient(to right, transparent 0%, black 50%, transparent 100%);
    -webkit-mask-size: 200% 100%;
    mask-size: 200% 100%;
    -webkit-mask-position: 0% 0%;
    mask-position: 0% 0%;
  }

  @keyframes ucuq-connection {
    100% {
    -webkit-mask-position: 0% 0%;
    mask-position: 0% 0%;
    }
    50% {
    -webkit-mask-position: 100% 0%;
    mask-position: 100% 0%;
    }
    0% {
    -webkit-mask-position: 200% 0%;
    mask-position: 200% 0%;
    }
  }
  </style>
  <h2 class="ucuq-connection">💻…📡…🛰️…<span style='display: inline-block;transform: scaleX(-1)';>📡</span>…🤖</h2>
  """,
  )

  if device or CONFIG_:
    device = getDevice(device)

  if not device:
    await dom.inner(
      target, "<h3>ERROR: Please launch the 'Config' application!</h3>"
    )
    raise SystemExit("Unable to connect to a device!")

  setDevice(device=device)

  start = time.monotonic()
  infos = await getInfosAwait(device)

  if (elapsed := time.monotonic() - start) < 3:
    await sleepAwait(3 - elapsed)

  deviceId = getDeviceId(infos)

  await dom.inner(target, ATK_BODY_.format(infos[IK_KIT_LABEL], deviceId))

  await dom.inner("ucuq_body", body)

  await sleepAwait(1.5)

  await dom.inner(target, body)

  atlastk.setCallback(UCUQ_XDEVICE_ACTION_, handleXDeviceRetrieving_)

  return infos


def getDevice(device=None, *, id=None, token=None):
  if device and (token or id):
    displayExitMessage_("'device' can not be given together with 'token' or 'id'!")

  if device is None:
    global device_

    if token or id:
      device_ = Device(id=id, token=token)
    elif device_ is None:
      device_ = Device()
      device_.connect()
    return device_
  else:
    return device


def addCommand(command, commit=False, /, device=None):
  getDevice(device).addCommand(command, commit)


# does absolutely nothing whichever method is called but returns 'self'.
# for the handling of the 'extra' parameter in the init method, which handles extra initialisation.
class Nothing:
  def __getattr__(self, name):
    def doNothing(*args, **kwargs):
      return self

    return doNothing

  def __bool__(self):
    return False


# does absolutely nothing whichever method is called.
# 'if Nothing()' returns 'False'.
class Nothing_:
  def __init__(self, object):
    self.object = object

  def __getattr__(self, name):
    def doNothing(*args, **kwargs):
      return self.object

    return doNothing

  def __bool__(self):
    return False


class Core_:
  def __new__(cls, *kargs, **kwargs):
    if "device" not in kwargs or (devices := kwargs["device"]) is None :
      devices = getDevice()
    
    if type(devices) is Multi:
      if "device" in kwargs:
        kwargs.pop("device")
        
      multi = Multi()
      
      for device in devices:
        obj = object.__new__(cls)
        cls.__init__(obj, *kargs, **kwargs, **{"device": device})
        multi.add(obj)
        
      return multi
    else:
      obj = object.__new__(cls)
      cls.__init__(obj, *kargs, **kwargs)
      return obj
  
  def __init__(self, device=None):
    self.id = None
    self.device_ = device

  def __del__(self):
    if self.id:
      self.addCommand(f"del {ITEMS_}[{self.id}]")

  def getDevice(self):
    return self.device_

  def getId(self):
    return self.id

  def init(self, modules, instanciation, device, extra, *, before=""):
    if self.device_:
      if device and device != self.device_:
        raise Exception("'device' already given!")
    else:
      self.device_ = getDevice(device)

    if modules:
      self.device_.addModules(modules)

    if before:
      self.addCommand(before)

    if instanciation:
      self.id = getObjectIndice()
      self.addCommand(f"{self.getObject()} = {instanciation}")

    return self if not isinstance(extra, bool) or extra else Nothing_(self)

  def getObject(self):
    return getObject_(self.id)

  def addCommand(self, command):
    self.device_.addCommand(command)
    return self

  def addMethods(self, methods):
    return self.addCommand(f"{self.getObject()}.{methods}")

  def callMethodAwait(self, method):
    return self.device_.commitAwait(f"{self.getObject()}.{method}")

  def sleepStart(self):
    return self.device_.sleepStart()

  def sleepWait(self, secs):
    self.device_.sleepWait(secs)
    return self

  def sleep(self, secs):
    self.device_.sleep(secs)
    return self
  
  def ntpSetTime(self):
    self.device_.ntpSetTime()
    return self
  
  def ntpSleepUntil(self, timestamp):
    self.device_.ntpSleepUntil(timestamp)
    return self
    
  def ntpSleep(self, delay):
    self.device_.ntpSleep(delay)
    return self
    
  def ntpTime(self):
    return self.device_.ntpTime()


class GPIO(Core_):
  def __init__(self, pin=None, device=None, extra=True):
    super().__init__(device)

    if pin:
      self.init(pin, device, extra)

  def init(self, pin, device=None, extra=True):
    self.pin = f'"{pin}"' if isinstance(pin, str) else pin

    super().init("GPIO-1", f"GPIO({self.pin})", device, extra)

  def high(self, value=True):
    return self.addMethods(f"high({value})")

  def low(self):
    return self.high(False)


class I2C_Core_(Core_):
  def __init__(self, sda=None, scl=None, soft=None, *, device=None):
    super().__init__(device)

    if sda == None != scl == None:
      raise Exception("None or both of sda/scl must be given!")
    elif sda != None:
      self.init(sda, scl, soft=soft, device=device)

  async def scanAwait(self):
    return await commitAwait(f"{self.getObject()}.scan()")


class I2C(I2C_Core_):
  def init(self, sda, scl, soft=None, *, device=None, extra=True):
    if soft == None:
      soft = False

    super().init(
      "I2C-1",
      f"machine.{'Soft' if soft else ''}I2C({'0,' if not soft else ''} sda=machine.Pin({sda}), scl=machine.Pin({scl}))",
      device=device,
      extra=extra,
    )


class SoftI2C(I2C):
  def init(self, sda, scl, *, soft=None, device=None):
    if soft == None:
      soft = True

    super().init(sda, scl, soft=soft, device=device)


class SPI(Core_):
  def __init__(
    self,
    id,
    sck=None,
    mosi=None,
    miso=None,
    baudrate=None,
    *,
    polarity=None,
    phase=None,
    bits=None,
    device=None,
  ):
    super().__init__(device)

    if sck == None != mosi == None or sck == None != miso == None:
      raise Exception("None or all of sck/ mosi/ miso must be given!")
    elif sck != None:
      self.init(
        id,
        sck,
        mosi,
        miso,
        baudrate=baudrate,
        polarity=polarity,
        phase=phase,
        bits=bits,
        device=device,
      )

  def init(
    self,
    id,
    sck=None,
    mosi=None,
    miso=None,
    baudrate=None,
    polarity=None,
    phase=None,
    bits=None,
    device=None,
    extra=True,
  ):
    super().init(
      None,
      f"machine.{'Soft' if not id else ''}SPI({str(id) + ', ' if id else ''}sck=machine.Pin({sck}){getParam('mosi', mosi, 'machine.Pin({})')}{getParam('miso', miso, 'machine.Pin({})')}{getParam('baudrate', baudrate)}{getParam('polarity', polarity)}{getParam('phase', phase)}{getParam('bits', bits)})",
      device=device,
      extra=extra,
    )


class SoftSPI(SPI):
  def __init__(
    self,
    sck,
    mosi,
    miso,
    *,
    id=None,
    baudrate=None,
    polarity=None,
    phase=None,
    bits=None,
    device=None,
  ):
    super().__init__(
      id,
      sck,
      mosi,
      miso,
      baudrate=baudrate,
      polarity=polarity,
      phase=phase,
      bits=bits,
      device=device,
    )


class WS2812(Core_):
  def __init__(self, n=None, pin=None, offset=0, device=None, extra=True):
    super().__init__(device)

    if (pin is None) != (n is None):
      raise Exception("Both or none of 'pin'/'n' must be given")

    if pin is not None:
      WS2812.init(self, n, pin, offset=offset, device=device, extra=extra)

  def init(self, n, pin, offset=0, device=None, extra=True):
    self.n_ = n
    self.offset_ = offset
    self.current_ = [(0,0,0)] * n
    self.new_ = [(0,0,0)] * n
    super().init(
      "WS2812-1", f"neopixel.NeoPixel(machine.Pin({pin}), {n})", device, extra
    ).flash(extra)

  def len(self):
    return self.n_
  
  async def straightLenAwait(self):
    return int(await self.callMethodAwait("__len__()"))
  
  def convert(self, index):
    return (index + self.offset_) % self.n_

  def setValue(self, index, val):
    self.new_[self.convert(index)] = tuple(val)
    return self
  
  def straightSetValue(self, index, val):
    self.setValue(index, val)
    return self.addMethods(f"__setitem__({self.convert(index)}, {json.dumps(val)})")
  
  def getValue(self, index):
    return self.new_[self.convert(index)]

  async def straightGetValueAwait(self, index):
    return await self.callMethodAwait(f"__getitem__({self.convert(index)})")
  
  def fill(self, val):
    self.new_ = [tuple(val)] * self.n_
    return self

  def straightFill(self, val):
    self.fill(val)
    return self.addMethods(f"fill({json.dumps(val)})")

  def straightWrite(self):
    self.current_ = copy.deepcopy(self.new_)
    return self.addMethods("write()")
  
  def write(self):
    diffs = []
    same = self.new_[0]
    
    for i in range(len(self.new_)):
      if self.new_[i] != self.current_[i]:
        diffs.append((i,self.new_[i]))
        
      if same is not None and same != self.new_[i]:
        same = None
      
    if len(diffs):
      if same is not None:
        self.straightFill(same)
      else:
        command = ""
        for diff in diffs:
          command += f"{self.getObject()}.__setitem__({diff[0]},{json.dumps(diff[1])})\n"
        self.addCommand(command)
      return self.straightWrite()
    else:
      return self

  def flash(self, extra=True):
    self.fill((255, 255, 255)).write()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.fill((0, 0, 0)).write()


class HT16K33(Core_):
  def __init__(self, i2c=None, addr=None, extra=True):
    super().__init__()

    if i2c:
      self.init(i2c, addr=addr, extra=extra)

  def init(self, i2c, addr=None, extra=True):
    return (
      super()
      .init(
        "HT16K33-1",
        f"HT16K33({i2c.getObject()}, {addr})",
        i2c.getDevice(),
        extra,
      )
      .setBrightness(15)
      .flash(extra)
      .setBrightness(0)
    )

  def flash(self, extra=True):
    self.draw("ffffffffffffffffffffffffffffffff")
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.draw("")

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

  def rect(self, x0, y0, x1, y1, ink=True):
    return self.addMethods(f"rect({x0}, {y0}, {x1}, {y1}, ink={1 if ink else 0})")

  def show(self):
    return self.addMethods(f"render()")


def getParam(label, value, expr=None):
  if value:
    return f", {label} = {value if expr is None else expr.format(value)}"
  else:
    return ""


class PWM(Core_):
  def __init__(
    self, pin=None, *, freq=None, ns=None, u16=None, device=None, extra=True
  ):
    super().__init__(device)

    if pin != None:
      self.init(pin, freq=freq, u16=u16, ns=ns, device=device, extra=extra)

  def init(self, pin, *, freq=None, u16=None, ns=None, device=None, extra=True):
    command = f"machine.PWM(machine.Pin({pin}, machine.Pin.OUT){getParam('freq', freq)}{getParam('duty_u16', u16)}{getParam('duty_ns', ns)})"
    super().init("PWM-1", command, device, extra, before=f"{command}.deinit()")

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
  
BUZZER_COEFF_ = 2 ** (1/12)
BASE_FREQ_ = 6.875

class Multi_:
  def __new__(cls, *kargs, **kwargs):
    position, name = cls.param_
    
    if name in kwargs:
      ArgIsKW = True
      values = kwargs[name]
    elif len(kargs) > position:
      values = kargs[position]
      ArgIsKW = False
      kargs = list(kargs)
    else:
      values = None
    
    if type(values) is Multi:
      multi = Multi()
      
      for value in values:
        if ArgIsKW:
          kwargs[name] = value
        else:
          kargs[position] = value

        obj = object.__new__(cls)
        cls.__init__(obj, *kargs, **kwargs)
        multi.add(obj)
      return multi
    else:
      obj = object.__new__(cls)
      cls.__init__(obj, *kargs, **kwargs)
      return obj

class Buzzer(Multi_):
  param_ = (0, "pwm")
  def __init__(self, pwm=None, *, u16=32000, extra=True):
    self.on_ = False
    Buzzer.init(self, pwm, u16=u16, extra=extra)

  def init(self, pwm, *, u16=32000, extra=True):
    self.u16_ = u16
    self.pwm_ = pwm
    
    if pwm is not None:
      self.pwm_.setU16(0)
    
    return self
    
  def off(self):
    if self.on_:
      self.on_ = False
      self.pwm_.setU16(0)
      
    return self
    
  def on(self, freq):
    if freq == 0:
      self.off()
    elif self.on_:
        self.pwm_.setFreq(freq)
    else:
        self.pwm_.setFreq(freq).setU16(self.u16_)
        self.on_ = True

    return self
        
  def play(self, note):
    if note == 0:
      return self.off()
    else:
      return self.on(round(BASE_FREQ_ * BUZZER_COEFF_ ** ( note + 3 )))


class PCA9685(Core_):
  def __init__(self, i2c=None, *, addr=None):
    super().__init__()

    if i2c:
      self.init(i2c, addr=addr)

  def init(self, i2c, addr=None):
    super().init(
      "PCA9685-1", f"PCA9685({i2c.getObject()}, {addr})", i2c.getDevice()
    )

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
  def __init__(self, pca=None, channel=None):
    super().__init__()

    if bool(pca) != (channel != None):
      raise Exception("Both or none of 'pca' and 'channel' must be given!")

    if pca:
      self.init(pca, channel)

  def init(self, pca, channel):
    super().init(
      "PWM_PCA9685-1",
      f"PWM_PCA9685({pca.getObject()}, {channel})",
      pca.getDevice(),
    )

    self.pca = pca  # Not used inside this object, but to avoid pca being destroyed by GC, as it is used on the µc.

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

  async def getU16Await(self, u16=None):
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


class HD44780_I2C(Multi_, Core_):
  param_ = (2, "i2c")
  def __init__(self, num_columns, num_lines, /, i2c, addr=None, extra=True):
    super().__init__()

    if i2c:
      HD44780_I2C.init(self, num_columns, num_lines, i2c, addr=addr, extra=extra)
    elif addr is not None:
      raise Exception("addr can not be given without i2c!")

  def init(self, num_columns, num_lines, i2c, addr=None, extra=True):
    return (
      super()
      .init(
        "HD44780_I2C-1",
        f"HD44780_I2C({i2c.getObject()},{num_lines},{num_columns},{addr})",
        i2c.getDevice(),
        extra,
      )
      .flash(extra)
    )

  def moveTo(self, x, y):
    return self.addMethods(f"move_to({x},{y})")

  def putString(self, string):
    return self.addMethods('putstr("{}")'.format(string.replace('"','\\"')))

  def clear(self):
    return self.addMethods("clear()")

  def showCursor(self, value=True):
    return self.addMethods("show_cursor()" if value else "hide_cursor()")

  def hideCursor(self):
    return self.showCursor(False)

  def blinkCursorOn(self, value=True):
    return self.addMethods("blink_cursor_on()" if value else "blink_cursor_off()")

  def blinkCursorOff(self):
    return self.blinkCursorOn(False)

  def displayOn(self, value=True):
    return self.addMethods("display_on()" if value else "display_off()")

  def displayOff(self):
    return self.displayOn(False)

  def backlightOn(self, value=True):
    return self.addMethods("backlight_on()" if value else "backlight_off()")

  def backlightOff(self):
    return self.backlightOn(False)

  def flash(self, extra=True):
    self.backlightOn()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.backlightOff()


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

  def __init__(self, pwm=None, specs=None, /, *, tweak=None, domain=None):
    super().__init__()

    self.test_(specs, tweak, domain)

    if pwm:
      self.init(pwm, specs, tweak=tweak, domain=domain)

  def init(self, pwm, specs, tweak=None, domain=None, extra=True):
    super().init("Servo-1", "", pwm.getDevice(), extra)

    self.test_(specs, tweak, domain)

    if not tweak:
      tweak = self.Tweak(specs.range / 2, 0, False)

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

    u16 = (
      self.specs.min
      + (angle + self.tweak.angle)
      * (self.specs.max - self.specs.min)
      / self.specs.range
      + self.tweak.offset
    )

    if u16 > self.domain.max:
      u16 = self.domain.max
    elif u16 < self.domain.min:
      u16 = self.domain.min

    return int(u16)

  def dutyToAngle(self, duty):
    angle = (
      self.specs.range
      * (duty - self.tweak.offset - self.specs.min)
      / (self.specs.mas - self.specs.min)
    )

    if self.tweak.invert:
      angle = -angle

    return angle - self.tweak.angle

  def reset(self):
    self.setAngle(0)

  async def getAngleAwait(self):
    return self.dutyToAngle(await self.pwm.getU16Await())

  def setAngle(self, angle):
    return self.pwm.setU16(self.angleToDuty(angle))


class OLED_(Core_):
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

  def pixel(self, x, y, col=1):
    return self.addMethods(f"pixel({x},{y},{col})")

  def scroll(self, dx, dy):
    return self.addMethods(f"scroll({dx},{dy})")

  def text(self, string, x, y, col=1):
    return self.addMethods(f"text('{string}',{x}, {y}, {col})")

  def hText(self, string, y, col=1, trueWidth=None):
    trueWidth = trueWidth or f"{self.getObject()}.width"
    return self.addMethods(
      f"text('{string}',max(( {trueWidth} - len('{string}' ) * 8) // 2, 0), {y}, {col})"
    )

  def rect(self, x, y, w, h, col, fill=False):
    return self.addMethods(f"rect({x},{y},{w},{h},{col},{fill})")

  def hline(self, x, y, w, col):
    return self.addMethods(f"hline({x},{y},{w},{col})")

  def vline(self, x, y, h, col):
    return self.addMethods(f"vline({x},{y},{h},{col})")

  def line(self, x1, y1, x2, y2, col):
    return self.addMethods(f"line({x1},{y1},{x2},{y2},{col})")

  def ellipse(self, x, y, rx, ry, col, fill=False, quad=15):
    return self.addMethods(f"ellipse({x},{y},{rx},{ry},{col},{fill},{quad})")

  def draw(self, pattern, width, ox=0, oy=0, mul=1):
    if width % 4:
      raise Exception("'width' must be a multiple of 4!")
    return self.addMethods(f"draw('{pattern}',{width},{ox},{oy},{mul})")

  def flash(self, extra=True):
    self.fill(1).show()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.fill(0).show()


class SSD1306(OLED_):
  def rotate(self, rotate=True):
    return self.addMethods(f"rotate({rotate})")


class SSD1306_I2C(Multi_, SSD1306):
  param_ = (2, 'i2c')
  def __init__(
    self,
    width=None,
    height=None,
    /,
    i2c=None,
    addr=None,
    external_vcc=False,
    extra=True,
  ):
    super().__init__()

    if bool(width) != bool(height) != bool(i2c):
      raise Exception("All or none of width/height/i2c must be given!")
    elif width:
      self.init(
        width, height, i2c, external_vcc=external_vcc, addr=addr, extra=extra
      )
    elif addr:
      raise Exception("addr can not be given without i2c!")

  def init(self, width, height, /, i2c, external_vcc=False, addr=None, extra=True):
    super().init(
      "SSD1306_I2C-1",
      f"SSD1306_I2C({width}, {height}, {i2c.getObject()}, {addr}, {external_vcc})",
      i2c.getDevice(),
      extra,
    ).flash(extra if not isinstance(extra, bool) else 0.15)


class SH1106(OLED_):
  pass


class SH1106_I2C(SH1106):
  def __init__(
    self,
    width=None,
    height=None,
    /,
    i2c=None,
    addr=None,
    external_vcc=False,
    extra=True,
  ):
    super().__init__()

    if bool(width) != bool(height) != bool(i2c):
      raise Exception("All or none of width/height/i2c must be given!")
    elif width:
      self.init(
        width, height, i2c, external_vcc=external_vcc, addr=addr, extra=extra
      )
    elif addr:
      raise Exception("addr can not be given without i2c!")

  def init(self, width, height, /, i2c, external_vcc=False, addr=None, extra=True):
    super().init(
      "SH1106_I2C-1",
      f"SH1106_I2C({width}, {height}, {i2c.getObject()}, addr={addr}, external_vcc={external_vcc})",
      i2c.getDevice(),
      extra,
    ).flash(extra if not isinstance(extra, bool) else 0.15)


OD_SH1106_ = "SH1106"
OD_SSD1306_ = "SSD1306"


class OLED_I2C:
  def __new__(cls, driver, *args, **kwargs):
    if driver == OD_SH1106_:
      return SH1106_I2C(*args, **kwargs)
    elif driver == OD_SSD1306_:
      return SSD1306_I2C(*args, **kwargs)
    else:
      raise Exception(f"Unknown OLED driver {driver}!")


c_ = lambda color: f"color565({color})"
f_ = lambda function, fill: f"{'fill_' if fill else 'draw_'}{function}"


def zoom_rgb565_(raw_data, width, height, hzoom, vzoom):
  zoomed_width = width * hzoom
  zoomed_height = height * vzoom

  zoomed_data = bytearray(zoomed_width * zoomed_height * 2)

  for y in range(height):
    for x in range(width):
      idx_src = (y * width + x) * 2
      pixel = raw_data[idx_src : idx_src + 2]  # 2 octets RGB565

      x_start = x * hzoom
      y_start = y * vzoom

      for dy in range(vzoom):
        for dx in range(hzoom):
          x_dst = x_start + dx
          y_dst = y_start + dy
          idx_dst = (y_dst * zoomed_width + x_dst) * 2
          zoomed_data[idx_dst : idx_dst + 2] = pixel

  return bytes(zoomed_data)


class ILI9341(Core_):
  def __init__(
    self,
    width,
    height,
    /,
    rotation=0,
    dc=None,
    cs=None,
    rst=None,
    spi=None,
    extra=True,
  ):
    super().__init__()

    if (
      bool(width)
      != bool(height)
      != bool(spi)
      != bool(dc)
      != bool(cs)
      != bool(rst)
    ):
      raise Exception("All or none of width/height/spi/dc/cs/rst must be given!")
    elif width:
      self.init(
        width,
        height,
        rotation=rotation,
        spi=spi,
        dc=dc,
        cs=cs,
        rst=rst,
        extra=extra,
      )

  def init(
    self,
    width,
    height,
    /,
    rotation=0,
    spi=None,
    dc=None,
    cs=None,
    rst=None,
    extra=True,
  ):
    super().init(
      "ILI9341-1",
      f"ILI9341({spi.getObject()}, machine.Pin({cs}), machine.Pin({dc}), machine.Pin({rst}), {width}, {height}, {rotation})",
      spi.getDevice(),
      extra,
    )

  def on(self, value=True):
    return self.addMethods(f"display_{'on' if value else 'off'}()")

  def off(self):
    return self.on(False)

  def clear(self, color=0):
    return self.addMethods(f"clear(color565({color}))")

  def cleanup(self):
    return self.addMethods("cleanup()")

  def invert(self, value=True):
    return self.addMethods(f"invert({value})")

  def pixel(self, x, y, color):
    return self.addMethods(f"draw_pixel({x}, {y}, {c_(color)})")

  def hline(self, x, y, w, color):
    return self.addMethods(f"draw_hline({x}, {y}, {w}, {c_(color)})")

  def vline(self, x, y, h, color):
    return self.addMethods(f"draw_vline({x}, {y}, {h}, {c_(color)})")

  def line(self, x0, y0, x1, y1, color):
    return self.addMethods(f"draw_line({x0}, {y0}, {x1}, {y1}, {c_(color)})")

  def lines(self, coords, color):
    return self.addMethods(f"draw_lines([tuple(map(int, pair.split(','))) for pair in '{{';'.join(f\"{{x}},{{y}}\" for x,y in coords)}}'.split(';')], {c_(color)})")

  def rect(self, x, y, w, h, color, fill=True):
    return self.addMethods(
      f"{f_('rectangle', fill)}({x}, {y}, {w}, {h}, {c_(color)})"
    )

  def poly(self, sides, x0, y0, r, color, rotate=0, fill=True):
    return self.addMethods(
      f"{f_('polygon', fill)}({sides}, {x0}, {y0}, {r}, {c_(color)}, {rotate})"
    )

  def circle(self, x, y, r, color, fill=True):
    return self.addMethods(f"{f_('circle', fill)}({x}, {y}, {r}, {c_(color)})")

  def ellipse(self, x, y, rx, ry, color, fill=True):
    return self.addMethods(
      f"{f_('ellipse', fill)}({x}, {y}, {rx}, {ry}, {c_(color)})"
    )

  def text(self, x, y, text, color=255, bgcolor=0, rotate=0):
    return self.addMethods(
      f"draw_text8x8({x}, {y}, '{text}', {c_(color)}, {c_(bgcolor)}, {rotate})"
    )

  def draw(self, stream, width, height, speed=1, hzoom=1, vzoom=0):
    if vzoom == 0:
      vzoom = hzoom

    for i in range(height // speed):
      data = stream.read(width * 2 * speed)
      self.addMethods(
        f"draw('{base64.b64encode(zoom_rgb565_(data, width, speed, hzoom, vzoom)).decode('ascii')}',0, {i*speed*vzoom}, {width*hzoom}, {speed*vzoom})"
      )

    if remainder := height % speed:
      data = stream.read(width * 2 * remainder)
      self.addMethods(
        f"draw('{base64.b64encode(zoom_rgb565_(data, width, speed, hzoom, vzoom)).decode('ascii')}',0, {(height // speed) * speed*vzoom}, {width*hzoom}, {remainder*vzoom})"
      )

    return self


class SSD1680_SPI(OLED_):
  def __init__(self, cs, dc, rst, busy, spi, landscape=True):
    super().__init__()
    self.init(cs, dc, rst, busy, spi, landscape=landscape)

  def init(self, cs, dc, rst, busy, spi, landscape=False, extra=True):
    super().init(
      "SSD1680-1",
      f"SSD1680({spi.getObject()},machine.Pin({cs}, machine.Pin.OUT),machine.Pin({dc}, machine.Pin.OUT),{rst},machine.Pin({busy}, machine.Pin.IN),{landscape})",
      spi.getDevice(),
      extra,
    )
    self.addMethods("init()")

  def hText(self, *args, trueWidth=None, **kargs):
    return super().hText(*args, trueWidth=trueWidth or 250, **kargs)


def pwmJumps(jumps, step=100, delay=0.05):
  command = "pwmJumps([\n"

  for jump in jumps:
    command += f"\t[{jump[0].getObject()},{jump[1]}],\n"

  command += f"], {step}, {delay})"

  return command


def execute_(command, device):
  device.addModule("PWMJumps-1")
  device.addCommand(command)


def servoMoves(moves, step=100, delay=0.05):
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
      return [i, 0, 0]
    case 1:
      return [i, i, 0]
    case 2:
      return [0, i, 0]
    case 3:
      return [0, i, i]
    case 4:
      return [0, 0, i]
    case 5:
      return [i, 0, i]


def rbShadeFade(variant, i, max):
  if i < max:
    return rbFade(variant, i, max, True)
  elif i > max * 6:
    return rbFade((variant + 5) % 6, i % max, max, False)
  else:
    return rbShade(variant + int((i - max) / max), i % max, max)


def setCommitBehavior(behavior):
  global defaultCommitBehavior_

  defaultCommitBehavior_ = behavior
  
  
PP_NOTE_MAP_ = {
  'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6,
  'E': -5, 'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1, 'Ab': -1,
  'A': 0, 'A#': 1, 'Bb': 1, 'B': 2
}  
  
def ppNote2Midi_(noteStr, octave):
  if noteStr == 'R':
    return 0  # silence
  elif noteStr == '-':
    return -1
  
  if len(noteStr) == 2 and noteStr[1] in('b','#'):
    noteKey = noteStr
  else:
    noteKey = noteStr[0]

  if noteKey not in PP_NOTE_MAP_:
    return 0
  
  return 12 * (int(octave) + 2) + PP_NOTE_MAP_[noteKey]


def ppDuration2Seconds_(duration, base, dots=0):
  value = 1 / (2 ** (4 - duration))

  total = value
  
  if dots == -1:
    total = total * 2  / 3
  else:
    for _ in range(dots):
      value /= 2
      total += value

  return base * total


def ppParseNoteString_(note_str, base):
  match = re.match(r'([A-Z][b#]?)(\d)(\d)(\.*,?)', re.sub(r"\s+", "", note_str))

  if not match:
    match = re.match(r'([R\-])(\d)(\.*,?)', note_str)

    if not match:
      return None

    octave = 0
    note, duration, dots = match.groups()
  else:
    note, octave, duration, dots = match.groups()
    
  return ppNote2Midi_(note, int(octave)), ppDuration2Seconds_(int(duration), base, len(dots) if len(dots) == 0 or dots[0] != ',' else -1),


def ppExtractNotes_(voice_str):
  return re.findall(r'([A-Z\-][b#]?\d\d\.*,?|[R\-]\d\.*,?)', voice_str)


def polyphonicPlay(voices, tempo, userObject, callback):
  voiceNotes = [ppExtractNotes_(v) for v in voices]
  
  raws = []

  for a in voiceNotes:
    raw = []
    for b in a:
      raw.append(ppParseNoteString_(b, 60.0 / tempo))
    raw.append((0, 0))
    raws.append(raw)

  indexes = [0 for _ in raws]
  notes = [0 for _ in raws]
  delays = [0 for _ in raws]

  while any(i is not None for i in indexes):
    events = []

    delay = 100000

    for i in range(len(indexes)):
      if indexes[i] is not None:
        if delays[i] == 0:
          notes[i], delays[i] = raws[i][indexes[i]]
          indexes[i] += 1
          events.append((i, notes[i]))
        delay = min(delay, delays[i])

    callback(userObject, events, delay)

    for i in range(len(indexes)):
      if indexes[i] is not None and indexes[i] >= len(raws[i]):
        indexes[i] = None
      else:
        delays[i] -= delay
        
        
###### Begin of section high precision time handling based on NTP #####
NTP_SCRIPT_ = """
import socket
import struct
import time
import machine
import gc

NTP_DELTA = 2208988800  # Différence entre epoch NTP (1900) et Unix (1970)

def unpack_ntp_timestamp_us(data, offset):
  sec, frac = struct.unpack("!II", data[offset:offset+8])
  unix_sec = sec - NTP_DELTA
  return unix_sec * 1_000_000 + (frac * 1_000_000) // 2**32


def ntp_time_t1_t4_us(host="fr.pool.ntp.org"):
  addr = socket.getaddrinfo(host, 123)[0][-1]
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.settimeout(2)

  packet = b'\x1b' + 47 * b'\0'

  T1_us = time.ticks_us()
  s.sendto(packet, addr)

  data = s.recv(48)
  T4_us = time.ticks_us()  # µs
  s.close()

  T2_us = unpack_ntp_timestamp_us(data, 32)
  T3_us = unpack_ntp_timestamp_us(data, 40)

  offset_us = ((T2_us - T1_us) + (T3_us - T4_us)) // 2

  return T4_us + offset_us


def precise_time_us():
  t_ntp_us, t0_ticks_us = TIME_ANCHOR_US
  elapsed_us = time.ticks_diff(time.ticks_us(), t0_ticks_us)
  return t_ntp_us + elapsed_us


def set_rtc_from_us(timestamp_us):
  ts = timestamp_us // 1_000_000
  tm = time.localtime(ts)
  us = timestamp_us % 1_000_000
  rtc_tuple = (tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], us)
  machine.RTC().datetime(rtc_tuple)


def sleep_until_us(target_time_us):
  while precise_time_us() < target_time_us:
    pass
        
        
def ntp_set_time():
  global TIME_ANCHOR_US
  t_ntp_us = ntp_time_t1_t4_us()
  t0_ticks_us = time.ticks_us()
  TIME_ANCHOR_US = (t_ntp_us, t0_ticks_us)

  set_rtc_from_us(precise_time_us())
"""

def ntpSetTime(device = None):
  return getDevice(device).ntpSetTime()

def ntpSleepUntil(timestamp, device = None):
  return getDevice(device).ntpSleepUntil(timestamp)

def ntpSleep(delay, device = None):
  return getDevice(device).ntpSleep(delay)

def ntpTime(device = None):
  return getDevice(device).ntpTime()

###### End of section high precision time handling based on NTP #####


##### Section dédicated to micro:bit #####

MB_SCRIPT_ = """
import time
from machine import UART

# --- UART + framing ---
MB_START_ = 0x7E
MB_END_   = 0x7F

mbUART_ = UART(1, baudrate=115200, tx=21, rx=20)

def mbChecksum_(data):
    return sum(data) & 0xFF

def mbSendFrame_(payload_str):
    data = payload_str.encode()
    frame = bytes([MB_START_, len(data)]) + data + bytes([mbChecksum_(data), MB_END_])
    mbUART_.write(frame)

# Buffer circulaire
mbRXBuffer_ = bytearray()

def mbFindByte_(buf, value, start=0):
    for i in range(start, len(buf)):
        if buf[i] == value:
            return i
    return -1

def mbReadFrame_():
    global mbRXBuffer_

    if mbUART_.any():
        mbRXBuffer_.extend(mbUART_.read())

    s = mbFindByte_(mbRXBuffer_, MB_START_)
    if s < 0:
        if len(mbRXBuffer_) > 128:
            mbRXBuffer_ = bytearray()
        return None

    e = mbFindByte_(mbRXBuffer_, MB_END_, s + 1)
    if e < 0:
        return None

    frame = mbRXBuffer_[s:e+1]
    mbRXBuffer_ = mbRXBuffer_[e+1:]

    if len(frame) < 4:
        return None

    length = frame[1]
    if len(frame) < 3 + length + 1:
        return None

    payload = frame[2:2+length]
    cks = frame[2+length]

    if mbChecksum_(payload) != cks:
        return None

    return ''.join(chr(b) for b in payload)

mbSeq_ = 0

def mbSendReliable_(content, retries=5, timeout_ms=600):
    global mbSeq_

    payload = "%d:%s" % (mbSeq_, content)

    for attempt in range(retries):

        # Purge du buffer avant envoi
        global mbRXBuffer_
        mbRXBuffer_ = bytearray()

        mbSendFrame_(payload)
        time.sleep_ms(20)

        t0 = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            msg = mbReadFrame_()
            if msg:

                if msg.startswith("ACK:"):
                    ack_seq = int(msg[4:])
                    if ack_seq == mbSeq_:
                        mbSeq_ ^= 1
                        return True

                if msg.startswith("NACK:"):
                    nack_seq = int(msg[5:])
                    if nack_seq == mbSeq_:
                        break

        # timeout → nouvelle tentative

    return False

# --- Envoi fiable AVEC valeur de retour (réponse + ACK) ---

def mbRequestValue_(cmd, prefix):
    global mbSeq_, mbRXBuffer_

    payload = "%d:%s" % (mbSeq_, cmd)

    for attempt in range(5):
        mbRXBuffer_ = bytearray()
        mbSendFrame_(payload)
        time.sleep_ms(20)

        t0 = time.ticks_ms()
        value = None

        while time.ticks_diff(time.ticks_ms(), t0) < 600:
            msg = mbReadFrame_()
            if not msg:
                continue

            # Réponse de la micro:bit
            if msg.startswith(prefix):
                try:
                    value = int(msg[len(prefix):])
                except:
                    value = None
                continue

            # ACK
            if msg.startswith("ACK:"):
                ack_seq = int(msg[4:])
                if ack_seq == mbSeq_:
                    mbSeq_ ^= 1
                    return value

        # timeout → retry

    return None


# --- SYNC initial ---

def mbSync():
    global mbSeq_
    mbSeq_ = 0
    print(mbSendReliable_("SYNC"))


# --- Classe Image (style micro:bit) ---

class Microbit:
    class Image:
        def __init__(self, data):
            self.data = data

        @staticmethod
        def fromRows(rows):
            return Microbit.Image("".join(rows))

    class Display:
        @staticmethod
        def clear():
            return mbSendReliable_("CLR")

        @staticmethod
        def setPixel(x, y, b):
            return mbSendReliable_("PIX:%d,%d,%d" % (x, y, b))

        @staticmethod
        def getPixel(x, y):
            return mbRequestValue_("GET:%d,%d" % (x, y), "VAL:")

        @staticmethod
        def showText(text, delay=150):
            return mbSendReliable_("SCR:%d:%s" % (delay, text))

        @staticmethod
        def scroll(text, delay=150):
            return Microbit.Display.showText(text, delay)

        @staticmethod
        def showImage(img):
            return mbSendReliable_("IMG:" + img)

        @staticmethod
        def animate(images, delay=150, loop=False):
            loop_flag = 1 if loop else 0
            payload = "ANM:%d:%d:%s" % (delay, loop_flag, "|".join(images))
            return mbSendReliable_(payload)

        @staticmethod
        def stopAnimation():
            return mbSendReliable_("STOP")

        @staticmethod
        def on():
            return mbSendReliable_("ON")

        @staticmethod
        def off():
            return mbSendReliable_("OFF")

        @staticmethod
        def isOn():
            val = mbRequestValue_("ISON", "ION:")
            return bool(val) if val is not None else None

        @staticmethod
        def readLightLevel():
            return mbRequestValue_("LUX", "LIG:")

        @staticmethod
        def show(obj, delay=400, loop=False, wait=True):
            if isinstance(obj, str):
                return Microbit.Display.scroll(obj, delay)

            if isinstance(obj, Microbit.Image):
                return Microbit.Display.showImage(obj.data)

            if isinstance(obj, list):
                frames = []
                for img in obj:
                    if isinstance(img, Microbit.Image):
                        frames.append(img.data)
                    else:
                        raise TypeError("List must contain Image objects")
                return Microbit.Display.animate(frames, delay=delay, loop=loop)

            raise TypeError("Unsupported type for show()")


# Quelques images pré-définies (optionnel)
Microbit.Image.HEART = Microbit.Image.fromRows([
    "09090",
    "99999",
    "99999",
    "09990",
    "00900",
])

Microbit.Image.HEART = Microbit.Image.fromRows([
    "09090",
    "99999",
    "99999",
    "09990",
    "00900",
])

Microbit.Image.HEART_SMALL = Microbit.Image.fromRows([
    "00000",
    "09090",
    "09990",
    "00900",
    "00000",
])

Microbit.Image.HAPPY = Microbit.Image.fromRows([
    "00000",
    "09090",
    "00000",
    "90009",
    "09990",
])

Microbit.Image.SAD = Microbit.Image.fromRows([
    "00000",
    "09090",
    "00000",
    "09990",
    "90009",
])


mbSync()
"""


class Microbit():
  def execute_(self, command):
    self.device_.addCommand(f"Microbit.Display.{command}")
    
  def __init__(self, device=None, extra=True):
    self.init(device=device, extra=extra)
    
  def init(self, device=None, extra=True):
    self.device_ = getDevice(device)
    self.device_.addCommand(MB_SCRIPT_)
    self.matrix_ = [[0] * 5 for _ in range(5)]
    self.flash()
    
  def clear(self):
    for x in range(5):
      for y in range(5):
        self.matrix_[x][y] = 0
    self.execute_("clear()")
    
  def setPixel(self, x, y, level):
    self.matrix_[x][y] = level
    self.execute_(f'setPixel({x}, {y}, {level})')
    
  def getPixel(self, x, y):
    return self.matrix_[x][y]
  
  def showText(self, text, delay=150):
    self.execute_(f'showText("{text}", {delay})')
    
  def flash(self):
    self.execute_("""show(Microbit.Image.fromRows([
  "99999",
  "99999",
  "99999",
  "99999",
  "99999",
]))
""")
    time.sleep(FLASH_DELAY_)
    self.clear()

##### End of section dedicated to micro:bit #####

##### Begin of section dedicated to the Ravel kit #####

def KitsClassPatch_(caller, owner):
#  return caller if caller != owner else owner.__base__
  return caller if caller != owner else owner.__bases__[0] # Workaround to Brython issue 'https://github.com/brython-dev/brython/issues/2663'.

class Ravel:
  class Ring(WS2812):
    def __new__(cls, offset=0, device=None, extra=True):
      return super().__new__(KitsClassPatch_(cls, Ravel.Ring), 8, 20, offset=offset, device=device, extra=extra)
      
  # class Buzzer(Buzzer):
  class Buzzer(globals()["Buzzer"]):  # Workaround to Brython issue 'https://github.com/brython-dev/brython/issues/2662'.
    def __new__(cls, device=None, extra=True):
      return super().__new__(KitsClassPatch_(cls, Ravel.Buzzer), PWM(5, device=device), extra=extra)

  class LCD(HD44780_I2C):
    def __new__(cls, device=None, extra=True):
      return super().__new__(KitsClassPatch_(cls, Ravel.LCD), 16, 2, SoftI2C(6, 7, device=device), extra=extra)
    
  class OLED(SSD1306_I2C):
    def __new__(cls, device=None, extra=True):
      return super().__new__(KitsClassPatch_(cls, Ravel.OLED), 128, 64, I2C(8, 9, device=device), extra=extra)

##### End of section dedicated to the Ravel kit #####
