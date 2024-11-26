import os, sys

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("../..","../../atlastk.zip"))

import ucuq, atlastk

# States
S_OFF_DUTY = 0
S_STRAIGHT = "Straight"
S_PCA9685 = "PCA9685"

state = S_OFF_DUTY

# Duties
D_RATIO = "Ratio"
D_WIDTH = "Width"

# Presets
P_USER = "None"
P_BIPEDAL = "Bipedal"
P_DOG = "Dog"
P_DIY = "DIY"

# Interface elements
W_PRESET = "Preset"
W_HARDWARE_BOX = "HardwareBox"
W_SWITCH = "Switch"
W_SETTINGS_BOX = "SettingsBox"
W_MODE = "Mode"
W_PIN = "Pin"
W_SDA = "SDA"
W_SCL = "SCL"
W_SOFT = "Soft"
W_CHANNEL = "Channel"
W_FREQ = "Freq"
W_OFFSET = "Offset"
W_DUTY = "Duty"
W_RATIO = "Ratio"
W_RATIO_STEP = "RatioStep"
W_WIDTH = "Width"

# Modes
M_NONE = "None"
M_STRAIGHT = "Straight"
M_PCA9685 = "PCA9685"

# Outputs
O_FREQ = "TrueFreq"
O_RATIO = "TrueRatio"
O_WIDTH = "TrueWidth"
O_PRESCALE = "TruePrescale"


# Default hardware settings
SETTINGS = {
  P_USER: {
    W_MODE: M_NONE,
    W_OFFSET: "0"
  },
  P_BIPEDAL: {
    W_MODE: M_STRAIGHT,
    W_PIN: "10",
    W_WIDTH: "1.5"
  },
  P_DOG: {
    W_MODE: M_PCA9685,
    W_SOFT: "false",
    W_SDA: "13",
    W_SCL: "14",
    W_OFFSET: "9",
    W_WIDTH: "1.5"
  },
  P_DIY: {
    W_MODE: M_PCA9685,
    W_SOFT: "false",
    W_SDA: "8",
    W_SCL: "9",
    W_OFFSET: "8",
    W_WIDTH: "1.5"
  }
}

# Presets by kit ids
PRESETS = {
  ucuq.K_UNKNOWN: P_USER,
  ucuq.K_BIPEDAL: P_BIPEDAL,
  ucuq.K_DOG: P_DOG,
  ucuq.K_DIY: P_DIY
}


def getParams():
  return (ucuq.commit(f"getParams({pwm.getObject()},{state == S_PCA9685})")) if state else None


def getDuty(dom):
  if not ( duty := dom.getValue("Duty") ) in [D_RATIO, D_WIDTH]:
    raise Exception ("Bad duty value!!!")

  return duty


def convert(value, converter):
  try:
    value = converter(value)
  except:
    return None
  else:
    return value


def getInputs(dom):
  values = dom.getValues([W_MODE, W_PIN, W_SDA, W_SCL, W_CHANNEL, W_SOFT, W_FREQ, W_OFFSET, W_DUTY, W_RATIO, W_WIDTH])

  return {
    W_MODE: values[W_MODE],
    W_PIN: convert(values[W_PIN], int),
    W_SDA: convert(values[W_SDA], int),
    W_SCL: convert(values[W_SCL], int),
    W_CHANNEL: convert(values[W_CHANNEL], int),
    W_SOFT: True if values[W_SOFT] == "true" else False,
    W_FREQ: convert(values[W_FREQ], int),
    W_OFFSET: convert(values[W_OFFSET], int),
    W_DUTY: {
      "Type": values[W_DUTY],
      "Value": convert(values[W_RATIO], int) if values[W_DUTY] == D_RATIO else convert(values[W_WIDTH], float)
    }
  }


def test(dom, inputs):
  error = True

  if inputs[W_MODE] == "":
    dom.alert("Please select a mode!")
  elif inputs[W_MODE] == M_STRAIGHT:
    if inputs[W_PIN] == None:
      dom.alert("Bad or no pin value!")
    else:
      error = False
  elif inputs[W_MODE] == M_PCA9685:
    if inputs[W_SCL] == None:
      dom.alert("No or bad SCL value!")
    elif inputs[W_SDA]== None:
      dom.alert("No or bad SDA value!")
    elif inputs[W_CHANNEL] == None:
      dom.alert("No or bad Channel value!")
    else:
      error = False
  else:
    raise Exception("Unknown mode!!!")


  if error:
    return False

  error = True

  if inputs[W_FREQ] ==  None:
    dom.alert("Bad or no freq. value!")
  elif inputs[W_DUTY]["Type"] == D_RATIO:
    if inputs[W_DUTY]["Value"] == None:
      dom.alert("Bad or no ratio value!")
    else:
      error = False
  elif inputs[W_DUTY]["Type"] == D_WIDTH:
    if inputs[W_DUTY]["Value"] == None:
      dom.alert("Bad or no width value!")
    else:
      error = False
  else:
    raise Exception("Unknown duty type!!!")

  return not error


def updateDutyBox(dom, params = None):
# 'params = getParams()' does not work as 'getParams()' is only called
# at function definition and not at calling.
  if params == None:
    params = getParams()

  match getDuty(dom):
    case "Ratio":
      dom.enableElement(W_RATIO)
      dom.disableElement(W_WIDTH)
      if state:
        dom.setValues({
          W_WIDTH: "",
          W_RATIO: params[1]
        })
    case "Width":
      dom.enableElement(W_WIDTH)
      dom.disableElement(W_RATIO)
      if state:
        dom.setValues({
          W_RATIO: "",
          W_WIDTH: params[2]/1000000
        })
    case _:
      raise Exception("!!!")


def updateDuties(dom, params = None):
  if params == None:
    params = getParams()

  if params != None:
    dom.setValues({
      O_FREQ: params[0],
      O_RATIO: params[1],
      O_WIDTH: params[2]/1000000,
      O_PRESCALE: params[3]
    })
  else:
    dom.setValues({
      O_FREQ: "N/A",
      O_RATIO: "N/A",
      O_WIDTH: "N/A",
      O_PRESCALE: "N/A"
    })


def initPWM(inputs):
  global pwm

  if inputs[W_MODE] == M_STRAIGHT:
    pwm = ucuq.PWM(inputs[W_PIN])
    pwm.setFreq(inputs[W_FREQ])
  elif inputs[W_MODE] == M_PCA9685:
    i2c = ucuq.SoftI2C if inputs[W_SOFT] else ucuq.I2C
    pwm = ucuq.PWM_PCA9685(ucuq.PCA9685(i2c(inputs[W_SDA], inputs[W_SCL])), inputs[W_CHANNEL])
    pwm.setOffset(inputs[W_OFFSET])
    pwm.setFreq(inputs[W_FREQ])
  else:
    raise Exception("Unknown mode!!!")

  if inputs[W_DUTY]["Type"] == D_RATIO:
    pwm.setU16(int(inputs[W_DUTY]["Value"]))
  else:
    pwm.setNS(int(1000000 * float(inputs[W_DUTY]["Value"])))

  return getParams()


def setFreq(freq):
  pwm.setFreq(freq)
  return getParams()


def setOffset(offset):
  pwm.setOffset(offset)
  return getParams()


def setRatio(ratio):
  pwm.setU16(ratio)
  return getParams()


def setWidth(width):
  pwm.setNS(width)
  return getParams()


def acConnect(dom):
  preset = PRESETS[ucuq.getKitId(ucuq.ATKConnect(dom, BODY))]

  updateSettingsUIFollowingPreset_(dom, preset)

  dom.setValue(W_PRESET, preset)
  
  ucuq.addCommand(MC_INIT)
  ucuq.commit()
  
  updateDutyBox(dom)
  dom.enableElement(W_HARDWARE_BOX)

def updateSettingsUIFollowingMode_(dom, mode):
  if mode == M_NONE:
    dom.enableElement("HideStraight")
    dom.enableElement("HidePCA9685")
  elif mode == M_STRAIGHT:
    dom.disableElement("HideStraight")
    dom.enableElement("HidePCA9685")
  elif mode == M_PCA9685:
    dom.enableElement("HideStraight")
    dom.disableElement("HidePCA9685")
  else:
    raise Exception("Unknown mode!")


def updateSettingsUIFollowingPreset_(dom, preset):
  setting = SETTINGS[preset]

  updateSettingsUIFollowingMode_(dom, setting[W_MODE])

  dom.setValues(setting)


def acPreset(dom, id):
  preset = dom.getValue(id)

  updateSettingsUIFollowingPreset_(dom, preset)


def acMode(dom, id):
  updateSettingsUIFollowingMode_(dom, dom.getValue(id))

def acSwitch(dom, id):
  global state

  if dom.getValue(id) == "true":
    inputs = getInputs(dom)

    if not test(dom, inputs):
      dom.setValue(id, False)
    else:
      state = S_PCA9685 if inputs[W_MODE] == M_PCA9685 else S_STRAIGHT
      dom.disableElements([W_SETTINGS_BOX, W_PRESET])
      updateDuties(dom, initPWM(inputs))
  else:
    if state:
      pwm.deinit()
      state = S_OFF_DUTY
    updateDuties(dom)
    dom.enableElements([W_SETTINGS_BOX, W_PRESET])


def acSelect(dom):
  updateDutyBox(dom)


def acFreq(dom, id):
  if state:
    freq = dom.getValue(id)

    try:
      freq = int(freq)
    except:
      pass
    else:
      updateDuties(dom, setFreq(freq))

def acOffset(dom, id):
  if state:
    offset = dom.getValue(id)

    try:
      offset = int(offset)
    except:
      pass
    else:
      updateDuties(dom, setOffset(offset))


def acRatio(dom, id):
  if state:
    value = dom.getValue(id)

    try:
      ratio = int(value)
    except:
      pass
    else:
      updateDuties(dom, setRatio(ratio))


def acRatioStep(dom, id):
  dom.setAttribute(W_RATIO, "step", dom.getValue(id)),


def acWidth(dom, id):
  if state:
    value = dom.getValue(id)

    try:
      width = float(value)
    except:
      pass
    else:
      updateDuties(dom, setWidth(int(1000000 * width)))


def acWidthStep(dom, id):
  dom.setAttribute(W_WIDTH, "step", dom.getValue(id)),


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Mode": acMode,
  "Switch": acSwitch,
  "Freq": acFreq,
  "Offset": acOffset,
  "Select": acSelect,
  "Ratio": acRatio,
  "RatioStep": acRatioStep,
  "Width": acWidth,
  "WidthStep": acWidthStep
}

MC_INIT = """
def getParams(pwm, prescale):
  return [pwm.freq(), pwm.duty_u16(), pwm.duty_ns(), pwm.prescale() if prescale else 0]
"""

with open('Body.html', 'r') as file:
  BODY = file.read()

with open('Head.html', 'r') as file:
  HEAD = file.read()

atlastk.launch(CALLBACKS, headContent=HEAD)