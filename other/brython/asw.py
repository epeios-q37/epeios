import javascript

print("Av.")
javascript.import_js("asw.js", alias="asw")
print("Ap.")

class WS:
  def __init__(self):
    self.result = ""

  def call(self, message):
    return asw.call(message)
  
ws_ = WS()

def launch(URL, uc1, uc2):
  asw.launch(URL, lambda : uc1(ws_), lambda : uc2(ws_) )
