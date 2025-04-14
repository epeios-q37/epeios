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

PROD = False
UCUQ = False

# Calculation states
CS_NONE = 0
CS_V1 = 1
CS_O = 2
CS_V2 = 3

BIGS = (25, 50, 75, 100)
LITTLES = tuple( x for x in range(1, 11) for _ in range(2))

cOLED = None
cards = []

class Player:
  def __init__(self):
    self.reset()

  def reset(self):
    self.cards = []
    self.usedCards = []
    self.calcState = CS_NONE
    self.calcs = []
    self.calc = [None, None, None]


OPERATOR_CARDS=("+", "-", "×", "÷")
TRUE_OPERATORS = ("+", "-", "*", "//")
W_OPERATORS = tuple(range(4))

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

async def atk(player, dom):
  global cOLED, cLCD

  if UCUQ:
    infos = ucuq.ATKConnect(dom, BODY)

    hardware = ucuq.getKitHardware(infos)

    cOLED = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(*ucuq.getHardware
    (hardware, "OLED", ["SDA", "SCL", "Soft"])))
    cLCD = ucuq.HD44780_I2C(ucuq.I2C(*ucuq.getHardware(hardware, "LCD", ["SDA", "SCL", "Soft"])), 2, 16).backlightOff()
  else:
    cOLED = cLCD = ucuq.Nothing()
    dom.inner("", BODY)

  if not PROD and False:
    await atkNew(dom)

  updateUIAwait(player, dom)


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
    html += buildCalc(i, player.cards, c, 10 + i not in player.usedCards)

  if len(cards) >= 10:
    html += buildCalc(len(player.calcs), player.cards, player.calc, player.calcState != CS_V1)

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
  
async def atkBroadcastDrawing(player, dom):
  player.reset()

  dom.setValues({i: "&nbsp;" for i in range(4, 10)})

  await updateUIAwait(player, dom)


async def atkBroadcastPlaying(player, dom):
  player.cards = cards
  player.calcState = CS_V1

  dom.setValues({i + 4: valeur for i, valeur in enumerate(cards[4:])})

  await updateUIAwait(player, dom)


async def atkNew():
  global cards

  cards = list(OPERATOR_CARDS)

  atlastk.broadcastAction("BroadcastDrawing")

  bigs = list(BIGS)
  littles = list(LITTLES)

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

  atlastk.broadcastAction("BroadcastPlaying")


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


async def atkOperator(player, dom, id):
  if player.calcState != CS_O:
    return

  if player.calcState == CS_O:
    player.calc[1] = int(id)
    player.calcState = CS_V2
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)
  

async def atkDelete(player, dom, id):
  id = int(await dom.getMark(id))

  if id == len(player.calcs) and player.calcState in (CS_NONE, CS_V1):
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
  
ATK_USER = Player
