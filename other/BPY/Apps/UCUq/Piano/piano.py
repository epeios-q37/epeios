import ucuq, atlastk, math

# Widgets
W_TARGET = "Target"
W_RATIO_SLIDE = "RatioSlide"
W_RATIO_VALUE = "RatioValue"

pwm = None
baseFreq = 440.0*math.pow(math.pow(2,1.0/12), -16)
ratio = 0.5
target = None

hardware = None

def turnMainOn(hardware):
  global pwm

  if hardware == None:
    raise Exception("Kit with no sound component!")
  
  pwm = ucuq.PWM(hardware["Pin"], freq=50, u16=0).setNS(0)


async def atk(dom):
  global pwm, target, hardware

  infos = ucuq.ATKConnectAwait(dom, BODY)

  if not pwm:
    hardware = ucuq.getKitHardware(infos)

    turnMainOn(ucuq.getHardware(hardware, "Buzzer"))

    if "Loudspeaker" in hardware:
      await dom.disableElement("HideTarget")
      target = "Buzzer"
  elif target: 
    await dom.setValue(W_TARGET, target)
    await dom.disableElement("HideTarget")


async def atkPlay(dom,id):
  freq = int(baseFreq*math.pow(math.pow(2,1.0/12), int(id)))
  pwm.setU16(int(ratio*65535))
  pwm.setFreq(freq)
  ucuq.sleep(.5)
  pwm.setU16(0)


async def atkSetRatio(dom, id):
  global ratio

  ratio = float(await dom.getValue(id))

  await dom.setValue(W_RATIO_SLIDE if id == W_RATIO_VALUE else W_RATIO_SLIDE, ratio)


async def atkSwitchTarget(dom, id):
  global target

  target = await dom.getValue(id)

  turnMainOn(ucuq.getHardware(hardware, target))
