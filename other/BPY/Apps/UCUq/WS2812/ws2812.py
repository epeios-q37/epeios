from itertools import count
import atlastk, ucuq, random, json

RB_DELAY = .05

SPOKEN_COLORS =  {
  "rouge": [255, 0, 0],
  "vert": [0, 255, 0],
  "verre": [0, 255, 0],
  "verte": [0, 255, 0],
  "bleu": [0, 0, 255],
  "jaune": [255, 255, 0],
  "cyan": [0, 255, 255],
  "magenta": [255, 0, 255],
  "orange": [255, 127, 0],
  "violet": [127, 0, 255],
  "rose": [255, 127, 127],
  "gris": [127, 127, 127],
  "noir": [0, 0, 0],
  "blanc": [255, 255, 255],
  "marron": [127, 59, 0],
  "turquoise": [0, 127, 127],
  "beige": [255, 212, 170]
}


class HW:
  def __init__(self, infos, device=None):
    self.device, self.smartRGB, self.lcd, self.matrix = ucuq.getBits(infos, ucuq.B_SMART_RGB, ucuq.B_LCD, ucuq.B_MATRIX, device=device)

    self.lcd.backlightOn()

    self.smartRGBCount, self.smartRGBOffset, self.smartRGBLimiter = ucuq.getFeatures(infos, "SmartRGB", ["Count", "Offset", "Limiter"])

  def sleepStart(self, chrono):
    self.device.sleepStart(chrono)

  def sleepWait(self, chrono, delay):
    self.device.sleepWait(chrono, delay)

  def matrixDrawBar_(self, x, height):
    y = int(height)

    if y != 0:
      self.matrix.rect(x * 6, 8 - y, x * 6 + 3, 7)

  def update(self, r, g, b, limit = None, *, color=""):
    if limit is None:
      limit = self.smartRGBLimiter

    self.smartRGB.fill(list(map(lambda c: limit * int(c) // 255, [r, g, b]))).write()

    self.matrix.clear()
    self.matrixDrawBar_(0, 8 * int(r) // 255)
    self.matrixDrawBar_(1, 8 * int(g) // 255)
    self.matrixDrawBar_(2, 8 * int(b) // 255)
    self.matrix.show()

    self.lcd.moveTo(0,0)\
      .putString("RGB: {} {} {}".format(*map(lambda c: str(limit * int(c) // 255).rjust(3), [r, g, b])))\
      .moveTo(0,1)\
      .putString(color.center(16))

  def rainbow(self):
    v =  random.randint(0, 5)
    i = 0
    chrono = ucuq.getObjectIndice()
    while i < 7 * 255:
      self.sleepStart(chrono)
      self.update(*ucuq.rbShadeFade(v, int(i), 255))
      self.sleepWait(chrono, RB_DELAY)
      i += 255 / 20
    self.update(0, 0, 0)


hw = None


def getValues_(target, R, G, B):
  return {
    target + "R": R,
    target + "G": G,
    target + "B": B
  }


def getNValues_(R, G, B):
  return getValues_("N", R, G, B)


def getSValues_(R, G, B):
  return getValues_("S", R, G, B)


def getAllValues_(R, G, B):
  return getNValues_(R, G, B) | getSValues_(R, G, B)


async def resetAwait(dom):
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  await dom.setValues(getAllValues_(0, 0, 0))
  hw.update(0, 0, 0, 255)    


async def atk(dom):
  global hw

  if not hw:
    hw = ucuq.Multi(HW(await ucuq.ATKConnectAwait(dom, BODY)))
  else:
    await dom.inner("", BODY)

  await dom.executeVoid("setColorWheel()")
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")


async def atkSelect(dom):
  R, G, B = (await dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
  await dom.setValues(getAllValues_(R, G, B))
  hw.update(R, G, B, 255)


async def atkSlide(dom):
  R, G, B  = (await dom.getValues(["SR", "SG", "SB"])).values()
  await dom.setValues(getNValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  hw.update(R, G, B, 255)


async def atkAdjust(dom):
  R, G ,B = (await dom.getValues(["NR", "NG", "NB"])).values()
  await dom.setValues(getSValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  hw.update(R, G, B, 255)


async def atkListen(dom):
  await dom.executeVoid("launch()")


# Launched by the JS 'launch()' script.
async def atkDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      r, g, b = [c for c in SPOKEN_COLORS[color]]
      await dom.setValues(getAllValues_(r, g, b))
      await dom.executeVoid(f"colorWheel.rgb = [{r},{g},{b}]")
      hw.update(r, g, b, color=color)
      break


async def atkRainbow(dom):
  await resetAwait(dom)
  hw.rainbow()


async def atkReset(dom):
  await resetAwait(dom)


async def UCUqXDevice(dom, device):
  hw.add(HW(await ucuq.getInfosAwait(device), device))

