import os, json, socket, sys, threading, datetime
from inspect import getframeinfo, stack

CONFIG_FILE = ( "/home/csimon/q37/epeios/tools/ucuq/remote/wrappers/PYH/" if "Q37_EPEIOS" in os.environ else "../" ) + "ucuq.json"

if not os.path.isfile(CONFIG_FILE):
  print("Please launch the 'Config' app first to set the device to use!")
  sys.exit(0)

with open(CONFIG_FILE, "r") as config:
  CONFIG_ = json.load(config)

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

uuid_ = 0
device_ = None
_writeLock = threading.Lock()

ITEMS_ = "i_"

# Request
R_PING_ = "Ping_1"
R_EXECUTE_ = "Execute_1"
R_UPLOAD_ = "Upload_1"

# Answer
A_OK_ = 0
A_ERROR_ = 1
A_PUZZLED_ = 2
A_DISCONNECTED = 3

def GetUUID_():
  global uuid_

  uuid_ += 1

  return uuid_

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

def render(expression=""):
  return getDevice_().render(expression)

def sleep(secs):
  return getDevice_().sleep(secs)

def getTokenAndDeviceId():
  return getDevice_().getTokenAndDeviceId()

def getToken():
  return getDevice_().getToken()

def getDeviceId():
  return getDevice_().getDeviceId()


CONFIG_DEVICE_ENTRY = "Device"
CONFIG_DEVICE_TOKEN_ENTRY = "Token"
CONFIG_DEVICE_ID_ENTRY = "Id"

def displayMissingConfigMessage_():
  raise Error("Please launch the 'Config' app first to set the device to use!")

def handlingConfig_(token, id):
  if CONFIG_DEVICE_ENTRY not in CONFIG_:
    displayMissingConfigMessage_()

  device = CONFIG_[CONFIG_DEVICE_ENTRY]

  if token == None:
    if CONFIG_DEVICE_TOKEN_ENTRY not in device:
      displayMissingConfigMessage_()

    token = device[CONFIG_DEVICE_TOKEN_ENTRY]

  if id == None:
    if CONFIG_DEVICE_ID_ENTRY not in device:
      displayMissingConfigMessage_()

    id = device[CONFIG_DEVICE_ID_ENTRY]

  return token, id


class Device_:
  def __init__(self, /, id = None, token = None, now = True):
    self.socket_ = None

    if now:
      self.connect(id, token)

  def connect(self, id, token):
    if token == None or id == None:
      token, id = handlingConfig_(token, id)

    self.token = token
    self.id = id

    self.socket_ = connect_(self.token, self.id)

  def getTokenAndDeviceId(self):
    return self.token, self.id

  def getToken(self):
    return self.getTokenAndDeviceId()[0]

  def getDeviceId(self):
    return self.getTokenAndDeviceId()[1]

  def upload(self, modules):
    writeString_(self.socket_, R_UPLOAD_)
    writeStrings_(self.socket_, modules)

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
      sys.exit(0)
    elif answer == A_PUZZLED_:
      readString_(self.socket_) # For future use
      raise Error("Puzzled!")
    elif answer == A_DISCONNECTED:
        raise Error("Disconnected from device!")
    else:
      raise Error("Unknown answer from device!")


  def execute_(self, script, expression = ""):
    if self.socket_:
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
        sys.exit(0)
      elif answer == A_PUZZLED_:
        readString_(self.socket_) # For future use
        raise Error("Puzzled!")
      elif answer == A_DISCONNECTED:
          raise Error("Disconnected from device!")
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
    
    
class Device(Device_):
  def __init__(self, /, id = None, token = None, now = True):
    self.pendingModules = ["Init"]
    self.handledModules = []
    self.commands = []

    super().__init__(id, token, now)

  def addModule(self, module):
    if not module in self.pendingModules and not module in self.handledModules:
      self.pendingModules.append(module)

  def addCommand(self, command):
    self.commands.append(command)

  def render(self, expression = ""):
    result = ""

    if self.pendingModules:
      super().upload(self.pendingModules)
      self.handledModules.extend(self.pendingModules)
      self.pendingModules = []

    if self.commands or expression:
      result = super().execute_('\n'.join(self.commands), expression)
      self.commands = []

    return result
  
  def sleep(self, secs):
    self.addCommand(f"time.sleep({secs})")

