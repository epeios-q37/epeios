import base64
import zlib
import ucuq # type: ignore

RGB_MAX_ = 10

def rainbowGradient_(n, max):
  colors = []
  
  for i in range(n):
    h = (i * 6) / n
    x = int((1 - abs((h % 2) - 1)) * max)

    if 0 <= h < 1:
      r, g, b = max, x, 0
    elif 1 <= h < 2:
      r, g, b = x, max, 0
    elif 2 <= h < 3:
      r, g, b = 0, max, x
    elif 3 <= h < 4:
      r, g, b = 0, x, max
    elif 4 <= h < 5:
      r, g, b = x, 0, max
    else:
      r, g, b = max, 0, x

    colors.append((r, g, b))
  return colors

RAINBOW = rainbowGradient_(50, RGB_MAX_)


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def polyphonicPlay(voices, tempo, userObject, callback):
#  ucuq.addCommand("__import__('gc').disable()")
  ucuq.polyphonicPlay(voices, tempo, userObject, callback)
#  ucuq.addCommand("__import__('gc').enable()")
