import javascript
from browser import aio

print("Av.")
javascript.import_js("asw.js", alias="asw")
print("Ap.")

class WS:
  def __init__(self):
    self.result = ""

  def call(self, message):
    return asw.call(message)

def launch__(uc, ws):
  bundle = asw.relay(uc, ws)
  aio.run(bundle.c(bundle.aws))


async def launch_(URL, uc1, uc2):
  ws_ = WS()
  await asw.launch(URL)

  launch__(uc1, ws_)
  launch__(uc2, ws_)
  
def launch(URL, uc1, uc2):
  aio.run(launch_(URL, uc1, uc2))