import atlastk

# Constants used for displaying the board:
EMPTY_SPACE = '.'  # A period is easier to count than a space.
PLAYER_X = 'X'
PLAYER_O = 'O'

BOARD_WIDTH = 7
BOARD_HEIGHT = 6

gameBoard = None
playerTurn = None


def newGame():
  global gameBoard, playerTurn

  gameBoard = getNewBoard()
  playerTurn = PLAYER_X


def getNewBoard():
  """Returns a dictionary that represents a Four in a Row board.

  The keys are (columnIndex, rowIndex) tuples of two integers, and the
  values are one of the 'X', 'O' or '.' (empty space) strings."""
  board = {}
  for columnIndex in range(BOARD_WIDTH):
    for rowIndex in range(BOARD_HEIGHT):
      board[(columnIndex, rowIndex)] = EMPTY_SPACE
  return board


async def displayBoard(dom, board, playerTile):
  """Display the board and its tiles in the browser."""

  '''Prepare a list to pass to the format() string method for the
  board template. The list holds all of the board's tiles (and empty
  spaces) going left to right, top to bottom:'''
  gameOver = True
  winner = getWinner(board)

  # Check for a win or tie:
  if winner is not None:
    await notify(dom, 'Player {} has won!'.format(winner))
  elif isFull(board):
    await notify(dom, 'There is a tie!')
  else:
    await notify(dom, "Player {}, click a column button.".format(playerTile))
    gameOver = False

  tileChars = []
  for rowIndex in range(BOARD_HEIGHT):
    for columnIndex in range(BOARD_WIDTH):
      tileChars.append(board[(columnIndex, rowIndex)])

  htmlFeatures = []
  for columnIndex in range(BOARD_WIDTH):
    if gameOver or gameBoard[(columnIndex, 0)] != EMPTY_SPACE:
      htmlFeatures.append('disabled="disabled"')
    else:
      htmlFeatures.append('')
    htmlFeatures.extend([columnIndex, columnIndex+1])

  # Display the board:
  await dom.inner("board", BOARD.format(*htmlFeatures, *tileChars))


def isFull(board):
  """Returns True if the `board` has no empty spaces, otherwise
  returns False."""
  for rowIndex in range(BOARD_HEIGHT):
    for columnIndex in range(BOARD_WIDTH):
      if board[(columnIndex, rowIndex)] == EMPTY_SPACE:
        return False  # Found an empty space, so return False.
  return True  # All spaces are full.


def getWinner(board):
  """Returns the player who has four tiles in a row on `board`,
  otherwise returns None."""

  # Go through the entire board, checking for four-in-a-row:
  for columnIndex in range(BOARD_WIDTH - 3):
    for rowIndex in range(BOARD_HEIGHT):
      # Check for horizontal four-in-a-row going right:
      tile1 = board[(columnIndex, rowIndex)]
      tile2 = board[(columnIndex + 1, rowIndex)]
      tile3 = board[(columnIndex + 2, rowIndex)]
      tile4 = board[(columnIndex + 3, rowIndex)]
      if tile1 == tile2 == tile3 == tile4 != EMPTY_SPACE:
        return tile1

  for columnIndex in range(BOARD_WIDTH):
    for rowIndex in range(BOARD_HEIGHT - 3):
      # Check for vertical four-in-a-row going down:
      tile1 = board[(columnIndex, rowIndex)]
      tile2 = board[(columnIndex, rowIndex + 1)]
      tile3 = board[(columnIndex, rowIndex + 2)]
      tile4 = board[(columnIndex, rowIndex + 3)]
      if tile1 == tile2 == tile3 == tile4 != EMPTY_SPACE:
        return tile1

  for columnIndex in range(BOARD_WIDTH - 3):
    for rowIndex in range(BOARD_HEIGHT - 3):
      # Check for four-in-a-row going right-down diagonal:
      tile1 = board[(columnIndex, rowIndex)]
      tile2 = board[(columnIndex + 1, rowIndex + 1)]
      tile3 = board[(columnIndex + 2, rowIndex + 2)]
      tile4 = board[(columnIndex + 3, rowIndex + 3)]
      if tile1 == tile2 == tile3 == tile4 != EMPTY_SPACE:
        return tile1

      # Check for four-in-a-row going left-down diagonal:
      tile1 = board[(columnIndex + 3, rowIndex)]
      tile2 = board[(columnIndex + 2, rowIndex + 1)]
      tile3 = board[(columnIndex + 1, rowIndex + 2)]
      tile4 = board[(columnIndex, rowIndex + 3)]
      if tile1 == tile2 == tile3 == tile4 != EMPTY_SPACE:
        return tile1
  return None


async def notify(dom, text):
  """ Displays a text with a little animation to attract attention."""
  await dom.inner("output", '<output class="fade-in">{}</output>'.format(text))


async def acConnect(dom):
  await dom.inner("", BODY)
  await displayBoard(dom, gameBoard, playerTurn)


async def baDisplay(dom):
  await displayBoard(dom, gameBoard, playerTurn)  


async def acSubmit(dom, id):
  global gameBoard, playerTurn
  
  columnIndex = int(id)

  # If the column is full, ask for a move again:
  if gameBoard[(columnIndex, 0)] != EMPTY_SPACE:
    await notify(dom, 'That column is full, select another one.')
    return

  # Starting from the bottom, find the first empty space.
  for rowIndex in range(BOARD_HEIGHT - 1, -1, -1):
    if gameBoard[(columnIndex, rowIndex)] == EMPTY_SPACE:
      playerMove = (columnIndex, rowIndex)
      break

  gameBoard[playerMove] = playerTurn

  # Switch turns to other player:
  if playerTurn == PLAYER_X:
    playerTurn = PLAYER_O
  elif playerTurn == PLAYER_O:
    playerTurn = PLAYER_X

  atlastk.broadcastAction("Display")


async def acNew():
  newGame()
  atlastk.broadcastAction("Display")


CALLBACKS = {
  "": acConnect,
  "Display": baDisplay,
  "Submit": acSubmit,
  "New": acNew
}

HEAD = """
<title>Four in a Row</title>
<style>
  td {
    text-align: center;
    width: 1ic;
  }

  @keyframes fadeIn {
    0% {
      opacity: 0;
    }

    100% {
      opacity: 1;
    }
  }

  .fade-in {
    animation-name: fadeIn;
    animation-duration: 1s;
  }
</style>
"""

BODY = """
<fieldset>
  <fieldset id="board" style="font-size: xx-large;"></fieldset>
  <fieldset id="output"></fieldset>
  <button style="display: flex; margin: 5px auto 0px;" xdh:onevent="New">New game</button>
</fieldset>
"""

BOARD = '<table style="margin: auto; width: 100%;"><tr>' +\
  BOARD_WIDTH * '<th><button xdh:onevent="Submit" {} id="{}">{}</button></th>' +\
  "</tr>" + BOARD_HEIGHT * ("<tr>" + BOARD_WIDTH * "<td>{}</td>" +
  "</tr>") + "</table>"

newGame()
atlastk.launch(CALLBACKS, headContent=HEAD)
