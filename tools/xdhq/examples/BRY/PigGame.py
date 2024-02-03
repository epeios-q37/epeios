import atlastk, random, threading, uuid

#DEBUG = True  # Uncomment for debug mode.

LIMIT = 100

GAME_CONTROLS = ["New"]
PLAY_CONTROLS = ["Roll", "Hold"]

METER = '<span class="{}" style="width: {}%;"></span>'

lock = threading.Lock()
games = {}


def uploadDice(affix):
  return open(f"{affix}.svg").read()


class Game:
  def __init__(self):
    self.current = 1 # 1 or 2

    self.available = 1 # 0 (no more player available), 1 or 2

    self.scores = {
      1: 0,
      2: 0
    }

    self.turn = 0  
    self.dice = 0


class User:
  def __init__(self):
    self._player = 0
    self._game = None
    self.token = None   # == None ('_game' != None): 2 human players
                        # != None ('_game' == None): human vs computer.
  def __del__(self):
    if self.token:
      removeGame(self.token, self._player)

  def init(self, token = None):
    deleted = False

    if self.token:
      deleted = removeGame(self.token, self._player)

    self.token = token
    self._game = None if token else Game()  
    self._player = 0

    return deleted

  def getGame(self):
    if self.token:
      game = getGame(self.token)
      if game is None:
        self.token = None
    else:
      game = self._game

    return game

  def getRawPlayer(self):
    return self._player

  def getPlayer(self): # Assign a place, if not yet done, and if possible.
    if self._player == 0:
      self._player = getGameAvailablePlayer(self.token) if self.token else getAvailablePlayer(self._game)

    return self._player


def debug():
  try:
    return DEBUG
  except:
    return False    


def createGame(token):
  global games

  game = Game()  

  with lock:
    games[token] = game
    if debug():
      print("Create: ", token)

  return game


def removeGame(token, player):
  with lock:
    if token in games:
      game = games[token]

      print(game.available, player)
      if game.available == 1 or player != 0:
        del games[token]
        if debug():
          print("Remove: ", token)
        return True

  return False


def getGame(token):
  with lock:
    return games[token] if token in games else None


def getAvailablePlayer(game):
  player = 0

  if game.available:
    player = game.available

    game.available = 2 if game.available == 1 else 0

  return player


def getGameAvailablePlayer(token):
  with lock:
    return getAvailablePlayer(games[token]) if token in games else 0


async def fade(dom, element):
  await dom.removeClass(element, "fade-in")
  await dom.flush()
  await dom.addClass(element, "fade-in")


async def updateMeter(dom, ab, score, turn, dice): # turn includes dice
  if turn != 0:
    await dom.end(f"ScoreMeter{ab}", METER.format("fade-in dice-meter", dice))
  else:
    await dom.inner(f"ScoreMeter{ab}", METER.format("score-meter", score))

  await dom.setValue(f"ScoreText{ab}", score)


async def disableGameControls(dom):
  await dom.disableElements(GAME_CONTROLS)


async def enableGameControls(dom):
  await dom.enableElements(GAME_CONTROLS)


async def disablePlayControls(dom):
  await dom.disableElements(PLAY_CONTROLS)


async def enablePlayControls(dom):
  await dom.enableElements(PLAY_CONTROLS)


def getOpponent(playerAB):
  if playerAB == 'A':
    return 'B'
  elif playerAB == 'B':
    return 'A'
  elif playerAB == 1:
    return 2
  else:
    return 1


async def markPlayer(dom, ab):
  if ab == 'B':
    await dom.disableElement("DisplayMarkerA")
  else:
    await dom.enableElement("DisplayMarkerA")


async def displayDice(dom, value):
  await fade(dom, "dice")

  if value <= 6:
    await dom.inner("dice", DICES[value])


async def updateMeters(dom, game, myTurn):
  if myTurn is None:
    a, b = 1, 2
    turnA = game.turn if game.current == 1 else 0
    turnB = game.turn if game.current == 2 else 0
    diceA = game.dice if game.current == 1 else 0
    diceB = game.dice if game.current == 2 else 0
  else:  
    a = game.current if myTurn else getOpponent(game.current)
    b = getOpponent(a)
    turnA = game.turn if myTurn else 0
    turnB = 0 if myTurn else game.turn
    diceA = game.dice if myTurn else 0
    diceB = 0 if myTurn else game.dice

  await updateMeter(dom, 'A', game.scores[a], turnA, diceA)
  await updateMeter(dom, 'B', game.scores[b], turnB, diceB)


async def updateMarkers(dom, game, myTurn):
  if myTurn is None:
    await markPlayer(dom, 'A' if game.current == 1 else 'B')
  elif myTurn:
    await markPlayer(dom, 'A')
  else:
    await markPlayer(dom, 'B')


async def updatePlayControls(dom, myTurn, winner):
  if myTurn is None or not myTurn or winner != 0:
    await disablePlayControls(dom)
  else:
    await enablePlayControls(dom)


async def displayTurn(dom, element, value):
    await fade(dom, element)
    await dom.setValue(element, value)


async def updateDice(dom, game, winner):
  if winner != 0 or game.turn != 0 or game.dice == 1:
    await displayDice(dom, game.dice)


async def updateTurn(dom, game):
  await displayTurn(dom, "Cumul", game.turn)
  await displayTurn(dom, "Total", game.scores[game.current] + game.turn)


async def reportWinner(dom, player, winner):
  ab = 'A' if winner == player or player == 0 and winner == 1 else 'B'
  await dom.setValue(f"ScoreMeter{ab}", "<span style='background-color: lightgreen; width: 100%;'><span class='winner'>Winner!</span></span>")
  await dom.setValue(f"ScoreText{ab}", 100)


async def updateLayout(dom, game, player):
  if game.scores[1] + (game.turn if game.current == 1 else 0) >= LIMIT:
    winner = 1
  elif game. scores[2] + (game.turn if game.current == 2 else 0) >= LIMIT:
    winner = 2
  else:
    winner = 0

  if player != 0:
    myTurn = player == game.current
  elif game.available != 0:
    myTurn = game.available == game.current
  else:
    myTurn = None

  await updateDice(dom, game, winner)
  await updateTurn(dom, game)
  await updateMeters(dom, game, myTurn)
  await updateMarkers(dom, game, myTurn)
  await updatePlayControls(dom, myTurn, winner)

  if winner != 0:
    await reportWinner(dom, player, winner)


async def display(dom, game, player):
  if game is None:
    await disablePlayControls(dom)
    await dom.alert("Game aborted!")
    return

  if game.available == 0 and player == 0:
    await dom.disableElement("PlayerView")

  await updateLayout(dom, game, player)


async def setLayout(dom):
  await dom.inner("", BODY)

  if debug():
    await dom.removeClass("debug", "removed")


async def acConnect(user, dom, id):
  await setLayout(dom)
  await displayDice(dom, 0)

  user.init(id)
  await display(dom, user.getGame(), user.getRawPlayer())


def getPlayer(user, dom):
  return user.getPlayer()


def botDecision(botScore, turnScore, humanScore, timesThrown):
  return turnScore < 20
  # Replace by your own algorithm.
  # Algorithm can be more elaborate by using the other parameters.


async def computerTurn(game, dom):
  game.current = 2
  timesThrown = 0

  await disableGameControls(dom)

  await atlastk.sleep(1000)

  while True:
    game.dice = random.randint(1, 6)
    timesThrown += 1

    if game.dice == 1:
      game.turn = 0
      game.current = 1
      await display(dom, game, 1)
      break

    game.turn += game.dice

    if game.scores[2] + game.turn >= LIMIT:
      await display(dom, game, 1)
      break

    await display(dom, game, 1)
    await atlastk.sleep(2500)    

    if not botDecision(game.scores[2], game.turn, game.scores[1], timesThrown):
      game.scores[2] += game.turn
      game.turn = 0
      game.current = 1
      await display(dom, game, 1)
      break

  await enableGameControls(dom)


def broadcast(token):
  atlastk.broadcastAction("Display", token)


async def acRoll(user, dom):
  await disablePlayControls(dom)
  player = getPlayer(user, dom)

  if player == 0:
    return

  game = user.getGame()

  if game is None:
    broadcast(user.token)
    return

  game.dice = random.randint(1, 6)

  if debug():
    debugDice = await dom.getValue("debug")
    if debugDice:
      game.dice = int(debugDice)

  if game.dice == 1:
    game.current = getOpponent(game.current)
    game.turn = 0
  else:
    game.turn += game.dice

  if user.token:
    broadcast(user.token)
  else:
    await display(dom, game, 1)
    if game.dice == 1:
      await computerTurn(game, dom)


async def acHold(user, dom):
  await disablePlayControls(dom)

  player = getPlayer(user, dom)

  if player == 0:
    return

  game = user.getGame()

  if game is None:
    await disablePlayControls(dom)
    await dom.alert("Game aborted!")
    return

  game.scores[player] += game.turn
  game.current = getOpponent(game.current)
  game.turn = 0
  game.dice = 0

  if user.token:
    broadcast(user.token)
  else:
    await display(dom, game, 1)
    await computerTurn(game, dom)


async def newBetweenHumans(user, dom):
  global games

  token = "debug" if debug() else str(uuid.uuid4())

  createGame(token)

  url = atlastk.getAppURL(token)
  escapedUrl = url.replace(":", "%3A").replace("?", "%3F").replace("=", "%3D")
  await dom.inner("qrcode", f'<a href="{url}" title="{url}" target="_blank"><img style="margin: auto; width:100%;" src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={escapedUrl}&bgcolor=FFB6C1"/></a>')
  await dom.disableElement("HideHHLinkSection")

  return user.init(token)


async def newAgainstComputer(user, dom):
  await dom.enableElement("HideHHLinkSection")
  deleted = user.init()

  user.getPlayer() ## To assign player.
  getAvailablePlayer(user.getGame()) # To eat remaining available player.

  return deleted


async def acNew(user, dom):
  mode = await dom.getValue("Mode")
  token = user.token

  await setLayout(dom)
  await dom.enableElement("PlayerView")
  await displayDice(dom, 0)

  deleted = (await newAgainstComputer(user, dom)) if mode == "HC" else (await newBetweenHumans(user, dom))

  await display(dom, user.getGame(), 1)

  if deleted:
    broadcast(token)


async def acDisplay(user, dom, id):
  if id != user.token:
    return

  game = user.getGame()

  if game is None:
    await disablePlayControls(dom)
    await dom.alert("Game aborted!")
    return

  await display(dom, user.getGame(), user.getRawPlayer())


CALLBACKS = {
  "": acConnect,
  "Roll": acRoll,
  "Hold": acHold,
  "New": acNew,
  "Display": acDisplay
}

HEAD = """
<title>The 🐷 game</title>
<style>
  .hidden {
    visibility: hidden;
  }

  .removed {
    display: none;
  }

  .meter-label {
    width: 9ch;
    font-family: monospace;
    font-size: larger;
  }

  .marker {
    width: 3ex;
    color:sandybrown;
  }

  .meter-container {
    width: 200px;
    display: flex;
    border: solid 1px;
    height: 20px;
  }

  .meter {
    display: block;
    height: 100%;
  }

  .score-meter {
    background-color: lightgreen;
  }

  .dice-meter {
    background-color: violet;
  }

  .winner_ {
    color: crimson;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: larger;
    letter-spacing: 5px;
    font-family: cursive;
    width: 100%;
    background-color: lightgreen;
}

  .score-text {
    width: 3ch;
    text-align: right;
    font-family: cursive;
  }

  .turn-text {
    width: 2ch;
    text-align: right;
    font-family: cursive;
    display: inline-block;
  }

  @keyframes fadeIn {
    0% {
      opacity: 0;
      transform: scale(0) rotate(-240deg); 
    }

    100% {
      opacity: 1;
      transform: scale(1) rotate(0deg);
    }
  }

  .fade-in {
    animation-name: fadeIn;
    animation-duration: 1s;
  }

  .marker-a {
    visibility: hidden;
  }

  .player {
    display: none;
  }

  .winner {
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: larger;
    letter-spacing: 5px;
    font-family: cursive;
    width: 100%;
    background-color: lightgreen;
    background: linear-gradient(to right, #6666ff, #0099ff , #00ff00, #ff3399, #6666ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: rainbow_animation 6s ease-in-out infinite;
    background-size: 400% 100%;
    height: 100%;
  }

  @keyframes rainbow_animation {
      0%,100% {
          background-position: 0 0;
      }

      50% {
          background-position: 100% 0;
      }
  }
</style>
<style id="DisplayMarkerA">
  .marker-a {
    visibility: initial;
  }

  .marker-b {
    visibility: hidden;
  }
</style>
<style id="HideHHLinkSection">
  #HHLinkSection {
    display: none;
  }
</style>
<style id="PlayerView">
  .viewer {
    display: none;
  }

  .player {
    display: initial;
  }
</style>
"""

BODY = """
<fieldset style="display: flex; flex-direction: column; padding-top: 15px; width: 50%;">
  <span style="display: flex; align-items: center;">
    <span class="meter-label player">You</span>
    <span class="meter-label viewer">Player 1</span>
    <span class="marker marker-a">➤</span>
    <span id="ScoreMeterA" class="meter-container"></span>
    <span style="width: 10px;"></span>
    <output id="ScoreTextA" class="score-text">100</output>
  </span>
  <span style="height: 15px;"></span>
  <span style="display: flex; align-items: center;">
    <span class="meter-label player">Opponent</span>
    <span class="meter-label viewer">Player 2</span>
    <span class="marker marker-b">➤</span>
    <span id="ScoreMeterB" class="meter-container"></span>
    <span style="width: 10px;"></span>
    <output id="ScoreTextB" class="score-text">10</output>
  </span>
  <span style="height: 15px;"></span>
  <span style="display: flex; flex-direction: row; justify-content: space-around">
    <span>
      <span>Cumul - Total: </span>
      <output id="Cumul" class="turn-text">59</output>
      <output id="Total" class="turn-text">95</output>
    </span>
  </span>
  <span style="height: 15px;"></span>
  <span style="width: 100%; display: flex; justify-content: space-around; align-items: center;">
    <button id="Roll" xdh:onevent="Roll">ROLL</button>
    <input id="debug" xdh:onevent="Roll" class="removed" size="3" maxlength="3" />
    <span id="dice" style="width: 100px; height: 100px;"></span>
    <button id="Hold" xdh:onevent="Hold">HOLD</button>
  </span>
  <span style="height: 15px;"></span>
  <span style="display: flex; justify-content: center;">
    <select id="Mode">
      <option value="HC">human vs computer</option>
      <option value="HH">human vs human</option>
    </select>
    <span style="width: 10px;"></span>
    <button id="New" xdh:onevent="New">New game</button>
  </span>
  <span style="height: 15px;"></span>
  <span id="HHLinkSection">
    <fieldset style="margin: auto; width: max-content;">
      <legend>URL for the opponent</legend>
      <details style="width: 100%;">
        <summary style="cursor: pointer;">What's this?</summary>
        <fieldset>
          <span>Your opponent may scan</span><br />
          <span>this QR code on her/him</span><br />
          <span>device, or you may copy</span><br />
          <span>and send her/him</span><br />
          <span>corresponding URL.</span>
        </fieldset>
      </details>
      <span id="qrcode" style="font-style: oblique; margin: auto; width:100%;">Computing QR Code…</span>
    </fieldset>
  </span>
</fieldset>
"""

PIG = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns="http://www.w3.org/2000/svg"
   viewBox="0 0 425 425"
>
  <defs
     id="defs4">
    <linearGradient
       id="linearGradient3274">
      <stop
         style="stop-color: rgb(255, 0, 0); stop-opacity: 1;"
         offset="0"
         id="stop3276" />
      <stop
         style="stop-color: rgb(255, 98, 98); stop-opacity: 1;"
         offset="1"
         id="stop3278" />
    </linearGradient>
    <linearGradient
       id="linearGradient3169">
      <stop
         style="stop-color: rgb(212, 212, 212); stop-opacity: 1;"
         offset="0"
         id="stop3171" />
      <stop
         style="stop-color: rgb(159, 150, 150); stop-opacity: 1;"
         offset="1"
         id="stop3173" />
    </linearGradient>
    <linearGradient
       id="linearGradient3161">
      <stop
         style="stop-color: rgb(0, 190, 255); stop-opacity: 1;"
         offset="0"
         id="stop3163" />
      <stop
         style="stop-color: rgb(0, 116, 255); stop-opacity: 1;"
         offset="1"
         id="stop3165" />
    </linearGradient>
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient3169"
       id="linearGradient3218"
       gradientUnits="userSpaceOnUse"
       gradientTransform="matrix(1.17318,0,0,1.22714,-28.2282,-58.9006)"
       x1="-133.21428"
       y1="544.86218"
       x2="393.21429"
       y2="602.7193" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient3169"
       id="linearGradient3220"
       gradientUnits="userSpaceOnUse"
       x1="-133.21428"
       y1="180.93361"
       x2="393.21429"
       y2="537.005" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient3161"
       id="linearGradient3222"
       gradientUnits="userSpaceOnUse"
       x1="-60.221073"
       y1="215.21931"
       x2="320.22107"
       y2="501.29077" />
    <linearGradient
       id="linearGradient2388">
      <stop
         style="stop-color:#ff0f0f;stop-opacity:1;"
         offset="0"
         id="stop2390" />
      <stop
         style="stop-color:#790000;stop-opacity:1.0000000;"
         offset="1.0000000"
         id="stop2392" />
    </linearGradient>
    <linearGradient
       id="linearGradient2342">
      <stop
         style="stop-color:#c98b2b;stop-opacity:0.0000000;"
         offset="0.0000000"
         id="stop2344" />
      <stop
         style="stop-color:#c98b2b;stop-opacity:1.0000000;"
         offset="1.0000000"
         id="stop2346" />
    </linearGradient>
    <linearGradient
       id="linearGradient2331">
      <stop
         style="stop-color:#fdfdfd;stop-opacity:1;"
         offset="0"
         id="stop2333" />
      <stop
         style="stop-color:#dcdcdc;stop-opacity:1.0000000;"
         offset="1.0000000"
         id="stop2335" />
    </linearGradient>
    <linearGradient
       id="linearGradient15809">
      <stop
         style="stop-color:#eeffaa;stop-opacity:1"
         offset="0"
         id="stop15811" />
      <stop
         style="stop-color:#82ad00;stop-opacity:1;"
         offset="1"
         id="stop15813" />
    </linearGradient>
    <linearGradient
       id="linearGradient6884">
      <stop
         style="stop-color:#ff8900;stop-opacity:1;"
         offset="0"
         id="stop6886" />
      <stop
         style="stop-color:#b64014;stop-opacity:1;"
         offset="1"
         id="stop6888" />
    </linearGradient>
    <linearGradient
       id="linearGradient5028">
      <stop
         style="stop-color:#2d5016;stop-opacity:1;"
         offset="0"
         id="stop5030" />
      <stop
         style="stop-color:#5aa02c;stop-opacity:1"
         offset="1"
         id="stop5032" />
    </linearGradient>
    <linearGradient
       id="linearGradient15803">
      <stop
         id="stop15805"
         offset="0"
         style="stop-color:#2b1100;stop-opacity:1;" />
      <stop
         id="stop15807"
         offset="1"
         style="stop-color:#d45500;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient11080">
      <stop
         style="stop-color:#f6ffd5;stop-opacity:1"
         offset="0"
         id="stop11082" />
      <stop
         style="stop-color:#529d50;stop-opacity:1;"
         offset="1"
         id="stop11084" />
    </linearGradient>
    <linearGradient
       id="linearGradient9737">
      <stop
         id="stop9739"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9741"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9761">
      <stop
         id="stop9763"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9765"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9749">
      <stop
         id="stop9751"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9753"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9767">
      <stop
         id="stop9769"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9771"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9773">
      <stop
         id="stop9775"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9777"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9797">
      <stop
         id="stop9799"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9801"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9779">
      <stop
         id="stop9781"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9783"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9755">
      <stop
         id="stop9757"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9759"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9785">
      <stop
         id="stop9787"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9789"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9743">
      <stop
         id="stop9745"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9747"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9791">
      <stop
         id="stop9793"
         offset="0"
         style="stop-color:#ffdd55;stop-opacity:1" />
      <stop
         id="stop9795"
         offset="1"
         style="stop-color:#4d7600;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient9149">
      <stop
         style="stop-color:#ffdd55;stop-opacity:1"
         offset="0"
         id="stop9151" />
      <stop
         style="stop-color:#4d7600;stop-opacity:1;"
         offset="1"
         id="stop9153" />
    </linearGradient>
    <linearGradient
       id="linearGradient15785">
      <stop
         style="stop-color:#2b1100;stop-opacity:1;"
         offset="0"
         id="stop15787" />
      <stop
         style="stop-color:#d45500;stop-opacity:1"
         offset="1"
         id="stop15789" />
    </linearGradient>
    <linearGradient
       id="linearGradient8530">
      <stop
         id="stop8532"
         offset="0"
         style="stop-color:#eeffaa;stop-opacity:1" />
      <stop
         style="stop-color:#90bf55;stop-opacity:1;"
         offset="0.5"
         id="stop14737" />
      <stop
         id="stop8534"
         offset="1"
         style="stop-color:#338000;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient5040">
      <stop
         style="stop-color:#800000;stop-opacity:1;"
         offset="0"
         id="stop5042" />
      <stop
         style="stop-color:#501616;stop-opacity:1"
         offset="1"
         id="stop5044" />
    </linearGradient>
    <linearGradient
       id="linearGradient15797">
      <stop
         id="stop15799"
         offset="0"
         style="stop-color:#2b1100;stop-opacity:1;" />
      <stop
         id="stop15801"
         offset="1"
         style="stop-color:#aa4400;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient12058">
      <stop
         style="stop-color:#d4aa00;stop-opacity:1"
         offset="0"
         id="stop12060" />
      <stop
         style="stop-color:#ffeeaa;stop-opacity:1"
         offset="1"
         id="stop12062" />
    </linearGradient>
    <linearGradient
       id="linearGradient12064">
      <stop
         id="stop12066"
         offset="0"
         style="stop-color:#e9cc55;stop-opacity:1" />
      <stop
         id="stop12068"
         offset="1"
         style="stop-color:#ffeeaa;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient11913">
      <stop
         id="stop11915"
         offset="0"
         style="stop-color:#e6aa00;stop-opacity:1;" />
      <stop
         id="stop11917"
         offset="1"
         style="stop-color:#ffeeaa;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient12236">
      <stop
         id="stop12238"
         offset="0"
         style="stop-color:#d4aa00;stop-opacity:1" />
      <stop
         id="stop12240"
         offset="1"
         style="stop-color:#ffe680;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient12230">
      <stop
         style="stop-color:#d4aa00;stop-opacity:1"
         offset="0"
         id="stop12232" />
      <stop
         style="stop-color:#f4eed7;stop-opacity:1"
         offset="1"
         id="stop12234" />
    </linearGradient>
    <linearGradient
       id="linearGradient12532">
      <stop
         style="stop-color:#e9cc55;stop-opacity:1"
         offset="0"
         id="stop12534" />
      <stop
         style="stop-color:#decd87;stop-opacity:1"
         offset="1"
         id="stop12536" />
    </linearGradient>
    <linearGradient
       id="linearGradient12538">
      <stop
         style="stop-color:#e9cc55;stop-opacity:1"
         offset="0"
         id="stop12540" />
      <stop
         style="stop-color:#ffeeaa;stop-opacity:1"
         offset="1"
         id="stop12542" />
    </linearGradient>
    <linearGradient
       id="linearGradient12526">
      <stop
         id="stop12528"
         offset="0"
         style="stop-color:#d4aa00;stop-opacity:1" />
      <stop
         id="stop12530"
         offset="1"
         style="stop-color:#e9ddaf;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient12520">
      <stop
         style="stop-color:#e9cc55;stop-opacity:1"
         offset="0"
         id="stop12522" />
      <stop
         style="stop-color:#fff6d5;stop-opacity:1"
         offset="1"
         id="stop12524" />
    </linearGradient>
    <linearGradient
       id="linearGradient10390">
      <stop
         id="stop10392"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop10394"
         offset="1"
         style="stop-color:#554400;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient10132">
      <stop
         style="stop-color:#afe9af;stop-opacity:1;"
         offset="0"
         id="stop10134" />
      <stop
         style="stop-color:#004900;stop-opacity:1;"
         offset="1"
         id="stop10136" />
    </linearGradient>
    <linearGradient
       id="linearGradient10260">
      <stop
         id="stop10262"
         offset="0"
         style="stop-color:#002b00;stop-opacity:1" />
      <stop
         id="stop10264"
         offset="1"
         style="stop-color:#7db27d;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9824">
      <stop
         style="stop-color:#9dc22c;stop-opacity:1;"
         offset="0"
         id="stop9826" />
      <stop
         style="stop-color:#eeffaa;stop-opacity:1"
         offset="1"
         id="stop9828" />
    </linearGradient>
    <linearGradient
       id="linearGradient11611">
      <stop
         id="stop11613"
         offset="0"
         style="stop-color:#000050;stop-opacity:1;" />
      <stop
         id="stop11615"
         offset="1"
         style="stop-color:#22280b;stop-opacity:0;" />
    </linearGradient>
    <linearGradient
       id="linearGradient12008">
      <stop
         style="stop-color:#552200;stop-opacity:1"
         offset="0"
         id="stop12010" />
      <stop
         style="stop-color:#002400;stop-opacity:1;"
         offset="1"
         id="stop12012" />
    </linearGradient>
    <linearGradient
       id="linearGradient9014">
      <stop
         style="stop-color:#ffff14;stop-opacity:1;"
         offset="0"
         id="stop9018" />
      <stop
         id="stop9020"
         offset="1"
         style="stop-color:#ffcc00;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9112">
      <stop
         id="stop9114"
         offset="0"
         style="stop-color:#d45500;stop-opacity:1" />
      <stop
         id="stop9116"
         offset="1"
         style="stop-color:#ffffff;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9427">
      <stop
         id="stop9429"
         offset="0"
         style="stop-color:#abc837;stop-opacity:1;" />
      <stop
         id="stop9431"
         offset="1"
         style="stop-color:#225500;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9044">
      <stop
         style="stop-color:#abc837;stop-opacity:1;"
         offset="0"
         id="stop9046" />
      <stop
         style="stop-color:#338000;stop-opacity:1"
         offset="1"
         id="stop9048" />
    </linearGradient>
    <linearGradient
       id="linearGradient9421">
      <stop
         style="stop-color:#aad400;stop-opacity:1"
         offset="0"
         id="stop9423" />
      <stop
         style="stop-color:#225500;stop-opacity:1"
         offset="1"
         id="stop9425" />
    </linearGradient>
    <linearGradient
       id="linearGradient9415">
      <stop
         style="stop-color:#ccff00;stop-opacity:1"
         offset="0"
         id="stop9417" />
      <stop
         style="stop-color:#447821;stop-opacity:1"
         offset="1"
         id="stop9419" />
    </linearGradient>
    <linearGradient
       id="linearGradient9433">
      <stop
         id="stop9435"
         offset="0"
         style="stop-color:#abc837;stop-opacity:1;" />
      <stop
         id="stop9437"
         offset="1"
         style="stop-color:#225500;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9478">
      <stop
         style="stop-color:#abc837;stop-opacity:1"
         offset="0"
         id="stop9480" />
      <stop
         style="stop-color:#338000;stop-opacity:1"
         offset="1"
         id="stop9482" />
    </linearGradient>
    <linearGradient
       id="linearGradient9472">
      <stop
         style="stop-color:#ccff00;stop-opacity:1"
         offset="0"
         id="stop9474" />
      <stop
         style="stop-color:#225500;stop-opacity:1"
         offset="1"
         id="stop9476" />
    </linearGradient>
    <linearGradient
       id="linearGradient9246">
      <stop
         id="stop9248"
         offset="0"
         style="stop-color:#aad400;stop-opacity:1" />
      <stop
         id="stop9250"
         offset="1"
         style="stop-color:#338000;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9276">
      <stop
         id="stop9278"
         offset="0"
         style="stop-color:#ccff00;stop-opacity:1" />
      <stop
         id="stop9280"
         offset="1"
         style="stop-color:#338000;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient9985">
      <stop
         style="stop-color:#ddff55;stop-opacity:1"
         offset="0"
         id="stop9987" />
      <stop
         style="stop-color:#338000;stop-opacity:1"
         offset="1"
         id="stop9989" />
    </linearGradient>
    <linearGradient
       id="linearGradient10384">
      <stop
         id="stop10386"
         offset="0"
         style="stop-color:#2b1100;stop-opacity:1;" />
      <stop
         id="stop10388"
         offset="1"
         style="stop-color:#603d00;stop-opacity:1;" />
    </linearGradient>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7154">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7156"
         d="m 24.114628,-171.41743 c -11.624027,0 -21.0146851,15.446 -21.0146851,34.49907 0,0.38816 0.031737,0.75675 0.039504,1.14182 -2.18718359,3.73628 -6.0219418,8.6763 -6.0219418,14.10955 l 0,1.22337 0,4.56726 0,54.737897 268.7291649,0 0,-54.737897 0,-4.56726 0,-1.22337 c 0,-5.49603 -4.70383,-10.52135 -6.93639,-14.27267 -1.09909,-15.36979 -10.25473,-27.40353 -21.37019,-27.40353 -6.79145,0 -12.82461,4.49867 -16.74855,11.4997 -2.21407,-1.32014 -5.20102,-1.53847 -8.37428,-0.24466 -2.14482,0.87449 -4.09661,2.33123 -5.68818,4.07791 -2.09561,-11.37957 -10.65042,-19.90018 -20.93568,-19.90018 -11.38862,0 -20.73063,10.4449 -21.4492,23.65185 -1.80465,-2.42411 -4.43306,-3.9148 -7.38674,-3.9148 -0.73957,0 -1.47959,0.1443 -2.17257,0.32625 -3.65034,-8.33355 -13.64281,-14.35422 -25.43883,-14.35422 -11.00112,0 -20.39835,5.2582 -24.5698,12.72307 -1.50862,-0.70191 -3.15655,-1.14182 -4.937664,-1.14182 -1.175013,0 -2.28856,0.25305 -3.35761,0.5709 -3.209028,-7.80121 -10.63342,-13.29397 -19.316128,-13.29397 -7.557488,0 -14.14265,4.14835 -17.854582,10.35788 -2.599965,-2.17315 -5.610109,-3.42543 -8.848288,-3.42543 -2.873267,0 -5.58836,0.95199 -7.97926,2.69141 -3.60427,-10.52525 -10.480367,-17.69811 -18.3681,-17.69813 z"
         style="fill:url(#linearGradient7158);fill-opacity:1;stroke:#8a916f;stroke-width:0.28937784;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <linearGradient
       id="linearGradient6546">
      <stop
         style="stop-color:#ff6600;stop-opacity:1;"
         offset="0"
         id="stop6548" />
      <stop
         style="stop-color:#ffa800;stop-opacity:1;"
         offset="1"
         id="stop6550" />
    </linearGradient>
    <linearGradient
       id="linearGradient6605">
      <stop
         style="stop-color:#008000;stop-opacity:1;"
         offset="0"
         id="stop6607" />
      <stop
         style="stop-color:#aad400;stop-opacity:1"
         offset="1"
         id="stop6609" />
    </linearGradient>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7148">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7150"
         d="m 30.731448,-166.89305 c -10.216822,-1.00666 -19.80829,11.75621 -21.4583096,28.50272 -0.033615,0.34117 -0.037641,0.66789 -0.064161,1.00701 -2.2459698,3.09455 -6.0443044,7.10444 -6.5148304,11.87994 l -0.1059454,1.07527 -0.3955296,4.01434 -4.7403689,48.111333 236.1968169,23.272273 4.74037,-48.111331 0.39553,-4.014345 0.10594,-1.07527 c 0.47596,-4.83068 -3.22322,-9.655 -4.86064,-13.14552 0.36501,-13.60431 -6.64011,-24.97413 -16.40993,-25.93674 -5.96928,-0.58815 -11.66165,2.84343 -15.71686,8.6571 -1.83171,-1.35206 -4.43815,-1.80264 -7.3393,-0.94026 -1.9609,0.58287 -3.80256,1.69423 -5.35272,3.09163 -0.85644,-10.18344 -7.6377,-18.4134 -16.67783,-19.30412 -10.00992,-0.98627 -19.12552,7.38515 -20.90084,18.93103 -1.37625,-2.28693 -3.55737,-3.82478 -6.15347,-4.08057 -0.65005,-0.064 -1.31297,-0.001 -1.93782,0.0986 -2.48673,-7.64081 -10.74811,-13.79798 -21.11611,-14.81953 -9.66933,-0.95271 -18.38429,2.85512 -22.697216,9.05504 -1.2652,-0.74758 -2.675535,-1.27695 -4.241025,-1.4312 -1.032766,-0.10176 -2.033423,0.0242 -3.000579,0.21102 -2.144949,-7.13471 -8.194865,-12.60547 -15.826444,-13.3574 -6.642579,-0.65449 -12.789793,2.42137 -16.590112,7.55772 -2.097016,-2.13523 -4.634302,-3.49659 -7.480468,-3.77702 -2.525429,-0.24883 -4.994276,0.35278 -7.246369,1.67457 -2.256438,-9.5632 -7.678937,-16.46319 -14.611779,-17.14629 z"
         style="fill:url(#linearGradient7152);fill-opacity:1;stroke:#8a916f;stroke-width:0.25557739;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7142">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7144"
         d="m 52.691746,-157.68036 c -11.468311,0.473 -20.104648,16.09421 -19.329347,34.89205 0.01579,0.38296 0.0621,0.74532 0.08544,1.12491 -2.005849,3.77523 -5.588219,8.80512 -5.367131,14.16559 l 0.04978,1.20698 0.185849,4.50607 2.227375,54.004631 265.129258,-10.935031 -2.22738,-54.00463 -0.18585,-4.50607 -0.0498,-1.20698 c -0.22364,-5.42241 -5.06894,-10.18901 -7.42424,-13.79922 -1.70979,-15.11918 -11.23246,-26.61915 -22.19901,-26.16685 -6.70047,0.27636 -12.46975,4.96026 -16.05624,12.02718 -2.23814,-1.21236 -5.19395,-1.30622 -8.27206,0.0994 -2.0805,0.95005 -3.94687,2.4667 -5.44604,4.25474 -2.5306,-11.14185 -11.31752,-19.20021 -21.465,-18.78169 -11.23606,0.46342 -20.0279,11.14855 -20.19943,24.20781 -1.87912,-2.3182 -4.53297,-3.68196 -7.44709,-3.56177 -0.72967,0.0301 -1.4539,0.20257 -2.13019,0.41028 -3.94054,-8.07337 -14.04414,-13.60678 -25.68215,-13.12678 -10.85375,0.44765 -19.91112,6.0178 -23.72294,13.55241 -1.51697,-0.63111 -3.16073,-0.99808 -4.91798,-0.9256 -1.15927,0.0478 -2.2476,0.34279 -3.2894,0.69988 -3.48348,-7.56612 -11.03193,-12.68319 -19.59832,-12.32987 -7.456247,0.30752 -13.784391,4.66826 -17.193922,10.94566 -2.653565,-2.03825 -5.674342,-3.15127 -8.869142,-3.0195 -2.834776,0.11692 -5.47476,1.16663 -7.762851,2.98004 -3.984277,-10.23759 -11.060137,-17.03456 -18.842207,-16.71362 z"
         style="fill:url(#linearGradient7146);fill-opacity:1;stroke:#8a916f;stroke-width:0.28574407;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7136">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7138"
         d="m -61.990915,-183.71631 c -12.595621,-1.41049 -24.645456,14.18708 -26.957407,34.8327 -0.0471,0.42061 -0.05744,0.82386 -0.09574,1.24205 -2.82337,3.78318 -7.578092,8.6708 -8.237377,14.55818 l -0.148447,1.32563 -0.554202,4.94901 -6.642052,59.313159 291.19087,32.608314 6.64205,-59.313163 0.5542,-4.949006 0.14845,-1.325624 c 0.6669,-5.95543 -3.82031,-11.97156 -5.78428,-16.30733 0.67405,-16.78785 -7.78666,-30.9384 -19.8312,-32.28717 -7.35911,-0.8241 -14.44243,3.31852 -19.54388,10.42858 -2.23895,-1.69914 -5.44906,-2.29816 -9.04456,-1.28126 -2.43021,0.68732 -4.7219,2.02899 -6.65845,3.72854 -0.88995,-12.58502 -9.12589,-22.85589 -20.27084,-24.10393 -12.34055,-1.38192 -23.730808,8.80243 -26.112008,23.02609 -1.661344,-2.84571 -4.328564,-4.77993 -7.529129,-5.13834 -0.801392,-0.0897 -1.620773,-0.0232 -2.393757,0.0899 -2.944231,-9.47305 -13.041357,-17.20947 -25.823348,-18.64083 -11.920651,-1.33491 -22.741387,3.22251 -28.16732,10.80515 -1.549546,-0.94363 -3.281838,-1.62028 -5.211824,-1.8364 -1.273226,-0.14258 -2.510557,-0.003 -3.70753,0.2112 -2.530635,-8.84267 -9.9090886,-15.69543 -19.3175405,-16.74902 -8.1891805,-0.91704 -15.8281335,2.77898 -20.6038085,9.05712 -2.553587,-2.67028 -5.663378,-4.39249 -9.17222,-4.78542 -3.113429,-0.34865 -6.17098,0.35345 -8.972788,1.94814 -2.628371,-11.84235 -9.208832,-20.44912 -17.755858,-21.40626 z"
         style="fill:url(#linearGradient7140);fill-opacity:1;stroke:#8a916f;stroke-width:0.31552541;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7130">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7132"
         d="m -49.147345,-185.04414 c -11.139993,-1.09761 -21.598126,12.81848 -23.397237,31.07817 -0.03665,0.37199 -0.04104,0.72823 -0.06996,1.098 -2.448911,3.37417 -6.590455,7.74638 -7.103497,12.95339 l -0.115518,1.17243 -0.431269,4.37707 -5.168699,52.458565 257.539065,25.375105 5.16869,-52.45857 0.43127,-4.37707 0.11552,-1.17243 c 0.51897,-5.26717 -3.51446,-10.5274 -5.29983,-14.33332 0.39799,-14.83357 -7.24011,-27.23074 -17.89271,-28.28033 -6.50864,-0.6413 -12.71537,3.10036 -17.13699,9.43933 -1.99723,-1.47423 -4.83918,-1.96551 -8.00247,-1.02522 -2.13808,0.63554 -4.14615,1.84733 -5.83638,3.37099 -0.93382,-11.1036 -8.32783,-20.0772 -18.1848,-21.0484 -10.914398,-1.07539 -20.853666,8.05245 -22.789399,20.6416 -1.500604,-2.49357 -3.878803,-4.17038 -6.709491,-4.44928 -0.708779,-0.0698 -1.431606,-0.001 -2.112914,0.10751 -2.711424,-8.33122 -11.719289,-15.04474 -23.024115,-16.15859 -10.543027,-1.0388 -20.045457,3.1131 -24.748089,9.87323 -1.379521,-0.81514 -2.917291,-1.39234 -4.624235,-1.56052 -1.126085,-0.11095 -2.217159,0.0264 -3.271705,0.23008 -2.338762,-7.77938 -8.9353355,-13.74447 -17.25648874,-14.56434 -7.24278826,-0.71363 -13.94545126,2.64016 -18.08915926,8.24062 -2.286498,-2.32816 -5.053048,-3.81254 -8.156387,-4.1183 -2.753621,-0.27132 -5.445549,0.38465 -7.901136,1.82588 -2.460325,-10.42731 -8.372789,-17.95077 -15.932068,-18.6956 z"
         style="fill:url(#linearGradient7134);fill-opacity:1;stroke:#8a916f;stroke-width:0.27867082;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7124">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7126"
         d="m -71.465985,-142.79742 c -12.391781,1.75324 -20.072975,19.63582 -17.199216,39.94733 0.05854,0.41379 0.147973,0.80195 0.214332,1.21127 -1.768105,4.312949 -5.111045,10.157651 -4.291552,15.949759 l 0.18452,1.304174 0.688874,4.868914 8.25607,58.353278 286.478427,-40.532184 -8.25607,-58.353281 -0.68888,-4.86891 -0.18452,-1.30417 c -0.82896,-5.85905 -6.60143,-10.50681 -9.54726,-14.16916 -3.48989,-16.21918 -15.0653,-27.66679 -26.91492,-25.99026 -7.24002,1.02435 -12.99313,6.73013 -16.12028,14.78541 -2.55942,-1.07338 -5.77659,-0.85562 -8.96429,1.00227 -2.15459,1.25575 -4.01557,3.10309 -5.44881,5.20519 -3.9504,-11.81509 -14.3554,-19.60817 -25.31999,-18.05685 -12.140831,1.71773 -20.524466,14.26156 -19.298508,28.44919 -2.289471,-2.31202 -5.316322,-3.50473 -8.465091,-3.05923 -0.788423,0.11155 -1.555553,0.37699 -2.266864,0.67549 -5.148375,-8.3334 -16.708929,-13.24457 -29.284064,-11.46539 -11.727735,1.65929 -20.952548,8.68216 -24.273604,17.26925 -1.71413,-0.52072 -3.537256,-0.74113 -5.436008,-0.47249 -1.252621,0.17723 -2.4015491,0.61496 -3.4932673,1.11504 -4.5976308,-7.83246 -13.3408631,-12.56819 -22.5970547,-11.25859 -8.056652,1.13989 -14.451065,6.55546 -17.471587,13.735 -3.099465,-1.92453 -6.497305,-2.80551 -9.949363,-2.3171 -3.063042,0.43337 -5.813878,1.85775 -8.100338,4.07268 -5.429842,-10.67681 -13.841974,-17.28631 -22.250686,-16.09663 z"
         style="fill:url(#linearGradient7128);fill-opacity:1;stroke:#8a916f;stroke-width:0.31156328;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7118">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7120"
         d="m -87.493454,-195.49881 c -12.595616,-1.41049 -24.645456,14.18708 -26.957406,34.83271 -0.0471,0.4206 -0.0574,0.82385 -0.0957,1.24204 -2.82337,3.78318 -7.5781,8.6708 -8.23738,14.55819 l -0.14845,1.32562 -0.5542,4.94901 -6.64204,59.313162 291.19086,32.608314 6.64205,-59.313166 0.5542,-4.949 0.14845,-1.32563 c 0.6669,-5.95542 -3.82031,-11.97156 -5.78428,-16.30733 0.67405,-16.78785 -7.78666,-30.93839 -19.8312,-32.28717 -7.35911,-0.82409 -14.44243,3.31852 -19.54388,10.42859 -2.23895,-1.69915 -5.44906,-2.29817 -9.04455,-1.28127 -2.43021,0.68732 -4.72191,2.02899 -6.65846,3.72854 -0.88995,-12.58502 -9.125891,-22.85588 -20.270842,-24.10393 -12.340543,-1.38192 -23.730809,8.80244 -26.112009,23.02609 -1.661344,-2.84571 -4.328564,-4.77993 -7.529129,-5.13834 -0.801392,-0.0897 -1.620772,-0.0232 -2.393757,0.0899 -2.944231,-9.47305 -13.041356,-17.20947 -25.823348,-18.64083 -11.920651,-1.33491 -22.7413869,3.22251 -28.1673197,10.80515 -1.5495465,-0.94363 -3.2818379,-1.62028 -5.2118239,-1.8364 -1.2732265,-0.14258 -2.5105564,-0.003 -3.7075304,0.2112 -2.530635,-8.84267 -9.909088,-15.69543 -19.31754,-16.74901 -8.189181,-0.91705 -15.828134,2.77897 -20.603809,9.05712 -2.553587,-2.67029 -5.663378,-4.3925 -9.17222,-4.78543 -3.113429,-0.34865 -6.17098,0.35345 -8.972788,1.94815 -2.628371,-11.84236 -9.208832,-20.44912 -17.755858,-21.40627 z"
         style="fill:url(#linearGradient7122);fill-opacity:1;stroke:#8a916f;stroke-width:0.31552541;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath7112">
      <path
         sodipodi:nodetypes="sscsccccccscscscscscscscscscs"
         inkscape:connector-curvature="0"
         id="path7114"
         d="m -223.86885,-217.73045 c -15.78606,-1.55539 -30.60588,18.16458 -33.15533,44.03968 -0.0519,0.52714 -0.0582,1.03196 -0.0991,1.55593 -3.47025,4.78141 -9.33908,10.97711 -10.06609,18.35576 l -0.1637,1.6614 -0.61113,6.20258 -7.32436,74.33702 364.948712,35.958087 7.324364,-74.337027 0.611135,-6.20257 0.163696,-1.66141 c 0.735414,-7.46391 -4.980207,-14.91798 -7.510192,-20.3112 0.56398,-21.02008 -10.259672,-38.58764 -25.355066,-40.07498 -9.223152,-0.90875 -18.018462,4.39341 -24.28418,13.37613 -2.830185,-2.08908 -6.857406,-2.78526 -11.339986,-1.4528 -3.029799,0.9006 -5.875354,2.61777 -8.270514,4.77689 -1.323284,-15.73448 -11.8010453,-28.45063 -25.7689818,-29.82688 -15.4663692,-1.52389 -29.5509242,11.41083 -32.2939772,29.25042 -2.126448,-3.53355 -5.496503,-5.90968 -9.507762,-6.30491 -1.004383,-0.099 -2.028674,-0.002 -2.994129,0.15235 -3.842255,-11.80585 -16.606955,-21.31931 -32.626589,-22.89772 -14.94012,-1.47203 -28.40565,4.41146 -35.06957,13.99098 -1.95486,-1.15509 -4.13398,-1.97303 -6.55282,-2.21135 -1.59574,-0.15723 -3.14185,0.0374 -4.63621,0.32604 -3.31417,-11.02386 -12.66192,-19.47676 -24.45351,-20.63858 -10.26348,-1.01125 -19.76156,3.74128 -25.63345,11.67748 -3.24011,-3.29915 -7.16048,-5.4026 -11.55811,-5.83589 -3.90205,-0.38447 -7.71667,0.54508 -11.19639,2.58738 -3.48643,-14.77613 -11.86476,-25.43734 -22.57672,-26.49281 z"
         style="fill:url(#linearGradient7116);fill-opacity:1;stroke:#8a916f;stroke-width:0.39489374;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    </clipPath>
    <linearGradient
       id="linearGradient11458">
      <stop
         style="stop-color:#2b1100;stop-opacity:1;"
         offset="0"
         id="stop11460" />
      <stop
         style="stop-color:#913300;stop-opacity:1"
         offset="1"
         id="stop11463" />
    </linearGradient>
    <linearGradient
       id="linearGradient5973">
      <stop
         style="stop-color:#3d1700;stop-opacity:1;"
         offset="0"
         id="stop5975" />
      <stop
         style="stop-color:#693009;stop-opacity:1"
         offset="1"
         id="stop5977" />
    </linearGradient>
    <linearGradient
       id="linearGradient16452">
      <stop
         style="stop-color:#552200;stop-opacity:1"
         offset="0"
         id="stop16454" />
      <stop
         style="stop-color:#c87137;stop-opacity:1"
         offset="1"
         id="stop16456" />
    </linearGradient>
    <linearGradient
       id="linearGradient6891">
      <stop
         style="stop-color:#b3b3b3;stop-opacity:1"
         offset="0"
         id="stop6893" />
      <stop
         style="stop-color:#f2f2f2;stop-opacity:1"
         offset="1"
         id="stop6895" />
    </linearGradient>
    <linearGradient
       id="linearGradient6885">
      <stop
         style="stop-color:#cccccc;stop-opacity:1"
         offset="0"
         id="stop6887" />
      <stop
         style="stop-color:#ffffff;stop-opacity:1"
         offset="1"
         id="stop6889" />
    </linearGradient>
    <linearGradient
       id="linearGradient6897">
      <stop
         style="stop-color:#e1e1e1;stop-opacity:1"
         offset="0"
         id="stop6899" />
      <stop
         style="stop-color:#ffffff;stop-opacity:1"
         offset="1"
         id="stop6901" />
    </linearGradient>
    <linearGradient
       id="linearGradient6557">
      <stop
         id="stop6559"
         offset="0"
         style="stop-color:#000000;stop-opacity:1" />
      <stop
         id="stop6561"
         offset="1"
         style="stop-color:#333333;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6551">
      <stop
         id="stop6553"
         offset="0"
         style="stop-color:#000000;stop-opacity:1" />
      <stop
         id="stop6555"
         offset="1"
         style="stop-color:#666666;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6563">
      <stop
         id="stop6565"
         offset="0"
         style="stop-color:#333333;stop-opacity:1" />
      <stop
         id="stop6567"
         offset="1"
         style="stop-color:#808080;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6412">
      <stop
         id="stop6414"
         offset="0"
         style="stop-color:#ececec;stop-opacity:1" />
      <stop
         id="stop6416"
         offset="1"
         style="stop-color:#cccccc;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6418">
      <stop
         id="stop6420"
         offset="0"
         style="stop-color:#f9f9f9;stop-opacity:1" />
      <stop
         id="stop6422"
         offset="1"
         style="stop-color:#e6e6e6;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient15946">
      <stop
         id="stop15948"
         offset="0"
         style="stop-color:#e9afaf;stop-opacity:1" />
      <stop
         id="stop15950"
         offset="1"
         style="stop-color:#d35f5f;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6394">
      <stop
         style="stop-color:#ffffff;stop-opacity:1"
         offset="0"
         id="stop6396" />
      <stop
         style="stop-color:#e6e6e6;stop-opacity:1"
         offset="1"
         id="stop6398" />
    </linearGradient>
    <linearGradient
       id="linearGradient6402">
      <stop
         id="stop6404"
         offset="0"
         style="stop-color:#ebebeb;stop-opacity:1" />
      <stop
         id="stop6406"
         offset="1"
         style="stop-color:#ffffff;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient15836">
      <stop
         style="stop-color:#c83737;stop-opacity:1"
         offset="0"
         id="stop15838" />
      <stop
         style="stop-color:#de8787;stop-opacity:1"
         offset="1"
         id="stop15840" />
    </linearGradient>
    <linearGradient
       id="linearGradient6805">
      <stop
         style="stop-color:#f2f2f2;stop-opacity:1"
         offset="0"
         id="stop6807" />
      <stop
         style="stop-color:#e6e6e6;stop-opacity:1"
         offset="1"
         id="stop6809" />
    </linearGradient>
    <linearGradient
       id="linearGradient6817">
      <stop
         style="stop-color:#f9f9f9;stop-opacity:1"
         offset="0"
         id="stop6819" />
      <stop
         style="stop-color:#e3dbdb;stop-opacity:1"
         offset="1"
         id="stop6821" />
    </linearGradient>
    <linearGradient
       id="linearGradient6811">
      <stop
         id="stop6813"
         offset="0"
         style="stop-color:#f9f9f9;stop-opacity:1" />
      <stop
         id="stop6815"
         offset="1"
         style="stop-color:#e3dbdb;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6201">
      <stop
         id="stop6203"
         offset="0"
         style="stop-color:#cccccc;stop-opacity:1" />
      <stop
         id="stop6205"
         offset="1"
         style="stop-color:#ececec;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6207">
      <stop
         id="stop6209"
         offset="0"
         style="stop-color:#cccccc;stop-opacity:1" />
      <stop
         id="stop6211"
         offset="1"
         style="stop-color:#f2f2f2;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6195">
      <stop
         style="stop-color:#e8e8e8;stop-opacity:1"
         offset="0"
         id="stop6197" />
      <stop
         style="stop-color:#ffffff;stop-opacity:1"
         offset="1"
         id="stop6199" />
    </linearGradient>
    <linearGradient
       id="linearGradient16206">
      <stop
         style="stop-color:#552200;stop-opacity:1"
         offset="0"
         id="stop16208" />
      <stop
         style="stop-color:#ffd496;stop-opacity:1;"
         offset="1"
         id="stop16210" />
    </linearGradient>
    <linearGradient
       id="linearGradient5376">
      <stop
         id="stop5378"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop5380"
         offset="1"
         style="stop-color:#ffd496;stop-opacity:1;" />
    </linearGradient>
    <linearGradient
       id="linearGradient5303">
      <stop
         id="stop5305"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop5307"
         offset="1"
         style="stop-color:#f2c78b;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6625">
      <stop
         id="stop6627"
         offset="0"
         style="stop-color:#784421;stop-opacity:1" />
      <stop
         id="stop6629"
         offset="1"
         style="stop-color:#e9ddaf;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6617">
      <stop
         style="stop-color:#552200;stop-opacity:1;"
         offset="0"
         id="stop6619" />
      <stop
         style="stop-color:#a05a2c;stop-opacity:1"
         offset="1"
         id="stop6621" />
    </linearGradient>
    <linearGradient
       id="linearGradient16009">
      <stop
         style="stop-color:#999999;stop-opacity:1"
         offset="0"
         id="stop16011" />
      <stop
         style="stop-color:#f9f9f9;stop-opacity:1"
         offset="1"
         id="stop16013" />
    </linearGradient>
    <linearGradient
       id="linearGradient4900">
      <stop
         style="stop-color:#cccccc;stop-opacity:1"
         offset="0"
         id="stop4902" />
      <stop
         style="stop-color:#f2f2f2;stop-opacity:1"
         offset="1"
         id="stop4904" />
    </linearGradient>
    <linearGradient
       id="linearGradient4976">
      <stop
         id="stop4978"
         offset="0"
         style="stop-color:#b3b3b3;stop-opacity:1" />
      <stop
         id="stop4980"
         offset="1"
         style="stop-color:#ececec;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient4982">
      <stop
         id="stop4984"
         offset="0"
         style="stop-color:#cccccc;stop-opacity:1" />
      <stop
         id="stop4986"
         offset="1"
         style="stop-color:#f2f2f2;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6273">
      <stop
         style="stop-color:#000000;stop-opacity:1"
         offset="0"
         id="stop6275" />
      <stop
         style="stop-color:#b3b3b3;stop-opacity:1"
         offset="1"
         id="stop6277" />
    </linearGradient>
    <linearGradient
       id="linearGradient6267">
      <stop
         id="stop6269"
         offset="0"
         style="stop-color:#000000;stop-opacity:1" />
      <stop
         id="stop6271"
         offset="1"
         style="stop-color:#4d4d4d;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient6279">
      <stop
         style="stop-color:#1a1a1a;stop-opacity:1"
         offset="0"
         id="stop6281" />
      <stop
         style="stop-color:#666666;stop-opacity:1"
         offset="1"
         id="stop6283" />
    </linearGradient>
    <linearGradient
       id="linearGradient19727-4">
      <stop
         style="stop-color:#ffd42a;stop-opacity:1;"
         offset="0"
         id="stop19729-9" />
      <stop
         style="stop-color:#ffe680;stop-opacity:1"
         offset="1"
         id="stop19731-8" />
    </linearGradient>
    <linearGradient
       id="linearGradient19770">
      <stop
         style="stop-color:#aa0000;stop-opacity:1;"
         offset="0"
         id="stop19772" />
      <stop
         style="stop-color:#800000;stop-opacity:1"
         offset="1"
         id="stop19774" />
    </linearGradient>
    <linearGradient
       id="linearGradient19855">
      <stop
         style="stop-color:#d45500;stop-opacity:1;"
         offset="0"
         id="stop19857" />
      <stop
         style="stop-color:#ffb600;stop-opacity:1;"
         offset="1"
         id="stop19859" />
    </linearGradient>
    <linearGradient
       id="linearGradient19847">
      <stop
         style="stop-color:#b3b3b3;stop-opacity:1;"
         offset="0"
         id="stop19849" />
      <stop
         style="stop-color:#d6d6d6;stop-opacity:1"
         offset="1"
         id="stop19851" />
    </linearGradient>
    <linearGradient
       id="linearGradient19807">
      <stop
         style="stop-color:#ffa400;stop-opacity:1;"
         offset="0"
         id="stop19809" />
      <stop
         style="stop-color:#ffd800;stop-opacity:1;"
         offset="1"
         id="stop19811" />
    </linearGradient>
    <linearGradient
       id="linearGradient19764">
      <stop
         style="stop-color:#cccccc;stop-opacity:1"
         offset="0"
         id="stop19766" />
      <stop
         style="stop-color:#f2f2f2;stop-opacity:1"
         offset="1"
         id="stop19768" />
    </linearGradient>
    <linearGradient
       id="linearGradient19727">
      <stop
         style="stop-color:#ffd42a;stop-opacity:1;"
         offset="0"
         id="stop19729" />
      <stop
         style="stop-color:#ffe680;stop-opacity:1"
         offset="1"
         id="stop19731" />
    </linearGradient>
    <linearGradient
       id="linearGradient19982">
      <stop
         id="stop19984"
         offset="0"
         style="stop-color:#502d16;stop-opacity:1" />
      <stop
         id="stop19986"
         offset="1"
         style="stop-color:#6e3e1e;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient19976">
      <stop
         id="stop19978"
         offset="0"
         style="stop-color:#502d16;stop-opacity:1" />
      <stop
         id="stop19980"
         offset="1"
         style="stop-color:#c87137;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient20109">
      <stop
         id="stop20111"
         offset="0"
         style="stop-color:#6c5d53;stop-opacity:1" />
      <stop
         id="stop20113"
         offset="1"
         style="stop-color:#ac9d93;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient20103">
      <stop
         id="stop20105"
         offset="0"
         style="stop-color:#917c6f;stop-opacity:1" />
      <stop
         id="stop20107"
         offset="1"
         style="stop-color:#e3dedb;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient24103">
      <stop
         style="stop-color:#8d4c21;stop-opacity:1;"
         offset="0"
         id="stop24105" />
      <stop
         id="stop24129"
         offset="0.5"
         style="stop-color:#713711;stop-opacity:1;" />
      <stop
         style="stop-color:#562301;stop-opacity:1"
         offset="1"
         id="stop24107" />
    </linearGradient>
    <linearGradient
       id="linearGradient5888">
      <stop
         id="stop5890"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop5892"
         offset="1"
         style="stop-color:#a05a2c;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient24131">
      <stop
         id="stop24133"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         style="stop-color:#965326;stop-opacity:1"
         offset="0.5"
         id="stop24135" />
      <stop
         id="stop24137"
         offset="1"
         style="stop-color:#562301;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient10132"
       id="linearGradient15204"
       gradientUnits="userSpaceOnUse"
       gradientTransform="matrix(0.67674199,0.75310567,-0.65890312,0.77349494,197.36131,-625.4677)"
       x1="793.37268"
       y1="-139.33138"
       x2="794.27441"
       y2="-120.1907" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient15272"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient15282"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient15292"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient24131"
       id="linearGradient15602"
       gradientUnits="userSpaceOnUse"
       x1="725.78387"
       y1="346.39603"
       x2="572.9505"
       y2="346.39603" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11250"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11252"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11254"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11468"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11470"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11472"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       id="linearGradient24103-7">
      <stop
         style="stop-color:#8d4c21;stop-opacity:1;"
         offset="0"
         id="stop24105-5" />
      <stop
         id="stop24129-8"
         offset="0.5"
         style="stop-color:#713711;stop-opacity:1;" />
      <stop
         style="stop-color:#562301;stop-opacity:1"
         offset="1"
         id="stop24107-4" />
    </linearGradient>
    <linearGradient
       id="linearGradient5888-0">
      <stop
         id="stop5890-9"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop5892-4"
         offset="1"
         style="stop-color:#a05a2c;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient8953">
      <stop
         id="stop8955"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop8957"
         offset="1"
         style="stop-color:#a05a2c;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient24131-3">
      <stop
         id="stop24133-5"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         style="stop-color:#965326;stop-opacity:1"
         offset="0.5"
         id="stop24135-8" />
      <stop
         id="stop24137-4"
         offset="1"
         style="stop-color:#562301;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       id="linearGradient8965">
      <stop
         id="stop8967"
         offset="0"
         style="stop-color:#552200;stop-opacity:1" />
      <stop
         id="stop8969"
         offset="1"
         style="stop-color:#a05a2c;stop-opacity:1" />
    </linearGradient>
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11737"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11747"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient11757"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient12351"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient12353"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient12355"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient13008"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient13018"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15946"
       id="linearGradient13028"
       gradientUnits="userSpaceOnUse"
       x1="676.80322"
       y1="808.9491"
       x2="1024.8917"
       y2="808.9491" />
    <linearGradient
       inkscape:collect="always"
       id="linearGradient15234">
      <stop
         style="stop-color:#909090;stop-opacity:1"
         offset="0"
         id="stop15236" />
      <stop
         style="stop-color:#000000;stop-opacity:1"
         offset="1"
         id="stop15238" />
    </linearGradient>
    <linearGradient
       inkscape:collect="always"
       id="linearGradient14564">
      <stop
         style="stop-color:#ffffff;stop-opacity:1;"
         offset="0"
         id="stop14566" />
      <stop
         style="stop-color:#000000;stop-opacity:1"
         offset="1"
         id="stop14568" />
    </linearGradient>
    <radialGradient
       inkscape:collect="always"
       xlink:href="#linearGradient14564"
       id="radialGradient14570"
       cx="-909.46179"
       cy="1803.0924"
       fx="-909.46179"
       fy="1803.0924"
       r="27.150221"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       gradientUnits="userSpaceOnUse" />
    <radialGradient
       inkscape:collect="always"
       xlink:href="#linearGradient14564-0"
       id="radialGradient14570-1"
       cx="-909.46179"
       cy="1803.0924"
       fx="-909.46179"
       fy="1803.0924"
       r="27.150221"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       gradientUnits="userSpaceOnUse" />
    <linearGradient
       inkscape:collect="always"
       id="linearGradient14564-0">
      <stop
         style="stop-color:#ffffff;stop-opacity:1;"
         offset="0"
         id="stop14566-6" />
      <stop
         style="stop-color:#000000;stop-opacity:1"
         offset="1"
         id="stop14568-3" />
    </linearGradient>
    <radialGradient
       r="27.150221"
       fy="1803.0924"
       fx="-909.46179"
       cy="1803.0924"
       cx="-909.46179"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       gradientUnits="userSpaceOnUse"
       id="radialGradient14604"
       xlink:href="#linearGradient14564-0"
       inkscape:collect="always" />
    <radialGradient
       inkscape:collect="always"
       xlink:href="#linearGradient14564-0"
       id="radialGradient14624"
       gradientUnits="userSpaceOnUse"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       cx="-909.46179"
       cy="1803.0924"
       fx="-909.46179"
       fy="1803.0924"
       r="27.150221" />
    <radialGradient
       inkscape:collect="always"
       xlink:href="#linearGradient14564-0-6"
       id="radialGradient14624-0"
       gradientUnits="userSpaceOnUse"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       cx="-909.46179"
       cy="1803.0924"
       fx="-909.46179"
       fy="1803.0924"
       r="27.150221" />
    <linearGradient
       inkscape:collect="always"
       id="linearGradient14564-0-6">
      <stop
         style="stop-color:#ffffff;stop-opacity:1;"
         offset="0"
         id="stop14566-6-1" />
      <stop
         style="stop-color:#000000;stop-opacity:1"
         offset="1"
         id="stop14568-3-5" />
    </linearGradient>
    <radialGradient
       inkscape:collect="always"
       xlink:href="#linearGradient14564-0-5"
       id="radialGradient14624-6"
       gradientUnits="userSpaceOnUse"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       cx="-909.46179"
       cy="1803.0924"
       fx="-909.46179"
       fy="1803.0924"
       r="27.150221" />
    <linearGradient
       inkscape:collect="always"
       id="linearGradient14564-0-5">
      <stop
         style="stop-color:#ffffff;stop-opacity:1;"
         offset="0"
         id="stop14566-6-6" />
      <stop
         style="stop-color:#000000;stop-opacity:1"
         offset="1"
         id="stop14568-3-9" />
    </linearGradient>
    <radialGradient
       r="27.150221"
       fy="1803.0924"
       fx="-909.46179"
       cy="1803.0924"
       cx="-909.46179"
       gradientTransform="matrix(2.5658275,0.84526511,-0.76262697,2.3149779,2798.609,-1599.1952)"
       gradientUnits="userSpaceOnUse"
       id="radialGradient14719"
       xlink:href="#linearGradient14564-0-5"
       inkscape:collect="always" />
    <radialGradient
       inkscape:collect="always"
       xlink:href="#linearGradient15234"
       id="radialGradient15240"
       cx="23.326487"
       cy="279.59131"
       fx="23.326487"
       fy="279.59131"
       r="8.8412333"
       gradientTransform="matrix(0.61254157,0.00527306,-0.00355441,0.46756178,10.288464,148.26761)"
       gradientUnits="userSpaceOnUse" />
  </defs>
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(984.75375,-174.49478)">
    <g
       id="layer1-6"
       inkscape:label="Layer 1"
       transform="translate(-398.11756,-42.031745)">
      <g
         transform="translate(-672.44869,-538.91921)"
         id="layer1-5"
         inkscape:label="Layer 1">
        <g
           id="g5144">
          <path
             style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:14.17671299;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans"
             d="m 243.29847,1046.3116 -4.59319,2.4626 c -8.11004,4.3287 -13.63886,12.9397 -17.2241,23.0383 -3.58524,10.0988 -5.23992,21.8523 -5.03053,33.1664 0.20939,11.3139 2.24234,22.1879 6.50054,30.5594 4.25819,8.3716 11.36534,14.4863 20.57711,14.2637 4.48868,-0.1085 8.36191,-1.5153 11.13499,-4.125 2.77308,-2.6097 4.32502,-6.1667 5.11134,-10.0615 1.57265,-7.7896 0.34524,-17.377 -1.81342,-27.6793 -4.31732,-20.6047 -12.74304,-44.3151 -14.09997,-56.4219 z"
             id="path6463"
             inkscape:connector-curvature="0"
             sodipodi:nodetypes="ccssssssscc" />
          <g
             transform="matrix(0.94511423,0,0,0.94511423,15.438141,25.440781)"
             id="g4916">
            <path
               style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:15;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans"
               d="m 324.13568,1080.6537 -4.09087,2.6196 c -7.22449,4.6075 -11.74145,13.0085 -14.34495,22.6517 -2.60351,9.6433 -3.29361,20.6852 -2.28313,31.1842 1.01048,10.499 3.68385,20.4575 8.24469,27.9301 4.56085,7.4726 11.60646,12.6425 20.15089,11.7713 4.1635,-0.4245 7.66145,-2.0111 10.05028,-4.6363 2.38883,-2.6252 3.57454,-6.0426 4.02441,-9.7187 0.89971,-7.3523 -0.9323,-16.1733 -3.68128,-25.5916 -5.49795,-18.8366 -15.03781,-40.263 -17.17187,-51.416 z"
               id="path6469"
               inkscape:connector-curvature="0"
               sodipodi:nodetypes="ccssssssscc" />
            <path
               sodipodi:nodetypes="ccssssssscc"
               inkscape:connector-curvature="0"
               id="path4868"
               d="m 324.13568,1080.6537 -4.09087,2.6196 c -7.22449,4.6075 -11.74145,13.0085 -14.34495,22.6517 -2.60351,9.6433 -3.29361,20.6852 -2.28313,31.1842 1.01048,10.499 3.68385,20.4575 8.24469,27.9301 4.56085,7.4726 11.60646,12.6425 20.15089,11.7713 4.1635,-0.4245 7.66145,-2.0111 10.05028,-4.6363 2.38883,-2.6252 3.57454,-6.0426 4.02441,-9.7187 0.89971,-7.3523 -0.9323,-16.1733 -3.68128,-25.5916 -5.49795,-18.8366 -15.03781,-40.263 -17.17187,-51.416 z"
               style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none;stroke-width:15;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans" />
          </g>
          <path
             sodipodi:nodetypes="ccssssssscc"
             inkscape:connector-curvature="0"
             id="path6457"
             d="m 203.99914,1048.3871 -5.17774,0.5938 c -9.13502,1.0305 -17.45126,6.9936 -24.51003,15.0566 -7.05877,8.0628 -12.93394,18.3763 -16.91438,28.969 -3.98044,10.5929 -6.10361,21.4495 -5.23519,30.8016 0.86841,9.352 5.21753,17.6579 13.86133,20.8502 4.21192,1.5555 8.33088,1.6774 11.87129,0.2752 3.54039,-1.4023 6.29536,-4.1355 8.46345,-7.4652 4.33614,-6.6596 6.73326,-16.0233 8.52867,-26.395 3.59083,-20.7436 4.5093,-45.8898 7.71576,-57.6429 z"
             style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:14.17671299;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans" />
          <g
             style="fill:none;stroke:#000000;stroke-width:14.24600029;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none"
             id="g4957"
             transform="matrix(0.94511423,0,0,0.94511423,9.7098842,45.967036)">
            <path
               sodipodi:nodetypes="cccc"
               inkscape:connector-curvature="0"
               id="path4953"
               d="m 211.74176,833.23218 c -38.793,-26.42931 -62.24067,-8.87973 -102.12585,-8.31163 31.39425,20.11449 52.94332,28.06479 67.62226,60.70157 z"
               style="fill:none;stroke:#000000;stroke-width:14.24600029;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none" />
          </g>
          <g
             transform="matrix(0.94511423,0,0,-0.94511423,0.73129901,1912.5945)"
             id="g5054"
             inkscape:transform-center-x="-49.117383">
            <path
               sodipodi:nodetypes="zzzzzzzzzz"
               inkscape:connector-curvature="0"
               id="path5047"
               d="m 449.45914,974.49604 c 12.16676,-0.98651 37.90658,29.55946 48.11385,20.77453 10.20727,-8.78496 1.75644,-24.68193 -7.24771,-27.45498 -9.00416,-2.77306 -19.45255,8.20025 -25.08128,3.13098 -5.62872,-5.06927 19.02313,-17.35874 31.78067,-14.83477 12.75753,2.52398 21.83171,10.83405 24.58265,23.95912 2.75094,13.12507 0.53203,28.53818 -15.38855,38.17308 -15.92058,9.6347 -47.09554,-6.2072 -59.87322,-14.6075 -12.77769,-8.40033 -15.60727,-10.69837 -14.43227,-17.9088 1.175,-7.21044 5.37909,-10.24514 17.54586,-11.23166 z"
               style="fill:#ffc5bb;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:13;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none" />
            <path
               style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none"
               d="m 449.45914,974.49604 c 12.16676,-0.98651 37.90658,29.55946 48.11385,20.77453 10.20727,-8.78496 1.75644,-24.68193 -7.24771,-27.45498 -9.00416,-2.77306 -19.45255,8.20025 -25.08128,3.13098 -5.62872,-5.06927 19.02313,-17.35874 31.78067,-14.83477 12.75753,2.52398 21.83171,10.83405 24.58265,23.95912 2.75094,13.12507 0.53203,28.53818 -15.38855,38.17308 -15.92058,9.6347 -47.09554,-6.2072 -59.87322,-14.6075 -12.77769,-8.40033 -15.60727,-10.69837 -14.43227,-17.9088 1.175,-7.21044 5.37909,-10.24514 17.54586,-11.23166 z"
               id="path5045"
               inkscape:connector-curvature="0"
               sodipodi:nodetypes="zzzzzzzzzz" />
            <path
               inkscape:connector-curvature="0"
               id="path5061"
               transform="matrix(1,0,0,-1,1080.0663,1394.0774)"
               d="m -586.125,372.8125 c -16.39382,-0.0499 -37.61119,11.06227 -47.59375,17.625 -12.77769,8.40033 -15.6125,10.69582 -14.4375,17.90625 1.175,7.21044 5.39573,10.26348 17.5625,11.25 12.16676,0.98651 37.88648,-29.56618 48.09375,-20.78125 4.33955,3.73486 5.3265,8.74919 4.3125,13.5 6.67151,-6.29697 12.85884,-13.01948 18.53125,-20.09375 -2.35633,-6.16563 -6.78692,-11.89628 -14.1875,-16.375 -3.48263,-2.10759 -7.69098,-3.01728 -12.28125,-3.03125 z m -25.0625,48.96875 c -1.35298,0.0189 -2.56961,0.39326 -3.625,1.34375 -2.91177,2.62236 2.29371,7.18851 9.75,10.625 3.44424,-2.30804 6.78395,-4.73004 10.0625,-7.21875 -5.79753,-0.86415 -11.70236,-4.81251 -16.1875,-4.75 z"
               style="fill:#ffc5bb;fill-opacity:1;fill-rule:nonzero;stroke:none" />
          </g>
          <path
             style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none;stroke-width:15;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans"
             d="m 203.99914,1048.3871 -5.17774,0.5938 c -9.13502,1.0305 -17.45126,6.9936 -24.51003,15.0566 -7.05877,8.0628 -12.93394,18.3763 -16.91438,28.969 -3.98044,10.5929 -6.10361,21.4495 -5.23519,30.8016 0.86841,9.352 5.21753,17.6579 13.86133,20.8502 4.21192,1.5555 8.33088,1.6774 11.87129,0.2752 3.54039,-1.4023 6.29536,-4.1355 8.46345,-7.4652 4.33614,-6.6596 6.73326,-16.0233 8.52867,-26.395 3.59083,-20.7436 4.5093,-45.8898 7.71576,-57.6429 z"
             id="path4872"
             inkscape:connector-curvature="0"
             sodipodi:nodetypes="ccssssssscc" />
          <path
             sodipodi:type="arc"
             style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:7.71924973;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none"
             id="path4792"
             sodipodi:cx="-880.85303"
             sodipodi:cy="155.34673"
             sodipodi:rx="86.368042"
             sodipodi:ry="86.368042"
             d="m -794.48499,155.34673 c 0,47.69975 -38.66828,86.36804 -86.36804,86.36804 -47.69975,0 -86.36804,-38.66829 -86.36804,-86.36804 0,-47.69976 38.66829,-86.368047 86.36804,-86.368047 47.69976,0 86.36804,38.668287 86.36804,86.368047 z"
             transform="matrix(1.8364802,0,0,1.6566014,1893.8645,704.70551)" />
          <g
             transform="matrix(0.94511423,0,0,0.94511423,35.487042,20.667233)"
             id="g4912">
            <path
               sodipodi:nodetypes="ccssssssscc"
               inkscape:connector-curvature="0"
               id="path6475"
               d="m 364.01809,1077.9256 -3.86713,2.94 c -6.83086,5.1732 -10.6581,13.9099 -12.47825,23.7312 -1.82015,9.8212 -1.62067,20.8829 0.23024,31.2668 1.85092,10.3838 5.31592,20.0952 10.46252,27.1772 5.1466,7.082 12.58488,11.6689 21.03167,10.1139 4.11592,-0.7578 7.47506,-2.6203 9.6452,-5.429 2.17014,-2.8086 3.07739,-6.3102 3.23038,-10.0107 0.30597,-7.4008 -2.22898,-16.0461 -5.72593,-25.213 -6.99389,-18.3338 -18.22474,-38.9243 -21.24817,-49.8698 z"
               style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:15;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans" />
            <path
               style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none;stroke-width:15;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans"
               d="m 364.01809,1077.9256 -3.86713,2.94 c -6.83086,5.1732 -10.6581,13.9099 -12.47825,23.7312 -1.82015,9.8212 -1.62067,20.8829 0.23024,31.2668 1.85092,10.3838 5.31592,20.0952 10.46252,27.1772 5.1466,7.082 12.58488,11.6689 21.03167,10.1139 4.11592,-0.7578 7.47506,-2.6203 9.6452,-5.429 2.17014,-2.8086 3.07739,-6.3102 3.23038,-10.0107 0.30597,-7.4008 -2.22898,-16.0461 -5.72593,-25.213 -6.99389,-18.3338 -18.22474,-38.9243 -21.24817,-49.8698 z"
               id="path4870"
               inkscape:connector-curvature="0"
               sodipodi:nodetypes="ccssssssscc" />
          </g>
          <path
             sodipodi:nodetypes="ccssssssscc"
             inkscape:connector-curvature="0"
             id="path4874"
             d="m 243.29847,1046.3116 -4.59319,2.4626 c -8.11004,4.3287 -13.63886,12.9397 -17.2241,23.0383 -3.58524,10.0988 -5.23992,21.8523 -5.03053,33.1664 0.20939,11.3139 2.24234,22.1879 6.50054,30.5594 4.25819,8.3716 11.36534,14.4863 20.57711,14.2637 4.48868,-0.1085 8.36191,-1.5153 11.13499,-4.125 2.77308,-2.6097 4.32502,-6.1667 5.11134,-10.0615 1.57265,-7.7896 0.34524,-17.377 -1.81342,-27.6793 -4.31732,-20.6047 -12.74304,-44.3151 -14.09997,-56.4219 z"
             style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none;stroke-width:15;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans" />
          <path
             transform="matrix(1.8364802,0,0,1.6566014,1893.8645,704.70551)"
             d="m -794.48499,155.34673 c 0,47.69975 -38.66828,86.36804 -86.36804,86.36804 -47.69975,0 -86.36804,-38.66829 -86.36804,-86.36804 0,-47.69976 38.66829,-86.368047 86.36804,-86.368047 47.69976,0 86.36804,38.668287 86.36804,86.368047 z"
             sodipodi:ry="86.368042"
             sodipodi:rx="86.368042"
             sodipodi:cy="155.34673"
             sodipodi:cx="-880.85303"
             id="path4794"
             style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none"
             sodipodi:type="arc" />
          <path
             id="path4811"
             d="m 276.20615,818.96651 c -87.59965,0 -158.63151,64.07448 -158.63151,143.09396 0,30.846 10.83485,59.41063 29.23947,82.77653 17.45124,4.4949 35.85436,6.9003 54.90523,6.9003 109.34145,0 198.13416,-79.28324 199.62584,-177.59529 -29.02602,-33.57277 -74.2836,-55.1755 -125.13903,-55.1755 z"
             style="fill:#ffc5bb;fill-opacity:1;fill-rule:nonzero;stroke:none"
             inkscape:connector-curvature="0" />
          <path
             inkscape:connector-curvature="0"
             style="font-size:medium;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-indent:0;text-align:start;text-decoration:none;line-height:normal;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;block-progression:tb;writing-mode:lr-tb;text-anchor:start;baseline-shift:baseline;color:#000000;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:3.78045702;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;marker:none;visibility:visible;display:inline;overflow:visible;enable-background:accumulate;font-family:Sans;-inkscape-font-specification:Sans"
             d="m 196.85922,890.35963 c -16.97456,0 -31.10579,12.39309 -31.10579,28.03138 0,15.63828 14.13123,28.03138 31.10579,28.03138 9.1926,0 17.5521,-3.65557 23.28413,-9.4719 5.79699,9.35571 17.10373,15.62072 29.88507,15.62072 18.53393,0 33.99935,-13.15265 33.99935,-29.83986 0,-16.68721 -15.46542,-29.83985 -33.99935,-29.83985 -10.59622,0 -20.17538,4.29866 -26.44897,11.09952 -5.4681,-8.21647 -15.47651,-13.63139 -26.72023,-13.63139 z"
             id="path6420" />
          <path
             sodipodi:type="arc"
             style="fill:#ffffff;fill-opacity:1;fill-rule:nonzero;stroke:none"
             id="path6308"
             sodipodi:cx="33"
             sodipodi:cy="-361.75"
             sodipodi:rx="39"
             sodipodi:ry="34.75"
             d="m 72,-361.75 c 0,19.1919 -17.460895,34.75 -39,34.75 -21.539105,0 -39,-15.5581 -39,-34.75 0,-19.1919 17.460895,-34.75 39,-34.75 21.539105,0 39,15.5581 39,34.75 z"
             transform="matrix(0.7233904,0,0,0.7233904,172.99709,1180.0669)" />
          <path
             sodipodi:type="arc"
             style="fill:#ffffff;fill-opacity:1;fill-rule:nonzero;stroke:none"
             id="path6310"
             sodipodi:cx="106.5"
             sodipodi:cy="-355.75"
             sodipodi:rx="43"
             sodipodi:ry="37.25"
             d="m 149.5,-355.75 c 0,20.57261 -19.25176,37.25 -43,37.25 -23.748244,0 -43,-16.67739 -43,-37.25 0,-20.57261 19.251756,-37.25 43,-37.25 23.74824,0 43,16.67739 43,37.25 z"
             transform="matrix(0.7233904,0,0,0.7233904,172.99709,1180.0669)" />
          <path
             sodipodi:type="arc"
             style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none"
             id="path6416"
             sodipodi:cx="88.25"
             sodipodi:cy="-356.75"
             sodipodi:rx="5.25"
             sodipodi:ry="5.25"
             d="m 93.5,-356.75 c 0,2.89949 -2.350505,5.25 -5.25,5.25 -2.899495,0 -5.25,-2.35051 -5.25,-5.25 0,-2.89949 2.350505,-5.25 5.25,-5.25 2.899495,0 5.25,2.35051 5.25,5.25 z"
             transform="matrix(1.3598634,0,0,1.3598634,122.45501,1409.1748)" />
          <path
             transform="matrix(1.3598634,0,0,1.3598634,80.969111,1406.5988)"
             d="m 93.5,-356.75 c 0,2.89949 -2.350505,5.25 -5.25,5.25 -2.899495,0 -5.25,-2.35051 -5.25,-5.25 0,-2.89949 2.350505,-5.25 5.25,-5.25 2.899495,0 5.25,2.35051 5.25,5.25 z"
             sodipodi:ry="5.25"
             sodipodi:rx="5.25"
             sodipodi:cy="-356.75"
             sodipodi:cx="88.25"
             id="path6418"
             style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none"
             sodipodi:type="arc" />
          <path
             transform="matrix(0.58379583,0,0,0.58379583,731.16428,892.46813)"
             d="m -794.48499,155.34673 c 0,47.69975 -38.66828,86.36804 -86.36804,86.36804 -47.69975,0 -86.36804,-38.66829 -86.36804,-86.36804 0,-47.69976 38.66829,-86.368047 86.36804,-86.368047 47.69976,0 86.36804,38.668287 86.36804,86.368047 z"
             sodipodi:ry="86.368042"
             sodipodi:rx="86.368042"
             sodipodi:cy="155.34673"
             sodipodi:cx="-880.85303"
             id="path4790"
             style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:16.18912315;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none"
             sodipodi:type="arc" />
          <path
             sodipodi:type="arc"
             style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none"
             id="path4786"
             sodipodi:cx="-880.85303"
             sodipodi:cy="155.34673"
             sodipodi:rx="86.368042"
             sodipodi:ry="86.368042"
             d="m -794.48499,155.34673 c 0,47.69975 -38.66828,86.36804 -86.36804,86.36804 -47.69975,0 -86.36804,-38.66829 -86.36804,-86.36804 0,-47.69976 38.66829,-86.368047 86.36804,-86.368047 47.69976,0 86.36804,38.668287 86.36804,86.368047 z"
             transform="matrix(0.58379583,0,0,0.58379583,731.16428,892.46813)" />
          <path
             inkscape:connector-curvature="0"
             id="path4822"
             d="m 216.92074,932.72815 c -27.84691,0 -50.41138,22.58757 -50.41138,50.4345 0,15.08759 6.62562,28.62035 17.12739,37.86045 33.32978,-4.8428 62.57459,-22.24738 82.81705,-47.2447 -4.3981,-23.36183 -24.89347,-41.05025 -49.53306,-41.05025 z"
             style="fill:#ffc5bb;fill-opacity:1;fill-rule:nonzero;stroke:none" />
          <path
             transform="matrix(1.3598634,0,0,1.3598634,117.05436,1470.6072)"
             d="m 93.5,-356.75 c 0,2.89949 -2.350505,5.25 -5.25,5.25 -2.899495,0 -5.25,-2.35051 -5.25,-5.25 0,-2.89949 2.350505,-5.25 5.25,-5.25 2.899495,0 5.25,2.35051 5.25,5.25 z"
             sodipodi:ry="5.25"
             sodipodi:rx="5.25"
             sodipodi:cy="-356.75"
             sodipodi:cx="88.25"
             id="path4827"
             style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none"
             sodipodi:type="arc" />
          <path
             sodipodi:type="arc"
             style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none"
             id="path4829"
             sodipodi:cx="88.25"
             sodipodi:cy="-356.75"
             sodipodi:rx="5.25"
             sodipodi:ry="5.25"
             d="m 93.5,-356.75 c 0,2.89949 -2.350505,5.25 -5.25,5.25 -2.899495,0 -5.25,-2.35051 -5.25,-5.25 0,-2.89949 2.350505,-5.25 5.25,-5.25 2.899495,0 5.25,2.35051 5.25,5.25 z"
             transform="matrix(1.3598634,0,0,1.3598634,75.568458,1468.0313)" />
          <path
             sodipodi:nodetypes="cccc"
             inkscape:connector-curvature="0"
             id="path4949"
             d="m 209.83003,833.46663 c -36.66381,-24.97872 -58.82454,-8.39236 -96.52059,-7.85544 29.67115,19.01049 50.03749,26.52443 63.91076,57.36991 z"
             style="fill:#ffc5bb;fill-opacity:1;fill-rule:nonzero;stroke:none" />
          <path
             inkscape:connector-curvature="0"
             id="path4961"
             d="m 173.93602,829.53893 c -10.73335,0.13106 -21.18026,3.57926 -34.7927,3.77315 13.56279,8.68977 24.09446,13.64598 32.25198,22.92337 8.31163,-7.56183 18.07729,-13.82679 28.877,-18.4297 -9.92137,-6.55318 -18.21699,-8.36597 -26.33628,-8.26682 z"
             style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none" />
          <g
             transform="matrix(0.93540525,0.13512186,-0.13512186,0.93540525,126.53111,12.674115)"
             id="g5120-3"
             inkscape:transform-center-x="-56.032926"
             inkscape:transform-center-y="-36.279864">
            <path
               transform="translate(0,-5e-6)"
               sodipodi:nodetypes="cccc"
               inkscape:connector-curvature="0"
               id="path4955-5"
               d="m 272.5714,829.34344 c 28.27584,-38.5191 55.23882,-36.98465 92.11617,-52.19027 -20.9188,30.86414 -34.02158,45.62508 -34.64164,81.4056 z"
               style="fill:none;stroke:#000000;stroke-width:14.24600029;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none" />
            <path
               sodipodi:nodetypes="cccc"
               inkscape:connector-curvature="0"
               id="path4951-6"
               d="m 266.8752,837.46904 c 25.22793,-39.58481 64.50019,-46.15275 101.37754,-61.35837 -20.9188,30.86414 -43.05493,52.09284 -43.67499,87.87336 z"
               style="fill:#ffc5bb;fill-opacity:1;fill-rule:nonzero;stroke:none" />
            <path
               sodipodi:nodetypes="cccc"
               style="fill:#ff9298;fill-opacity:1;fill-rule:nonzero;stroke:none"
               d="m 347.85978,791.49499 c -35.10488,7.44014 -54.03132,26.51248 -72.73933,43.24972 11.31309,2.29806 33.51776,17.85388 44.21957,21.16467 -7.8668,-11.99686 9.69635,-53.4038 28.51976,-64.41439 z"
               id="path4963-4"
               inkscape:connector-curvature="0" />
          </g>
        </g>
      </g>
    </g>
  </g>
</svg>
"""

DICE_1 = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="red"
    d="M302.87 255.5a47.37 47.37 0 1 1-47.37-47.37 47.37 47.37 0 0 1 47.37 47.37zM484.5 428.02a56.48 56.48 0 0 1-56.48 56.48h-344a56.48 56.48 0 0 1-56.52-56.48v-344A56.48 56.48 0 0 1 83.98 27.5h344a56.48 56.48 0 0 1 56.52 56.48zm-20-344a36.48 36.48 0 0 0-36.48-36.52h-344A36.48 36.48 0 0 0 47.5 83.98v344a36.48 36.48 0 0 0 36.48 36.52h344a36.48 36.48 0 0 0 36.52-36.48z"
    class="cls-1" />
</svg>
"""

DICE_2 = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="#000"
    d="M383 81.68A47.37 47.37 0 1 1 335.58 129 47.37 47.37 0 0 1 383 81.68zM81.67 383A47.37 47.37 0 1 0 129 335.59 47.37 47.37 0 0 0 81.67 383zM428 47.57H84A36.48 36.48 0 0 0 47.57 84v344A36.48 36.48 0 0 0 84 464.43h344A36.48 36.48 0 0 0 464.43 428V84A36.48 36.48 0 0 0 428 47.57m0-20A56.54 56.54 0 0 1 484.43 84v344A56.54 56.54 0 0 1 428 484.43H84A56.54 56.54 0 0 1 27.57 428V84A56.54 56.54 0 0 1 84 27.57z"
    class="cls-1" />
</svg>
"""

DICE_3 = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="#000"
    d="M302.87 255.5a47.37 47.37 0 1 1-47.37-47.37 47.37 47.37 0 0 1 47.37 47.37zM382.5 81.18a47.37 47.37 0 1 0 47.32 47.32 47.37 47.37 0 0 0-47.32-47.32zm-254 253.91a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.41-47.41zm356 92.94a56.48 56.48 0 0 1-56.48 56.47h-344a56.48 56.48 0 0 1-56.52-56.48v-344A56.48 56.48 0 0 1 83.98 27.5h344a56.48 56.48 0 0 1 56.52 56.48zm-20-344a36.48 36.48 0 0 0-36.48-36.53h-344A36.48 36.48 0 0 0 47.5 83.98v344a36.48 36.48 0 0 0 36.48 36.52h344a36.48 36.48 0 0 0 36.52-36.48z"
    class="cls-1" />
</svg>
"""

DICE_4 = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="#000"
    d="M175.91 128.5a47.37 47.37 0 1 1-47.41-47.32 47.37 47.37 0 0 1 47.41 47.32zM382.5 81.18a47.37 47.37 0 1 0 47.32 47.32 47.37 47.37 0 0 0-47.32-47.32zm-254 253.91a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.41-47.41zm253.91 0a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.32-47.41zm102 92.93a56.48 56.48 0 0 1-56.39 56.48h-344a56.48 56.48 0 0 1-56.52-56.48v-344A56.48 56.48 0 0 1 83.98 27.5h344a56.48 56.48 0 0 1 56.52 56.48zm-20-344a36.48 36.48 0 0 0-36.39-36.52h-344A36.48 36.48 0 0 0 47.5 83.98v344a36.48 36.48 0 0 0 36.48 36.52h344a36.48 36.48 0 0 0 36.52-36.48z"
    class="cls-1" />
</svg>
"""

DICE_5 = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="#000"
    d="M302.87 255.5a47.37 47.37 0 1 1-47.37-47.37 47.37 47.37 0 0 1 47.37 47.37zM128.5 81.18a47.37 47.37 0 1 0 47.41 47.32 47.37 47.37 0 0 0-47.41-47.32zm253.91 0a47.37 47.37 0 1 0 47.41 47.32 47.37 47.37 0 0 0-47.32-47.32zM128.5 335.09a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.41-47.41zm253.91 0a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.32-47.41zm102 92.93a56.48 56.48 0 0 1-56.39 56.48h-344a56.48 56.48 0 0 1-56.52-56.48v-344A56.48 56.48 0 0 1 83.98 27.5h344a56.48 56.48 0 0 1 56.52 56.48zm-20-344a36.48 36.48 0 0 0-36.39-36.52h-344A36.48 36.48 0 0 0 47.5 83.98v344a36.48 36.48 0 0 0 36.48 36.52h344a36.48 36.48 0 0 0 36.52-36.48z"
    class="cls-1" />
</svg>
"""

DICE_6 = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="#000"
    d="M175.91 128.5a47.37 47.37 0 1 1-47.41-47.32 47.37 47.37 0 0 1 47.41 47.32zM382.5 81.18a47.37 47.37 0 1 0 47.32 47.32 47.37 47.37 0 0 0-47.32-47.32zm-254 126.95a47.37 47.37 0 1 0 47.41 47.37 47.37 47.37 0 0 0-47.41-47.37zm253.91 0a47.37 47.37 0 1 0 47.41 47.37 47.37 47.37 0 0 0-47.32-47.37zM128.5 335.09a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.41-47.41zm253.91 0a47.37 47.37 0 1 0 47.41 47.41 47.37 47.37 0 0 0-47.32-47.41zm102 92.93a56.48 56.48 0 0 1-56.39 56.48h-344a56.48 56.48 0 0 1-56.52-56.48v-344A56.48 56.48 0 0 1 83.98 27.5h344a56.48 56.48 0 0 1 56.52 56.48zm-20-344a36.48 36.48 0 0 0-36.39-36.52h-344A36.48 36.48 0 0 0 47.5 83.98v344a36.48 36.48 0 0 0 36.48 36.52h344a36.48 36.48 0 0 0 36.52-36.48z"
    class="cls-1" />
</svg>
"""

DICES = [
  PIG,
  DICE_1,
  DICE_2,
  DICE_3,
  DICE_4,
  DICE_5,
  DICE_6
]

atlastk.launch(CALLBACKS, User, HEAD)
