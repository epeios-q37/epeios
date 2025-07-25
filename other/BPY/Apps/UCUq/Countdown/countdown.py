import atlastk, ucuq, random, time, threading

# BEGIN BRY
from browser import aio
# END BRY

# Languages
L_FR = 0
L_EN = 1

ATK_L10N = (
  (
    "en",
    "fr"
  ),
  (
    "Drawing in progress…",
    "Tirage en cours…"
  ),
  (
    "It's up to you!",
    "À vous de jouer !"
  ),
  (
    "Only one game master allowed!",
    "Un seul maître de jeu autorisé !"
  ),
  (
    "There are already two players…",
    "Il y a déjà deux joueurs…"
  ),
  (
    "Waiting for the second player…",
    "En attente du second joueur…"
  ),
  (
    "Time elapsed!",
    "Temps écoulé !"
  ),
  (
    "Well done!",
    "Bien joué !"
  ),
  (
    "Too slow!",
    "Trop lent !"
  ),
  (
    "Waiting for the drawing...",
    "En attente du tirage..."
  ),
  (
    "New",
    "Nouveau"
  ),
  (
    "Click on '{new}'.",
    "Cliquez sur '{new}'."
  ),
  (
    "To be scanned by second player…",
    "À scanner par le second joueur…"
  ),
  (
    "Waiting for the second player...",
    "En attente du   second joueur..."
  ),
  (
    "Waiting for the drawing...      ",
    "En attente du   tirage...       "
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
def jauge(v):
  oled = {oled}
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
    jauge(1- (elapsed / {delay}))

    if {lcdAvailable}:
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
CS_VALUE_1 = 1
CS_OPERATOR = 2
CS_VALUE_2 = 3

BIG_CARDS = (25, 50, 75, 100)
LITTLE_CARDS = tuple( x for x in range(1, 11) for _ in range(2))

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

hw = None
cards = []
players = 0 # Amount of players.
toFind = 0
winner = 0 # if != 0, the role of the player which wins.

class HW():
  def __init__(self, infos, device=None):
    self.device, self.lcd, self.oled, self.buzzer, self.smartRGB = ucuq.getBits(infos, "LCD", "OLED", "Buzzer", "SmartRGB", device=device)
    
    self.lcd.backlightOn()
    self.buzzer.setNS(0)

    self.smartRGBCount, self.smartRGBOffset, self.smartRGBLimiter = ucuq.getFeatures(infos, "SmartRGB", ["Count", "Offset", "Limiter"]) if self.smartRGB else (10,0,0)

    self.device.addCommand(JAUGE_SCRIPT.format(aw="aw" + "ait", delay=DELAY * 1000,oled=self.oled.getObject(),lcdAvailable="True" if self.lcd else "False",lcd=self.lcd.getObject() if self.lcd else "None"))

    self.reset()

  def reset(self):
    self.oled.fill(0).show()
    self.smartRGB.fill((0,0,0)).write()
    self.lcd.clear()
    
  def oledDisplayDigit_(self, n, offset):
    self.oled.draw(DIGITS[n], 8, offset, mul=6)

  def oledDisplayNumber(self, n):
    self.oled.fill(0)

    if n >= 100:
      self.oledDisplayDigit_(n // 100, 8)

    if n >= 10:
      self.oledDisplayDigit_(n // 10 % 10, 48)

    self.oledDisplayDigit_(n % 10, 88)

    self.oled.show()

  def smartRGBDisplayCounter(self, v):
    if v < 1:
      limit = round(0.5 + self.smartRGBCount * v)

      for l in range(self.smartRGBCount):
        colorCore = int(self.smartRGBLimiter * (l / self.smartRGBCount))
        color = (colorCore, 0, self.smartRGBLimiter - colorCore)
        self.smartRGB.setValue((l + self.smartRGBOffset) % self.smartRGBCount, color if l < limit else (0,0,0))
    else:
      self.smartRGB.fill((self.smartRGBLimiter, 0, 0))

    self.smartRGB.write()

  def oledJauge(self, v): # v: 0 <= v <= 1
    l = int(126*v)
    self.oled.rect(0,50,127,13,0).rect(0, 50, l, 13, 1).rect(l, 50, 127-l, 13, 1, False).show()

  async def counterAwait(self, winner):
    hw.addCommand("elapsed = 0\nstop = False\nasyncio.create_task(counter_())")
    elapsed = 0

    while not winner() and elapsed <= DELAY:
      self.smartRGBDisplayCounter(elapsed / DELAY)
      elapsed = await self.device.commitAwait("elapsed") / 1000

    if winner():
      hw.addCommand("stop = True")

    hw.addCommand("jauge(0)")

    if not winner():
      self.smartRGBDisplayCounter(1)
      atlastk.broadcastAction(atkBElapsed)
    else:
      self.smartRGB.fill([0,0,self.smartRGBLimiter]).write()

  def lcdDisplayCards(self, cards, center = True):
    text = ""

    for c in cards[4:]:
      text += " " + str(c)

    text = text[1:]

    if center:
      text = text.center(16)
    else:
      text = text.ljust(16)

    self.lcd.moveTo(0,0).putString(text)

  def oledClear(self):
    self.oled.fill(0).show()

  def lcdPutString(self, x, y, text):
    self.lcd.moveTo(x,y).putString(text).backlightOn()

  def smartRGBSet(self, index, colors):
    self.smartRGB.setValue((index + self.smartRGBOffset) % self.smartRGBCount, tuple(int(color * self.smartRGBLimiter) for color in colors))

  def smartRGBWrite(self):
    self.smartRGB.write()

  def smartRGBFading(self, index, colors):
    for l in range(self.smartRGBCount):
      self.smartRGBSet(l + index, tuple(color * l / ( self.smartRGBCount -1 ) for color in colors))
    self.smartRGBWrite()

  def sleep(self, delay):
    self.device.sleep(delay)

  def sleepStart(self, chrono):
    self.device.sleepStart(chrono)

  def sleepWait(self, chrono, delay):
    self.device.sleepWait(chrono, delay)

  def addCommand(self, command):
    self.device.addCommand(command)


# 'ucuq.Multi' does not handle coroutines.
class Multi(ucuq.Multi):
  async def counterAwait(self, winner):
    for object in self.objects:
      await object.counterAwait(winner)


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


async def setHardwareAwait(dom):
  global hw

  body = BODY.format(**dom.getL10n(new=10, qrcode=12))

  if UCUq:
    if hw == None:
      hw = Multi(HW(await ucuq.ATKConnectAwait(dom, body)))

    return True
  else:
    hw = ucuq.Nothing()
    await dom.inner("", body)

    return False

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
    html += buildCalc(len(player.calcs), player.cards, player.calc, player.calcState not in (CS_VALUE_1, CS_NONE))

  return html + "</tr>"


async def updateUIAwait(player, dom):
  await dom.inner(W_CALCULATIONS, buildCalcs(player))

  if player.calcState == CS_NONE:
    await enable(player, dom, ())
  elif player.calcState in (CS_VALUE_1, CS_VALUE_2):
    await enable(player, dom, list(W_OPERATORS) + player.usedCards + [len(player.calcs) + 10], False)
  elif player.calcState == CS_OPERATOR:
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
  
  hw.lcdPutString(7 if player.role == 2 else 0, 1,buildProgress(player))


async def atkBSecondPlayer(player, dom):
  if player.role == 1:
    await dom.enableElement(S_HIDE_QR_CODE)
    await dom.disableElement(S_HIDE_NEW_BUTTON)
    await dom.setValue(W_OUTPUT, dom.getL10n(11).format(**dom.getL10n(new=10)))


async def atkBDrawing(player, dom):
  player.reset()

  await dom.setValues({i: "&nbsp;" for i in range(4, 10)})

  await updateUIAwait(player, dom)

  await dom.setValue(W_OUTPUT, dom.getL10n(1))


async def atkBPlaying(player, dom):
  player.cards = list(cards)
  player.calcState = CS_VALUE_1

  await dom.setValues({i + 4: valeur for i, valeur in enumerate(cards[4:])})

  await updateUIAwait(player, dom)

  displayProgress(player, player.role)

  await dom.setValue(W_OUTPUT, dom.getL10n(2))


async def atkBDisplayProgress(player, dom, id):
  assert str(id) in ("1", "2")

  if int(id) != player.role:
    return
  
  displayProgress(player, player.role)


async def atkBElapsed(player, dom):
  hw.lcdPutString(0 if player.role == 1 else 7, 1,(
      ( "> " if player.role == winner else "" )
      + str(evalCalc(player.cards, player.calcs[-1]) if len(player.calcs) else "/") )
    .center(6))

  player.calcState = CS_NONE

  await updateUIAwait(player, dom)

  if winner == 0:
    await dom.setValue(W_OUTPUT, dom.getL10n(6))
  elif player.role == winner:
    await dom.setValue(W_OUTPUT, dom.getL10n(7))
  else:
    await dom.setValue(W_OUTPUT, dom.getL10n(8))

  if player.role == 1:
    await dom.disableElement(S_HIDE_NEW_BUTTON)



# BEGIN PYH
import urllib
encode = lambda t: urllib.parse.quote(t)
# END PYH
# BEGIN BRY
import browser
encode = lambda t: browser.window.encodeURIComponent(t)
# END BRY


async def atk(player, dom, id):
  global players

  assert id == "" or id == "Partner"

  if id == "Partner":
    if players >= 2:
      await dom.alert(dom.getL10n(3))
      return
    
    await dom.inner("", BODY)
    
    players = player.role = 2

    await dom.setValue(W_OUTPUT, dom.getL10n(9))

    atlastk.broadcastAction(atkBSecondPlayer)
    hw.lcdPutString(0,0,dom.getL10n(14))
  else:
    if players != 0:
      await dom.alert(dom.getL10n(4))
      return
    
    await setHardwareAwait(dom)
    
    players = player.role = 1

    url = atlastk.getAppURL(id="Partner")

    await dom.end(W_QR_CODE, f'<a href="{url}" title="{url}" target="Debug"><img src="https://api.qrserver.com/v1/create-qr-code/?size=125x125&data={encode(url)}"/></a>')

    await dom.disableElement(S_HIDE_QR_CODE)

    await dom.setValue(W_OUTPUT, dom.getL10n(5))
    hw.lcdPutString(0,0,dom.getL10n(13))

  await updateUIAwait(player, dom)


async def atkNew(player, dom):
  global cards, toFind, winner

  if player.role == 1:
    await dom.enableElement(S_HIDE_NEW_BUTTON)

  cards = list(OPERATOR_CARDS)

  atlastk.broadcastAction(atkBDrawing)

  bigs = list(BIG_CARDS)
  littles = list(LITTLE_CARDS)

  hw.reset()

  while ( len(bigs) > 2 or len(littles) > 16 ):
    changed = True
    if random.randint(0,2) == 0 and len(bigs) > 2:
      cards.append(bigs.pop(random.randint(0, len(bigs) - 1)))
    elif len(littles) > 16:
      cards.append(littles.pop(random.randint(0, len(littles) - 1)))
    else:
      changed = False

    if changed:
      hw.lcdDisplayCards(cards, False)
      hw.oledClear()
      hw.sleep(0.1)
      hw.oledDisplayNumber(cards[-1])
      if PROD:
        hw.sleep(1)

  toFind = cards[-1] + cards[-2] + cards[-3]

  cards = cards[:4] + sorted(cards[4:])

  hw.lcdPutString(0,0,"".center(16))

  if PROD:
    hw.sleep(0.5)

  hw.lcdDisplayCards(cards)

  if PROD:
    await ucuq.sleepAwait(8)

  chrono = ucuq.getObjectIndice()

  for c in range( 40 if PROD else 0):
    hw.sleepStart(chrono)
    hw.oledDisplayNumber(random.randint(101,999))
    hw.smartRGBFading(c, (1,0,1))
    hw.sleepWait(chrono, 0.15)

  if PROD and not CHEAT:
    toFind = random.randint(101,999)
  
  hw.oledDisplayNumber(toFind)

  winner = 0

  atlastk.broadcastAction(atkBPlaying)

# BEGIN PYH
  threading.Thread(target=hw.counterAwait, args=(lambda: winner != 0,)).start()
# END PYH

# BEGIN BRY
  aio.run(hw.counterAwait(lambda: winner != 0))
# END BRY


async def atkCard(player, dom, id):
  global winner

  if player.calcState not in (CS_VALUE_1, CS_VALUE_2):
    return

  id = int(id)

  if player.calcState == CS_VALUE_1:
    player.usedCards.append(id)
    player.calc[0] = id
    player.calcState = CS_OPERATOR
  elif player.calcState == CS_VALUE_2:
    player.usedCards.append(id)
    player.calc[2] = id
    player.calcs.append(player.calc)
    player.cards.append(result := evalCalc(player.cards, player.calc))
    if result == toFind:
      winner = player.role
    player.calc =  [None, None, None]
    player.calcState = CS_VALUE_1
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)

  if winner != 0:
    atlastk.broadcastAction(atkBElapsed, str(player.role))
  else:
    atlastk.broadcastAction(atkBDisplayProgress, str(player.role))


async def atkOperator(player, dom, id):
  if player.calcState != CS_OPERATOR:
    return

  if player.calcState == CS_OPERATOR:
    player.calc[1] = int(id)
    player.calcState = CS_VALUE_2
  else:
    raise Exception("Unexpected state")
  
  await updateUIAwait(player, dom)

  atlastk.broadcastAction(atkBDisplayProgress, str(player.role))


async def atkDelete(player, dom, id):
  id = int(await dom.getMark(id))

  if player.calcState == CS_NONE:
    return

  if id == len(player.calcs) and player.calcState == CS_VALUE_1:
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
    player.calcState = CS_VALUE_1

  await updateUIAwait(player, dom)
  
  atlastk.broadcastAction(atkBDisplayProgress, str(player.role))


async def UCUqXDevice(dom, device):
  hw.add(HW(await ucuq.getInfosAwait(device), device))


ATK_USER = Player
