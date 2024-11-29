import os, sys

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("../..","../../atlastk.zip"))

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


def setPin(dom, preset):
  if preset != P_USER:
    dom.setValue(W_PIN, PINS[preset])


def acConnect(dom):
  id = ucuq.getKitId(ucuq.ATKConnect(dom, BODY))

  if id == ucuq.K_BIPEDAL:
    preset = P_BUZZER
  elif id == ucuq.K_DIY:
    preset = P_DIY
  else:
    preset = P_USER

  dom.setValue(W_PRESET, preset)

  setPin(dom, preset)  


def acPlay(dom,id):
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
    dom.alert("Please switch on!")


def acSetRatio(dom, id):
  global ratio

  ratio = float(dom.getValue(id))

  dom.setValue(W_RATIO_SLIDE if id == W_RATIO_VALUE else W_RATIO_SLIDE, ratio)


def acPreset(dom, id):
  global onDuty, pwm

  setPin(dom, dom.getValue(id))


def acSwitch(dom, id):
  global onDuty, pwm

  state = dom.getValue(id) == "true"

  if state:
    rawPin = dom.getValue(W_PIN)

    try:
      pin = int(rawPin)
    except:
      dom.alert("No or bad pin value!")
      dom.setValue(id, "false")
    else:
      pwm = ucuq.PWM(pin)
      ucuq.commit()
      onDuty = True
  else:
    onDuty = False

  if onDuty:
    dom.disableElement(W_PIN_BOX)
  else:
    dom.enableElement(W_PIN_BOX)


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Play": acPlay,
  "SetRatio": acSetRatio
}

with open('Body.html', 'r') as file:
  BODY = file.read()

with open('Head.html', 'r') as file:
  HEAD = file.read()

atlastk.launch(CALLBACKS, headContent=HEAD)
