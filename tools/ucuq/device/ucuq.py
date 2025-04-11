# MicroController Remote Server (runs on the µcontroller)
# Use of asyncio in prevision of the future handling of sensors.

import asyncio, sys, uos, time, network, json, binascii, io, ssl
from machine import Pin

WLAN = "" # Connect to one of the WLAN defined in 'ucuq.json'.
# WLAN = "<name>" # Connects to the WLAN <name> as defined in 'ucuq.json'.
# WLAN = ("<ssid>","<key>") # Connects to WLAN <ssid> using <key>.

with open("ucuq.json", "r") as config:
  CONFIG_ = json.load(config)

K_IDENTIFICATION = "Identification"
K_ONBOARD_LED = "OnBoardLed"
K_PROXY = "Proxy"
K_WIFI_POWER = "WifiPower"

DEFAULT_ONBOARD_LED = (None, True)
DEFAULT_PROXY = ("ucuq.q37.info", 53843, True)
DEFAULT_WIFI_POWER = [None]

def getConfig(key):
  return CONFIG_[key] if key in CONFIG_ else None

CONFIG_IDENTIFICATION = CONFIG_[K_IDENTIFICATION]
CONFIG_ONBOARD_LED = getConfig(K_ONBOARD_LED)
CONFIG_PROXY = getConfig(K_PROXY)
CONFIG_WIFI_POWER = getConfig(K_WIFI_POWER)

WLAN_FALLBACK_ = "q37"

PROTOCOL_LABEL_ = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION_ = "0"

# Connection status.
S_FAILURE_ = 0
S_SEARCHING_ = 1 # Search an available WLAN.
S_WLAN_ = 2 # Connecting to WLAN. There is a delay of 0.5 second between two calls.
S_UCUQ_ = 3 # Connecting to UCUq server.
S_SUCCESS_ = 4
S_DECONNECTION_ = 5

# Request
R_PING_ = 0
R_EXECUTE_ = 1

# Answer; must match in device.h: device::eAnswer.
A_RESULT_ = 0
A_SENSOR_ = 1
A_ERROR_ = 2
A_PUZZLED_ = 3
A_DISCONNECTED_ = 4

wifi = None

def getMacAddress_():
  global wifi
  if not wifi:
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True) # Otherwise the MAC address is NUL.
  return binascii.hexlify(network.WLAN(network.STA_IF).config('mac')).decode()

# NOTA: also used in the script for 'getInfos()'… 
def getIdentificationId_(identification):
  if isinstance(identification[1], str):
    return identification[1]
  else:
    mac = getMacAddress_()

    if mac in identification[1]:
      return identification[1][mac]
    else:
      raise Exception("Unable to get an id for this device.")

    
WLANS_ = CONFIG_["WLAN"]

def wlanIsShortcut_(wlan):
  if isinstance(wlan, str):
    return True
  elif isinstance(wlan, (list, tuple)) and len(wlan) == 2:
    return False
  else:
    raise TypeError("'wlan' parameter can only be a string (shortcut), a list or a tuple of 2 strings (SSID and key)")


def wlanGetKnownStation_(wifi, callback):
  known = ""
  tries = 0

  wifi.active(True)
  
  while not known:
    if not callback(S_SEARCHING_, tries):
      callback(S_FAILURE_, 0)
      exit_()
    
    for station in wifi.scan():
      if known:
        break
      for name in WLANS_:
        if known:
          break
        if station[0].decode("utf-8") == WLANS_[name][0]:
          known = name

    tries += 1
    time.sleep(0.5)

  return known


def wlanDisconnect_():
  wifi = network.WLAN(network.STA_IF)

  wifi.disconnect()

  while wifi.status() != network.STAT_IDLE:
    pass


def wlanConnect_(wlan, callback):
  global wifi

  wifi = network.WLAN(network.STA_IF)

  if not wifi.isconnected():
    if wlanIsShortcut_(wlan):
      if wlan == "":
        wlan = WLANS_[wlanGetKnownStation_(wifi, callback)]
      else:
        try:
          wlan = WLANS_[wlan]
        except KeyError:
          wlan = WLANS_[WLAN_FALLBACK_]

    tries = 0

    wifi.active(True)

    id = getIdentificationId_(CONFIG_IDENTIFICATION)

    # An ESP32-C3 supermini does not connect to WiFi with default WiFi power when plugged in a breadboard.
    # See https://www.reddit.com/r/arduino/comments/1dl6atc/esp32c3_boards_cant_connect_to_wifi_when_plugged/
    # RPi Pico does not support a float.
    wifiPowerParams = getEntry(CONFIG_WIFI_POWER, getIdentificationId_(CONFIG_IDENTIFICATION), DEFAULT_WIFI_POWER)

    if wifiPowerParams[0]:
      wifi.config(txpower=wifiPowerParams)

    wifi.connect(wlan[0], wlan[1])

    while not wifi.isconnected():
      time.sleep(0.5)
      if not callback(S_WLAN_, tries):
        return False
      tries += 1

  return True

IN = 0
OUT = 1

buffer_ = bytes()


async def recv_(size):
  global buffer_

  while len(buffer_) < size:
    buffer_ += await proxy[IN].read(4096)

  result = buffer_[:size]

  buffer_ = buffer_[size:]

  return result


async def send_(data):
  totalAmount = len(data)
  amountSent = 0

  while amountSent < totalAmount:
    amount = totalAmount - amountSent

    if amount > 4096:
      amount = 4096

    proxy[OUT].write(data[amountSent:amountSent + amount])	
    await proxy[OUT].drain()

    amountSent += amount


async def writeUInt_(value):
  result = bytes([value & 0x7f])
  value >>= 7

  while value != 0:
    result = bytes([(value & 0x7f) | 0x80]) + result
    value >>= 7

  await send_(result)


async def writeString_(string):
  bString = bytes(string, "utf-8")
  await writeUInt_(len(bString))
  await send_(bString)


def blockingWriteString_(string):
  return asyncio.run(writeString_(string))


async def readByte_():
  return ord(await recv_(1))


async def readUInt_():
  byte = await readByte_()
  value = byte & 0x7f

  while byte & 0x80:
    byte = await readByte_()
    value = (value << 7) + (byte & 0x7f)

  return value


async def readString_():
  size = await readUInt_()

  if size:
    return (await recv_(size)).decode("utf-8")
  else:
    return ""
  

def exit_(message=None):
  if (message):
    print(message, file=sys.stderr)

  sys.exit(-1)


def init(callback):
  global proxy
  proxyParam = getEntry(CONFIG_PROXY, getIdentificationId_(CONFIG_IDENTIFICATION), getEntry(CONFIG_PROXY, "_default", DEFAULT_PROXY))

  callback(S_UCUQ_, 0)

  try:
    proxy = asyncio.run(asyncio.open_connection(proxyParam[0], proxyParam[1], proxyParam[2]))
  except:
    return False
  else:
    return True
  

def getDeviceLabel_():
  return uos.uname().sysname


def blockingReadString_():
  return asyncio.run(readString_())


def handshake_():
  blockingWriteString_(PROTOCOL_LABEL_)
  blockingWriteString_(PROTOCOL_VERSION_)
  blockingWriteString_("Device")
  blockingWriteString_(getDeviceLabel_())

  error = blockingReadString_()

  if error:
    sys.exit(error)

  notification = blockingReadString_()

  if notification:
    print(notification)


def ignition_():
  blockingWriteString_(CONFIG_IDENTIFICATION[0])
  blockingWriteString_(getIdentificationId_(CONFIG_IDENTIFICATION))

  error = blockingReadString_()

  if error:
    sys.exit(error)

async def serve_():
  while True:
    request = await readUInt_()

    if request == R_EXECUTE_:
      script = await readString_()
      expression = await readString_()
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
          await writeUInt_(A_ERROR_)
          await writeString_(error)
      else:
        if expression:
          await writeUInt_(A_RESULT_)
          await writeString_(returned)
    else:
      await writeUInt_(A_PUZZLED_)
      await writeString_("")  # For future use


def defaultCallback_(status, tries):
  if tries == 0:
    if status != S_FAILURE_:
      print("\r                                                                                \r", end="")
    if status == S_SEARCHING_:
      print("Searching for available WLAN...", end="")
    elif status == S_WLAN_:
      print("Connecting to WLAN...", end="")
    elif status == S_UCUQ_:
      print("Connecting to UCUq server...", end="")
    elif status == S_SUCCESS_:
      print("", end="") # Erase line and go to the beginning of the line. 
  else:
    print(".", end="")

  if status == S_FAILURE_:
    print("FAILURE!!!")
  elif status == S_DECONNECTION_:
    print("Deconnection!")

  return True if tries <= 200 else False 


def handleLed_(pin, state, onValue):
  Pin(pin, Pin.OUT).value(1 if state == onValue else 0)


def ledBlink_(pin, count, onValue):
  for _ in range(count):
    handleLed_(pin, True, onValue)
    time.sleep(0.1)
    handleLed_(pin, False, onValue)
    time.sleep(0.1)


def ledCallback_(status, tries, pin, onValue):
  if status == S_SEARCHING_:
    ledBlink_(pin, 1, onValue)
  elif status == S_WLAN_:
    handleLed_(pin, not( tries % 2), onValue )
  elif status == S_UCUQ_:
    handleLed_(pin, False, onValue)
  elif status == S_FAILURE_:
    handleLed_(pin, True, onValue)
  elif status == S_DECONNECTION_:
    handleLed_(pin, True, onValue)
  elif status == S_SUCCESS_:
    ledBlink_(pin, 3, onValue)
  return defaultCallback_(status, tries) and not ( ( status == S_UCUQ_) and ( tries > 5 ) )

def complete(data, default):
    if data is None:
        return default  
    elif isinstance(data, (int, str, float)):  # Vérifie si 'data' est une donnée simple  
        return [data] + default[1:]  
    elif isinstance(data, (list, tuple)):  # Vérifie si 'data' est un tableau 
        return data + list(default[len(data):])
        return default  
    else:
        return default  # Retourne 'default' si 'data' n'est ni None, ni simple, ni un tableau


def getEntry(data, device, default):
    if not isinstance(data, (list, tuple)) or not all(isinstance(item, (list, tuple)) for item in data):
        return complete(data, default)  # Si 'data' n'est pas un tableau de tableaux, utilise A  
    else:
        for sublist in data:
            if device in sublist[1]:
                return complete(sublist[0], default)  # Appelle A avec le premier élément de la sous-liste  
        return default  # Retourne 'default' si aucune entrée correspondante n'existe


def getCallback_():
  onBoardLed = getEntry(CONFIG_ONBOARD_LED, getIdentificationId_(CONFIG_IDENTIFICATION), getEntry(CONFIG_ONBOARD_LED, "_default", DEFAULT_ONBOARD_LED))

  if onBoardLed[0]:
    return lambda status, tries: ledCallback_(status, tries, onBoardLed[0], onBoardLed[1])
    
  return defaultCallback_


def main():
  callback = getCallback_()

  if not wlanConnect_(WLAN, callback):
    callback(S_FAILURE_, 0)
    exit_()

  if not init(callback):
    if ( WLAN != "" ):
      callback(S_FAILURE_, 0)
      exit_()

    wlanDisconnect_()

    if not wlanConnect_(WLAN, callback):
      callback(S_FAILURE_, 0)
      exit_()

    if not init(callback):
      callback(S_FAILURE_, 0)
      exit_()

  callback(S_SUCCESS_, 0)

  handshake_()

  ignition_()

  try:
    asyncio.run(serve_())
  except Exception as exception:
    try:
      writeUInt_(A_DISCONNECTED_)
    except:
      pass
    getCallback_()(S_DECONNECTION_, 0)
    raise exception

main()
