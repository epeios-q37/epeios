import ucuq, atlastk, math

BUZZER_PIN = 2
LOUDSPEAKER_PIN = 6

# Presets
P_USER = "User"
P_BUZZER = "Buzzer"
P_LOUDSPEAKER = "Loudspeaker"
P_DIY = "DIY"


PINS = {
  P_BUZZER: 2,
  P_LOUDSPEAKER: 6,
  P_DIY: 21
}

# Widgets
W_PIN_BOX = "PinBox"
W_PIN = "Pin"
W_PRESET = "Preset"
W_RATIO_SLIDE = "RatioSlide"
W_RATIO_VALUE = "RatioValue"

onDuty = False

pwm = None
baseFreq = 440.0*math.pow(math.pow(2,1.0/12), -16)
ratio = 0.5


async def setPin(dom, preset):
  if preset != P_USER:
    await dom.setValue(W_PIN, PINS[preset])


async def acConnect(dom):
  id = ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))

  if id == ucuq.K_BIPEDAL:
    preset = P_BUZZER
  elif id == ucuq.K_DIY:
    preset = P_DIY
  else:
    preset = P_USER

  await dom.setValue(W_PRESET, preset)

  await setPin(dom, preset)  


async def acPlay(dom,id):
  global pwm

  if onDuty:
    freq = int(baseFreq*math.pow(math.pow(2,1.0/12), int(id)))
    pwm.setU16(int(ratio*65535))
    pwm.setFreq(freq)
    ucuq.commit()
    ucuq.sleep(.5)
    pwm.setU16(0)
    ucuq.commit()
  else:
    await dom.alert("Please switch on!")


async def acSetRatio(dom, id):
  global ratio

  ratio = float(await dom.getValue(id))

  await dom.setValue(W_RATIO_SLIDE if id == W_RATIO_VALUE else W_RATIO_SLIDE, ratio)


async def acPreset(dom, id):
  global onDuty, pwm

  await setPin(dom, await dom.getValue(id))


async def acSwitch(dom, id):
  global onDuty, pwm

  state = await dom.getValue(id) == "true"

  if state:
    rawPin = await dom.getValue(W_PIN)

    try:
      pin = int(rawPin)
    except:
      await dom.alert("No or bad pin value!")
      await dom.setValue(id, "false")
    else:
      pwm = ucuq.PWM(pin)
      ucuq.commit()
      onDuty = True
  else:
    onDuty = False

  if onDuty:
    await dom.disableElement(W_PIN_BOX)
  else:
    await dom.enableElement(W_PIN_BOX)


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Play": acPlay,
  "SetRatio": acSetRatio
}

HEAD = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/beautiful-piano@0.0.6/styles.min.css"></link>
<script src="https://cdn.jsdelivr.net/npm/beautiful-piano@0.0.6/dist/piano.min.js"></script>
<style>
/* Switch begin */
.switch-container {
	padding-left: 10px;
  display: flex;
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
"""

BODY = """
<fieldset>
  <fieldset>
    <ul id="beautiful-piano">
      <li>
        <div id="0" xdh:onevent="Play" class="anchor F3"></div>
      </li>
      <li>
        <div id="2" xdh:onevent="Play" class="anchor G3"></div>
        <span id="1" xdh:onevent="Play" class="Fs3 Gb3"></span>
      </li>
      <li>
        <div id="4" xdh:onevent="Play" class="anchor A3"></div>
        <span id="3" xdh:onevent="Play" class="Gs3 Ab3"></span>
      </li>
      <li>
        <div id="6" xdh:onevent="Play" class="anchor B3"></div>
        <span id="5" xdh:onevent="Play" class="As3 Bb3"></span>
      </li>
      <li>
        <div id="7" xdh:onevent="Play" class="anchor C4"></div>
      </li>
      <li>
        <div id="9" xdh:onevent="Play" class="anchor D4"></div>
        <span id="8" xdh:onevent="Play" class="Cs4 Db4"></span>
      </li>
      <li>
        <div id="11" xdh:onevent="Play" class="anchor E4"></div>
        <span id="10" xdh:onevent="Play" class="Ds4 Eb4"></span>
      </li>
      <li>
        <div id="12" xdh:onevent="Play" class="anchor F4"></div>
      </li>
      <li>
        <div id="14" xdh:onevent="Play" class="anchor G4"></div>
        <span id="13" xdh:onevent="Play" class="Fs4 Gb4"></span>
      </li>
      <li>
        <div id="16" xdh:onevent="Play" class="anchor A4"></div>
        <span id="15" xdh:onevent="Play" class="Gs4 Ab4"></span>
      </li>
      <li>
        <div id="18" xdh:onevent="Play" class="anchor B4"></div>
        <span id="17" xdh:onevent="Play" class="As4 Bb4"></span>
      </li>
      <li>
        <div id="19" xdh:onevent="Play" class="anchor C5"></div>
      </li>
      <li>
        <div id="21" xdh:onevent="Play" class="anchor D5"></div>
        <span id="20" xdh:onevent="Play" class="Cs5 Db5"></span>
      </li>
      <li>
        <div id="23" xdh:onevent="Play" class="anchor E5"></div>
        <span id="22" xdh:onevent="Play" class="Ds5 Eb5"></span>
      </li>
      <li>
        <div id="24" xdh:onevent="Play" class="anchor F5"></div>
      </li>
      <li>
        <div id="26" xdh:onevent="Play" class="anchor G5"></div>
        <span id="25" xdh:onevent="Play" class="Fs5 Gb5"></span>
      </li>
      <li>
        <div id="28" xdh:onevent="Play" class="anchor A5"></div>
        <span id="27" xdh:onevent="Play" class="Gs5 Ab5"></span>
      </li>
      <li>
        <div id="30" xdh:onevent="Play" class="anchor B5"></div>
        <span id="29" xdh:onevent="Play" class="As5 Bb5"></span>
      </li>
      <li>
        <div id="31" xdh:onevent="Play" class="anchor C6"></div>
      </li>
      <li>
        <div id="33" xdh:onevent="Play" class="anchor D6"></div>
        <span id="32" xdh:onevent="Play" class="Cs6 Db6"></span>
      </li>
      <li>
        <div id="35" xdh:onevent="Play" class="anchor E6"></div>
        <span id="34" xdh:onevent="Play" class="Ds6 Eb6"></span>
      </li>
    </ul>
  </fieldset>
  <fieldset style="display: flex; justify-content: space-around">
    <fieldset id="PinBox">
      <legend>Pin</legend>
      <select id="Preset" xdh:onevent="Preset">
        <option value="User">User defined</option>
        <optgroup label="Freenove Bipedal Robot">
          <option value="Buzzer">Buzzer</option>
          <option value="Loudspeaker">Loudspeaker</option>
        </optgroup>
        <optgroup label="q37.info">
          <option value="DIY">DIY</option>
        </optgroup>
      </select>
      <input id="Pin" type="number" size="2" min="1" max="99">
    </fieldset>
    <span class="switch-container">
       <label class="switch">
        <input id="Switch"  type="checkbox" xdh:onevent="Switch">
        <span class="slider round"></span>
       </label>
    </span>        
    <fieldset style="display: flex; align-items: center;">
      <legend>Ratio</legend>
      <input id="RatioSlide" xdh:onevent="SetRatio" type="range" min="0" max="1" step=".025" value=".5">
      <span>&nbsp;</span>
      <input id="RatioValue" xdh:onevent="SetRatio" type="number" min="0" max="1" step=".025" value="0.5">
    </fieldset>
  </fieldset>
</fieldset>
"""

atlastk.launch(CALLBACKS, headContent=HEAD)