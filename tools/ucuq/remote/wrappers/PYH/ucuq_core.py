import os, json, socket, sys, threading, datetime, time, threading
from inspect import getframeinfo, stack

CONFIG_FILE = ( "/home/csimon/q37/epeios/tools/ucuq/remote/wrappers/PYH/" if "Q37_EPEIOS" in os.environ else "../" ) + "ucuq.json"
DEFAULT_COMMIT = False

try:
  with open(CONFIG_FILE, "r") as config:
    CONFIG = json.load(config)
except:
  CONFIG = None

UCUQ_DEFAULT_HOST_ = "ucuq.q37.info"
UCUQ_DEFAULT_PORT_ = "53800"

UCUQ_HOST_ = CONFIG["Proxy"]["Host"] if CONFIG and "Proxy" in CONFIG and "Host" in CONFIG["Proxy"] and CONFIG["Proxy"]["Host"] else UCUQ_DEFAULT_HOST_

# only way to test if the entry contains a valid int.
try:
  UCUQ_PORT_ = int(CONFIG["Proxy"]["Port"])
except:
  UCUQ_PORT_ = int(UCUQ_DEFAULT_PORT_)

PROTOCOL_LABEL_ = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION_ = "0"

uuid_ = 0
device_ = None
_writeLock = threading.Lock()

ITEMS_ = "i_"

# Request
R_EXECUTE_ = "Execute_1"
R_UPLOAD_ = "Upload_1"

# Answer
# Answer; must match in device.h: device::eAnswer.
A_RESULT_ = 0
A_SENSOR_ = 1
A_ERROR_ = 2
A_PUZZLED_ = 3
A_DISCONNECTED_ = 4


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


def ignition_(socket, token, deviceId, errorAsException):
  writeString_(socket, token)
  writeString_(socket, deviceId)

  error = readString_(socket)

  if error:
    if errorAsException:
      raise Error(error)
    else:
      return False
    
  return True


def connect_(token, deviceId, errorAsException):
  socket = init_()
  handshake_(socket)
  if ignition_(socket, token, deviceId, errorAsException):
    return socket
  else:
    return None


class Error(Exception):
  pass

def commit(expression=""):
  return getDevice_().commit(expression)

def sleep(secs):
  return getDevice_().sleep(secs)

def displayExitMessage_(Message):
  raise Error(Message)


def readThread(socket, resultBegin, resultEnd):
  while True:
    if ( answer := readUInt_(socket) ) == A_RESULT_:
      resultBegin.set()
      resultEnd.wait()
      resultEnd.clear()
    elif answer == A_SENSOR_:
      raise Error("Sensor handling not yet implemented!")
    elif answer == A_ERROR_:
      result = readString_(socket)
      print(f"\n>>>>>>>>>> ERROR FROM DEVICE BEGIN <<<<<<<<<<")
      print("Timestamp: ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
      caller = getframeinfo(stack()[1][0])
      print(f"Caller: {caller.filename}:{caller.lineno}")
      print(f">>>>>>>>>> ERROR FROM DEVICE CONTENT <<<<<<<<<<")
      print(result)
      print(f">>>>>>>>>> END ERROR FROM DEVICE END <<<<<<<<<<")
      sys.exit(0)
    elif answer == A_PUZZLED_:
      readString_(socket) # For future use
      raise Error("Puzzled!")
    elif answer == A_DISCONNECTED_:
        raise Error("Disconnected from device!")
    else:
      raise Error("Unknown answer from device!")


class Device_:
  def __init__(self, *, id = None, token = None):
    self.socket_ = None

    if id or token:
      self.connect(id, token)

  def connect(self, id = None, token = None, errorAsException = True):
    if token == None and id == None:
      token, id = handlingConfig_(token, id)

    self.token = token if token else ALL_DEVICES_VTOKEN
    self.id = id if id else ""

    self.socket_ = connect_(self.token, self.id, errorAsException = errorAsException)

    if self.socket_ != None:
      self.resultBegin_ = threading.Event()
      self.resultEnd_ = threading.Event()
      threading.Thread(target = readThread, args=(self.socket_, self.resultBegin_, self.resultEnd_)).start()
      return True
    else:
      return False
    

  def upload(self, modules):
    writeString_(self.socket_, R_UPLOAD_)
    writeStrings_(self.socket_, modules)


  def execute_(self, script, expression = ""):
    if self.socket_:
      writeString_(self.socket_, R_EXECUTE_)
      writeString_(self.socket_, script)
      writeString_(self.socket_, expression)

      if expression:
        self.resultBegin_.wait()
        self.resultBegin_.clear()
        result = readString_(self.socket_)
        self.resultEnd_.set()

        if result:
          return json.loads(result)
        else:
          return None


class Device(Device_):
  def __init__(self, *, id = None, token = None):
    self.pendingModules = ["Init-1"]
    self.handledModules = []
    self.commands = []

    super().__init__(id = id, token = token)

  def addModule(self, module):
    if not module in self.pendingModules and not module in self.handledModules:
      self.pendingModules.append(module)

  def addModules(self, modules):
    if isinstance( modules, str):
      self.addModule(modules)
    else:
      for module in modules:
        self.addModule(module)

  def addCommand(self, command, commit = None):
    self.commands.append(command)

    if commit == None and DEFAULT_COMMIT:
      self.commit()

  def commit(self, expression = ""):
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
    

def getDemoDevice():
  device = Device()

  if device.connect(token = ONE_DEVICE_VTOKEN, errorAsException = False):
    return device
  else:
    return None   

def setDefaultCommit(value=True):
  global DEFAULT_COMMIT
  
  DEFAULT_COMMIT = value
