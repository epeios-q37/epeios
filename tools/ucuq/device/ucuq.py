# MicroController Remote Server (runs on the µcontroller)

import asyncio, sys, uos, time, network, json, binascii, io
from machine import Pin

WLAN = "" # Connects to one of the WLAN defined in 'ucuq.json'.
# WLAN = "<name>" # Connects to the WLAN <name> as defined in 'ucuq.json'.
# WLAN = ("<ssid>","<key>") # Connects to WLAN <ssid> using <key>.

with open("ucuq.json", "r") as config:
  CONFIG = json.load(config)

K_IDENTIFICATION = "Identification"
K_ONBOARD_LED = "OnBoardLed"
K_PROXY = "Proxy"
K_WIFI_POWER = "WifiPower"

DEFAULT_ONBOARD_LED = (None, True)
DEFAULT_PROXY = ("ucuq.q37.info", 53800, False)
DEFAULT_WIFI_POWER = [None]

getConfig = lambda key: CONFIG[key] if key in CONFIG else None

CONFIG_IDENTIFICATION = CONFIG[K_IDENTIFICATION]
CONFIG_ONBOARD_LED = getConfig(K_ONBOARD_LED)
CONFIG_PROXY = getConfig(K_PROXY)
CONFIG_WIFI_POWER = getConfig(K_WIFI_POWER)

WLAN_FALLBACK = "q37"

PROTOCOL_LABEL = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION = "0"

# Connection status.
S_FAILURE = 0
S_SEARCHING = 1 # Search an available WLAN.
S_WLAN = 2 # Connecting to WLAN. There is a delay of 0.5 second between two calls.
S_UCUQ = 3 # Connecting to UCUq server.
S_SUCCESS = 4
S_DECONNECTION = 5

# Request
R_PING = 0  # Deprecated!
R_EXECUTE = 1

# Answer; must match in device.h: device::eAnswer.
A_RESULT = 0
A_SENSOR = 1
A_ERROR = 2
A_PUZZLED = 3
A_DISCONNECTED = 4

P_READER = 0
P_WRITER = 1

wifi = None
buffer = bytes()


def getMacAddress():
  global wifi
  if not wifi:
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True) # Otherwise the MAC address is NUL.
  return binascii.hexlify(network.WLAN(network.STA_IF).config('mac')).decode()


# NOTA: also used in the script for 'getInfos()'… 
def getIdentificationId(identification):
  if isinstance(identification[1], str):
    return identification[1]
  else:
    mac = getMacAddress()

    if mac in identification[1]:
      return identification[1][mac]
    else:
      raise Exception("Unable to get an id for this device.")

    
WLANS = CONFIG["WLAN"]

def wlanIsShortcut(wlan):
  if isinstance(wlan, str):
    return True
  elif isinstance(wlan, (list, tuple)) and len(wlan) == 2:
    return False
  else:
    raise TypeError("'wlan' parameter can only be a string (shortcut), a list or a tuple of 2 strings (SSID and key)")


def wlanGetKnownStation(wifi, callback):
  known = ""
  tries = 0

  wifi.active(True)
  
  while not known:
    if not callback(S_SEARCHING, tries):
      callback(S_FAILURE, 0)
      exit()
    
    for station in wifi.scan():
      if known:
        break
      for name in WLANS:
        if known:
          break
        if station[0].decode("utf-8") == WLANS[name][0]:
          known = name

    tries += 1
    time.sleep(0.5)

  return known


def wlanDisconnect():
  wifi = network.WLAN(network.STA_IF)

  wifi.disconnect()

  while wifi.status() != network.STAT_IDLE:
    pass


def wlanConnect(wlan, callback):
  global wifi

  wifi = network.WLAN(network.STA_IF)

  if not wifi.isconnected():
    if wlanIsShortcut(wlan):
      if wlan == "":
        wlan = WLANS[wlanGetKnownStation(wifi, callback)]
      else:
        try:
          wlan = WLANS[wlan]
        except KeyError:
          wlan = WLANS[WLAN_FALLBACK]

    tries = 0

    wifi.active(True)

    id = getIdentificationId(CONFIG_IDENTIFICATION)

    # An ESP32-C3 supermini does not connect to WiFi with default WiFi power when plugged in a breadboard.
    # See https://www.reddit.com/r/arduino/comments/1dl6atc/esp32c3_boards_cant_connect_to_wifi_when_plugged/
    # RPi Pico does not support a float.
    wifiPowerParams = getParams(CONFIG_WIFI_POWER, getIdentificationId(CONFIG_IDENTIFICATION), DEFAULT_WIFI_POWER)

    if wifiPowerParams[0]:
      wifi.config(txpower=wifiPowerParams[0])

    wifi.connect(wlan[0], wlan[1])

    while not wifi.isconnected():
      time.sleep(0.5)
      if not callback(S_WLAN, tries):
        return False
      tries += 1

  return True


async def recv(size):
  global buffer

  while len(buffer) < size:
    # With ESP8266 and SSL, returns always an empty buffer.
    buffer += await proxy[P_READER].read(4096)

  result = buffer[:size]

  buffer = buffer[size:]

  return result


async def send(data):
  totalAmount = len(data)
  amountSent = 0

  while amountSent < totalAmount:
    amount = totalAmount - amountSent

    if amount > 4096:
      amount = 4096

    proxy[P_WRITER].write(data[amountSent:amountSent + amount])	
    await proxy[P_WRITER].drain()

    amountSent += amount


async def writeUInt(value):
  result = bytes([value & 0x7f])
  value >>= 7

  while value != 0:
    result = bytes([(value & 0x7f) | 0x80]) + result
    value >>= 7

  await send(result)


async def writeString(string):
  bString = bytes(string, "utf-8")
  await writeUInt(len(bString))
  await send(bString)


def blockingWriteString(string):
  return asyncio.run(writeString(string))


async def readByte():
  return ord(await recv(1))


async def readUInt():
  byte = await readByte()
  value = byte & 0x7f

  while byte & 0x80:
    byte = await readByte()
    value = (value << 7) + (byte & 0x7f)

  return value


async def readString():
  size = await readUInt()

  if size:
    return (await recv(size)).decode("utf-8")
  else:
    return ""
  

def exit(message=None):
  if (message):
    print(message, file=sys.stderr)

  sys.exit(-1)


def init(callback):
  global proxy
  proxyParam = getParams(CONFIG_PROXY, getIdentificationId(CONFIG_IDENTIFICATION), getParams(CONFIG_PROXY, "_default", DEFAULT_PROXY))

  callback(S_UCUQ, 0)

  try:
    proxy = asyncio.run(asyncio.open_connection(proxyParam[0], proxyParam[1], proxyParam[2]))
  except:
    return False
  else:
    return True
  

def getDeviceLabel():
  return uos.uname().sysname


def blockingReadString():
  return asyncio.run(readString())


def handshake():
  blockingWriteString(PROTOCOL_LABEL)
  blockingWriteString(PROTOCOL_VERSION)
  blockingWriteString("Device")
  blockingWriteString(getDeviceLabel())

  error = blockingReadString()

  if error:
    sys.exit(error)

  notification = blockingReadString()

  if notification:
    print(notification)


def ignition():
  blockingWriteString(CONFIG_IDENTIFICATION[0])
  blockingWriteString(getIdentificationId(CONFIG_IDENTIFICATION))

  error = blockingReadString()

  if error:
    sys.exit(error)


async def serve():
  while True:
    request = await readUInt()

    if request == R_EXECUTE:
      script = await readString()
      expression = await readString()
      returned = ""
      try:
        exec(script)
        if expression:
          returned = json.dumps(eval(expression))
      except Exception as exception:
        with io.StringIO() as stream:
          sys.print_exception(exception, stream)
          error = stream.getvalue()
          print("Error: ", error)
          await writeUInt(A_ERROR)
          await writeString(error)
      else:
        if expression:
          await writeUInt(A_RESULT)
          await writeString(returned)
    else:
      await writeUInt(A_PUZZLED)
      await writeString("")  # For future use


def defaultCallback(status, tries):
  if tries == 0:
    if status != S_FAILURE:
      print("\r                                                                                \r", end="")
    if status == S_SEARCHING:
      print("Searching for available WLAN...", end="")
    elif status == S_WLAN:
      print("Connecting to WLAN...", end="")
    elif status == S_UCUQ:
      print("Connecting to UCUq server...", end="")
    elif status == S_SUCCESS:
      print("", end="") # Erase line and go to the beginning of the line. 
  else:
    print(".", end="")

  if status == S_FAILURE:
    print("FAILURE!!!")
  elif status == S_DECONNECTION:
    print("Deconnection!")

  return True if tries <= 200 else False 


def handleLed(pin, state, onValue):
  Pin(pin, Pin.OUT).value(1 if state == onValue else 0)


def ledBlink(pin, count, onValue):
  for _ in range(count):
    handleLed(pin, True, onValue)
    time.sleep(0.1)
    handleLed(pin, False, onValue)
    time.sleep(0.1)


def ledCallback(status, tries, pin, onValue):
  if status == S_SEARCHING:
    ledBlink(pin, 1, onValue)
  elif status == S_WLAN:
    handleLed(pin, not( tries % 2), onValue )
  elif status == S_UCUQ:
    handleLed(pin, False, onValue)
  elif status == S_FAILURE:
    handleLed(pin, True, onValue)
  elif status == S_DECONNECTION:
    handleLed(pin, True, onValue)
  elif status == S_SUCCESS:
    ledBlink(pin, 3, onValue)
  return defaultCallback(status, tries) and not ( ( status == S_UCUQ) and ( tries > 5 ) )


def completeParam(params, default):
  if params is None:
    return default  
  elif isinstance(params, (int, str, float)):
    return [params] + default[1:]  
  elif isinstance(params, (list, tuple)):
    return params + list(default[len(params):])
  else:
    return default


def getParams(paramSet, device, default):
  if not isinstance(paramSet, (list, tuple)) or not all(isinstance(item, (list, tuple)) for item in paramSet):
    return completeParam(paramSet, default)
  else:
    for params in paramSet:
      if device in params[1]:
        return completeParam(params[0], default)
    return default


def getCallback():
  onBoardLed = getParams(CONFIG_ONBOARD_LED, getIdentificationId(CONFIG_IDENTIFICATION), getParams(CONFIG_ONBOARD_LED, "_default", DEFAULT_ONBOARD_LED))

  if onBoardLed[0]:
    return lambda status, tries: ledCallback(status, tries, onBoardLed[0], onBoardLed[1])
    
  return defaultCallback


def main():
  callback = getCallback()

  if not wlanConnect(WLAN, callback):
    callback(S_FAILURE, 0)
    exit()

  if not init(callback):
    if ( WLAN != "" ):
      callback(S_FAILURE, 0)
      exit()

    wlanDisconnect()

    if not wlanConnect(WLAN, callback):
      callback(S_FAILURE, 0)
      exit()

    if not init(callback):
      callback(S_FAILURE, 0)
      exit()

  callback(S_SUCCESS, 0)

  handshake()

  ignition()

  try:
    asyncio.run(serve())
  except Exception as exception:
    try:
      writeUInt(A_DISCONNECTED)
    except:
      pass

    getCallback()(S_DECONNECTION, 0)
    raise exception


main()
