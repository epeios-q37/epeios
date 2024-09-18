import atlastk, mcrcq

import math

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
  <fieldset style="display: flex">
    <fieldset xdh:radio="Device" xdh:onevent="Check">
      <label>
        <input type="radio" name="Device" value="Buzzer" checked="checked">
        <span>Buzzer</span>
      </label>
      <label>
        <input type="radio" name="Device" value="Loudspeaker">
        <span>Loudspeaker</span>
      </label>
    </fieldset>
    <fieldset>
      <label style="display: flex; align-items: center;">
        <span>Ratio: </span>
        <input xdh:onevent="Slide" type="range" min="0" max="100" value="50">
      </label>
    </fieldset>
  </fieldset>
</fieldset>
"""

BUZZER_PIN = 2
LOUDSPEAKER_PIN = 6

INIT = """
from machine import Pin, PWM
from time import sleep

BuzzerObj=PWM(Pin({}))

def buzzer(buzzerPinObject,frequency,ratio):
    buzzerPinObject.duty_u16(int(65536*ratio))
    buzzerPinObject.freq(frequency)
    sleep(0.5)
    buzzerPinObject.duty_u16(int(65536*0))
"""

baseFreq = 440.0*math.pow(math.pow(2,1.0/12), -16)
ratio = 0.5

def acConnect(dom):
  dom.inner("", BODY)
  mcrcq.execute(INIT.format(BUZZER_PIN))

def acPlay(dom,id):
  freq = int(baseFreq*math.pow(math.pow(2,1.0/12), int(id)))
  mcrcq.execute(f"buzzer(BuzzerObj,{freq},{ratio})")

def acSlide(dom, id):
  global ratio
  
  ratio = int(dom.getValue(id))/100.0

def acCheck(dom, id):
  device = dom.getValue(id)
  mcrcq.execute(f"BuzzerObj=PWM(Pin({BUZZER_PIN if device == "Buzzer" else LOUDSPEAKER_PIN}))")

CALLBACKS = {
  "": acConnect,
  "Play": acPlay,
  "Slide": acSlide,
  "Check": acCheck
}

mcrcq.connect()

atlastk.launch(CALLBACKS, headContent=HEAD)
