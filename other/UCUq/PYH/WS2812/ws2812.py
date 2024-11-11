import os, sys

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("../..","../../atlastk.zip"))

import atlastk, ucuq

with open('Body.html', 'r') as file:
  BODY = file.read()

with open('Head.html', 'r') as file:
  HEAD = file.read()

ws2812 = None
onDuty = False

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

def update_(R, G, B):
  if ws2812:
    ws2812.fill((int(R), int(G), int(B)))
    ws2812.write()
    ws2812.commit()

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

    match dom.getValue("Preset"):
      case "User":
        dom.enableElements(["Pin", "Count"])
      case "Bipedal":
        dom.setValues({
          "Pin": 16,
          "Count": 4
        })
        dom.disableElements(["Pin", "Count"])
      case "Dog":
        dom.setValues({
          "Pin": 0,
          "Count": 4
        })
        dom.disableElements(["Pin", "Count"])
      case _:
        raise Exception("Unknown preset!")

def acConnect(dom):
  label = ucuq.handleATK(dom)

  dom.inner("", BODY)
  dom.executeVoid("setColorWheel()")
  dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not onDuty:
    match label:
      case "Freenove.Robot.Bipedal.RPIPicoW":
        dom.setValue("Preset", "Bipedal")
      case "Freenove.Robot.Dog.ESP32":
        dom.setValue("Preset", "Dog")

  updateUI(dom, False)

def acPreset(dom):
  match dom.getValue("Preset"):
    case "User":
      dom.setValues({
        "Pin": "",
        "Count": ""
      })
    case "Bipedal" | "Dog":
      pass
    case _:
      raise Exception("Unknown preset!")
    
  updateUI(dom, onDuty)


def acSwitch(dom, id):
  global onDuty

  state = dom.getValue(id) == "true"

  if state:
    updateUI(dom, state)

    try:
      pin, count = (int(value.strip()) for value in dom.getValues(["Pin", "Count"]).values())
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
    R, G, B = dom.getValues(["rgb-r", "rgb-g", "rgb-b"]).values()
    dom.setValues(getAllValues_(R, G, B))
    update_(R, G, B)
  else:
    dom.executeVoid(f"colorWheel.rgb = [0,0,0]")  

def acSlide(dom):
  (R,G,B) = dom.getValues(["SR", "SG", "SB"]).values()
  dom.setValues(getNValues_(R, G, B))
  dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)

def acAdjust(dom):
  (R,G,B) = dom.getValues(["NR", "NG", "NB"]).values()
  dom.setValues(getSValues_(R, G, B))
  dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)

def acReset(dom):
  dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0)

def connect_(id):
  device = ucuq.UCUq()

  if not device.connect(id):
    print(f"Device '{id}' not available.")

  return device


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Select": acSelect,
  "Slide": acSlide,
  "Adjust": acAdjust,
  "Reset": acReset
}

atlastk.launch(CALLBACKS, headContent=HEAD)
