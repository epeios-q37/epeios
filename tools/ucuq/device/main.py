__version__ = "2025-11-07"

import ucuq, time

try:
  import ble
  BLE = True
except Exception as e:
  # raise e
  BLE = False
  

def show(script):
  print("\n---------")
  
  for c in script:
    print(c if c == '\n' or 32 <= ord(c) <= 126 else '?', end='')


def callback(script, expression):
  try:
    exec(script)
  except:
    show(script)
    raise
  else:
    # show(script)
    pass

  if expression:
    return eval(expression)


if BLE:
  def bleOn(state = True):
    if state:
      ble.launch(lambda message: callback(*message.split('\0')))
    else:
      ble.close()

  def bleOff():
    bleOn(False)

  bleOn()


try:
  ucuq.main(callback)
except Exception as e:
#    raise e
  pass

while True:
  time.sleep(10)

