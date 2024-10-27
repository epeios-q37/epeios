import os, json, socket, sys, threading, io, datetime, uuid
from inspect import getframeinfo, stack

CONFIG_FILE = ( "/home/csimon/q37/epeios/tools/ucuq/remote/wrappers/PYH/" if "Q37_EPEIOS" in os.environ else "../" ) + "ucuq.json"

if not os.path.isfile(CONFIG_FILE):
  print("Please launch the 'Config' app first to set the device to use!")
  sys.exit(0)

with open(CONFIG_FILE, "r") as config:
  CONFIG_ = json.load(config)

DEVICE_ = CONFIG_["Device"]

UCUQ_DEFAULT_HOST_ = "ucuq.q37.info"
UCUQ_DEFAULT_PORT_ = "53800"

UCUQ_HOST_ = CONFIG_["Proxy"]["Host"] if "Proxy" in CONFIG_ and "Host" in CONFIG_["Proxy"] and CONFIG_["Proxy"]["Host"] else UCUQ_DEFAULT_HOST_

# only way to test if the entry contains a valid int.
try:
  UCUQ_PORT_ = int(CONFIG_["Proxy"]["Port"])
except:
  UCUQ_PORT_ = int(UCUQ_DEFAULT_PORT_)

PROTOCOL_LABEL_ = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION_ = "0"

_writeLock = threading.Lock()

# Request
R_PING_ = "Ping_1"
R_EXECUTE_ = "Execute_1"
R_UPLOAD_ = "Upload_1"

# Answer
A_OK_ = 0
A_ERROR_ = 1
A_PUZZLED_ = 2
A_DISCONNECTED = 3

def GetUUID():
  return uuid.uuid4()

def recv_(socket, size):
  buffer = bytes()
  l = 0

  while l != size:
    buffer += socket.recv(size-l)
    l = len(buffer)

  return buffer


def send_(socket, value):
  totalAmount = len(value)
  amountSent = 0

  while amountSent < totalAmount:
    amountSent += socket.send(value[amountSent:])


def writeUInt_(socket, value):
  result = bytes([value & 0x7f])
  value >>= 7

  while value != 0:
    result = bytes([(value & 0x7f) | 0x80]) + result
    value >>= 7

  send_(socket, result)


def writeString_(socket, string):
  bString = bytes(string, "utf-8")
  writeUInt_(socket, len(bString))
  send_(socket, bString)


def writeStrings_(socket, strings):
  writeUInt_(socket, len(strings))

  for string in strings:
    writeString_(socket, string)


def readByte_(socket):
  return ord(recv_(socket, 1))


def readUInt_(socket):
  byte = readByte_(socket)
  value = byte & 0x7f

  while byte & 0x80:
    byte = readByte_(socket)
    value = (value << 7) + (byte & 0x7f)

  return value


def readString_(socket):
  size = readUInt_(socket)

  if size:
    return recv_(socket, size).decode("utf-8")
  else:
    return ""


def exit_(message=None):
  if message:
    print(message, file=sys.stderr)
  sys.exit(-1)


def init_():
  s = socket.socket()

  print("Connection to UCUq server…", end="", flush=True)

  try:
    s.connect((UCUQ_HOST_, UCUQ_PORT_))
  except Exception as e:
    raise e
  else:
    print("\r                                         \r",end="")

  return s


def handshake_(socket):
  with _writeLock:
    writeString_(socket, PROTOCOL_LABEL_)
    writeString_(socket, PROTOCOL_VERSION_)
    writeString_(socket, "Remote")
    writeString_(socket, "PYH")

  error = readString_(socket)

  if error:
    sys.exit(error)

  notification = readString_(socket)

  if notification:
    pass
    # print(notification)


def getTokenAndId_(deviceId):
  return DEVICE_["Token"], DEVICE_["Id"] if deviceId == "" else deviceId


def ignition_(socket, token, deviceId):
  writeString_(socket, token)
  writeString_(socket, deviceId)

  error = readString_(socket)

  if error:
    raise Error(error)


def connect_(token, deviceId):
  socket = init_()
  handshake_(socket)
  ignition_(socket, token, deviceId)

  return socket


class Error(Exception):
  pass


class UCUq_:
  def connect_(self, deviceId):
    self.token, self.deviceId = getTokenAndId_(deviceId)
    self.socket_ = connect_(self.token, self.deviceId)


  def __init__(self, deviceId = None, dryRun=False):
    if ( deviceId != None ) and not dryRun:
      self.connect_(deviceId)

    self.dryRun_ = dryRun


  def connect(self, deviceId = None):
    if not self.dryRun_:
      try:
        self.connect_(deviceId if deviceId != None else "")
      except:
        self.dryRun_ = True
        return False
      else:
        return True


  def getTokenAndDeviceId(self):
    return self.token, self.deviceId


  def getToken(self):
    return self.getTokenAndDeviceId()[0]


  def getDeviceId(self):
    return self.getTokenAndDeviceId()[1]


  def upload(self, scripts):
    if self.dryRun_:
      print(scripts)
    else:
      writeString_(self.socket_, R_UPLOAD_)
      writeStrings_(self.socket_, scripts)

      if ( answer := readUInt_(self.socket_) ) == A_OK_:
        pass
      elif answer == A_ERROR_:
        result = readString_(self.socket_)
        print(f"\n>>>>>>>>>> ERROR FROM DEVICE BEGIN <<<<<<<<<<")
        print("Timestamp: ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
        caller = getframeinfo(stack()[1][0])
        print(f"Caller: {caller.filename}:{caller.lineno}")
        print(f">>>>>>>>>> ERROR FROM DEVICE CONTENT <<<<<<<<<<")
        print(result)
        print(f">>>>>>>>>> END ERROR FROM DEVICE END <<<<<<<<<<")
      elif answer == A_PUZZLED_:
        readString_(self.socket_) # For future use
        raise Error("Puzzled!")
      elif answer == A_DISCONNECTED:
          raise Error("Disconnected from DEVICE!")
      else:
        raise Error("Unknown answer from device!")


  def execute(self, script, expression = ""):
    if self.dryRun_:
      print(script)
    elif self.socket_:
      writeString_(self.socket_, R_EXECUTE_)
      writeString_(self.socket_, script)
      writeString_(self.socket_, expression)

      if ( answer := readUInt_(self.socket_) ) == A_OK_:
        if result := readString_(self.socket_):
          return json.loads(result)
        else:
          return None
      elif answer == A_ERROR_:
        result = readString_(self.socket_)
        print(f"\n>>>>>>>>>> ERROR FROM DEVICE BEGIN <<<<<<<<<<")
        print("Timestamp: ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
        caller = getframeinfo(stack()[1][0])
        print(f"Caller: {caller.filename}:{caller.lineno}")
        print(f">>>>>>>>>> ERROR FROM DEVICE CONTENT <<<<<<<<<<")
        print(result)
        print(f">>>>>>>>>> END ERROR FROM DEVICE END <<<<<<<<<<")
      elif answer == A_PUZZLED_:
        readString_(self.socket_) # For future use
        raise Error("Puzzled!")
      elif answer == A_DISCONNECTED:
          raise Error("Disconnected from DEVICE!")
      else:
        raise Error("Unknown answer from device!")


  def ping(self):
    writeString_(self.socket_, R_PING_)

    if ( answer := readUInt_(self.socket_) ) == A_OK_:
      readString_(self.socket_) # For future use
    elif answer == A_ERROR_:
      raise Error("Unexpected response from device!")
    elif answer == A_PUZZLED_:
      readString_(self.socket_) # For future use
      raise Error("Puzzled!")
    elif answer == A_DISCONNECTED:
        raise Error("Disconnected from device!")
    else:
      raise Error("Unknown answer from device!")
    
class UCUq(UCUq_):
  def __init__(self, deviceId = None, dryRun = False):
    super().__init__(deviceId, dryRun)
    self.pendingScripts = ["Init"]
    self.handledScripts = []
    self.commands = []

  def connect(self, deviceId = None):
    super().connect(deviceId)

  def addScript(self, script):
    if not script in self.pendingScripts and not script in self.handledScripts:
      self.pendingScripts.append(script)

  def addCommand(self, command):
    if not command in self.commands:
      self.commands.append(command)

  def render(self):
    if self.pendingScripts:
      super().upload(self.pendingScripts)
      self.handledScripts.extend(self.pendingScripts)
      self.pendingScripts = []

    if self.commands:
      super().execute('\n'.join(self.commands))
      self.commands = []

class Core_:
  def __init__(self, ucuq, script):
    self.ucuq = ucuq
    self.ucuq.addScript(script)
    self.id = None

  def __del__(self):
    if self.id:
      self.addCommand(f"del ucuqObjects['{self.id}']")

  def init(self):
    self.id = GetUUID()

  def getObject(self):
    return f"ucuqObjects['{self.id}']"
  
  def addCommand(self, command):
    self.ucuq.addCommand(command)
  


class GPIO(Core_):
  def __init__(self, ucuq, pin = None):
    super().__init__(ucuq, "GPIO")

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


class HT16K33(Core_):
  def __init__(self, ucuq, sda = None, scl = None):
    super().__init__(ucuq, "HT16K33")

    if bool(sda) != bool(scl):
      raise Exception("None or both of sda/scl must be defined!")
    elif sda:
      self.init(sda, scl)

  def init(self, sda, scl):
    super().init()

    self.ucuq.addCommand(f"{self.getObject()} = HT16K33(I2C(0, scl=Pin({scl}), sda=Pin({sda})))")
    self.ucuq.addCommand(f"{self.getObject()}.set_brightness(0)")

  def draw(self, motif):
    self.ucuq.addCommand(f"{self.getObject()}.clear().draw('{motif}').render()")

  