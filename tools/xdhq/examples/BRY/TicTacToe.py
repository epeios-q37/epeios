import atlastk

from functools import reduce 

currentPlayer = ""
winningCombos = []

def initWinningCombos():
  global winningCombos

  for i in range(3):
    winningCombos.append([(i,j) for j in range(3)])
    winningCombos.append([(j,i) for j in range(3)])

  winningCombos.append([(i, i) for i in range(3)])
  winningCombos.append([(i, 2-i) for i in range(3)])


async def setStatus(dom, text):
  await dom.setValue("status", text)


async def newGame(dom):
  global currentPlayer

  ids = []

  for i in range(3):
    ids.extend([f"cell{i}{j}" for j in range(3)])

  await dom.setValues(dict(zip(ids, [""]*9)))
  await dom.removeClasses(dict(zip(ids, [["o", "x", "win"]]*9)))

  currentPlayer = "x"
  await setStatus(dom, f'{currentPlayer} playing…')


async def getCell(dom, i, j):
  return await dom.getValue(f"cell{i}{j}")


async def getBoard(dom):
  board = []

  for i in range(3):
    board.append(list((await dom.getValues([f"cell{i}{j}" for j in range(3)])).values()))
  
  return board


def getWinner(combo, board):
  values = [board[i][j] for i, j in combo]

  return values[0] if values[0] != "" and len(set(values)) == 1 else ""


async def checkWinner(dom):
  board = await getBoard(dom)

  for combo in winningCombos:
    winner = await getWinner(combo, board)
    if winner:
      await dom.addClasses(dict(zip([f"cell{i}{j}" for i, j in combo], ["win"]*3)))
      return winner

  for i in range(3):
    for j in range(3):
      if board[i][j] == "":
        return None

  return "tie"


async def nextTurn(dom):
  global currentPlayer

  winner = await checkWinner(dom)

  if winner == "tie":
    await setStatus(dom, "It's a tie!")
    currentPlayer = ""
    return
  elif winner is not None:
    await setStatus(dom, f'{winner} wins')
    currentPlayer = ""
    return

  currentPlayer = "o" if currentPlayer == "x" else "x"

  await setStatus(dom, f'{currentPlayer} playing…')


async def setCell(dom, i, j, value):
  cellId = f"cell{i}{j}"

  await dom.setValue(cellId, value)
  await dom.removeClass(cellId, ["x","o","win"])
  await dom.addClass(cellId, value)


async def acClick(dom, id):
  i = await dom.getAttribute(id, "data-x")
  j = await dom.getAttribute(id, "data-y")

  if currentPlayer == "":
    return

  value = await getCell(dom, i, j)

  if value == "":
    await setCell(dom, i, j, currentPlayer)
    await nextTurn(dom)


async def acConnect(dom):
  initWinningCombos()
  await dom.inner("", BODY)
  await newGame(dom)


async def acNew(dom):
  await newGame(dom)


CALLBACKS = {
  "": acConnect,
  "Click": acClick,
  "New": acNew
}

HEAD = """
<link href="https://fonts.googleapis.com/css?family=Indie+Flower" rel="stylesheet">
<style>
h1, h2 {
  font-family: 'Indie Flower', 'Comic Sans', cursive;
  text-align: center;
  margin: 10px;
}

#board {
  font-family: 'Indie Flower', 'Comic Sans', cursive;
  position: relative;
  font-size: 120px;
  margin: 1% auto;
  border-collapse: collapse;
}

#board td {
  border: 4px solid rgb(60, 60, 60);
  width: 90px;
  height: 90px;
  vertical-align: middle;
  text-align: center;
  cursor: pointer;
}

#board td div {
  width: 90px;
  height: 90px;
  line-height: 90px;
  display: block;
  overflow: hidden;
  cursor: pointer;
}

.x {
  color: darksalmon;
  position: relative;
  font-size: 1.2em;
  cursor: default;
}

.o {
  color: aquamarine;
  position: relative;
  font-size: 1.0em;
  cursor: default;
}

.win {
  background-color: lightblue;
}
</style>
"""

ROW = '<td><div id="cell{}{}" data-x="{}" data-y="{}" class="cell" xdh:onevent="Click"></div></td>'

def expand(i):
  return reduce(lambda a, b: a+b, [[i, j]*2 for j in range(3)])

BODY= """
<h1>Tic-Tac-Toe</h1>
<table id="board">
  <tr>
""" + (ROW*3).format(*expand(0)) + """
  </tr>
  <tr>
""" + (ROW*3).format(*expand(1)) + """
  </tr>
  <tr>
""" + (ROW*3).format(*expand(2)) + """
  </tr>
</table>
<h2 id="status"></h2>
<div style="display: flex;"> 
  <button xdh:onevent="New" style="margin: auto;">New game</button>
</div>
"""

atlastk.launch(CALLBACKS, headContent = HEAD)