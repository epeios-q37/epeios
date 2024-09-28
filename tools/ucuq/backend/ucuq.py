# MicroController Remove Server (runs on the µcontroller)

WLAN = "" # Search for one of the WLAN defined in 'wireless.py' and connect to it if available.
# WLAN = "<name>" # Connects to the WLAN <name> as defined in 'wireless.py'.
# WLAN = ("<ssid>","<key>") # Connects to WLAN <ssid> using <key>.

UCUQ_ADDRESS_ = "ucuq.q37.info"
UCUQ_ADDRESS_ = "192.168.1.87" # dev
UCUQ_PORT_ = 53800

import socket, sys, _thread, uos, time, network, json
from machine import Pin

WLAN_FALLBACK_ = "q37"

PROTOCOL_LABEL_ = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION_ = "0"

# Connection status.
S_FAILURE = 0
S_SEARCHING = 1 # Search an available WLAN.
S_WLAN = 2 # Connecting to WLAN. There is a delay of 0.5 second between tow calls.
S_UCUQ = 3 # Connecting to UCUq server. 
S_SUCCESS = 4


with open("ucuq.json", "r") as config:
  CONFIG = json.load(config)

WLANS = CONFIG["WLAN"]["Known"]

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

  while not known:
    if not callback(S_SEARCHING, tries):
      callback(S_FAILURE, 0)
      exit_()
    
    wifi.active(True)

    for station in wifi.scan():
      if known:
        break
      for name in WLANS:
        if known:
          break
        if station[0].decode("utf-8") == WLANS[name][0]:
          known = name

    tries += 1

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
        wlan = WLANS[wlanGetKnownStation_(wifi, callback)]
      else:
        try:
          wlan = WLANS[wlan]
        except KeyError:
          wlan = WLANS[WLAN_FALLBACK_]

    tries = 0

    wifi.active(True)

    wifi.connect(wlan[0], wlan[1])

    while not wifi.isconnected():
      time.sleep(0.5)
      if not callback(S_WLAN, tries):
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


def getString_():
  size = readUInt_()

  if size:
    return recv_(size).decode("utf-8")
  else:
    return ""
  

def exit_(message=None):
  if (message):
    print(message, file=sys.stderr)

  sys.exit(-1)


def init_(address, port):
  global socket_

  socket_ = socket.socket()

  try:
    socket_.connect(socket.getaddrinfo(address, port)[0][-1])
  except:
    return False

  return True
  

def handshake_():
  with _writeLock:
    writeString_(PROTOCOL_LABEL_)
    writeString_(PROTOCOL_VERSION_)
    writeString_("Backend")
    writeString_(uos.uname().sysname)

  error = getString_()

  if error:
    sys.exit(error)

  notification = getString_()

  if notification:
    print(notification)


def ignition_():
  print("Token handling to come...")


def serve_():
  while True:
    command = getString_()

    try:
      exec(command)
    except:
      pass


def defaultCallback_(status, tries):
  if tries == 0:
    if status != S_FAILURE:
      print("\r                                        \r", end="")
    if status == S_SEARCHING:
      print("Searching for available WLAN...", end="")
    elif status == S_WLAN:
      print("Connecting to WLAN...", end="")
    elif status == S_UCUQ:
      print("Connecting to UCUq server...", end="")
    elif status == S_SUCCESS:
      print()
  else:
    print(".", end="")

  if status == S_FAILURE:
    print("FAILURE!!!")

  return True if tries <= 20 else False 


def picoLed_(on):
  Pin("LED", Pin.OUT).value(1 if on else 0)


def picoCallback_(status, tries):
  if status == S_SEARCHING:
    picoLed_(True)
    time.sleep(0.1)
    picoLed_(False)
  elif status == S_WLAN:
    picoLed_(tries % 2)
  elif status == S_UCUQ:
    picoLed_(False)
  elif status == S_FAILURE:
    picoLed_(True)
  elif status == S_SUCCESS:
    picoLed_(False)

  return defaultCallback_(status, tries)


CALLBACKS_ = {
  "rp2": picoCallback_
}


def getCallback_():
  deviceName = uos.uname().sysname

  return CALLBACKS_[deviceName] if deviceName in CALLBACKS_ else defaultCallback_ 

def main():
  callback = getCallback_()

  if not wlanConnect_(WLAN, callback):
    callback(S_FAILURE, 0)
    exit_()

  callback(S_UCUQ, 0)

  if init_(UCUQ_ADDRESS_, UCUQ_PORT_):
    callback(S_SUCCESS, 0)
  else:
    if ( WLAN != "" ):
      callback(S_FAILURE, 0)
      exit_()

    wlanDisconnect_()

    if not wlanConnect_(WLAN, callback):
      callback(S_FAILURE, 0)
      exit_()

    callback(S_UCUQ, 0)

    if not init_(UCUQ_ADDRESS_, UCUQ_PORT_):
        callback(S_FAILURE, 0)
        exit_()

  callback(S_SUCCESS, 0)

  handshake_()

  ignition_()

  serve_()

main()