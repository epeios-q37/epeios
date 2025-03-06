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
    W_MODE: M_STRAIGHT,
    W_SOFT: "false",
    W_PIN: "12",
    W_WIDTH: "1.5"
  }
}

# Presets by kit ids
PRESETS = {
  ucuq.K_UNKNOWN: P_USER,
  ucuq.K_BIPEDAL: P_BIPEDAL,
  ucuq.K_DOG: P_DOG,
  ucuq.K_DIY_SERVOS: P_DIY
}


async def getParams():
  return (await ucuq.commitAwait(f"getParams({pwm.getObject()},{state == S_PCA9685})")) if state else None


async def getDuty(dom):
  if not ( duty := await dom.getValue("Duty") ) in [D_RATIO, D_WIDTH]:
    raise Exception ("Bad duty value!!!")

  return duty


def convert(value, converter):
  try:
    value = converter(value)
  except:
    return None
  else:
    return value


async def getInputs(dom):
  values = await dom.getValues([W_MODE, W_PIN, W_SDA, W_SCL, W_CHANNEL, W_SOFT, W_FREQ, W_OFFSET, W_DUTY, W_RATIO, W_WIDTH])

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


async def test(dom, inputs):
  error = True

  if inputs[W_MODE] == "":
    await dom.alert("Please select a mode!")
  elif inputs[W_MODE] == M_STRAIGHT:
    if inputs[W_PIN] == None:
      await dom.alert("Bad or no pin value!")
    else:
      error = False
  elif inputs[W_MODE] == M_PCA9685:
    if inputs[W_SCL] == None:
      await dom.alert("No or bad SCL value!")
    elif inputs[W_SDA]== None:
      await dom.alert("No or bad SDA value!")
    elif inputs[W_CHANNEL] == None:
      await dom.alert("No or bad Channel value!")
    else:
      error = False
  else:
    raise Exception("Unknown mode!!!")


  if error:
    return False

  error = True

  if inputs[W_FREQ] ==  None:
    await dom.alert("Bad or no freq. value!")
  elif inputs[W_DUTY]["Type"] == D_RATIO:
    if inputs[W_DUTY]["Value"] == None:
      await dom.alert("Bad or no ratio value!")
    else:
      error = False
  elif inputs[W_DUTY]["Type"] == D_WIDTH:
    if inputs[W_DUTY]["Value"] == None:
      await dom.alert("Bad or no width value!")
    else:
      error = False
  else:
    raise Exception("Unknown duty type!!!")

  return not error


async def updateDutyBox(dom, params = None):
# 'params = getParams()' does not work as 'getParams()' is only called
# at function definition and not at calling.
  if params == None:
    params = await getParams()

  match await getDuty(dom):
    case "Ratio":
      await dom.enableElement(W_RATIO)
      await dom.disableElement(W_WIDTH)
      if state:
        await dom.setValues({
          W_WIDTH: "",
          W_RATIO: params[1]
        })
    case "Width":
      await dom.enableElement(W_WIDTH)
      await dom.disableElement(W_RATIO)
      if state:
        await dom.setValues({
          W_RATIO: "",
          W_WIDTH: params[2]/1000000
        })
    case _:
      raise Exception("!!!")


async def updateDuties(dom, params = None):
  if params == None:
    params = await getParams()

  if params != None:
    await dom.setValues({
      O_FREQ: params[0],
      O_RATIO: params[1],
      O_WIDTH: params[2]/1000000,
      O_PRESCALE: params[3]
    })
  else:
    await dom.setValues({
      O_FREQ: "N/A",
      O_RATIO: "N/A",
      O_WIDTH: "N/A",
      O_PRESCALE: "N/A"
    })


async def initPWM(inputs):
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

  return await getParams()


async def setFreq(freq):
  pwm.setFreq(freq)
  return await getParams()


async def setOffset(offset):
  pwm.setOffset(offset)
  return await getParams()


async def setRatio(ratio):
  pwm.setU16(ratio)
  return await getParams()


async def setWidth(width):
  pwm.setNS(width)
  return await getParams()


async def atkConnect(dom):
  preset = PRESETS[ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))]

  await updateSettingsUIFollowingPreset_(dom, preset)

  await dom.setValue(W_PRESET, preset)
  
  ucuq.addCommand(MC_INIT)
  
  await updateDutyBox(dom)
  await dom.enableElement(W_HARDWARE_BOX)


async def updateSettingsUIFollowingMode_(dom, mode):
  if mode == M_NONE:
    await dom.enableElement("HideStraight")
    await dom.enableElement("HidePCA9685")
  elif mode == M_STRAIGHT:
    await dom.disableElement("HideStraight")
    await dom.enableElement("HidePCA9685")
  elif mode == M_PCA9685:
    await dom.enableElement("HideStraight")
    await dom.disableElement("HidePCA9685")
  else:
    raise Exception("Unknown mode!")


async def updateSettingsUIFollowingPreset_(dom, preset):
  setting = SETTINGS[preset]

  await updateSettingsUIFollowingMode_(dom, setting[W_MODE])

  await dom.setValues(setting)


async def atkPreset(dom, id):
  preset = await dom.getValue(id)

  await updateSettingsUIFollowingPreset_(dom, preset)


async def atkMode(dom, id):
  await updateSettingsUIFollowingMode_(dom, await dom.getValue(id))
  

async def atkSwitch(dom, id):
  global state

  if await dom.getValue(id) == "true":
    inputs = await getInputs(dom)

    if not await test(dom, inputs):
      await dom.setValue(id, False)
    else:
      state = S_PCA9685 if inputs[W_MODE] == M_PCA9685 else S_STRAIGHT
      await dom.disableElements([W_SETTINGS_BOX, W_PRESET])
      await updateDuties(dom, await initPWM(inputs))
  else:
    if state:
      pwm.deinit()
      state = S_OFF_DUTY
    await updateDuties(dom)
    await dom.enableElements([W_SETTINGS_BOX, W_PRESET])


async def atkSelect(dom):
  await updateDutyBox(dom)


async def atkFreq(dom, id):
  if state:
    freq = await dom.getValue(id)

    try:
      freq = int(freq)
    except:
      pass
    else:
      await updateDuties(dom, await setFreq(freq))


async def atkOffset(dom, id):
  if state:
    offset = await dom.getValue(id)

    try:
      offset = int(offset)
    except:
      pass
    else:
      await updateDuties(dom, await setOffset(offset))


async def atkRatio(dom, id):
  if state:
    value = await dom.getValue(id)

    try:
      ratio = int(value)
    except:
      pass
    else:
      await updateDuties(dom, await setRatio(ratio))


async def atkRatioStep(dom, id):
  await dom.setAttribute(W_RATIO, "step", await dom.getValue(id)),


async def atkWidth(dom, id):
  if state:
    value = await dom.getValue(id)

    try:
      width = float(value)
    except:
      pass
    else:
      await updateDuties(dom, await setWidth(int(1000000 * width)))


async def atkWidthStep(dom, id):
  await dom.setAttribute(W_WIDTH, "step", await dom.getValue(id)),

MC_INIT = """
def getParams(pwm, prescale):
  return [pwm.freq(), pwm.duty_u16(), pwm.duty_ns(), pwm.prescale() if prescale else 0]
"""
