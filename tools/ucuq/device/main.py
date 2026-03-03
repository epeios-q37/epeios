__version__ = "2025-08-20"

import ucuq, time

_BLE_FALLBACK_SERVICE_UUID = "b6000102-1ba1-4916-9493-e4279b6988ac"
_BLE_CHAR_UUID = "56562c57-1508-4242-be45-976c42598a95"

try:
  import ble
  _BLE = True
except Exception as e:
  # raise e
  _BLE = False
  

def show(script):
  print("\n---------")
  
  for c in script:
    print(c if c == '\n' or 32 <= ord(c) <= 126 else '?', end='')


def callback(script, expression):
#  show(script)
  exec(script)
  if expression:
    return eval(expression)


if _BLE:
  ble.launch(_BLE_FALLBACK_SERVICE_UUID, _BLE_CHAR_UUID, lambda message: callback(*message.split('\0')))


try:
  ucuq.main(callback)
except Exception as e:
#    raise e
  pass

while True:
  time.sleep(10)

