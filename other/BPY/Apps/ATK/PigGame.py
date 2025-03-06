import atlastk, random, string

#DEBUG = True  # Uncomment for debug mode.

LIMIT = 100

GAME_CONTROLS = ["New"]
PLAY_CONTROLS = ["Roll", "Hold"]

METER = '<span class="{}" style="width: {}%;"></span>'

games = {}

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

  games[token] = game
  if debug():
    print("Create: ", token)

  return game


def removeGame(token, player):
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
  return games[token] if token in games else None


def getAvailablePlayer(game):
  player = 0

  if game.available:
    player = game.available

    game.available = 2 if game.available == 1 else 0

  return player


def getGameAvailablePlayer(token):
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

    if value < 2:
      await dom.end("dice", SOUND)


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

  token = "debug" if debug() else ''.join(random.sample(string.ascii_letters + string.digits, 20))

  createGame(token)

  url = atlastk.getAppURL(token)
  escapedUrl = url.replace(":", "%3A").replace("?", "%3F").replace("=", "%3D").replace("&", "%26")
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
  color: sandybrown;
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
  display: block;
  text-align: center;
  font-size: larger;
  letter-spacing: 5px;
  font-family: cursive;
  width: 100%;
  background-color: lightgreen;
  background: linear-gradient(to right, #6666ff, #0099ff, #00ff00, #ff3399, #6666ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: rainbow_animation 6s ease-in-out infinite;
  background-size: 400% 100%;
  height: 100%;
}

@keyframes rainbow_animation {

  0%,
  100% {
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
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 425 425">
  <path style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
    d="M157.486 290.866l-4.593 2.462c-8.11 4.33-13.64 12.94-17.224 23.039-3.586 10.099-5.24 21.852-5.03 33.166.209 11.314 2.241 22.188 6.5 30.56 4.258 8.371 11.365 14.486 20.577 14.263 4.488-.108 8.362-1.515 11.135-4.125 2.773-2.61 4.325-6.166 5.111-10.061 1.573-7.79.345-17.377-1.813-27.68-4.318-20.604-12.743-44.315-14.1-56.421z"
    font-weight="400" color="#000" stroke="#000" stroke-width="14.177" overflow="visible" font-family="Sans" />
  <g font-weight="400" color="#000" font-family="Sans">
    <path style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
      d="M235.97 291.336l-3.865 2.476c-6.828 4.355-11.097 12.295-13.558 21.409-2.46 9.114-3.113 19.55-2.158 29.472.955 9.923 3.482 19.335 7.792 26.397 4.31 7.063 10.97 11.949 19.045 11.125 3.935-.4 7.241-1.9 9.499-4.381 2.258-2.481 3.378-5.711 3.803-9.186.85-6.948-.88-15.285-3.479-24.187-5.196-17.802-14.212-38.053-16.23-48.594z"
      stroke="#000" stroke-width="14.177" overflow="visible" />
    <path
      d="M235.97 291.336l-3.865 2.476c-6.828 4.355-11.097 12.295-13.558 21.409-2.46 9.114-3.113 19.55-2.158 29.472.955 9.923 3.482 19.335 7.792 26.397 4.31 7.063 10.97 11.949 19.045 11.125 3.935-.4 7.241-1.9 9.499-4.381 2.258-2.481 3.378-5.711 3.803-9.186.85-6.948-.88-15.285-3.479-24.187-5.196-17.802-14.212-38.053-16.23-48.594z"
      style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
      fill="#ff9298" overflow="visible" />
  </g>
  <path
    d="M118.187 292.941l-5.178.594c-9.135 1.03-17.451 6.994-24.51 15.057-7.059 8.063-12.934 18.376-16.915 28.969-3.98 10.593-6.103 21.45-5.235 30.801.869 9.352 5.218 17.658 13.862 20.85 4.212 1.556 8.33 1.678 11.87.276 3.541-1.403 6.296-4.136 8.464-7.465 4.337-6.66 6.734-16.024 8.529-26.395 3.59-20.744 4.51-45.89 7.716-57.643z"
    style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
    font-weight="400" color="#000" stroke="#000" stroke-width="14.177" overflow="visible" font-family="Sans" />
  <path d="M124.018 78.02c-36.664-24.978-58.825-8.391-96.521-7.855 29.671 19.01 50.037 26.525 63.91 57.37z" fill="none"
    stroke="#000" stroke-width="13.464" />
  <path
    d="M339.709 236.139c11.499.932 35.826-27.937 45.473-19.635 9.647 8.303 1.66 23.328-6.85 25.948-8.51 2.621-18.385-7.75-23.704-2.959-5.32 4.791 17.979 16.406 30.036 14.02 12.057-2.385 20.633-10.239 23.233-22.643 2.6-12.405.503-26.972-14.544-36.078-15.046-9.106-44.51 5.866-56.587 13.806-12.076 7.939-14.75 10.11-13.64 16.925 1.11 6.815 5.084 9.683 16.583 10.616z"
    fill="#ffc5bb" stroke="#000" stroke-width="12.286" />
  <path
    d="M339.709 236.139c11.499.932 35.826-27.937 45.473-19.635 9.647 8.303 1.66 23.328-6.85 25.948-8.51 2.621-18.385-7.75-23.704-2.959-5.32 4.791 17.979 16.406 30.036 14.02 12.057-2.385 20.633-10.239 23.233-22.643 2.6-12.405.503-26.972-14.544-36.078-15.046-9.106-44.51 5.866-56.587 13.806-12.076 7.939-14.75 10.11-13.64 16.925 1.11 6.815 5.084 9.683 16.583 10.616z"
    fill="#ff9298" />
  <path
    d="M381.75 191.937c-15.494-.047-35.547 10.455-44.982 16.657-12.076 7.94-14.755 10.11-13.645 16.924 1.11 6.815 5.1 9.7 16.599 10.632 11.499.933 35.807-27.943 45.454-19.64 4.101 3.53 5.034 8.269 4.076 12.759a186.826 186.826 0 0017.514-18.991c-2.227-5.827-6.415-11.243-13.41-15.476-3.29-1.992-7.268-2.852-11.606-2.865zm-23.687 46.28c-1.279.019-2.429.373-3.426 1.27-2.752 2.48 2.168 6.795 9.215 10.043 3.255-2.182 6.411-4.47 9.51-6.823-5.48-.817-11.06-4.548-15.3-4.49z"
    fill="#ffc5bb" />
  <path style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
    d="M118.187 292.941l-5.178.594c-9.135 1.03-17.451 6.994-24.51 15.057-7.059 8.063-12.934 18.376-16.915 28.969-3.98 10.593-6.103 21.45-5.235 30.801.869 9.352 5.218 17.658 13.862 20.85 4.212 1.556 8.33 1.678 11.87.276 3.541-1.403 6.296-4.136 8.464-7.465 4.337-6.66 6.734-16.024 8.529-26.395 3.59-20.744 4.51-45.89 7.716-57.643z"
    font-weight="400" color="#000" fill="#ff9298" overflow="visible" font-family="Sans" />
  <path
    d="M-794.485 155.347c0 47.7-38.668 86.368-86.368 86.368-47.7 0-86.368-38.669-86.368-86.368 0-47.7 38.668-86.368 86.368-86.368 47.7 0 86.368 38.668 86.368 86.368z"
    transform="matrix(1.83648 0 0 1.6566 1808.052 -50.74)" fill="#ff9298" stroke="#000" stroke-width="7.719" />
  <g font-weight="400" color="#000" font-family="Sans">
    <path
      d="M293.713 283.984l-3.655 2.779c-6.456 4.89-10.073 13.146-11.793 22.429-1.72 9.282-1.532 19.736.218 29.55 1.749 9.814 5.024 18.993 9.888 25.686 4.864 6.693 11.894 11.028 19.877 9.559 3.89-.717 7.065-2.477 9.116-5.131 2.051-2.655 2.908-5.964 3.053-9.462.29-6.994-2.107-15.165-5.412-23.829-6.61-17.327-17.224-36.788-20.082-47.132z"
      style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
      stroke="#000" stroke-width="14.177" overflow="visible" />
    <path style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
      d="M293.713 283.984l-3.655 2.779c-6.456 4.89-10.073 13.146-11.793 22.429-1.72 9.282-1.532 19.736.218 29.55 1.749 9.814 5.024 18.993 9.888 25.686 4.864 6.693 11.894 11.028 19.877 9.559 3.89-.717 7.065-2.477 9.116-5.131 2.051-2.655 2.908-5.964 3.053-9.462.29-6.994-2.107-15.165-5.412-23.829-6.61-17.327-17.224-36.788-20.082-47.132z"
      fill="#ff9298" overflow="visible" />
  </g>
  <path
    d="M157.486 290.866l-4.593 2.462c-8.11 4.33-13.64 12.94-17.224 23.039-3.586 10.099-5.24 21.852-5.03 33.166.209 11.314 2.241 22.188 6.5 30.56 4.258 8.371 11.365 14.486 20.577 14.263 4.488-.108 8.362-1.515 11.135-4.125 2.773-2.61 4.325-6.166 5.111-10.061 1.573-7.79.345-17.377-1.813-27.68-4.318-20.604-12.743-44.315-14.1-56.421z"
    style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
    font-weight="400" color="#000" fill="#ff9298" overflow="visible" font-family="Sans" />
  <path
    d="M348.996 206.607c0 79.02-71.013 143.078-158.613 143.078S31.77 285.627 31.77 206.607 102.783 63.53 190.383 63.53s158.613 64.058 158.613 143.077z"
    fill="#ff9298" />
  <path
    d="M190.394 63.52c-87.6 0-158.632 64.075-158.632 143.095 0 30.846 10.835 59.41 29.24 82.776 17.45 4.495 35.854 6.9 54.905 6.9 109.341 0 198.134-79.283 199.626-177.595-29.026-33.572-74.284-55.175-125.14-55.175z"
    fill="#ffc5bb" />
  <path style="text-indent:0;text-align:start;line-height:normal;text-transform:none;block-progression:tb;marker:none"
    d="M111.047 134.914c-16.975 0-31.106 12.393-31.106 28.031 0 15.639 14.131 28.032 31.106 28.032 9.192 0 17.552-3.656 23.284-9.472 5.797 9.355 17.104 15.62 29.885 15.62 18.534 0 34-13.152 34-29.84 0-16.687-15.466-29.84-34-29.84-10.596 0-20.175 4.3-26.45 11.1-5.467-8.216-15.476-13.631-26.72-13.631z"
    font-weight="400" color="#000" stroke="#000" stroke-width="3.78" overflow="visible" font-family="Sans" />
  <path
    d="M139.269 162.935c0 13.883-12.631 25.138-28.213 25.138-15.58 0-28.212-11.255-28.212-25.138 0-13.884 12.631-25.138 28.212-25.138 15.582 0 28.213 11.254 28.213 25.138z"
    fill="#fff" />
  <path
    d="M195.331 167.275c0 14.882-13.926 26.946-31.105 26.946-17.18 0-31.106-12.064-31.106-26.946 0-14.882 13.926-26.946 31.106-26.946 17.179 0 31.105 12.064 31.105 26.946z"
    fill="#fff" />
  <path
    d="M163.79 168.598a7.14 7.14 0 11-14.279 0 7.14 7.14 0 0114.279 0zm-41.486-2.576a7.14 7.14 0 11-14.279 0 7.14 7.14 0 0114.279 0z" />
  <path
    d="M181.535 227.713c0 27.847-22.575 50.421-50.422 50.421-27.846 0-50.42-22.574-50.42-50.42 0-27.848 22.574-50.422 50.42-50.422 27.847 0 50.422 22.574 50.422 50.421z"
    fill="#ff9298" stroke="#000" stroke-width="9.451" />
  <path
    d="M181.535 227.713c0 27.847-22.575 50.421-50.422 50.421-27.846 0-50.42-22.574-50.42-50.42 0-27.848 22.574-50.422 50.42-50.422 27.847 0 50.422 22.574 50.422 50.421z"
    fill="#ff9298" />
  <path
    d="M131.108 177.282c-27.847 0-50.411 22.588-50.411 50.435 0 15.088 6.625 28.62 17.127 37.86 33.33-4.842 62.575-22.247 82.817-47.244-4.398-23.362-24.893-41.05-49.533-41.05z"
    fill="#ffc5bb" />
  <path
    d="M158.39 230.03a7.14 7.14 0 11-14.28 0 7.14 7.14 0 0114.28 0zm-41.487-2.576a7.14 7.14 0 11-14.278 0 7.14 7.14 0 0114.278 0z" />
  <path d="M124.018 78.02c-36.664-24.978-58.825-8.391-96.521-7.855 29.671 19.01 50.037 26.525 63.91 57.37z"
    fill="#ffc5bb" />
  <path
    d="M88.124 74.093c-10.734.131-21.18 3.58-34.793 3.773 13.563 8.69 24.094 13.646 32.252 22.924 8.311-7.562 18.077-13.827 28.877-18.43-9.922-6.553-18.217-8.366-26.336-8.267z"
    fill="#ff9298" />
  <g>
    <path d="M183.62 69.83c31.656-32.21 56.67-27.13 93.22-36.37-23.738 26.044-37.989 38.08-43.404 71.466z" fill="none"
      stroke="#000" stroke-width="13.464" />
    <path d="M177.195 76.662c28.947-33.619 66.57-34.456 103.12-43.697-23.738 26.044-47.313 42.91-52.728 76.296z"
      fill="#ffc5bb" />
    <path
      d="M259.16 44.6c-33.842 2.217-54.123 17.5-73.885 30.628 10.272 3.678 28.94 21.23 38.504 25.772-5.738-12.285 16.286-48.644 35.381-56.4z"
      fill="#ff9298" />
  </g>
</svg>"""

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

SOUND = """
<audio autoplay src="data:audio/mp3;base64,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"></audio>
"""

atlastk.launch(CALLBACKS, userCallback=User, headContent=HEAD)
