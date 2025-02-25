import atlastk, ucuq, json, math, random

onDuty = False
cRing = None
cOLED = None
cBuzzer = None
cLCD = None

DIGITS = [
  0x3a33ae62e,
  0x11842108e, 
  0x3a213221f,
  0x7c223062e,
  0x8ca97c42,
  0x7e1e0862e,
  0x3a30f462e,
  0x7c2222108,
  0x3a317462e,
  0x3a317862e,
]

EN = {
  0: "Welcome to",
  1: "Simon's game!",
  2: "Reproduce the",
  3: "sequence...",
  4: "Well done!",
  5: "Game over! Click",
  6: "New to restart!",
}

FR = {
  0: "Bienvenue au jeu",
  1: "'Simon' !",
  2: "Reproduire la",
  3: "sequence...",
  4: "Bravo !",
  5: "Perdu ! 'New'",
  6: "pour rejouer !",
}

STRINGS = EN

OLED_COEFF = 8
ringCount = 0
ringOffset = 0
ringLimiter = 0

# Presets
P_USER = "User"
P_DIY = "DIY"
P_WOKWI = "Wokwi"

# Widgets
# Hardware widgets
W_HARDWARE = "Hardware"
W_H_SWITCH = "Switch"
W_H_PRESET = "Preset"
W_H_RING_PIN = "Ring_Pin"
W_H_RING_COUNT = "Ring_Count"
W_H_RING_OFFSET = "Ring_Offset"
W_H_RING_LIMITER = "Ring_Limiter"
W_H_BUZZER_ON = "Buzzer_On"
W_H_BUZZER_PIN = "Buzzer_Pin"
W_H_OLED_SOFT = "OLED_Soft"
W_H_OLED_SDA = "OLED_SDA"
W_H_OLED_SCL = "OLED_SCL"
W_H_LCD_SOFT = "LCD_Soft"
W_H_LCD_SDA = "LCD_SDA"
W_H_LCD_SCL = "LCD_SCL"
# Board widgets
W_BOARD = "Board"
W_B_R = "R"
W_B_G = "G"
W_B_B = "B"
W_B_Y = "Y"
W_B_NEW = "New"
W_B_REPEAT = "Repeat"

def getValuesOfVarsBeginningWith(prefix):
  return [value for var, value in globals().items() if var.startswith(prefix)]

def remove(source, items):
  return [item for item in source if item not in items]


HARDWARE_WIDGETS = getValuesOfVarsBeginningWith("W_H_")
HARDWARE_WIDGETS_WITHOUT_SWITCH = remove(HARDWARE_WIDGETS, [W_H_SWITCH])
BOARD_WIDGETS = getValuesOfVarsBeginningWith("W_B_")

print(HARDWARE_WIDGETS_WITHOUT_SWITCH, BOARD_WIDGETS)

# Default hardware settings
SETTINGS = {
  P_USER: {
  },
  P_DIY: {
    W_H_RING_PIN: ucuq.H_DIY_DISPLAYS["Ring"]["Pin"],
    W_H_RING_COUNT: ucuq.H_DIY_DISPLAYS["Ring"]["Count"],
    W_H_RING_OFFSET: ucuq.H_DIY_DISPLAYS["Ring"]["Offset"],
    W_H_RING_LIMITER:ucuq.H_DIY_DISPLAYS["Ring"]["Limiter"],
    W_H_BUZZER_ON: "true",
    W_H_BUZZER_PIN: ucuq.H_DIY_DISPLAYS["Buzzer"]["Pin"],
    W_H_OLED_SOFT: ucuq.H_DIY_DISPLAYS["OLED"]["Soft"],
    W_H_OLED_SDA: ucuq.H_DIY_DISPLAYS["OLED"]["SDA"],
    W_H_OLED_SCL: ucuq.H_DIY_DISPLAYS["OLED"]["SCL"],
    W_H_LCD_SOFT: ucuq.H_DIY_DISPLAYS["LCD"]["Soft"],
    W_H_LCD_SDA: ucuq.H_DIY_DISPLAYS["LCD"]["SDA"],
    W_H_LCD_SCL: ucuq.H_DIY_DISPLAYS["LCD"]["SCL"],
  },
  P_WOKWI: {
    W_H_RING_PIN: ucuq.H_WOKWI_DISPLAYS["Ring"]["Pin"],
    W_H_RING_COUNT: ucuq.H_WOKWI_DISPLAYS["Ring"]["Count"],
    W_H_RING_OFFSET: ucuq.H_WOKWI_DISPLAYS["Ring"]["Offset"],
    W_H_RING_LIMITER:ucuq.H_WOKWI_DISPLAYS["Ring"]["Limiter"],
    W_H_BUZZER_ON: "true",
    W_H_BUZZER_PIN: ucuq.H_WOKWI_DISPLAYS["Buzzer"]["Pin"],
    W_H_OLED_SOFT: ucuq.H_WOKWI_DISPLAYS["OLED"]["Soft"],
    W_H_OLED_SDA: ucuq.H_WOKWI_DISPLAYS["OLED"]["SDA"],
    W_H_OLED_SCL: ucuq.H_WOKWI_DISPLAYS["OLED"]["SCL"],
    W_H_LCD_SOFT: ucuq.H_WOKWI_DISPLAYS["LCD"]["Soft"],
    W_H_LCD_SDA: ucuq.H_WOKWI_DISPLAYS["LCD"]["SDA"],
    W_H_LCD_SCL: ucuq.H_WOKWI_DISPLAYS["LCD"]["SCL"],
  }
}

PRESETS = {
  ucuq.K_UNKNOWN: P_USER,
  ucuq.K_DIY_DISPLAYS: P_DIY,
  ucuq.K_WOKWI_DISPLAYS: P_WOKWI
}

seq = ""
userSeq = ""

def digit(n,off):
  pattern = DIGITS[n]

  for x in range(5):
    for y in range(7):
      cOLED.rect(off+x*OLED_COEFF,y*OLED_COEFF,OLED_COEFF,OLED_COEFF,1 if pattern & (1 << ((4 - x ) + (6 - y) * 5)) else 0)
  
  cOLED.show()

def number(n):
  try:
    digit(n // 10, 12)
    digit(n % 10, 76)
  except:
    cOLED.fill(0).show()

BUTTONS = {
  "R": [[255, 0, 0], 5, 9],
  "B": [[0, 0, 255], 7, 12],
  "Y": [[255, 255, 0], 1, 17],
  "G": [[0, 255, 0], 3, 5],
}

SPOKEN_COLORS = {
  "rouge": "R",
  "bleu": "B",
  "jaune": "Y",
  "vert": "G",
  "verre": "G",
  "verte": "G"
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


def convert(value, converter):
  try:
    return converter(value)
  except:
    raise Exception("Bad or missing value!")


async def getInputs(dom):
  values = await dom.getValues([
      W_H_RING_PIN, W_H_RING_COUNT, W_H_RING_OFFSET, W_H_RING_LIMITER,
      W_H_BUZZER_ON, W_H_BUZZER_PIN,
      W_H_OLED_SOFT, W_H_OLED_SDA, W_H_OLED_SCL,
      W_H_LCD_SOFT, W_H_LCD_SDA, W_H_LCD_SCL])

  return {
    W_H_RING_PIN: convert(values[W_H_RING_PIN], int),
    W_H_RING_COUNT: convert(values[W_H_RING_COUNT], int),
    W_H_RING_OFFSET: convert(values[W_H_RING_OFFSET], int),
    W_H_RING_LIMITER: convert(values[W_H_RING_LIMITER], int),
    W_H_BUZZER_ON: True if values[W_H_BUZZER_ON] == "true" else False,
    W_H_BUZZER_PIN: convert(values[W_H_BUZZER_PIN], int),
    W_H_OLED_SOFT: True if values[W_H_OLED_SOFT] == "true" else False,
    W_H_OLED_SDA: convert(values[W_H_OLED_SDA], int),
    W_H_OLED_SCL: convert(values[W_H_OLED_SCL], int),
    W_H_LCD_SOFT: True if values[W_H_LCD_SOFT] == "true" else False,
    W_H_LCD_SDA: convert(values[W_H_LCD_SDA], int),
    W_H_LCD_SCL: convert(values[W_H_LCD_SCL], int),
  }

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
#  number(None)
  for n in jingle:
    while True:
      button = random.choice(list(BUTTONS.keys())) 
      if ( button != prevButton ) and ( button != prevPrevButton ):
        break
    prevPrevButton = prevButton
    flash(prevButton := button)
    beep(n, 0.15, 0)
  flash("")


async def updateHardwareUI(dom):
  await dom.setValues(SETTINGS[await dom.getValue(W_H_PRESET)])


async def atkConnect(dom):
  preset = PRESETS[ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))]

  await dom.setValue(W_H_PRESET, preset)

  await updateHardwareUI(dom)


async def atkPreset(dom):
  await updateHardwareUI(dom)


async def atkSwitch(dom, id):
  global onDuty, cRing, cOLED, cBuzzer, cLCD, ringCount, ringOffset, ringLimiter

  if await dom.getValue(id) == "true":
    try:
      inputs = await getInputs(dom)
    except Exception as exc:
      await dom.setValue(W_H_SWITCH, "false")
      await dom.alert(exc)
      return

    ringCount = inputs[W_H_RING_COUNT]
    ringOffset = inputs[W_H_RING_OFFSET]
    ringLimiter = inputs[W_H_RING_LIMITER]

    print(ringOffset)

    ucuq.setCommitBehavior(ucuq.CB_MANUAL)

    cRing = ucuq.WS2812(inputs[W_H_RING_PIN], inputs[W_H_RING_COUNT])
    cOLED = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(inputs[W_H_OLED_SDA], inputs[W_H_OLED_SCL], soft = inputs[W_H_OLED_SOFT]))
    cLCD = ucuq.HD44780_I2C(ucuq.I2C(inputs[W_H_LCD_SDA], inputs[W_H_LCD_SCL], soft = inputs[W_H_LCD_SOFT]), 2, 16).backlightOff()
    if inputs[W_H_BUZZER_ON]:
#      ucuq.PWM(inputs[W_H_BUZZER_PIN], freq=50, u16 = 0).deinit()
      cBuzzer = ucuq.PWM(inputs[W_H_BUZZER_PIN], freq=50, u16 = 0)
    else:
      cBuzzer = ucuq.Nothing()
    cBuzzer.setFreq(50).setNS(0)
    number(None)
    cLCD.backlightOff()
    ucuq.commit()
    await dom.enableElements(BOARD_WIDGETS)
    await dom.disableElements(HARDWARE_WIDGETS_WITHOUT_SWITCH)
    onDuty = True
  else:
    onDuty = False
    await dom.disableElements(BOARD_WIDGETS)
    await dom.enableElements(HARDWARE_WIDGETS_WITHOUT_SWITCH)


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
    display(s)
    seq += s

  
async def atkDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      ucuq.sleep(.25)
      display(SPOKEN_COLORS[color])
      ucuq.commit()


async def atkNew():
  global seq
  
  number(None)

  cLCD.clear()\
  .backlightOn()\
  .moveTo(0,0)\
  .putString(STRINGS[0])\
  .moveTo(0,1)\
  .putString(STRINGS[1])

  playJingle(LAUNCH_JINGLE)
  ucuq.sleep(0.5)
  cLCD.clear()

  seq = random.choice("RGBY")
  cLCD.clear().moveTo(0,0).putString(STRINGS[2]).moveTo(0,1).putString(STRINGS[3])
  number(len(seq))
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
      cLCD.moveTo(0,0).putString(STRINGS[4])
      number(None)
      cOLED.draw("000006c006c0000000000440038", 16, mul=8).show()
      playJingle(SUCCESS_JINGLE)
      ucuq.sleep(0.5)
      cLCD.clear()
      ucuq.commit()
      userSeq = ""
      seq += random.choice("RGBY")
      cLCD.clear().moveTo(0,0).putString(STRINGS[2]).moveTo(0,1).putString(STRINGS[3])
      number(None)
      number(len(seq))
      ucuq.sleep(.75)
      play(seq)
    else:
      cLCD.backlightOff()
  else:
    cLCD.moveTo(0,0).putString(STRINGS[5]).moveTo(0,1).putString(STRINGS[6])
    number(len(seq))
    cBuzzer.setFreq(30).setU16(50000)
    number(None)
    cOLED.fill(0).draw("000006c006c0000000000380044", 16, mul=8).show()
    ucuq.sleep(1)
    cBuzzer.setU16(0)
    ucuq.commit()
    userSeq = ""
    seq = ""

  ucuq.commit()
