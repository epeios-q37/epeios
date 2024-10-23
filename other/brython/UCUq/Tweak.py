import os, sys, time, io, json, datetime

import ucuq, atlastk

onDuty = False

# Duties
D_RATIO = "Ratio"
D_WIDTH = "Width"

# Inputs
I_MODE_BOX = "ModeBox"
I_MODE = "Mode"
I_PIN = "Pin"
I_SDA = "SDA"
I_SCL = "SCL"
I_DRIVER = "Driver"
I_FREQ = "Freq"
I_DUTY = "Duty"
I_RATIO = "Ratio"
I_RATIO_STEP = "RatioStep"
I_WIDTH = "Width"

# Modes
M_STRAIGHT = "Straight"
M_PCA9685 = "PCA9685"

# Outputs
O_FREQ = "TrueFreq"
O_RATIO = "TrueRatio"
O_WIDTH = "TrueWidth"


async def getParams():
  return await ucuq.execute(MC_PARAMS, "getParams(pwm)") if onDuty else None


async def getDuty(dom):
  if not ( duty:= await dom.getValue("Duty") ) in [D_RATIO, D_WIDTH]:
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
  values = await dom.getValues([I_MODE, I_PIN, I_SDA, I_SCL, I_DRIVER, I_FREQ, I_DUTY, I_RATIO, I_WIDTH])

  return {
    I_MODE: values[I_MODE],
    I_PIN: convert(values[I_PIN], int),
    I_SDA: convert(values[I_SDA], int),
    I_SCL: convert(values[I_SCL], int),
    I_DRIVER: convert(values[I_DRIVER], int),
    I_FREQ: convert(values[I_FREQ], int),
    I_DUTY: {
      "Type": values[I_DUTY],
      "Value": convert(values[I_RATIO], int) if values[I_DUTY] == D_RATIO else convert(values[I_WIDTH], float)
    } 
  }


async def test(dom, inputs):
  error = True

  if inputs[I_MODE] == "":
    await dom.alert("Please select a mode!")
  elif inputs[I_MODE] == M_STRAIGHT:
    if inputs[I_PIN] == None:
      await dom.alert("Bad or no pin value!")
    else:
      error = False
  elif inputs[I_MODE] == M_PCA9685:
    if inputs[I_SCL] == None:
      await dom.alert("No or bad SCL value!")
    elif inputs[I_SDA]== None:
      await dom.alert("No or bad SDA value!")
    elif inputs[I_DRIVER] == None:
      await dom.alert("No or bad Driver value!")
    else:
      error = False
  else:
    raise Exception("Unknown mode!!!")
  
  
  if error:
    return False
  
  error = True

  if inputs[I_FREQ] ==  None:
    await dom.alert("Bad or no freq. value!")
  elif inputs[I_DUTY]["Type"] == D_RATIO:
    if inputs[I_DUTY]["Value"] == None:
      await dom.alert("Bad or no ratio value!")
    else:
      error = False
  elif inputs[I_DUTY]["Type"] == D_WIDTH:
    if inputs[I_DUTY]["Value"] == None:
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
      await dom.enableElement(I_RATIO)
      await dom.disableElement(I_WIDTH)
      if onDuty:
        await dom.setValues({
        I_WIDTH: "",
        I_RATIO: params[1] if onDuty else ""})
    case "Width":
      await dom.enableElement("Width")
      await dom.disableElement("Ratio")
      await dom.setValues({
        I_RATIO: "",
        I_WIDTH: params[2]/1000000 if onDuty else ""})
    case _:
      raise Exception("!!!")
    

async def updateDuties(dom, params = None):
  if params == None:
    params = await getParams()

  if params != None:
    await dom.setValues({
      O_FREQ: params[0],
      O_RATIO: params[1],
      O_WIDTH: params[2]/1000000
    })
  else:
    await dom.setValues({
      O_FREQ: "N/A",
      O_RATIO: "N/A",
      O_WIDTH: "N/A",
    })



async def initPWM(inputs):
  if inputs["Mode"] == M_STRAIGHT:
    script = MC_INIT_STRAIGHT
  elif inputs["Mode"] == M_PCA9685:
    script = MC_INIT_PCA9685
  else:
    raise Exception("Unknwon mode!!!")
    
  return await ucuq.execute(script.format(
    pin = inputs[I_PIN],
    sda = inputs[I_SDA],
    scl = inputs[I_SCL],
    driver = inputs[I_DRIVER],
    freq = inputs[I_FREQ],
    duty = "duty_u16" if inputs[I_DUTY]["Type"] == D_RATIO else "duty_ns",
    value = int(inputs[I_DUTY]["Value"] * (1 if inputs[I_DUTY]["Type"] == D_RATIO else 1000000))),
    "getParams(pwm)")
  

async def setFreq(freq):
  return await ucuq.execute(MC_SET_FREQ.format(freq), "getParams(pwm)")
  

async def setRatio(ratio):
  return await ucuq.execute(MC_SET_RATIO.format(ratio), "getParams(pwm)")
  

async def setWidth(width):
  return await ucuq.execute(MC_SET_WIDTH.format(width), "getParams(pwm)")
  

async def acConnect(dom):
  await dom.inner("", BODY)
  await ucuq.execute(MC_INIT)
  await updateDutyBox(dom)


async def acMode(dom, id):
  match await dom.getValue(id):
    case "Straight":
      await dom.disableElement("HideStraight")
      await dom.enableElement("HidePCA9685")
    case "PCA9685":
      await dom.enableElement("HideStraight")
      await dom.disableElement("HidePCA9685")
    case _:
      raise Exception("Unknown mode!")
  
  
async def acSwitch(dom, id):
  global onDuty

  if await dom.getValue(id) == "true":
    inputs = await getInputs(dom)

    if not await test(dom, inputs):
      await dom.setValue(id, False)
    else:
      await dom.disableElement(I_MODE_BOX)
      await updateDuties(dom, await initPWM(inputs))
      onDuty = True
  else:
    if onDuty:
      await ucuq.execute(MC_RESET_PWM)
      onDuty = False
    await updateDuties(dom)
    await dom.enableElement(I_MODE_BOX)


async def acSelect(dom):
  await updateDutyBox(dom)


async def acFreq(dom, id):
  if onDuty:
    value = await dom.getValue(id)

    try:
      freq = int(value)
    except:
      pass
    else:
      await updateDuties(dom, await setFreq(freq))


async def acRatio(dom, id):
  if onDuty:
    value = await dom.getValue(id)

    try:
      ratio = int(value)
    except:
      pass
    else:
      await updateDuties(dom, await setRatio(ratio))


async def acRadioStep(dom, id):
  await dom.setAttribute(I_RATIO, "step", await dom.getValue(id)),


async def acWidth(dom, id):
  if onDuty:
    value = await dom.getValue(id)

    try:
      width = float(value)
    except:
      pass
    else:
      await updateDuties(dom, await setWidth(int(1000000 * width)))


async def acWidthStep(dom, id):
  await dom.setAttribute(I_WIDTH, "step", await dom.getValue(id)),


CALLBACKS = {
  "": acConnect,
  "Mode": acMode,
  "Switch": acSwitch,
  "Freq": acFreq,
  "Select": acSelect,
  "Ratio": acRatio,
  "RatioStep": acRadioStep,
  "Width": acWidth,
  "WidthStep": acWidthStep
}

MC_INIT = """
import machine, ustruct, time

class PCA9685:
  def __init__(self, i2c, address=0x40):
    self.i2c = i2c
    self.address = address
    self.reset()

  def _write(self, address, value):
    self.i2c.writeto_mem(self.address, address, bytearray([value]))

  def _read(self, address):
    return self.i2c.readfrom_mem(self.address, address, 1)[0]

  def reset(self):
    self._write(0x00, 0x00) # Mode1

  def freq(self, freq=None):
    if freq is None:
      return int(25000000.0 / 4096 / (self._read(0xfe) - 1))
    prescale = int(25000000.0 / 4096.0 / freq + 1)
    old_mode = self._read(0x00) # Mode 1
    self._write(0x00, (old_mode & 0x7F) | 0x10) # Mode 1, sleep
    self._write(0xfe, prescale) # Prescale
    self._write(0x00, old_mode) # Mode 1
    time.sleep_us(5)
    self._write(0x00, old_mode | 0xa1) # Mode 1, autoincrement on

  def pwm(self, index, on=None, off=None):
    if on is None or off is None:
      data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
      return ustruct.unpack('<HH', data)
    data = ustruct.pack('<HH', on, off)
    self.i2c.writeto_mem(self.address, 0x06 + 4 * index,  data)

  def duty(self, index, value=None, invert=False):
    if value is None:
      pwm = self.pwm(index)
      if pwm == (0, 4096):
        value = 0
      elif pwm == (4096, 0):
        value = 4095
      value = pwm[1]
      if invert:
        value = 4095 - value
      return value
    if not 0 <= value <= 4095:
      raise ValueError("Out of range")
    if invert:
      value = 4095 - value
    if value == 0:
      self.pwm(index, 0, 4096)
    elif value == 4095:
      self.pwm(index, 4096, 0)
    else:
      self.pwm(index, 0, value)

class Straight:
  def __init__(self, pin, freq, *, duty_ns = None, duty_u16 = None):
    self.pwm = machine.PWM(machine.Pin(pin), freq=freq)

    if duty_ns != None:
      if duty_u16 != None:
        raise Exception ("duty_ns and duty_u16 can not be specified together!")
      self.pwm.duty_ns(duty_ns)
    elif duty_u16 != None:
      self.pwm.duty_u16(duty_u16)


  def deinit(self):
    self.pwm.deinit()

  def freq(self, value = None):
    if value == None:
      return self.pwm.freq()
    else:
      return self.pwm.freq(value)
  
  def duty_u16(self, value = None):
    if value == None:
      return self.pwm.duty_u16()
    else:
      return self.pwm.duty_u16(value)
  
  def duty_ns(self, value = None):
    if value == None:
      return self.pwm.duty_ns()
    else:
      return self.pwm.duty_ns(value)
  

class PCA:
  def __init__(self, sda, scl, driver, freq, *, duty_ns = None, duty_u16 = None):
    self.driver = driver
    self.pca = PCA9685(machine.I2C(sda = sda, scl = scl))
    self.pca.freq(freq)
    if duty_ns != None:
      if duty_u16 != None:
        raise Exception ("duty_ns and duty_u16 can not be specified together!")
      self.pca.duty(driver, self.nsToU12_(duty_ns))
    elif duty_u16 != None:
      self.pca.duty(driver, duty_u16 >> 4)
    
  def deinit(self):
    self.pca.reset()

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))
  
  def freq(self, value = None):
    return self.pca.freq(value)
  
  def duty_ns(self, value = None):
    if value == None:
      return self.u12ToNS_(self.pca.duty(self.driver))
    self.pca.duty(self.driver, self.nsToU12_(value))

  def duty_u16(self, value = None):
    if value == None:
      return self.pca.duty(self.driver) << 4
    self.pca.duty(self.driver, value >> 4)
  

def getParams(pwm):
  return [pwm.freq(), pwm.duty_u16(), pwm.duty_ns()]
"""

MC_INIT_STRAIGHT = """
pwm = Straight({pin}, {freq}, {duty}={value})
"""

MC_INIT_PCA9685 = """
pwm = PCA({sda}, {scl}, {driver}, {freq}, {duty}={value})
"""

MC_RESET_PWM = """
pwm.deinit()
"""

MC_SET_FREQ = """
pwm.freq({})
"""

MC_SET_RATIO = """
pwm.duty_u16({})
"""

MC_SET_WIDTH = """
pwm.duty_ns({})
"""

MC_PARAMS = """
"""

HEAD = """
<style>
output {
  padding-left: 5px;
}

.switch-container {
	margin: auto;
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
</style>
<style id="HideStraight">
  .straight {
    display: none;
  }
</style>
<style id="HidePCA9685">
  .pca9685 {
    display: none;
  }
</style>
"""

BODY = """
<fieldset style="display: flex; flex-direction: column">
  <legend>PWM</legend>
  <div style="display: flex; justify-content: space-between;">
    <fieldset id="ModeBox" style="display: flex;">
      <div style="align-content: center;">
        <select id="Mode" xdh:onevent="Mode">
          <option selected="Selected" disabled="disabled" value="">Select mode</option>
          <option value="Straight">Straight</option>
          <option value="PCA9685">PCA9685</option>
        </select>
      </div>
      <div>
        <div class="straight">
          <label>
            <span>Pin:</span>
            <input id="Pin" type="number" size="2" value="15" min="0" max="99">
          </label>
        </div>
        <div class="pca9685">
          <fieldset>
            <label>
              <span>SDA:</span>
              <input id="SDA" type="number" size="2" value="13" min="0" max="99">
            </label>
            <label>
              <span>SCL:</span>
              <input id="SCL" type="number" size="2" value="14" min="0" max="99">
            </label>
            <label>
              <span>Driver:</span>
              <input id="Driver" size="2" value="0">
            </label>
          </fieldset>
        </div>
    </fieldset>
    <span class="switch-container">
      <label class="switch">
        <input type="checkbox" xdh:onevent="Switch">
        <span class="slider round"></span>
      </label>
    </span>
  </div>
  <div xdh:radio="duty" id="Duty" xdh:onevent="Select"
    style="display: grid; grid-template-columns: repeat(3, max-content);">
    <label style="display: flex; justify-content: right;">Freq. (Hz):&nbsp;</label>
    <span>
      <input id="Freq" xdh:onevents="(click|Freq)(change|Freq)" type="number" size="7" value="50">
    </span>
    <output id="TrueFreq">N/A</output>
    <label style="display: flex; justify-content: space-between;">
      <input name="duty" type="radio" value="Ratio" checked="checked">
      <span>Ratio (/65535):&nbsp;</span>
    </label>
    <span>
      <input id="Ratio" xdh:onevents="(click|Ratio)(change|Ratio)" type="number" size="5" min="0" max="65535"
        disabled="disabled" value="7000">
      <select id="RatioStep" xdh:onevent="RatioStep">
        <optgroup label="Select step">
          <option value="1">1</option>
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100">100</option>
          <option value="1000">1000</option>
        </optgroup>
      </select>
    </span>
    <output id="TrueRatio">N/A</output>
    <label style="display: flex; justify-content: space-between;">
      <input name="duty" type="radio" value="Width">
      <span>Width (ms):&nbsp;</span>
    </label>
    <span>
      <input id="Width" xdh:onevents="(click|Width)(change|Width)" type=number size="5" min="0" disabled="disabled"
        step=".1">
      <select id="WidthStep" xdh:onevent="WidthStep">
        <optgroup label="Select step">
          <option value=".1">0.1</option>
          <option value=".2">0.2</option>
          <option value=".5">0.5</option>
          <option value="1">1</option>
        </optgroup>
      </select>
    </span>
    <output id="TrueWidth">N/A</output>
  </div>
</fieldset>
"""

ucuq.launch() # If no id given, using the one in teh config file.

atlastk.launch(CALLBACKS, headContent=HEAD)

