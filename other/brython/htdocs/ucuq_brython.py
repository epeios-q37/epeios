import javascript, json, sys

from browser import aio, alert, console
from browser.local_storage import storage

javascript.import_js("ucuq.js", "ucuqjs")

LIB_VERSION = "0.0.1"

CONFIG_ITEM = "ucuq-config"
CONFIG_DEVICE_ENTRY = "Device"
CONFIG_DEVICE_TOKEN_ENTRY = "Token"
CONFIG_DEVICE_ID_ENTRY = "Id"

ITEMS_ = "i_"

device_ = None
uuid_ = 0

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

  async def acquire(self):
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
    raise Exception(result)

  try:
    jsonResult = json.loads(result) if result else None
  except:
    jsonResult = result

  if data:
    data["code"] = code
    data["result"] = jsonResult
    data["lock"].release()


def launchCallback_(lock):
  lock.release()


def displayExitMessage_(message):
  alert(message)
  console.error = javascript.UNDEFINED  # To avoid the displaying of an alert by below 'exit()'.
  sys.exit()

def handlingConfig_(token, id):
  if not CONFIG_ITEM in storage:
    displayMissingConfigMessage_()

  try:
    config = json.loads(storage[CONFIG_ITEM])
  except:
    displayMissingConfigMessage_()

  if CONFIG_DEVICE_ENTRY not in config:
    displayMissingConfigMessage_()

  device = config[CONFIG_DEVICE_ENTRY]

  if token == None:
    if CONFIG_DEVICE_TOKEN_ENTRY not in device:
      displayMissingConfigMessage_()

    token = device[CONFIG_DEVICE_TOKEN_ENTRY]

  if id == None:
    if CONFIG_DEVICE_ID_ENTRY not in device:
      displayMissingConfigMessage_()

    id = device[CONFIG_DEVICE_ID_ENTRY]

  return token, id


class Device:
  def __init__(self, *, id = None, token = None, now = True):
    if now:
      self.connect(id, token)

  def __del__(self):
    self.commit()

  def connect(self, id, token = None):
    self.pendingModules_ = ["Init-1"]
    self.handledModules_ = []
    self.commands_ = []

    if token == None or id == None:
      token, id = handlingConfig_(token, id)

    self.device_ = ucuqjs.launch(token, id, LIB_VERSION, lambda: None)

  
  def upload_(self, modules):
    ucuqjs.upload(self.device_, modules, lambda code, result: uploadCallback_(code, result))


  async def executeAwait_(self, script, expression):
    lock = Lock_()

    await lock.acquire()

    data = {
      "lock": lock
    }

    ucuqjs.execute(self.device_, script, expression, lambda code, result: executeCallback_(data, code, result))

    await lock.acquire()
    
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

