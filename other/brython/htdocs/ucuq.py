import javascript, json, sys
from browser import aio, alert, console
from browser.local_storage import storage

javascript.import_js("ucuq.js", "ucuqjs")

LIB_VERSION = "0.0.1"

CONFIG_ITEM = "ucuq-config"

class Lock:
  def __init__(self):
    self.locked_ = False

  async def acquire(self):
    while self.locked_:
      await aio.sleep(0)
    self.locked_ = True

  def release(self):
    self.locked_ = False


def launch(deviceId=None):
  if not CONFIG_ITEM in storage:
    alert("Please launch the 'Config' app first to set the device to use!")
    console.error = javascript.UNDEFINED  # To avoid the displaying of an alert by below 'exit()'.
    sys.exit()

  config = json.loads(storage[CONFIG_ITEM])

  device = config["Device"]

  ucuqjs.launch(device["Token"], deviceId if deviceId != None else device["Id"], LIB_VERSION)


def executeCallback(data, code, result):
  data["code"] = code
  data["result"] = json.loads(result) if result else None
  data["lock"].release()

  if code != 0:
    raise Exception(result)


async def execute(script, expression = ""):
  lock = Lock()

  await lock.acquire()

  data = {
    "lock": lock
  }

  ucuqjs.execute(script, expression, lambda code, result: executeCallback(data, code, result))

  await lock.acquire()
  
  return data["result"]


