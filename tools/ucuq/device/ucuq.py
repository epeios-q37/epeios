# MicroController Remote Server (runs on the µcontroller)

import asyncio, sys, uos, time, network, json, binascii, io
from machine import Pin

_WLAN = "" # Connects to one of the WLAN defined in 'ucuq.json'.
# _WLAN = "<name>" # Connects to the WLAN <name> as defined in 'ucuq.json'.
# _WLAN = ("<ssid>","<key>") # Connects to WLAN <ssid> using <key>.

with open("ucuq.json", "r") as config:
  CONFIG = json.load(config)

_K_IDENTIFICATION = "Identification"
_K_ONBOARD_LED = "OnBoardLed"
_K_PROXY = "Proxy"
_K_WIFI_POWER = "WifiPower"

_DEFAULT_ONBOARD_LED = (None, True)
_DEFAULT_PROXY = ("ucuq.q37.info", 53800, False)
_DEFAULT_WIFI_POWER = [None]

getConfig = lambda key: CONFIG[key] if key in CONFIG else None

_CONFIG_IDENTIFICATION = CONFIG[_K_IDENTIFICATION]
_CONFIG_ONBOARD_LED = getConfig(_K_ONBOARD_LED)
_CONFIG_PROXY = getConfig(_K_PROXY)
_CONFIG_WIFI_POWER = getConfig(_K_WIFI_POWER)

_WLAN_FALLBACK = "q37"

_PROTOCOL_LABEL = "c37cc83e-079f-448a-9541-5c63ce00d960"
_PROTOCOL_VERSION = "0"

# Connection status.
_S_FAILURE = const(0)
_S_SEARCHING = const(1) # Search an available WLAN.
_S_WLAN = const(2) # Connecting to WLAN. There is a delay of 0.5 second between two calls.
_S_UCUQ = const(3) # Connecting to UCUq server.
_S_SUCCESS = const(4)
_S_DECONNECTION = const(5)

# Request
_R_PING = const(0)  # Deprecated!
_R_EXECUTE = const(1)

# Answer; must match in device.h: device::eAnswer.
_A_RESULT = const(0)
_A_SENSOR = const(1)
_A_ERROR = const(2)
_A_PUZZLED = const(3)
_A_DISCONNECTED_ = const(4)

_P_READER = const(0)
_P_WRITER = const(1)

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

    
_WLANS = CONFIG["WLAN"]

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
    if not callback(_S_SEARCHING, tries):
      callback(_S_FAILURE, 0)
      exit()
    
    for station in wifi.scan():
      if known:
        break
      for name in _WLANS:
        if known:
          break
        if station[0].decode("utf-8") == _WLANS[name][0]:
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
        wlan = _WLANS[wlanGetKnownStation(wifi, callback)]
      else:
        try:
          wlan = _WLANS[wlan]
        except KeyError:
          wlan = _WLANS[_WLAN_FALLBACK]

    tries = 0

    wifi.active(True)

    id = getIdentificationId(_CONFIG_IDENTIFICATION)

    # An ESP32-C3 supermini does not connect to WiFi with default WiFi power when plugged in a breadboard.
    # See https://www.reddit.com/r/arduino/comments/1dl6atc/esp32c3_boards_cant_connect_to_wifi_when_plugged/
    # RPi Pico does not support a float.
    wifiPowerParams = getParams(_CONFIG_WIFI_POWER, getIdentificationId(_CONFIG_IDENTIFICATION), _DEFAULT_WIFI_POWER)

    if wifiPowerParams[0]:
      wifi.config(txpower=wifiPowerParams[0])

    wifi.connect(wlan[0], wlan[1])

    while not wifi.isconnected():
      time.sleep(0.5)
      if not callback(_S_WLAN, tries):
        return False
      tries += 1

  return True


async def recv(size):
  global buffer

  while len(buffer) < size:
    # With ESP8266 and SSL, returns always an empty buffer.
    buffer += await proxy[_P_READER].read(4096)

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

    proxy[_P_WRITER].write(data[amountSent:amountSent + amount])	
    await proxy[_P_WRITER].drain()

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


async def init_async(callback):
  global proxy

  proxyParam = getParams(_CONFIG_PROXY, getIdentificationId(_CONFIG_IDENTIFICATION), getParams(_CONFIG_PROXY, "_default", _DEFAULT_PROXY))

  callback(_S_UCUQ, 0)

  try:
    proxy = await asyncio.open_connection(proxyParam[0], proxyParam[1], proxyParam[2])
    return True
  except OSError:
    return False
  
  
def init(callback):
    return asyncio.run(init_async(callback))  


def getDeviceLabel():
  return uos.uname().sysname


def blockingReadString():
  return asyncio.run(readString())


def handshake():
  blockingWriteString(_PROTOCOL_LABEL)
  blockingWriteString(_PROTOCOL_VERSION)
  blockingWriteString("Device")
  blockingWriteString(getDeviceLabel())

  error = blockingReadString()

  if error:
    sys.exit(error)

  notification = blockingReadString()

  if notification:
    print(notification)


def ignition():
  blockingWriteString(_CONFIG_IDENTIFICATION[0])
  blockingWriteString(getIdentificationId(_CONFIG_IDENTIFICATION))

  error = blockingReadString()

  if error:
    sys.exit(error)


async def serve():
  while True:
    request = await readUInt()

    if request == _R_EXECUTE:
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
          await writeUInt(_A_ERROR)
          await writeString(error)
      else:
        if expression:
          await writeUInt(_A_RESULT)
          await writeString(returned)
    else:
      await writeUInt(_A_PUZZLED)
      await writeString("")  # For future use


def defaultCallback(status, tries):
  if tries == 0:
    if status != _S_FAILURE:
      print("\r                                                                                \r", end="")
    if status == _S_SEARCHING:
      print("Searching for available WLAN...", end="")
    elif status == _S_WLAN:
      print("Connecting to WLAN...", end="")
    elif status == _S_UCUQ:
      print("Connecting to UCUq server...", end="")
    elif status == _S_SUCCESS:
      print("", end="") # Erase line and go to the beginning of the line. 
  else:
    print(".", end="")

  if status == _S_FAILURE:
    print("FAILURE!!!")
  elif status == _S_DECONNECTION:
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
  if status == _S_SEARCHING:
    ledBlink(pin, 1, onValue)
  elif status == _S_WLAN:
    handleLed(pin, not( tries % 2), onValue )
  elif status == _S_UCUQ:
    handleLed(pin, False, onValue)
  elif status == _S_FAILURE:
    handleLed(pin, True, onValue)
  elif status == _S_DECONNECTION:
    handleLed(pin, True, onValue)
  elif status == _S_SUCCESS:
    ledBlink(pin, 3, onValue)
  return defaultCallback(status, tries) and not ( ( status == _S_UCUQ) and ( tries > 5 ) )


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
  onBoardLed = getParams(_CONFIG_ONBOARD_LED, getIdentificationId(_CONFIG_IDENTIFICATION), getParams(_CONFIG_ONBOARD_LED, "_default", _DEFAULT_ONBOARD_LED))

  if onBoardLed[0]:
    return lambda status, tries: ledCallback(status, tries, onBoardLed[0], onBoardLed[1])
    
  return defaultCallback


def main():
  callback = getCallback()

  if not wlanConnect(_WLAN, callback):
    callback(_S_FAILURE, 0)
    exit()

  if not init(callback):
    if ( _WLAN != "" ):
      callback(_S_FAILURE, 0)
      exit()

    wlanDisconnect()

    if not wlanConnect(_WLAN, callback):
      callback(_S_FAILURE, 0)
      exit()

    if not init(callback):
      callback(_S_FAILURE, 0)
      exit()

  callback(_S_SUCCESS, 0)

  handshake()

  ignition()

  try:
    asyncio.run(serve())
  except Exception as exception:
    try:
      writeUInt(_A_DISCONNECTED_)
    except:
      pass

    getCallback()(_S_DECONNECTION, 0)
    raise exception


main()
