# MicroController Remove Server (runs on the µcontroller)

import socket, sys, _thread, uos, time, network, json, binascii, io, select
from machine import Pin


WLAN = "" # Search for one of the WLAN defined in 'wireless.py' and connect to it if available.
# WLAN = "<name>" # Connects to the WLAN <name> as defined in 'wireless.py'.
# WLAN = ("<ssid>","<key>") # Connects to WLAN <ssid> using <key>.

with open("ucuq.json", "r") as config:
  CONFIG_ = json.load(config)

SELECTOR_ = CONFIG_["Selector"]

UCUQ_DEFAULT_HOST_ = "ucuq.q37.info"
UCUQ_DEFAULT_PORT_ = "53800"

UCUQ_HOST_ = CONFIG_["Proxy"]["Host"] if "Proxy" in CONFIG_ and "Host" in CONFIG_["Proxy"] and CONFIG_["Proxy"]["Host"] else UCUQ_DEFAULT_HOST_

# only way to test if the entry contains a valid int.
try:
  UCUQ_PORT_ = int(CONFIG_["Proxy"]["Port"])
except:
  UCUQ_PORT_ = int(UCUQ_DEFAULT_PORT_)

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

# Answer
A_OK_ = 0
A_ERROR_ = 1
A_PUZZLED_ = 2
A_DISCONNECTED_ = 3  # Never returned bu backend, only here as placeholder

def getMacAddress_():
  return binascii.hexlify(network.WLAN(network.STA_IF).config('mac')).decode()


def getSelectorId_(selector):
  if isinstance(selector[1], str):
    return selector[1]
  else:
    mac = getMacAddress_()

    if mac in selector[1]:
      return selector[1][mac]
    else:
      raise Exception("Unable to get an id for this device.")

    
WLANS_ = CONFIG_["WLAN"]["Known"]

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

    wifi.connect(wlan[0], wlan[1])

    while not wifi.isconnected():
      time.sleep(0.5)
      if not callback(S_WLAN_, tries):
        return False
      tries += 1

  return True


_writeLock = _thread.allocate_lock()

def recv_(size):
  global socket_

  buffer = bytes()
  l = 0

  while l != size:
    buffer += socket_.recv(size-l)
    l = len(buffer)

  return buffer


def send_(value):
  global socket_

  totalAmount = len(value)
  amountSent = 0

  while amountSent < totalAmount:
    amountSent += socket_.send(value[amountSent:])	


def writeUInt_(value):
  result = bytes([value & 0x7f])
  value >>= 7

  while value != 0:
    result = bytes([(value & 0x7f) | 0x80]) + result
    value >>= 7

  send_(result)


def writeString_(string):
  bString = bytes(string, "utf-8")
  writeUInt_(len(bString))
  send_( bString)


def readByte_():
  return ord(recv_(1))


def readUInt_():
  byte = readByte_()
  value = byte & 0x7f

  while byte & 0x80:
    byte = readByte_()
    value = (value << 7) + (byte & 0x7f)

  return value


def readString_():
  size = readUInt_()

  if size:
    return recv_(size).decode("utf-8")
  else:
    return ""
  

def exit_(message=None):
  if (message):
    print(message, file=sys.stderr)

  sys.exit(-1)


def init_(host, port, callback):
  global socket_
  cont = True
  tries = 0

  socket_ = socket.socket()

  callback(S_UCUQ_, 0)

  try:
    socket_.connect(socket.getaddrinfo(host, port)[0][-1])
  except:
    return False
  else:
    return True


def handshake_():
  with _writeLock:
    writeString_(PROTOCOL_LABEL_)
    writeString_(PROTOCOL_VERSION_)
    writeString_("Backend")
    writeString_(uos.uname().sysname)

  error = readString_()

  if error:
    sys.exit(error)

  notification = readString_()

  if notification:
    print(notification)


def ignition_():
  writeString_(SELECTOR_[0])
  writeString_(getSelectorId_(SELECTOR_))

  error = readString_()

  if error:
    sys.exit(error)

def serve_():
  while True:
    request = readUInt_()

    if request == R_PING_:
      writeUInt_(A_OK_)
      writeString_("")  # For future use.
    elif request == R_EXECUTE_:
      script = readString_()
      expression = readString_()
      returned = ""

      try:
        exec(script)
        if expression:
          returned = json.dumps(eval(expression))
      except Exception as exception:
        with io.StringIO() as stream:
          sys.print_exception(exception, stream)
          writeUInt_(A_ERROR_)
          writeString_(stream.getvalue())
      else:
        writeUInt_(A_OK_)
        writeString_(returned)
        print(returned)
    else:
      writeUInt_(A_PUZZLED_)
      writeString_("")  # For future use


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
    handleLed_(pin, True), onValue
  elif status == S_SUCCESS_:
    ledBlink_(pin, 3, onValue)
  return defaultCallback_(status, tries) and not ( ( status == S_UCUQ_) and ( tries > 5 ) )


CALLBACKS_ = {
  "rp2": lambda status, tries: ledCallback_(status, tries, "LED", True),
  "esp32": lambda status, tries: ledCallback_(status, tries, CONFIG_["OnBoardLed"][getSelectorId_(SELECTOR_)][0], CONFIG_["OnBoardLed"][getSelectorId_(SELECTOR_)][1])
}


def getCallback_():
  deviceName = uos.uname().sysname

  return CALLBACKS_[deviceName] if deviceName in CALLBACKS_ else defaultCallback_ 

def main():
  callback = getCallback_()

  if not wlanConnect_(WLAN, callback):
    callback(S_FAILURE_, 0)
    exit_()

  if not init_(UCUQ_HOST_, UCUQ_PORT_, callback):
    if ( WLAN != "" ):
      callback(S_FAILURE_, 0)
      exit_()

    wlanDisconnect_()

    if not wlanConnect_(WLAN, callback):
      callback(S_FAILURE_, 0)
      exit_()

    if not init_(UCUQ_HOST_, UCUQ_PORT_, callback):
      callback(S_FAILURE_, 0)
      exit_()

  callback(S_SUCCESS_, 0)

  handshake_()

  ignition_()

  try:
    serve_()
  except Exception as exception:
    try:
      writeUInt_(A_DISCONNECTED_)
    except:
      pass
    getCallback_()(S_DECONNECTION_, 0)
    raise exception

main()