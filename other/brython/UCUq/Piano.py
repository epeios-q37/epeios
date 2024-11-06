import ucuq, atlastk, math

BUZZER_PIN = 2
LOUDSPEAKER_PIN = 6

pinNotSet = True

pwm = None
baseFreq = 440.0*math.pow(math.pow(2,1.0/12), -16)
ratio = 0.5

async def acConnect(dom):
  await dom.inner("", BODY)


async def acPlay(dom,id):
  global pwm

  if pinNotSet:
    await dom.alert("Please select a pin number!")
  else:
    freq = int(baseFreq*math.pow(math.pow(2,1.0/12), int(id)))
    pwm.setU16(int(ratio*65535))
    pwm.setFreq(freq)
    ucuq.render()
    await ucuq.sleepAwait(500)
    pwm.setU16(0)
    ucuq.render()


async def acSetRatio(dom, id):
  global ratio

  ratio = float(dom.getValue(id))

  await dom.setValue("RatioSlide" if id == "RatioValue" else "RatioValue", ratio)


async def acSetPin(dom, id):
  global pinNotSet, pwm

  rawPin = await dom.getValue(id)
  pin = None

  if rawPin in ("Buzzer", "Loudspeaker"):
    pin = BUZZER_PIN if rawPin == "Buzzer" else LOUDSPEAKER_PIN

    await dom.disableElement("UserPin")
    await dom.setValue("UserPin", pin)
  elif rawPin != "User":
    pin = int(rawPin)
  else:
    await dom.enableElement("UserPin")

  if pin:
    pinNotSet = False
    pwm = ucuq.PWM(pin)
    ucuq.render()

CALLBACKS = {
  "": acConnect,
  "Play": acPlay,
  "SetRatio": acSetRatio,
  "SetPin": acSetPin
}

HEAD = """
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/beautiful-piano@0.0.6/styles.min.css"></link>
  <script src="https://cdn.jsdelivr.net/npm/beautiful-piano@0.0.6/dist/piano.min.js"></script>
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
    <fieldset>
      <legend>Pin</legend>
      <select id="PredefinedPin" xdh:onevent="SetPin">
        <option value="User">User defined</option>
        <optgroup label="Freenove Bipedal Robot">
          <option value="Buzzer">Buzzer</option>
          <option value="Loudspeaker">Loudspeaker</option>
        </optgroup>
      </select>
      <input xdh:onevent="SetPin" id="UserPin" type="number" size="2" min="1" max="99">
    </fieldset>
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