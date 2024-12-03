import javascript, json, sys

from browser import aio, alert, console
from browser.local_storage import storage

javascript.import_js("ucuq.js", "ucuqjs")

LIB_VERSION = "0.0.1"

CONFIG_ITEM = "ucuq-config"

ITEMS_ = "i_"

device_ = None
uuid_ = 0

try:
  CONFIG = json.loads(storage[CONFIG_ITEM])
except:
  CONFIG = None


async def sleepAwait(time):
  await ucuqjs.sleep(1000 * time, lambda : None)

def GetUUID_():
  global uuid_

  uuid_ += 1

  return uuid_


def launchAsync(func, *args, **kwargs):
  aio.run(func(*args, **kwargs))

def commit():
  getDevice_().commit()

async def commitAwait(expr):
  return await getDevice_().commitAwait(expr)

def sleep(secs):
  getDevice_().sleep(secs)

class Lock_:
  def __init__(self):
    self.locked_ = False

  async def acquireAwait(self):
    while self.locked_:
      await aio.sleep(0)
    self.locked_ = True

  def release(self):
    self.locked_ = False


def uploadCallback_(code, result):
  if code != 0:
    raise Exception(result)


def executeCallback_(data, code, result):
  if code != 0:
    if not data:
      raise Exception(result)
    else:
      jsonResult = result
  else:
    try:
      jsonResult = json.loads(result) if result else None
    except:
      jsonResult = result

  if data:
    data["code"] = code
    data["result"] = jsonResult
    data["lock"].release()


def displayExitMessage_(message):
  alert(message)
  console.error = javascript.UNDEFINED  # To avoid the displaying of an alert by below 'exit()'.
  sys.exit()


class Device:
  def __init__(self, *, id = None, token = None, callback = None):
    if id or token or callback:
      self.connect(id = id, token = token, callback = callback)

  def __del__(self):
    self.commit()

  def connect(self, *, id = None, token = None, callback = None):
    if not token and not id:
      if callback:
        raise Exception("'callback' can not be given without 'id' or 'token'!")
      token, id = handlingConfig_(token, id)

    self.device_ = ucuqjs.launch(token if token else ALL_DEVICES_VTOKEN, id if id else "", LIB_VERSION, callback if callback else lambda answer: answer.replace(ALL_DEVICES_VTOKEN, "<demo token>")) # 'None' is NOT converted in 'undefined' in JS.

    self.pendingModules_ = ["Init-1"]
    self.handledModules_ = []
    self.commands_ = []
  
  def upload_(self, modules):
    ucuqjs.upload(self.device_, modules, lambda code, result: uploadCallback_(code, result))

  async def executeAwait_(self, script, expression):
    lock = Lock_()

    await lock.acquireAwait()

    data = {
      "lock": lock
    }

    ucuqjs.execute(self.device_, script, expression, lambda code, result: executeCallback_(data, code, result))

    await lock.acquireAwait()

    if data["code"]:
      raise Exception(data["result"])
    
    return data["result"]


  def execute_(self, script):
    ucuqjs.execute(self.device_, script, "", lambda code, result: executeCallback_(None, code, result))


  def addModule(self, module):
    if not module in self.pendingModules_ and not module in self.handledModules_:
      self.pendingModules_.append(module)

  def addModules(self, modules):
    if isinstance( modules, str):
      self.addModule(modules)
    else:
      for module in modules:
        self.addModule(module)

  def addCommand(self, command):
    self.commands_.append(command)

    return self

  async def commitAwait(self, expression):
    result = ""

    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.extend(self.pendingModules_)
      self.pendingModules_ = []

    result = await self.executeAwait_('\n'.join(self.commands_) if self.commands_ else "", expression)
    self.commands_ = []

    return result
  
  def sleep(self, secs):
    self.addCommand(f"time.sleep({secs})")

  def commit(self):
    if self.pendingModules_:
      self.upload_(self.pendingModules_)
      self.handledModules_.extend(self.pendingModules_)
      self.pendingModules_ = []

    if self.commands_:
      self.execute_('\n'.join(self.commands_))
    
    self.commands_ = []

# Workaround to the 'Brython' 'unicodedata.normalize()' bug (https://github.com/brython-dev/brython/issues/2514).
def toASCII(text):
  return ucuqjs.toASCII(text)


def ignitionCallback(data, answer, errorMessage):
  success = not(len(answer))

  data["success"] = success
  data["lock"].release()

  return "" if success else errorMessage


async def findDeviceAwait(dom):
  data = {
    "lock": Lock_()
  }

  await data["lock"].acquireAwait()

  for deviceId in VTOKENS:
    await dom.inner("", f"<h3>Connecting to '{deviceId}'…</h3>")

    lastKey = list(VTOKENS.keys())[-1]

    device = Device(token = VTOKENS[deviceId], callback = lambda answer: ignitionCallback(data, answer, "Unable to connect to a device!" if deviceId == lastKey else ""))

    await data["lock"].acquireAwait()

    if data["success"]:
      return device
  
  return None


