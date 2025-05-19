import atlastk, ucuq, json, math, random

ATK_L10N = (
  ( 
    "en",
    "fr",
  ), (
    'Welcome to',
    'Bienvenue au jeu', 
  ), (
    "Simon's game!",
    "'Simon'!",
  ), (
    'Reproduce the',
    'Reproduire la',
  ), (
    'sequence...',
    'sequence...',
  ), (
    'Well done!',
    'Bravo!',
  ), (
    "Game over! '{new}'",
    "Perdu! '{new}'",
  ), (
    'to play again!',
    'pour rejouer!',
  ), (
    "New",
    "Nouveau",
  ), (
    "Repeat",
    "Répéter",
  ), (
    "Click '{new}' to",
    "'{new}'",
  ), (
    "begin the game!",
    "pour commencer !",
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

class HW:
  def turnBuzzerOn_(self):
    self.buzzer = ucuq.PWM(self.buzzerPin, freq=50, u16 = 0).setNS(0)

  def __init__(self, hwDesc):
    self.buzzerPin, = ucuq.getHardware(hwDesc, "Buzzer", ["Pin"])
    self.turnBuzzerOn_()

    self.lcd = ucuq.HD44780_I2C(16, 2, ucuq.I2C(*ucuq.getHardware(hwDesc, "LCD", ["SDA", "SCL", "Soft"]))).backlightOn()
    self.oled =  ucuq.SSD1306_I2C(128, 64, ucuq.I2C(*ucuq.getHardware(hwDesc, "OLED", ["SDA", "SCL", "Soft"])))
    pin, self.ringCount, self.ringOffset, self.ringLimiter = ucuq.getHardware(hwDesc, "Ring", ["Pin", "Count", "Offset", "Limiter"])
    self.ring = ucuq.WS2812(pin, self.ringCount)

  def buzzerBeep_(self, note, delay = 0.29, sleep = 0.01):
    self.buzzer.setFreq(pitches[note]).setU16(30000)
    ucuq.sleep(delay)
    self.buzzer.setU16(0)
    if sleep:
      ucuq.sleep(sleep)

  def ringFlash_(self, button):
    self.ring.fill([0,0,0])
    if button in BUTTONS:
      for i in range(1 + self.ringCount // 4):
        self.ring.setValue((list(BUTTONS.keys()).index(button) * self.ringCount // 4 + i + self.ringOffset) % self.ringCount,[self.ringLimiter * item // 255 for item in BUTTONS[button][0]])
    self.ring.write()

  def oledDigit_(self, n, offset):
    self.oled.draw(DIGITS[n], 8, offset, mul=8)

  def playJingle_(self, jingle):
    prevButton = ""
    prevPrevButton = ""

    for n in jingle:
      while True:
        button = random.choice(list(BUTTONS.keys())) 
        if ( button != prevButton ) and ( button != prevPrevButton ):
          break
      prevPrevButton = prevButton
      self.ringFlash_(prevButton := button)
      self.buzzerBeep_(n, 0.15, 0)
    self.ringFlash_("")

  def oledNumber(self, n):
    try:
      self.oledDigit_(n // 10, 12)
      self.oledDigit_(n % 10, 76)
    except:
      self.oled.fill(0)
    self.oled.show()

  def lcdDisplaySequence(self, seq):
    self.lcd.clear().moveTo(0,0).putString(seq).backlightOn()

  def begin(self, l10n):
    self.lcd.clear().moveTo(0,0).putString(l10n(10).format(**l10n(new=8))).moveTo(0,1).putString(l10n(11))
    self.oledNumber(None)
    ucuq.commit()

    return not isinstance(self.buzzer, ucuq.Nothing)

  def new(self, seq, l10n):
    self.oledNumber(None)
    self.lcd.clear().moveTo(0,0).putString(l10n(3)).moveTo(0,1).putString(l10n(4))
    self.oledNumber(0)
    ucuq.sleep(.75)
    self.play(seq)
    ucuq.commit()

  def restart(self, seq, l10n):
    self.oledNumber(None)

    self.lcd.clear()\
    .backlightOn()\
    .moveTo(0,0)\
    .putString(l10n(1))\
    .moveTo(0,1)\
    .putString(l10n(2))

    self.playJingle_(LAUNCH_JINGLE)
    ucuq.sleep(0.5)

    self.new(seq, l10n)

  def success(self, l10n):
    self.lcd.moveTo(0,0).putString(l10n(5))
    self.oledNumber(None)
    self.oled.draw(HAPPY_MOTIF, 16, mul=4, ox=32).show()
    self.playJingle_(SUCCESS_JINGLE)
    ucuq.sleep(0.5)
    self.lcd.clear()
    ucuq.commit()

  def failure(self, l10n):
    self.lcd.moveTo(0,0).putString(l10n(6).format(**l10n(new=8))).moveTo(0,1).putString(l10n(7))
    self.oledNumber(len(seq))
    self.buzzer.setFreq(30).setU16(50000)
    self.oledNumber(None)
    self.oled.fill(0).draw(SAD_MOTIF, 16, mul=4, ox=32).show()
    ucuq.sleep(1)
    self.buzzer.setU16(0)
    ucuq.commit()

  def buzzerSwitch(self, status):
    if status:
      self.turnBuzzerOn_()
    else:
      self.buzzer = ucuq.Nothing()  

  def displayButton(self, button):
    self.ring.fill([0,0,0])
    if button in BUTTONS:
      for i in range(1 + self.ringCount // 4):
        self.ring.setValue((list(BUTTONS.keys()).index(button) * self.ringCount // 4 + i + self.ringOffset) % self.ringCount,[self.ringLimiter * item // 255 for item in BUTTONS[button][0]])
    self.ring.write()
    self.buzzer.setFreq(pitches[BUTTONS[button][2]]).setU16(30000)
    ucuq.sleep(0.29)
    self.buzzer.setU16(0)
    self.ring.fill([0,0,0]).write()
    ucuq.sleep(0.01)

  def play(self, sequence):
    seq=""
    for s in sequence:
      self.oledNumber(len(seq)+1)
      self.displayButton(s)
      seq += s
      if len(seq) % 5:
        ucuq.commit()


hw = None

def getValuesOfVarsBeginningWith(prefix):
  return [value for var, value in globals().items() if var.startswith(prefix)]


def remove(source, items):
  return [item for item in source if item not in items]


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

def restart(dom):
  global seq

  seq = random.choice("RGBY")
  hw.restart(seq, lambda m: dom.getL10n(m))


async def atk(dom):
  global hw, seq, userSeq

  body = BODY.format(**dom.getL10n(new=8, repeat=9))

  if not hw:
    infos = await ucuq.ATKConnectAwait(dom, body)
    hw = HW(ucuq.getKitHardware(infos))
    ucuq.setCommitBehavior(ucuq.CB_MANUAL)
  else:
    await dom.inner("", body)

  seq = ""
  userSeq = ""

  if hw.begin(lambda *args, **kwargs: dom.getL10n(*args, **kwargs)):
    await dom.setAttribute("Buzzer", "checked", "")


async def atkRepeat():
  hw.play(seq)
  ucuq.commit()

  
async def atkNew(dom):
  restart(dom)

async def atkClick(dom, id):
  global seq, userSeq

  if not seq:
    return
  
  userSeq += id
  hw.lcdDisplaySequence(userSeq)
  hw.oledNumber(len(seq)-len(userSeq))
  hw.displayButton(id)

  if seq.startswith(userSeq):
    if len(seq) <= len(userSeq):
      hw.success(lambda m: dom.getL10n(m))
      userSeq = ""
      seq += random.choice("RGBY")
      hw.new(seq, lambda m: dom.getL10n(m))
    else:
      hw.lcd.backlightOff()
  else:
    hw.failure(lambda m: dom.getL10n(m))
    userSeq = ""
    seq = ""

  ucuq.commit()


async def atkSwitchSound(dom, id):
  hw.buzzerSwitch(await dom.getValue(id) == "true")
