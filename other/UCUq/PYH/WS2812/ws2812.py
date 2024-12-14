import os, sys, random, json

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("../..","../../atlastk.zip"))

import atlastk, ucuq
RB_MAX = 30
RB_DELAY = .05

ws2812 = None
onDuty = False
oledDIY = None

# Presets
P_USER = "User"
P_BIPEDAL = "Bipedal"
P_DOG = "Dog"
P_DIY = "DIY"

SPOKEN_COLORS =  {
  "rouge": [255, 0, 0],
  "vert": [0, 255, 0],
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
  for i in range(0, RB_MAX * 7, 1+int(RB_MAX/20)):
    ws2812.fill(ucuq.rbShadeFade(v, i, RB_MAX)).write()
    ucuq.sleep(RB_DELAY)
  ws2812.fill([0]*3).write()
  ucuq.commit() 


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
    ucuq.commit()

def launch(dom, pin, count):
  global ws2812, onDuty

  try:
    ws2812 = ucuq.WS2812(pin, count)
    ucuq.commit()
  except Exception as err:
    dom.alert(err)
    onDuty = False
  else:
    onDuty = True


def reset(dom):
  dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0)    


def updateUI(dom, onDuty):
  ids = ["SlidersBox", "PickerBox"]

  if onDuty:
    dom.enableElements(ids)
    dom.disableElement("HardwareBox")
    dom.setValue("Switch", "true")
  else:
    dom.disableElements(ids)
    dom.enableElement("HardwareBox")
    dom.setValue("Switch", "false")

    preset = dom.getValue("Preset")

    if preset == P_BIPEDAL:
      dom.setValues({
        "Pin": 16,
        "Count": 4
      })
    elif preset == P_DOG:
        dom.setValues({
          "Pin": 0,
          "Count": 4
        })
    elif preset == P_DIY:
        dom.setValues({
          "Pin": 3,
          "Count": 8
        })
    elif preset != P_USER:
      raise Exception("Unknown preset!")

def acConnect(dom):
  global oledDIY
  id = ucuq.getKitId(ucuq.ATKConnect(dom, BODY))

  dom.executeVoid("setColorWheel()")
  dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not onDuty:
    if id == ucuq.K_BIPEDAL:
      dom.setValue("Preset", P_BIPEDAL)
    elif id == ucuq.K_DOG:
      dom.setValue("Preset", P_DOG)
    elif id == ucuq.K_DIY:
      oledDIY = ucuq.SSD1306_I2C(128, 64, ucuq.SoftI2C(0, 1))
      dom.setValue("Preset", P_DIY)

  updateUI(dom, False)

def acPreset(dom):
  updateUI(dom, onDuty)


def acSwitch(dom, id):
  global onDuty

  state = (dom.getValue(id)) == "true"

  if state:
    updateUI(dom, state)

    try:
      pin, count = (int(value.strip()) for value in (dom.getValues(["Pin", "Count"])).values())
    except:
      dom.alert("No or bad value for Pin/Count!")
      updateUI(dom, False)
    else:
      launch(dom, pin, count)
  else:
    onDuty = False

  updateUI(dom, onDuty)


def acSelect(dom):
  if onDuty:
    R, G, B = (dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
    dom.setValues(getAllValues_(R, G, B))
    update_(R, G, B)
  else:
    dom.executeVoid(f"colorWheel.rgb = [0,0,0]")  

def acSlide(dom):
  (R,G,B) = (dom.getValues(["SR", "SG", "SB"])).values()
  dom.setValues(getNValues_(R, G, B))
  dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)

def acAdjust(dom):
  (R,G,B) = (dom.getValues(["NR", "NG", "NB"])).values()
  dom.setValues(getSValues_(R, G, B))
  dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


def acListen(dom):
  dom.executeVoid("launch()")
  
def acDisplay(dom):
  colors = json.loads(dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      r, g, b = [int(RB_MAX * c / 255) for c in SPOKEN_COLORS[color]]
      dom.setValues(getAllValues_(r, g, b))
      dom.executeVoid(f"colorWheel.rgb = [{r},{g},{b}]")
      update_(r, g, b)
      if oledDIY:
        oledDIY.text(color, 0, 50).show()
        ucuq.commit()
      break;

def acRainbow(dom):
  reset(dom)
  rainbow()

def acReset(dom):
  reset(dom)

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

with open('Body.html', 'r') as file:
  BODY = file.read()

with open('Head.html', 'r') as file:
  HEAD = file.read()

atlastk.launch(CALLBACKS, headContent=HEAD)