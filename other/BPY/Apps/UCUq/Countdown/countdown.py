import atlastk, ucuq, random

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

BIGS = (25, 50, 75, 100)
LITTLES = list( x for x in range(1, 11) for _ in range(2))

print(BIGS, LITTLES)


cOLED = None

def displayDigit(n,offset):
  cOLED.draw(DIGITS[n], 8, offset, mul=6)


def displayNumber(n):
  try:
    displayDigit(n // 100, 8)
    displayDigit(n // 10 % 10, 48)
    displayDigit(n % 10, 88)
  except:
    cOLED.fill(0)
  cOLED.show()
  

def jauge(v): # v: 0 <= v <= 1
  l = int(126*v)
  cOLED.rect(0, 50, l, 13, 1).rect(l, 50, 127-l, 13, 1, False)


def displayCardsOnLCD(cards, center = True):
  text = ""

  for c in cards:
    text += " " + str(c)

  text = text[1:]

  if center:
    text = text.center(16)
  else:
    text = text.ljust(16)

  cLCD.moveTo(0,0).putString(text)


async def atk(dom):
  global cOLED, cLCD

  infos = ucuq.ATKConnect(dom, BODY)

  hardware = ucuq.getKitHardware(infos)

  cOLED = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(*ucuq.getHardware(hardware, "OLED", ["SDA", "SCL", "Soft"])))
  cLCD = ucuq.HD44780_I2C(ucuq.I2C(*ucuq.getHardware(hardware, "LCD", ["SDA", "SCL", "Soft"])), 2, 16).backlightOff()


async def atkNew(dom):
  bigs = list(BIGS)
  littles = list(LITTLES)
  cards = []

  dom.setValues({chr(65 + i): "&nbsp;" for i in range(7)})

  cOLED.fill(0).show()
  cLCD.backlightOn()

  while ( len(bigs) > 2 or len(littles) > 16 ):
    changed = True
    if random.randint(0,2) == 0 and len(bigs) > 2:
      cards.append(bigs.pop(random.randint(0, len(bigs) - 1)))
    elif len(littles) > 16:
      cards.append(littles.pop(random.randint(0, len(littles) - 1)))
    else:
      changed = False

    if changed:
      displayCardsOnLCD(cards, False)
      ucuq.sleep(1)


  cards.sort()

  cLCD.moveTo(0,0).putString("".center(16))

  ucuq.sleep(0.5)
  
  displayCardsOnLCD(cards)

  ucuq.sleepAwait(6.5)

  dom.setValues({chr(65 + i): valeur for i, valeur in enumerate(cards)})

  for i in range(50):
    displayNumber(random.randint(101,999))
