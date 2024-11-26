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


async def acConnect(dom):
  preset = PRESETS[ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))]

  await updateSettingsUIFollowingPreset_(dom, preset)

  await dom.setValue(W_PRESET, preset)
  
  ucuq.addCommand(MC_INIT)
  ucuq.commit()
  
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


async def acPreset(dom, id):
  preset = await dom.getValue(id)

  await updateSettingsUIFollowingPreset_(dom, preset)


async def acMode(dom, id):
  await updateSettingsUIFollowingMode_(dom, await dom.getValue(id))

async def acSwitch(dom, id):
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


async def acSelect(dom):
  await updateDutyBox(dom)


async def acFreq(dom, id):
  if state:
    freq = await dom.getValue(id)

    try:
      freq = int(freq)
    except:
      pass
    else:
      await updateDuties(dom, await setFreq(freq))

async def acOffset(dom, id):
  if state:
    offset = await dom.getValue(id)

    try:
      offset = int(offset)
    except:
      pass
    else:
      await updateDuties(dom, await setOffset(offset))


async def acRatio(dom, id):
  if state:
    value = await dom.getValue(id)

    try:
      ratio = int(value)
    except:
      pass
    else:
      await updateDuties(dom, await setRatio(ratio))


async def acRatioStep(dom, id):
  await dom.setAttribute(W_RATIO, "step", await dom.getValue(id)),


async def acWidth(dom, id):
  if state:
    value = await dom.getValue(id)

    try:
      width = float(value)
    except:
      pass
    else:
      await updateDuties(dom, await setWidth(int(1000000 * width)))


async def acWidthStep(dom, id):
  await dom.setAttribute(W_WIDTH, "step", await dom.getValue(id)),


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

HEAD = """
<style>
output {
  padding-left: 5px;
}

/* Switch begin */
.switch-container {
	padding-left: 10px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 30px;
  height: 17px;
  margin: auto;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: .4s;
  transition: .4s cubic-bezier(0,1,0.5,1);
  border-radius: 4px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 13px;
  width: 13px;
  left: 3px;
  bottom: 2px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s cubic-bezier(0,1,0.5,1);
  border-radius: 3px;
}

input:checked + .slider {
  background-color: #52c944;
}

input:focus + .slider {
  box-shadow: 0 0 4px #7efa70;
}

input:checked + .slider:before {
  -webkit-transform: translateX(10px);
  -ms-transform: translateX(10px);
  transform: translateX(10px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 17px;
}

.slider.round:before {
  border-radius: 50%;
}

#round {
  border-radius: 17px;
}

#round:before {
  border-radius: 50%;
}
/* Switch end */

</style>
<style id="HideStraight">
  .straight {
    display: none;
  }
</style>
<style>
label.prescale-offset {
  display: flex;
  justify-content: right;
}
</style>
<style id="HidePCA9685">
  .pca9685, .prescale-offset, label.prescale-offset {
    display: none;
  }
</style>
"""

BODY = """
<fieldset style="display: flex; flex-direction: column">
  <legend>PWM</legend>
  <div style="display: flex; justify-content: space-between;">
    <fieldset id="HardwareBox" style="display: flex; flex-direction: column" disabled="">
      <legend>Hardware</legend>
      <div style="display: flex; justify-content: space-evenly;">
        <label>
          <span>Preset:</span>
          <select id="Preset" xdh:onevent="Preset">
            <option value="None">User</option>
            <optgroup label="Freenove">
              <option value="Bipedal">Bipedal</option>
              <option value="Dog">Dog</option>
            </optgroup>
            <option value="DIY">DIY</option>
          </select>
        </label>
        <span class="switch-container">
          <label class="switch">
            <input id="Switch"  type="checkbox" xdh:onevent="Switch">
            <span class="slider round"></span>
          </label>
        </span>        
      </div>
      <fieldset id="SettingsBox" style="display: flex; ">
        <legend>Settings</legend>
        <div style="align-content: center;">
          <select id="Mode" xdh:onevent="Mode">
            <option selected="Selected" disabled="disabled" value="None">Select mode</option>
            <option value="Straight">Straight</option>
            <option value="PCA9685">PCA9685</option>
          </select>
        </div>
        <div>
          <div class="straight">
            <label>
              <span>Pin:</span>
              <input id="Pin" type="number" size="2" value="10" min="0" max="99">
            </label>
          </div>
          <div class="pca9685">
            <fieldset>
              <label>
                <span>SDA:</span>
                <input id="SDA" type="number" size="2" value="0" min="0" max="99">
              </label>
              <label>
                <span>SCL:</span>
                <input id="SCL" type="number" size="2" value="1" min="0" max="99">
              </label>
              <br>
              <span style="display: flex; justify-content: space-between">
                <label>
                  <span>Soft:</span>
                  <input id="Soft" type="checkbox">
                </label>
                <label>
                  <span>Channel:</span>
                  <input type="number" id="Channel" size="2" value="0">
                </label>
              </span>
            </fieldset>
          </div>
        </div>
      </fieldset>
    </fieldset>
  </div>
  <fieldset xdh:radio="duty" id="Duty" xdh:onevent="Select"
    style="display: grid; grid-template-columns: repeat(3, max-content);">
    <legend>Parameters</legend>
    <label class="prescale-offset">Prescale offset:&nbsp;</label>
    <span class="prescale-offset">
      <input id="Offset" xdh:onevents="(click|Offset)(change|Offset)" type="number" size="5" value="0">
    </span>
    <output class="prescale-offset" id="TruePrescale">N/A</output>
    <label style="display: flex; justify-content: right;">Freq. (Hz):&nbsp;</label>
    <span>
      <input id="Freq" xdh:onevents="(click|Freq)(change|Freq)" type="number" size="5" value="50">
    </span>
    <output id="TrueFreq">N/A</output>
    <label style="display: flex; justify-content: space-between;">
      <input name="duty" style="margin: auto 10px auto 0px;" type="radio" value="Width" checked="checked">
      <span>Width (ms):&nbsp;</span>
    </label>
    <span>
      <input id="Width" xdh:onevents="(click|Width)(change|Width)" type=number size="5" min="0" disabled="disabled"
        step=".05" value="1">
      <select id="WidthStep" xdh:onevent="WidthStep">
        <optgroup label="Select step">
          <option value=".01">0.01</option>
          <option value=".02">0.02</option>
          <option value=".05" selected="selected">0.05</option>
          <option value=".1">0.1</option>
        </optgroup>
      </select>
    </span>
    <output id="TrueWidth">N/A</output>
    <label style="display: flex; justify-content: space-between;">
      <input name="duty" style="margin: auto 10px auto 0px;" type="radio" value="Ratio">
      <span>Ratio (/65535):&nbsp;</span>
    </label>
    <span>
      <input id="Ratio" xdh:onevents="(click|Ratio)(change|Ratio)" step="100" type="number" size="5" min="0" max="65535"
        disabled="disabled">
      <select id="RatioStep" xdh:onevent="RatioStep">
        <optgroup label="Select step">
          <option value="1">1</option>
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100" selected="selected">100</option>
          <option value="1000">1000</option>
        </optgroup>
      </select>
    </span>
    <output id="TrueRatio">N/A</output>
  </fieldset>
</fieldset>
"""

atlastk.launch(CALLBACKS, headContent=HEAD)
