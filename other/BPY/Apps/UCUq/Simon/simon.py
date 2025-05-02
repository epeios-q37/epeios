import atlastk, ucuq, json, math, random

cRing = None
cOLED = None
cBuzzer = None
cLCD = None

buzzerPin = None

ringCount = 0
ringOffset = 0
ringLimiter = 0

L_FR = 0
L_EN = 1

LANGUAGE = None # If None, uses the language of the browser.

L10N = (
  (
    'Bienvenue au jeu', 
    'Welcome to'
  ), (
    "'Simon'!",
    "Simon's game!"
  ), (
    'Reproduire la',
    'Reproduce the'
  ), (
    'sequence...',
    'sequence...'
  ), (
    'Bravo!',
    'Well done!'
  ), ( # 5
    "Perdu! 'Nouveau'",
    "Game over! 'New'"
  ), (
    'pour rejouer!',
    'to play again!'
  ),
  (
    "Nouveau",
    "New"
  ),
  ( "Répéter",
    "Repeat"
  )
)

DIGITS = (
  "708898A8C88870",
  "20602020202070",
  "708808304080f8",
  "f8081030088870",
  "10305090f81010",
  "f880f008088870",
  "708880f0888870",
  "f8081020404040",
  "70888870888870",
  "70888878088870",
)

HAPPY_MOTIF = "03c00c30181820044c32524a80018001824181814812442223c410080c3003c0"
SAD_MOTIF = "03c00c30181820044c3280018001824181814002400227e410080c3003c0"

OLED_COEFF = 8

seq = ""
userSeq = ""

getL10N = lambda m, *args, **kwargs: L10N[m][language].format(*args, **kwargs)


def getValuesOfVarsBeginningWith(prefix):
  return [value for var, value in globals().items() if var.startswith(prefix)]


def remove(source, items):
  return [item for item in source if item not in items]


def digit(n,offset):
  cOLED.draw(DIGITS[n], 8, offset, mul=8)


def number(n):
  try:
    digit(n // 10, 12)
    digit(n % 10, 76)
  except:
    cOLED.fill(0)
  cOLED.show()


BUTTONS = {
  "R": [[255, 0, 0], 5, 9],
  "B": [[0, 0, 255], 7, 12],
  "Y": [[255, 255, 0], 1, 17],
  "G": [[0, 255, 0], 3, 5],
}


pitches = []

for i in range(24):
  pitches.append(int(220*math.pow(math.pow(2,1.0/12), i)))

LAUNCH_JINGLE = [
  3, 10,
  0, 8, 7, 5,
  3, 7, 10,
  8, 5, 3
]

SUCCESS_JINGLE = [
  7, 10, 19, 15, 17, 22
]

FAIL_JINGLE = [
  7, 10, 19, 15, 17, 22
]


def flash(button):
  cRing.fill([0,0,0])
  if button in BUTTONS:
    for i in range(1 + ringCount // 4):
      cRing.setValue((list(BUTTONS.keys()).index(button) * ringCount // 4 + i + ringOffset) % ringCount,[ringLimiter * item // 255 for item in BUTTONS[button][0]])
  cRing.write()


def beep(note, delay = 0.29, sleep = 0.01):
  cBuzzer.setFreq(pitches[note]).setU16(30000)
  ucuq.sleep(delay)
  cBuzzer.setU16(0)
  if sleep:
    ucuq.sleep(sleep)


def playJingle(jingle):
  prevButton = ""
  prevPrevButton = ""

  for n in jingle:
    while True:
      button = random.choice(list(BUTTONS.keys())) 
      if ( button != prevButton ) and ( button != prevPrevButton ):
        break
    prevPrevButton = prevButton
    flash(prevButton := button)
    beep(n, 0.15, 0)
  flash("")


def turnBuzzerOn(hardware):
  global cBuzzer, buzzerPin

  if buzzerPin == None:
    if not hardware:
      raise Exception("No buzzer!")
    
    buzzerPin = hardware["Pin"]
  
  cBuzzer = ucuq.PWM(buzzerPin, freq=50).setNS(0)


def turnRingOn(hardware):
  global cRing, ringCount, ringOffset, ringLimiter

  if not hardware:
    raise Exception("No ring!")
  
  ringCount = hardware["Count"]
  ringOffset = hardware["Offset"]
  ringLimiter = hardware["Limiter"]

  cRing = ucuq.WS2812(hardware["Pin"], ringCount).fill([0,0,0]).write()  


def getI2C(hardware):
  sda = hardware["SDA"]
  scl = hardware["SCL"]
  soft = hardware["Soft"]

  return ucuq.I2C(sda, scl, soft=soft)


def turnLCDOn(hardware):
  global cLCD

  if not hardware:
    raise Exception("No LCD!")
  
  cLCD = ucuq.HD44780_I2C(getI2C(hardware), 2, 16).backlightOff()


def turnOLEDOn(hardware):
  global cOLED

  if not hardware:
    raise Exception("No LCD!")
  
  cOLED = ucuq.SSD1306_I2C(128, 64, getI2C(hardware))


async def atk(dom):
  global language

  language = LANGUAGE if LANGUAGE != None else L_FR if dom.language.startswith("fr") else L_EN

  infos = await ucuq.ATKConnectAwait(dom, BODY.format(new=getL10N(7), repeat=getL10N(8)))

  hardware = ucuq.getKitHardware(infos)

  turnBuzzerOn(ucuq.getHardware(hardware, "Buzzer"))
  turnRingOn(ucuq.getHardware(hardware, "Ring"))
  turnLCDOn(ucuq.getHardware(hardware, "LCD"))
  turnOLEDOn(ucuq.getHardware(hardware, "OLED"))

  ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  number(None)
  cLCD.backlightOff()
  ucuq.commit()


async def atkRepeat():
  play(seq)
  ucuq.commit()


def display(button):
  cRing.fill([0,0,0])
  if button in BUTTONS:
    for i in range(1 + ringCount // 4):
      cRing.setValue((list(BUTTONS.keys()).index(button) * ringCount // 4 + i + ringOffset) % ringCount,[ringLimiter * item // 255 for item in BUTTONS[button][0]])
  cRing.write()
  cBuzzer.setFreq(pitches[BUTTONS[button][2]]).setU16(30000)
  ucuq.sleep(0.29)
  cBuzzer.setU16(0)
  cRing.fill([0,0,0]).write()
  ucuq.sleep(0.01)


def play(sequence):
  seq=""
  for s in sequence:
    number(len(seq)+1)
    display(s)
    seq += s
    if len(seq) % 5:
      ucuq.commit()

  
async def atkNew():
  global seq
  
  number(None)

  cLCD.clear()\
  .backlightOn()\
  .moveTo(0,0)\
  .putString(getL10N(0))\
  .moveTo(0,1)\
  .putString(getL10N(1))

  playJingle(LAUNCH_JINGLE)
  ucuq.sleep(0.5)
  cLCD.clear()

  seq = random.choice("RGBY")
  cLCD.clear().moveTo(0,0).putString(getL10N(2)).moveTo(0,1).putString(getL10N(3))
  number(0)
  ucuq.sleep(.75)
  play(seq)
  ucuq.commit()


async def atkClick(dom, id):
  global seq, userSeq

  if not seq:
    return
  
  userSeq += id
  cLCD.clear().moveTo(0,0).putString(userSeq).backlightOn()
  number(len(seq)-len(userSeq))
  display(id)

  if seq.startswith(userSeq):
    if len(seq) <= len(userSeq):
      cLCD.moveTo(0,0).putString(getL10N(4))
      number(None)
      cOLED.draw(HAPPY_MOTIF, 16, mul=4, ox=32).show()
      playJingle(SUCCESS_JINGLE)
      ucuq.sleep(0.5)
      cLCD.clear()
      ucuq.commit()
      userSeq = ""
      seq += random.choice("RGBY")
      cLCD.clear().moveTo(0,0).putString(getL10N(2)).moveTo(0,1).putString(getL10N(3))
      number(None)
      ucuq.commit()
      number(0)
      ucuq.sleep(.75)
      play(seq)
    else:
      cLCD.backlightOff()
  else:
    cLCD.moveTo(0,0).putString(getL10N(5)).moveTo(0,1).putString(getL10N(6))
    number(len(seq))
    cBuzzer.setFreq(30).setU16(50000)
    number(None)
    cOLED.fill(0).draw(SAD_MOTIF, 16, mul=4, ox=32).show()
    ucuq.sleep(1)
    cBuzzer.setU16(0)
    ucuq.commit()
    userSeq = ""
    seq = ""

  ucuq.commit()


async def atkSwitchSound(dom, id):
  global cBuzzer
  
  if await dom.getValue(id) == "true":
    turnBuzzerOn(None)
  else:
    cBuzzer = ucuq.Nothing()

