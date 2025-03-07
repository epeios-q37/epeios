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
  P_DIY: 5
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


async def atk(dom):
  id = ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))

  if id == ucuq.K_BIPEDAL:
    preset = P_BUZZER
  elif id == ucuq.K_DIY_DISPLAYS:
    preset = P_DIY
  else:
    preset = P_USER

  await dom.setValue(W_PRESET, preset)

  await setPin(dom, preset)  


async def atkPlay(dom,id):
  global pwm

  if onDuty:
    freq = int(baseFreq*math.pow(math.pow(2,1.0/12), int(id)))
    pwm.setU16(int(ratio*65535))
    pwm.setFreq(freq)
    ucuq.sleep(.5)
    pwm.setU16(0)
  else:
    await dom.alert("Please switch on!")


async def atkSetRatio(dom, id):
  global ratio

  ratio = float(await dom.getValue(id))

  await dom.setValue(W_RATIO_SLIDE if id == W_RATIO_VALUE else W_RATIO_SLIDE, ratio)


async def atkPreset(dom, id):
  global onDuty, pwm

  await setPin(dom, await dom.getValue(id))


async def atkSwitch(dom, id):
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
      pwm = ucuq.PWM(pin, freq=50, u16=0)
      onDuty = True
  else:
    onDuty = False

  if onDuty:
    await dom.disableElement(W_PIN_BOX)
  else:
    await dom.enableElement(W_PIN_BOX)
