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


ws2812 = None
lcd = None
matrix = None


def rainbow():
  v =  random.randint(0, 5)
  i = 0
  while i < 7 * ws2812Limiter:
    update_(*ucuq.rbShadeFade(v, int(i), ws2812Limiter), ws2812Limiter)
    ucuq.sleep(RB_DELAY)
    i += ws2812Limiter / 20
  update_(0, 0, 0, ws2812Limiter)


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


def drawBarOnMatrix(x, height):
  y = int(height)

  if y != 0:
    matrix.rect(x * 6, 8 - y, x * 6 + 3, 7)


def update_(r, g, b, limit, color=""):
  ws2812.fill(list(map(int, [r, g, b]))).write()

  if matrix:
    matrix.clear()
    drawBarOnMatrix(0, int(r) * 8 / limit)
    drawBarOnMatrix(1, int(g) * 8 / limit)
    drawBarOnMatrix(2, int(b) * 8 / limit)
    matrix.show()

  if lcd:
    lcd.moveTo(0,0)\
      .putString("RGB: {} {} {}".format(*map(lambda s: str(s).rjust(3), [r, g, b])))\
      .moveTo(0,1)\
      .putString(color.center(16))


async def resetAwait(dom):
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  await dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0, 255)    


def turnOnMain(hardware):
  global ws2812, ws2812Limiter

  if hardware:
    pin = hardware["Pin"]
    count = hardware["Count"]
    ws2812Limiter = hardware["Limiter"]

    ws2812 = ucuq.WS2812(pin, count)
  else:
    raise("Kit has no ws2812!")
  

def turnOnLCD(hardware):
  global lcd

  if hardware:
    soft = hardware["Soft"]
    sda = hardware["SDA"]
    scl = hardware["SCL"]

    lcd = ucuq.HD44780_I2C(ucuq.I2C(sda, scl, soft=soft), 2, 16).backlightOn()
  else:
    lcd = ucuq.Nothing()


def turnOnMatrix(hardware):
  global matrix

  if hardware:
    soft = hardware["Soft"]
    sda = hardware["SDA"]
    scl = hardware["SCL"]

    matrix = ucuq.HT16K33(ucuq.I2C(sda, scl, soft=soft)).clear().show()
  else:
    matrix = ucuq.Nothing()


async def atk(dom):
  infos = await ucuq.ATKConnectAwait(dom, BODY, True)

  await dom.executeVoid("setColorWheel()")
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not ws2812:
    hardware = ucuq.getKitHardware(infos)

    turnOnMain(ucuq.getHardware(hardware, ("Ring", "RGB")))
    turnOnMatrix(ucuq.getHardware(hardware, "Matrix"))
    turnOnLCD(ucuq.getHardware(hardware, "LCD"))


async def atkSelect(dom):
  R, G, B = (await dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
  await dom.setValues(getAllValues_(R, G, B))
  update_(R, G, B, 255)


async def atkSlide(dom):
  (R,G,B) = (await dom.getValues(["SR", "SG", "SB"])).values()
  await dom.setValues(getNValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B, 255)


async def atkAdjust(dom):
  (R,G,B) = (await dom.getValues(["NR", "NG", "NB"])).values()
  await dom.setValues(getSValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B, 255)


async def atkListen(dom):
  await dom.executeVoid("launch()")


# Launched by the JS 'launch()' script.
async def atkDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      r, g, b = [ws2812Limiter * c // 255 for c in SPOKEN_COLORS[color]]
      await dom.setValues(getAllValues_(r, g, b))
      await dom.executeVoid(f"colorWheel.rgb = [{r},{g},{b}]")
      update_(r, g, b, ws2812Limiter, color)
      break


async def atkRainbow(dom):
  await resetAwait(dom)
  rainbow()


async def atkReset(dom):
  await resetAwait(dom)

