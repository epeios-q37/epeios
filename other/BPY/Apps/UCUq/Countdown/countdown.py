import atlastk, ucuq, random, time, threading

# BEGIN BRY
from browser import aio
# END BRY

# Languages
L_FR = 0
L_EN = 1

LANGUAGE = None

L10N = (
  (
    "Tirage en cours…",
    "Drawing in progress…"
  ),
  (
    "À vous de jouer !",
    "It's up to you!"
  ),
  (
    "Un seul maître de jeu autorisé !",
    "Only one game master allowed!"
  ),
  (
    "Il y a déjà deux joueurs…",
    "There are already two players…"
  ),
  (
    "En attente du second joueur…",
    "Waiting for the second player…"
  ),
  # 5
  (
    "Temps écoulé !",
    "Time elapsed!"
  ),
  (
    "Bien joué !",
    "Well done!"
  ),
  (
    "Trop lent !",
    "Too slow!"
  ),
  (
    "En attente du tirage...",
    "Waiting for the drawing..."
  ),
  (
    "Nouveau",
    "New"
  ),
  # 10
  (
    "Cliquez sur '{new}'.",
    "Click on '{new}'."
  ),
  (
    "À scanner par le second joueur…",
    "To be scanned by second player…"
  ),
  (
    "En attente du   second joueur...",
    "Waiting for the second player..."
  ),
  (
    "En attente du   tirage...       ",
    "Waiting for the drawing...      "
  )
)

getL10N = lambda lang, m, *args, **kwargs: L10N[m][lang].format(*args, **kwargs)

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

JAUGE_SCRIPT = """
def jauge(oled, v):
  l = int(126*v)
  oled.rect(0, 50, 127, 13, 0, True)
  oled.rect(0, 50, l, 13, 1, True)
  oled.rect(l, 50, 127-l, 13, 1, False)
  oled.show()

async def counter_():
  global elapsed

  elapsed = 0

  start = time.ticks_ms()

  while not stop and ( elapsed := time.ticks_diff(time.ticks_ms(), start) ) < {delay}:
    jauge({oled}, 1- (elapsed / {delay}))
    {lcd}.move_to(13,1)
    {lcd}.putstr("{{:>3}}".format(({delay} - elapsed)//1000))
    {aw} asyncio.sleep(0)
"""


PROD = True
UCUq = True
CHEAT = True

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
W_QR_CODE = "QRCode"
W_OUTPUT = "Output"
W_CALCULATIONS = "Calculations"

# Styles
S_HIDE_QR_CODE = "HideQRCode"
S_HIDE_NEW_BUTTON = "HideNewButton"

cOLED = None
cLCD = None
cRing = None
cRingCount = 0
cRingLimiter = 0
cRingOffset = 0
cards = []
players = 0 # Amount of players.
toFind = 0
winner = 0 # if != 0, the role of the player which wins.

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


async def setHardwareAwait(language, dom):
  global cOLED, cLCD,cRing, cRingCount, cRingLimiter, cRingOffset

  body = BODY.format(new=getL10N(language, 9), qrcode=getL10N(language, 11))

  if UCUq:
    infos = await  ucuq.ATKConnectAwait(dom, body)

    hardware = ucuq.getKitHardware(infos)

    cOLED = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(*ucuq.getHardware
    (hardware, "OLED", ("SDA", "SCL", "Soft"))))
    cLCD = ucuq.HD44780_I2C(ucuq.I2C(*ucuq.getHardware(hardware, "LCD", ("SDA", "SCL", "Soft"))), 2, 16).backlightOff()
    pin, cRingCount, cRingLimiter, cRingOffset = ucuq.getHardware(hardware, "Ring", ("Pin", "Count", "Limiter", "Offset"))
    cRing = ucuq.WS2812(pin, cRingCount).fill((0,0,0)).write()
    ucuq.addCommand(JAUGE_SCRIPT.format(aw="aw" + "ait", delay=DELAY * 1000,oled=cOLED.getObject(),lcd=cLCD.getObject()))

    return True
  else:
    cOLED = cLCD = cRing = ucuq.Nothing()
    await dom.inner("", body)

    return False


def displayDigit(n,offset):
  cOLED.draw(DIGITS[n], 8, offset, mul=6)


def displayNumber(n):
  cOLED.fill(0)

  if n >= 100:
    displayDigit(n // 100, 8)


  if n >= 10:
    displayDigit(n // 10 % 10, 48)

  displayDigit(n % 10, 88)

  cOLED.show()
  

def jauge(v): # v: 0 <= v <= 1
  l = int(126*v)
  cOLED.rect(0,50,127,13,0).rect(0, 50, l, 13, 1).rect(l, 50, 127-l, 13, 1, False).show()


def ringCounter(v):
  if v < 1:
    limit = round(0.5 + cRingCount * v)

    for l in range(cRingCount):
      colorCore = int(cRingLimiter * (l / cRingCount))
      color = (colorCore, 0, cRingLimiter - colorCore)
      cRing.setValue((l + cRingOffset) % cRingCount, color if l < limit else (0,0,0))
  else:
    cRing.fill((cRingLimiter, 0, 0))

  cRing.write()


async def counterAwait():
  ucuq.addCommand("elapsed = 0\nstop = False\nasyncio.create_task(counter_())")

  elapsed = 0

  while not winner and elapsed <= DELAY:
    ringCounter(elapsed / DELAY)
    elapsed = await ucuq.commitAwait("elapsed") / 1000

  if winner:
    ucuq.addCommand("stop = True")

  ucuq.addCommand(f"jauge({cOLED.getObject()}, 0)")
  
  if not winner:
    ringCounter(1)
    atlastk.broadcastAction(atkBElapsed)
  else:
    cRing.fill([0,0,cRingLimiter]).write()


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

  await dom.addClasses(like)
  await dom.removeClasses(opposite)


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
  await dom.inner(W_CALCULATIONS, buildCalcs(player))

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

  cLCD.moveTo(7 if player.role == 2 else 0, 1).putString(buildProgress(player))


async def atkBSecondPlayer(player, dom):
  if player.role == 1:
    await dom.enableElement(S_HIDE_QR_CODE)
    await dom.disableElement(S_HIDE_NEW_BUTTON)
    await dom.setValue(W_OUTPUT, getL10N(player.language, 10, new=getL10N(player.language, 9)))


async def atkBDrawing(player, dom):
  player.reset()

  await dom.setValues({i: "&nbsp;" for i in range(4, 10)})

  await updateUIAwait(player, dom)

  await dom.setValue(W_OUTPUT, getL10N(player.language, 0))


async def atkBPlaying(player, dom):
  player.cards = list(cards)
  player.calcState = CS_V1

  await dom.setValues({i + 4: valeur for i, valeur in enumerate(cards[4:])})

  await updateUIAwait(player, dom)

  displayProgress(player, player.role)

  await dom.setValue(W_OUTPUT, getL10N(player.language, 1))


async def atkBDisplayProgress(player, dom, id):
  assert str(id) in ("1", "2")

  if int(id) != player.role:
    return
  
  displayProgress(player, player.role)


async def atkBElapsed(player, dom):
  cLCD.moveTo(0 if player.role == 1 else 7, 1)

  cLCD.putString((
      ( "> " if player.role == winner else "" )
      + str(evalCalc(player.cards, player.calcs[-1]) if len(player.calcs) else "/") )
    .center(6))

  player.calcState = CS_NONE

  await updateUIAwait(player, dom)

  if winner == 0:
    await dom.setValue(W_OUTPUT, getL10N(player.language, 5))
  elif player.role == winner:
    await dom.setValue(W_OUTPUT, getL10N(player.language, 6))
  else:
    await dom.setValue(W_OUTPUT, getL10N(player.language, 7))

  if player.role == 1:
    await dom.disableElement(S_HIDE_NEW_BUTTON)



# BEGIN_PYH
import urllib
encode = lambda t: urllib.parse.quote(t)
# END_PYH
# BEGIN BRY
import browser
encode = lambda t: browser.window.encodeURIComponent(t)
# END BRY


async def atk(player, dom, id):
  global players

  player.language = LANGUAGE if LANGUAGE != None else L_FR if dom.language.startswith("fr") else L_EN

  assert id == "" or id == "Partner"

  if id == "Partner":
    if players >= 2:
      await dom.alert(getL10N(player.language, 2))
      return
    
    await dom.inner("", BODY)
    
    players = player.role = 2

    await dom.setValue(W_OUTPUT, getL10N(player.language, 8))

    atlastk.broadcastAction(atkBSecondPlayer)
    cLCD.moveTo(0,0).putString(getL10N(player.language, 13))
  else:
    if players != 0:
      await dom.alert(getL10N(player.language, 3))
      return
    
    if not await setHardwareAwait(player.language, dom):
      await dom.inner("", BODY)
    
    players = player.role = 1

    url = atlastk.getAppURL(id="Partner")

    await dom.end(W_QR_CODE, f'<a href="{url}" title="{url}" target="Debug"><img src="https://api.qrserver.com/v1/create-qr-code/?size=125x125&data={encode(url)}"/></a>')

    await dom.disableElement(S_HIDE_QR_CODE)

    await dom.setValue(W_OUTPUT, getL10N(player.language, 4))
    cLCD.moveTo(0,0).putString(getL10N(player.language, 12)).backlightOn()

  await updateUIAwait(player, dom)


async def atkNew(player, dom):
  global cards, toFind, winner

  if player.role == 1:
    await dom.enableElement(S_HIDE_NEW_BUTTON)

  cards = list(OPERATOR_CARDS)

  atlastk.broadcastAction(atkBDrawing)

  bigs = list(BIGS)
  littles = list(LITTLES)

  cOLED.fill(0).show()
  cRing.fill((0,0,0)).write()
  cLCD.moveTo(0,1).putString("".ljust(16))

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
      cOLED.fill(0).show()
      ucuq.sleep(0.1)
      displayNumber(cards[-1])
      if PROD:
        ucuq.sleep(1)

  toFind = cards[-1] + cards[-2] + cards[-3]

  cards = cards[:4] + sorted(cards[4:])

  cLCD.moveTo(0,0).putString("".center(16))

  if PROD:
    ucuq.sleep(0.5)

  displayCardsOnLCD(cards)

  if PROD:
    ucuq.sleepAwait(8)

  for c in range( 50 if PROD else 0):
    displayNumber(random.randint(101,999))
    for l in range(cRingCount):
      cRing.setValue((l + c) % cRingCount, (0, 0, l * cRingLimiter // (cRingCount - 1)))
    cRing.write()

  if PROD and not CHEAT:
    toFind = random.randint(101,999)
  
  displayNumber(toFind)

  winner = 0

  atlastk.broadcastAction(atkBPlaying)

# BEGIN PYH
  threading.Thread(target=counterAwait).start()
# END PYH

# BEGIN BRY
  aio.run(counterAwait())
# END BRY


async def atkCard(player, dom, id):
  global winner

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
    player.cards.append(result := evalCalc(player.cards, player.calc))
    if result == toFind:
      winner = player.role
    player.calc =  [None, None, None]
    player.calcState = CS_V1
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)

  if winner != 0:
    atlastk.broadcastAction(atkBElapsed, str(player.role))
  else:
    atlastk.broadcastAction(atkBDisplayProgress, str(player.role))


async def atkOperator(player, dom, id):
  if player.calcState != CS_O:
    return

  if player.calcState == CS_O:
    player.calc[1] = int(id)
    player.calcState = CS_V2
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)

  atlastk.broadcastAction(atkBDisplayProgress, str(player.role))


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
  
  atlastk.broadcastAction(atkBDisplayProgress, str(player.role))


ATK_USER = Player
