from itertools import count
import atlastk, ucuq, random, json

RB_DELAY = .05

ws2812 = None
ws2812Limiter = 0
onDuty = False
lcd = None

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

# Widgets
W_UCUQ_SWITCH = "UCUqSwitch"
# Below generated with 'Q_CreateWidgetConstants Body.html'.
W_HARDWARE_VIEW = "HardwareView"
W_PIN = "Pin"
W_COUNT = "Count"
W_OFFSET = "Offset"
W_LIMITER = "Limiter"
W_LCD_SWITCH = "LCDSwitch"
W_SOFT = "Soft"
W_SDA = "SDA"
W_SCL = "SCL"
W_MAIN_VIEW = "MainView"
W_S_R = "SR"
W_N_R = "NR"
W_S_G = "SG"
W_N_G = "NG"
W_S_B = "SB"
W_N_B = "NB"
W_PICKER_BOX = "PickerBox"
W_COLOR = "Color"


W_LCD_WIDGETS=(W_SOFT, W_SDA, W_SCL)


# Kits
K_BIPEDAL =0
K_DOG = 1
K_DIY = 2
K_WOKWI = 3

KITS = {
  "Freenove/Bipedal/RPiPico(2)W": K_BIPEDAL,
  "Freenove/Dog/ESP32": K_DOG,
  "q37.info/DIY/Displays": K_DIY,
  "q37.info/Wokwi/Displays": K_WOKWI,
}

def rainbow():
  v =  random.randint(0, 5)
  i = 0
  while i < 7 * ws2812Limiter:
    update_(*ucuq.rbShadeFade(v, int(i), ws2812Limiter))
    ucuq.sleep(RB_DELAY)
    i += ws2812Limiter / 20
  update_(0,0,0)


def convert_(hex):
  return int(int(hex,16) * 100 / 256)


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


def update_(r, g, b, color=""):
  if ws2812:
    ws2812.fill(list(map(int, [r, g, b]))).write()

    r, g, b = map(lambda s: str(s).rjust(3), [r, g, b])
    lcd.moveTo(0,0)\
      .putString("RGB: {} {} {}".format(*map(lambda s: str(s).rjust(3), [r, g, b])))\
      .moveTo(0,1)\
      .putString(color.center(16))


async def resetAwait(dom):
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  await dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0)    


async def fillHardwareAwait(dom, infos):
  hardware = ucuq.getKitHardware(infos)

  kit = KITS[ucuq.getKitLabel(infos)]

  lcd = None

  values = {}

  if kit == K_BIPEDAL or kit == K_DOG:
    ws2812 = hardware["RGB"]
  elif kit == K_DIY or kit == K_WOKWI:
    ws2812 = hardware["Ring"]
    lcd = hardware["LCD"]
  else:
    raise Exception("Unknown kit!")

  values.update({
    W_PIN: ws2812["Pin"],
    W_COUNT: ws2812["Count"],
    W_OFFSET: ws2812["Offset"],
    W_LIMITER: ws2812["Limiter"],
  })

  if lcd:
    values.update({
      W_LCD_SWITCH: "true",
      W_SOFT: "true" if lcd["Soft"] else "false",
      W_SDA: lcd["SDA"],
      W_SCL: lcd["SCL"],
    })
  else:
    values[W_LCD_SWITCH] = "false"

  await dom.setValues(values)


async def updateUIAwait(dom, onDuty):
  if onDuty:
    await dom.removeClass(W_MAIN_VIEW, "hide")
    await dom.addClass(W_HARDWARE_VIEW, "hide")
    await dom.setValue(W_UCUQ_SWITCH, "true")
  else:
    await dom.addClass(W_MAIN_VIEW, "hide")
    await dom.removeClass(W_HARDWARE_VIEW, "hide")
    await dom.setValue(W_UCUQ_SWITCH, "false")

  if dom.getValue(W_LCD_SWITCH) == "true":
    dom.enableElements(W_LCD_WIDGETS)
  else:
    dom.disableElements(W_LCD_WIDGETS)



async def atk(dom):
  infos = await ucuq.ATKConnectAwait(dom, BODY)

  await dom.executeVoid("setColorWheel()")
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not onDuty:
    await fillHardwareAwait(dom, infos)
  else:
    await dom.disableElement(W_UCUQ_SWITCH)

  await updateUIAwait(dom, onDuty)


async def atkSwitchLCD(dom):
  await updateUIAwait(dom, onDuty)


async def turnOnMainAwait(dom):
  global ws2812, ws2812Limiter

  try:
    pin, count, ws2812Limiter = (int(value.strip()) for value in (await dom.getValues([W_PIN, W_COUNT, W_LIMITER])).values())
  except:
    await dom.alert("No or bad value for Pin/Count!")
    return False
  else:
    ws2812 = ucuq.WS2812(pin, count)
    return True
  

async def turnOnLCDAwait(dom):
  global lcd

  values = dom.getValues((W_LCD_SWITCH, W_SOFT, W_SDA, W_SCL))

  if values[W_LCD_SWITCH] == "true":
    try:
      sda = int(values[W_SDA].strip())
      scl = int(values[W_SCL].strip())
    except:
      await dom.alert("No or bad value for SDA/SCL!")
      return False
    else:
      lcd = ucuq.HD44780_I2C(ucuq.I2C(sda, scl, soft=values[W_SOFT] == "true"), 2, 16).backlightOn()
      return True
  else:
    lcd = ucuq.Nothing()
    return True


async def atkUCUqSwitch(dom, id):
  global onDuty

  if (await dom.getValue(id)) == "true":
    onDuty = turnOnMainAwait(dom) and turnOnLCDAwait(dom)
  else:
    onDuty = False

  await updateUIAwait(dom, onDuty)


async def atkSelect(dom):
  if onDuty:
    R, G, B = (await dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
    await dom.setValues(getAllValues_(R, G, B))
    update_(R, G, B)
  else:
    await dom.executeVoid(f"colorWheel.rgb = [0,0,0]")  


async def atkSlide(dom):
  (R,G,B) = (await dom.getValues(["SR", "SG", "SB"])).values()
  await dom.setValues(getNValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


async def atkAdjust(dom):
  (R,G,B) = (await dom.getValues(["NR", "NG", "NB"])).values()
  await dom.setValues(getSValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


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
      update_(r, g, b, color)
      break


async def atkRainbow(dom):
  await resetAwait(dom)
  rainbow()


async def atkReset(dom):
  await resetAwait(dom)

