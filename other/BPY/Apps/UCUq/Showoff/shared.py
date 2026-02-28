import base64
import zlib

import ucuq

RGB_MAX = 10

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

RAINBOW = rainbowGradient_(50, RGB_MAX)


def unpack(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def playVoices(voices, tempo, userObject, callback):
#  ucuq.addCommand("__import__('gc').disable()")
  ucuq.playVoices(voices, tempo, userObject, callback)
#  ucuq.addCommand("__import__('gc').enable()")

def handleDevices(devices: str):
  parts = devices.split()
  if len(parts) == 1:
    return parts[0]
  return tuple(parts)


INDY_VOICES = ("""
E43. F42
G43 C54. -C53 R2 D43. E42
F45 F43 R3 G43. A42
B43 F54. -F53 R2 A43. B42
C54 D54 E53 -E52 R2 E43. F42
G43 C54. -C53 R2 D53. E52
F55 R54 G43 -G41. R0 G42
E54 D53 R2 G42 E54 D53 R2 G42
E54 D53 R2 G42 F54 E53. D52
C55
""",)

INDY_TEMPO = 130