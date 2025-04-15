import atlastk, ucuq, random, time, threading, urllib

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

HTML_CALCULATION = """
<tr xdh:mark="1{0}">
  <td class="disabled" id="V1{0}">{1}</td>
  <td class="disabled" id="O{0}">{2}</td>
  <td class="disabled" id="V2{0}">{3}</td>
  <td class="disabled">=</td>
  <td id="1{0}" class="disabled" xdh:onevent="Card">{4}</td>
  <td xdh:onevent="Delete" class={5}>❌</td>
</tr>
"""

JAUGE_SCRIPT="""
def jauge(oled, v):
  l = int(126*v)
  oled.rect(0, 50, 127, 13, 0, True)
  oled.rect(0, 50, l, 13, 1, True)
  oled.rect(l, 50, 127-l, 13, 1, False)
  oled.show()
"""


PROD = False
UCUQ = True

if PROD:
  DELAY = 45
else:
  DELAY = 15

# Calculation states
CS_NONE = 0
CS_V1 = 1
CS_O = 2
CS_V2 = 3

BIGS = (25, 50, 75, 100)
LITTLES = tuple( x for x in range(1, 11) for _ in range(2))

OPERATOR_CARDS=("+", "-", "×", "÷")
TRUE_OPERATORS = ("+", "-", "*", "//")

# Widgets
W_OPERATORS = tuple(range(4))
W_QRCODE = "QRCode"

# Styles
S_HIDE_QR_CODE = "HideQRCode"

cOLED = None
cLCD = None
cRing = None
cRingCount = 0
cRingLimiter = 0
cRingOffset = 9
cards = []
players = 0 # Amount of players.

class Player:
  def __init__(self):
    self.role = 0
    self.reset()

  def reset(self):
    self.cards = []
    self.usedCards = []
    self.calcState = CS_NONE
    self.calcs = []
    self.calc = [None, None, None]


def setHardwareAwait(dom):
  global cOLED, cLCD,cRing, cRingCount, cRingLimiter, cRingOffset

  if UCUQ:
    infos = ucuq.ATKConnect(dom, BODY)

    hardware = ucuq.getKitHardware(infos)

    cOLED = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(*ucuq.getHardware
    (hardware, "OLED", ("SDA", "SCL", "Soft"))))
    cLCD = ucuq.HD44780_I2C(ucuq.I2C(*ucuq.getHardware(hardware, "LCD", ("SDA", "SCL", "Soft"))), 2, 16).backlightOff()
    pin, cRingCount, cRingLimiter, cRingOffset = ucuq.getHardware(hardware, "Ring", ("Pin", "Count", "Limiter", "Offset"))
    cRing = ucuq.WS2812(pin, cRingCount).fill((0,0,0)).write()
    ucuq.addCommand(JAUGE_SCRIPT)

    return True
  else:
    cOLED = cLCD = ucuq.Nothing()
    dom.inner("", BODY)

    return False


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
  cOLED.rect(0,50,127,13,0).rect(0, 50, l, 13, 1).rect(l, 50, 127-l, 13, 1, False).show()


def ringCounter(v):
  limit = int((cRingCount - 1) * v)
  colorCore = int(cRingLimiter * v)
  color = (colorCore, cRingLimiter - colorCore, 0)

  for l in range(cRingCount):
    cRing.setValue((l + cRingOffset) % cRingCount, color if l <= limit else (0,0,0))

  cRing.write()


def counter():
  ucuq.addCommand("start = time.ticks_ms()")

  start = time.monotonic()

  while((elapsed := time.monotonic() - start) < DELAY ):
    ucuq.addCommand(f"jauge({cOLED.getObject()}, ({DELAY * 1000} - time.ticks_diff(time.ticks_ms(), start)) / {DELAY * 1000})")
    ringCounter(elapsed / DELAY)
    time.sleep(1.5)

  ucuq.addCommand(f"jauge({cOLED.getObject()}, 0)")
  ringCounter(1)

  atlastk.broadcastAction("BElapsed")


def displayCardsOnLCD(cards, center = True):
  text = ""

  for c in cards[4:]:
    text += " " + str(c)

  text = text[1:]

  if center:
    text = text.center(16)
  else:
    text = text.ljust(16)

  cLCD.moveTo(0,0).putString(text)


async def enable(player, dom, wIds, state = True):
  like = {}
  opposite = {}

  for i in range(11 + len(player.calcs)):
    like[i], opposite[i] = ("enabled", "disabled") if state == (i in wIds) else ("disabled", "enabled")

  dom.addClasses(like)
  dom.removeClasses(opposite)


patchCard = lambda c: TRUE_OPERATORS[OPERATOR_CARDS.index(c)] if c in OPERATOR_CARDS else c


def evalCalc(cards, calc):
  if all(item is not None for item in calc):
    result = eval("".join(str(patchCard(cards[c])) for c in calc))
    return result
  else:
    return ""


def buildCalc(index, cards, calc, enabled):
  return HTML_CALCULATION.format(index, *(cards[i] if i is not None else "" for i in calc), evalCalc(cards, calc), "enabled" if enabled else "disabled")


def buildCalcs(player):
  html = "<tr>"

  for i, c in enumerate(player.calcs):
    html += buildCalc(i, player.cards, c, 10 + i not in player.usedCards and player.calcState != CS_NONE)

  if len(cards) >= 10:
    html += buildCalc(len(player.calcs), player.cards, player.calc, player.calcState not in (CS_V1, CS_NONE))

  return html + "</tr>"


async def updateUIAwait(player, dom):
  await dom.inner("Calculations", buildCalcs(player))

  if player.calcState == CS_NONE:
    await enable(player, dom, ())
  elif player.calcState in (CS_V1, CS_V2):
    await enable(player, dom, list(W_OPERATORS) + player.usedCards + [len(player.calcs) + 10], False)
  elif player.calcState == CS_O:
    await enable(player, dom, W_OPERATORS)
  else:
    raise Exception("Unknown state")
  

def buildProgress(player):
  usedCalcs = sum(1 for c in player.usedCards if c >= 10)

  return f"{len(player.usedCards) - usedCalcs} {usedCalcs}/{len(player.calcs)}"


def displayProgress(player, id):
  assert str(id) in ("1", "2")

  if int(id) != player.role:
    return

  cLCD.moveTo(8 if player.role == 2 else 0, 1).putString(buildProgress(player).center(8))


async def atkBSecondPlayer(player, dom):
  if player.role == 1:
    await dom.enableElement(S_HIDE_QR_CODE)


async def atkBDrawing(player, dom):
  player.reset()

  dom.setValues({i: "&nbsp;" for i in range(4, 10)})

  await updateUIAwait(player, dom)


async def atkBPlaying(player, dom):
  player.cards = list(cards)
  player.calcState = CS_V1

  dom.setValues({i + 4: valeur for i, valeur in enumerate(cards[4:])})

  await updateUIAwait(player, dom)

  displayProgress(player, player.role)


async def atkBDisplayProgress(player, dom, id):
  assert str(id) in ("1", "2")

  if int(id) != player.role:
    return
  
  displayProgress(player, player.role)


async def atkBElapsed(player, dom):
  cLCD.moveTo(8 if player.role == 1 else 0, 1)
  cLCD.putString((str(evalCalc(player.cards, player.calcs[-1]) if len(player.calcs) else "/")).center(8))

  player.calcState = CS_NONE

  await updateUIAwait(player, dom)

  dom.alert("Finished!!!")


async def atk(player, dom, id):
  global players

  assert (cOLED == None) == (cLCD == None)
  assert id == "" or id == "Partner"

  if id == "Partner":
    assert players >= 1

    if players >= 2:
      dom.alert("No more players allowed!")
      return
    
    dom.inner("", BODY)
    
    players = player.role = 2

    atlastk.broadcastAction("BSecondPlayer")
  else:
    if players != 0:
      dom.alert("No more players allowed!")
      return
    
    if not await setHardwareAwait(dom):
      await dom.inner("", BODY)
    
    players = player.role = 1

    url = atlastk.getAppURL(id="Partner")

    dom.end(W_QRCODE, f'<a href="{url}" title="{url}" target="Debug"><img src="https://api.qrserver.com/v1/create-qr-code/?size=125x125&data={urllib.parse.quote(url)}"/></a>')

    dom.disableElement(S_HIDE_QR_CODE)

  await updateUIAwait(player, dom)


async def atkNew():
  global cards

  cards = list(OPERATOR_CARDS)

  atlastk.broadcastAction("BDrawing")

  bigs = list(BIGS)
  littles = list(LITTLES)

  cOLED.fill(0).show()
  cLCD.clear()
  cLCD.backlightOn()
  cRing.fill((0,0,0)).write()

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
      if PROD:
        ucuq.sleep(1)

  cards = cards[:4] + sorted(cards[4:])

  cLCD.moveTo(0,0).putString("".center(16))

  if PROD:
    ucuq.sleep(0.5)

  displayCardsOnLCD(cards)

  if PROD:
    ucuq.sleepAwait(6.5)

  for _ in range( 50 if PROD else 1):
    displayNumber(random.randint(101,999))

  atlastk.broadcastAction("BPlaying")

  threading.Thread(target=counter).start()


async def atkCard(player, dom, id):
  if player.calcState not in (CS_V1, CS_V2):
    return

  id = int(id)

  if player.calcState == CS_V1:
    player.usedCards.append(id)
    player.calc[0] = id
    player.calcState = CS_O
  elif player.calcState == CS_V2:
    player.usedCards.append(id)
    player.calc[2] = id
    player.calcs.append(player.calc)
    player.cards.append(evalCalc(player.cards, player.calc))
    player.calc =  [None, None, None]
    player.calcState = CS_V1
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)

  atlastk.broadcastAction("BDisplayProgress", str(player.role))


async def atkOperator(player, dom, id):
  if player.calcState != CS_O:
    return

  if player.calcState == CS_O:
    player.calc[1] = int(id)
    player.calcState = CS_V2
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)

  atlastk.broadcastAction("BDisplayProgress", str(player.role))


async def atkDelete(player, dom, id):
  id = int(await dom.getMark(id))

  if player.calcState == CS_NONE:
    return

  if id == len(player.calcs) and player.calcState == CS_V1:
    return
  
  if id in player.usedCards:
    return
  
  if id < 10 + len(player.calcs):
    player.usedCards.remove(player.calcs[id - 10][0])
    player.usedCards.remove(player.calcs[id - 10][2])

    del player.cards[id]
    del player.calcs[id - 10]
  else:
    player.usedCards.remove(player.calc[0])
    player.calc = [None, None, None]
    player.calcState = CS_V1

  await updateUIAwait(player, dom)
  
  atlastk.broadcastAction("BDisplayProgress", str(player.role))


ATK_USER = Player
