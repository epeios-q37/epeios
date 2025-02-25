import atlastk, ucuq, random, json

RB_DELAY = .05

ws2812 = None
ws2812Limiter = 0
onDuty = False
oledDIY = None

# Presets
P_USER = "User"
P_BIPEDAL = "Bipedal"
P_DOG = "Dog"
P_DIY = "DIY"
P_WOKWI = "Wokwi"

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


def rainbow():
  v =  random.randint(0, 5)
  i = 0
  while i < 7 * ws2812Limiter:
    ws2812.fill(ucuq.rbShadeFade(v, int(i), ws2812Limiter)).write()
    ucuq.sleep(RB_DELAY)
    i += ws2812Limiter / 20
  ws2812.fill([0]*3).write()


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


def update_(r, g, b):
  if ws2812:
    ws2812.fill([int(r), int(g), int(b)]).write()
    if oledDIY:
      oledDIY.fill(0).text(f"R: {r}", 0, 5).text(f"G: {g}", 0, 20).text(f"B: {b}", 0, 35).show()


async def launchAwait(dom, pin, count):
  global ws2812, onDuty

  try:
    ws2812 = ucuq.WS2812(pin, count)
  except Exception as err:
    await dom.alert(err)
    onDuty = False
  else:
    onDuty = True


async def resetAwait(dom):
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  await dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0)    


async def updateUIAwait(dom, onDuty):
  ids = ["SlidersBox", "PickerBox"]

  if onDuty:
    await dom.enableElements(ids)
    await dom.disableElements(["HardwareBox", "Preset"])
    await dom.setValue("Switch", "true")
  else:
    await dom.disableElements(ids)
    await dom.enableElements(["HardwareBox", "Preset"])
    await dom.setValue("Switch", "false")

    preset = await dom.getValue("Preset")

    if preset == P_BIPEDAL:
      await dom.setValues({
        "Pin": ucuq.H_BIPEDAL["RGB"]["Pin"],
        "Count": ucuq.H_BIPEDAL["RGB"]["Count"],
        "Offset": ucuq.H_BIPEDAL["RGB"]["Offset"],
        "Limiter": ucuq.H_BIPEDAL["RGB"]["Limiter"],
      })
    elif preset == P_DOG:
      await dom.setValues({
        "Pin": ucuq.H_DOG["RGB"]["Pin"],
        "Count": ucuq.H_DOG["RGB"]["Count"],
        "Offset": ucuq.H_DOG["RGB"]["Offset"],
        "Limiter": ucuq.H_DOG["RGB"]["Limiter"],
      })
    elif preset == P_DIY:
      await dom.setValues({
        "Pin": ucuq.H_DIY_DISPLAYS["Ring"]["Pin"],
        "Count": ucuq.H_DIY_DISPLAYS["Ring"]["Count"],
        "Offset": ucuq.H_DIY_DISPLAYS["Ring"]["Offset"],
        "Limiter": ucuq.H_DIY_DISPLAYS["Ring"]["Limiter"],
      })
    elif preset == P_WOKWI:
      await dom.setValues({
        "Pin": ucuq.H_WOKWI_DISPLAYS["Ring"]["Pin"],
        "Count": ucuq.H_WOKWI_DISPLAYS["Ring"]["Count"],
        "Offset": ucuq.H_WOKWI_DISPLAYS["Ring"]["Offset"],
        "Limiter": ucuq.H_WOKWI_DISPLAYS["Ring"]["Limiter"],
      })
    elif preset != P_USER:
      raise Exception("Unknown preset!")


async def acConnect(dom):
  global oledDIY
  id = ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))

  await dom.executeVoid("setColorWheel()")
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not onDuty:
    if id == ucuq.K_BIPEDAL:
      await dom.setValue("Preset", P_BIPEDAL)
    elif id == ucuq.K_DOG:
      await dom.setValue("Preset", P_DOG)
    elif id == ucuq.K_DIY_DISPLAYS:
      oledDIY = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(ucuq.H_DIY_DISPLAYS["OLED"]["SDA"], ucuq.H_DIY_DISPLAYS["OLED"]["SCL"], soft = ucuq.H_DIY_DISPLAYS["OLED"]["Soft"]))
      await dom.setValue("Preset", P_DIY)
    elif id == ucuq.K_WOKWI_DISPLAYS:
      oledDIY = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(ucuq.H_WOKWI_DISPLAYS["OLED"]["SDA"], ucuq.H_WOKWI_DISPLAYS["OLED"]["SCL"], soft = ucuq.H_WOKWI_DISPLAYS["OLED"]["Soft"]))
      await dom.setValue("Preset", P_WOKWI)

  await updateUIAwait(dom, False)


async def acPreset(dom):
  await updateUIAwait(dom, onDuty)


async def acSwitch(dom, id):
  global onDuty, ws2812Limiter

  state = (await dom.getValue(id)) == "true"

  if state:
    await updateUIAwait(dom, state)

    try:
      pin, count, ws2812Limiter = (int(value.strip()) for value in (await dom.getValues(["Pin", "Count", "Limiter"])).values())
    except:
      await dom.alert("No or bad value for Pin/Count!")
      await updateUIAwait(dom, False)
    else:
      await launchAwait(dom, pin, count)
  else:
    onDuty = False

  await updateUIAwait(dom, onDuty)


async def acSelect(dom):
  if onDuty:
    R, G, B = (await dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
    await dom.setValues(getAllValues_(R, G, B))
    update_(R, G, B)
  else:
    await dom.executeVoid(f"colorWheel.rgb = [0,0,0]")  


async def acSlide(dom):
  (R,G,B) = (await dom.getValues(["SR", "SG", "SB"])).values()
  await dom.setValues(getNValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


async def acAdjust(dom):
  (R,G,B) = (await dom.getValues(["NR", "NG", "NB"])).values()
  await dom.setValues(getSValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


async def acListen(dom):
  await dom.executeVoid("launch()")

  
async def acDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      r, g, b = [ws2812Limiter * c // 255 for c in SPOKEN_COLORS[color]]
      await dom.setValues(getAllValues_(r, g, b))
      await dom.executeVoid(f"colorWheel.rgb = [{r},{g},{b}]")
      update_(r, g, b)
      if oledDIY:
        oledDIY.text(color, 0, 50).show()
      break


async def acRainbow(dom):
  await resetAwait(dom)
  rainbow()


async def acReset(dom):
  await resetAwait(dom)


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Select": acSelect,
  "Slide": acSlide,
  "Adjust": acAdjust,
  "Listen": acListen,
  "Display": acDisplay,
  "Rainbow": acRainbow,
  "Reset": acReset
}

