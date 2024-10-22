import javascript
from browser import aio

LIB_VERSION = "0.0.1"

javascript.import_js("ucuq.js", "ucuqjs")

class Lock:
  def __init__(self):
    self.locked_ = False

  async def acquire(self):
    while self.locked_:
      await aio.sleep(0)
    self.locked_ = True

  def release(self):
    self.locked_ = False


async def launch(deviceToken, deviceId):
  lock = Lock()

  await lock.acquire()

  ucuqjs.launch(deviceToken, deviceId, LIB_VERSION, lambda: lock.release())

  await lock.acquire()


def executeCallback(data, code, result):
  data["code"] = code
  data["result"] = result
  data["lock"].release()


async def execute(script, expression = ""):
  lock = Lock()

  await lock.acquire()

  data = {
    "lock": lock
  }

  ucuqjs.execute(script, expression, lambda code, result: executeCallback(data, code, result))

  await lock.acquire()
  
  return data["result"]


