import datetime, http, os, json, socket, ssl, sys, threading, urllib
from inspect import getframeinfo, stack


CONFIG_FILE_ = ( "/home/csimon/q37/epeios/other/BPY/Apps/UCUq/" if "Q37_EPEIOS" in os.environ else "../" ) + "ucuq.json"
KITS_FILE_ = ( "/home/csimon/epeios/other/BPY/Apps/UCUq/" if "Q37_EPEIOS" in os.environ else "../" ) + "kits.json"

try:
  with open(CONFIG_FILE_, "r") as config:
    CONFIG_ = json.load(config)
except:
  CONFIG_ = None


try:
  with open(KITS_FILE_, "r") as kits:
    KITS_ = json.load(kits)
except:
  KITS_ = None


UCUQ_DEFAULT_HOST_ = "ucuq.q37.info"
UCUQ_DEFAULT_PORT_ = "53843"
UCUQ_DEFAULT_SSL_ = True

UCUQ_HOST_ = CONFIG_["Proxy"]["Host"] if CONFIG_ and "Proxy" in CONFIG_ and "Host" in CONFIG_["Proxy"] and CONFIG_["Proxy"]["Host"] else UCUQ_DEFAULT_HOST_

# only way to test if the entry contains a valid int.
try:
  UCUQ_PORT_ = int(CONFIG_["Proxy"]["Port"])
except:
  UCUQ_PORT_ = int(UCUQ_DEFAULT_PORT_)

UCUQ_SSL_ = CONFIG_["Proxy"]["SSL"] if CONFIG_ and "Proxy" in CONFIG_ and "SSL" in CONFIG_["Proxy"] and CONFIG_["Proxy"]["SSL"] != None else UCUQ_DEFAULT_SSL_


PROTOCOL_LABEL_ = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION_ = "0"

writeLock_ = threading.Lock()

Lock_ = threading.Lock

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

useUCUqDemoDevices = lambda: False

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
  print("Connection to UCUq server…", end="", flush=True)

  try:
    s = socket.create_connection((UCUQ_HOST_, UCUQ_PORT_))
    if UCUQ_SSL_:
      s = ssl.create_default_context().wrap_socket(s, server_hostname="q37.info" if UCUQ_HOST_ == UCUQ_DEFAULT_HOST_ else UCUQ_HOST_)
  except Exception as e:
    raise e
  else:
    print("\r                                         \r",end="")

  return s


def handshake_(socket):
  with writeLock_:
    writeString_(socket, PROTOCOL_LABEL_)
    writeString_(socket, PROTOCOL_VERSION_)
    writeString_(socket, "Remote")
    writeString_(socket, "PYH")

  error = readString_(socket)

  if error:
    exit_(error)

  notification = readString_(socket)

  if notification:
    pass
    # print(notification)


def ignition_(socket, token, deviceId, errorAsException):
  with writeLock_:
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


def displayExitMessage_(Message):
  raise Error(Message)


def readingThread(proxy):
  while True:
    if ( answer := readUInt_(proxy.socket) ) == A_RESULT_:
      proxy.resultBegin.set()
      proxy.resultEnd.wait()
      proxy.resultEnd.clear()
    elif answer == A_SENSOR_:
      raise Error("Sensor handling not yet implemented!")
    elif answer == A_ERROR_:
      result = readString_(proxy.socket)
      print(f"\n>>>>>>>>>> ERROR FROM DEVICE BEGIN <<<<<<<<<<")
      print("Timestamp: ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
      caller = getframeinfo(stack()[1][0])
      print(f"Caller: {caller.filename}:{caller.lineno}")
      print(f">>>>>>>>>> ERROR FROM DEVICE CONTENT <<<<<<<<<<")
      print(result)
      print(f">>>>>>>>>> END ERROR FROM DEVICE END <<<<<<<<<<")
      proxy.exit = True
      proxy.resultBegin.set()
      exit_()
    elif answer == A_PUZZLED_:
      readString_(proxy.socket) # For future use
      raise Error("Puzzled!")
    elif answer == A_DISCONNECTED_:
        raise Error("Disconnected from device!")
    else:
      raise Error("Unknown answer from device!")


class Proxy:
  def __init__(self, socket):
    self.socket = socket
    if socket != None:
      self.resultBegin = threading.Event()
      self.resultEnd = threading.Event()
      self.exit = False
      threading.Thread(target = readingThread, args=(self,)).start()


class Device_:
  def __init__(self, *, id = None, token = None, callback = None):
    if callback != None:
      exit_("'callback' in only used by the Brython version!")

    if id or token:
      self.connect(id, token)

  def connect(self, id = None, token = None, errorAsException = True):
    if token == None and id == None:
      token, id = handlingConfig_(token, id)

    if not token:
      token = getConfigToken_()

    self.token = token if token else ALL_DEVICES_VTOKEN
    self.id = id if id else ""

    self.proxy = Proxy(connect_(self.token, self.id, errorAsException = errorAsException))

    return self.proxy.socket != None
  
  def upload_(self, modules):
    with writeLock_:
      writeString_(self.proxy.socket, R_UPLOAD_)
      writeStrings_(self.proxy.socket, modules)

  def execute_(self, script, expression = ""):
    if self.proxy.socket:
      with writeLock_:
        writeString_(self.proxy.socket, R_EXECUTE_)
        writeString_(self.proxy.socket, script)
        writeString_(self.proxy.socket, expression)

      if expression:
        self.proxy.resultBegin.wait()
        self.proxy.resultBegin.clear()
        if self.proxy.exit:
          exit()
        else:
          result = readString_(self.proxy.socket)
          self.proxy.resultEnd.set()

          if result:
            return json.loads(result)
          else:
            return None
          
  def commit(self, expression = ""):
    result = ""

    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.extend(self.pendingModules_)
      self.pendingModules_ = []

    if self.commands_ or expression:
      result = self.execute_('\n'.join(self.commands_), expression)
      self.commands_ = []

    return result

def getDemoDevice():
  return None

def getWebFileContent(url):
  parsedURL = urllib.parse.urlparse(url)

  with http.client.HTTPSConnection(parsedURL.netloc) as connection:
    connection.request("GET", parsedURL.path)

    response = connection.getresponse()

    if response.status == 200:
      return response.read().decode('utf-8')  
    else:
      raise Exception(f"Error retrieving the file '{url}': {response.status} {response.reason}")
    
def getKits():
  pass# With Python, the kits are already retrieved.

