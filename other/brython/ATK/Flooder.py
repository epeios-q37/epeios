import atlastk
import random

# Set up the constants:
BOARD_WIDTH = 16  # (!) Try changing this to 4 or 40.
BOARD_HEIGHT = 14  # (!) Try changing this to 4 or 20.
MOVES_PER_GAME = 20  # (!) Try changing this to 3 or 300.

# Constants for the different shapes used for colorblind:
HEART     = '♥'
DIAMOND   = '♦'
SPADE     = '♠'
CLUB      = '♣'
BALL      = '●'
TRIANGLE  = '▲'

# All the color/shape tiles used on the board:
TILE_TYPES = (0, 1, 2, 3, 4, 5)
COLORS_MAP = {0: 'cyan', 1: 'lightgreen', 2:'lightblue',
              3: 'yellow', 4:'salmon', 5:'burlywood'}
SHAPES_MAP = {0: HEART, 1: TRIANGLE, 2: DIAMOND,
              3: BALL, 4: CLUB, 5: SPADE}


def main():
  newGame()
  atlastk.launch(CALLBACKS, headContent=HEAD)  


def newGame():
  global gameBoard, movesLeft

  gameBoard = getNewBoard()   
  movesLeft = MOVES_PER_GAME


def getNewBoard():
  """Return a dictionary of a new Flood It board."""

  # Keys are (x, y) tuples, values are the tile at that position.
  board = {}

  # Create random colors for the board.
  for x in range(BOARD_WIDTH):
    for y in range(BOARD_HEIGHT):
      board[(x, y)] = random.choice(TILE_TYPES)

  # Make several tiles the same as their neighbor. This creates groups
  # of the same color/shape.
  for i in range(BOARD_WIDTH * BOARD_HEIGHT):
    x = random.randint(0, BOARD_WIDTH - 2)
    y = random.randint(0, BOARD_HEIGHT - 1)
    board[(x + 1, y)] = board[(x, y)]

  return board


async def displayBoard(board, dom):
  """Display the board in the browser."""

  HTML = ""

  # Display each row:
  for y in range(BOARD_HEIGHT):
    HTML += "<tr>"

    # Display each tile in this row:
    for x in range(BOARD_WIDTH):
      tile = board[(x, y)]
      HTML += '<td xdh:onevent="Submit" data-tile="{}" style="background-color: {};">{}</td>'.format(tile, COLORS_MAP[tile],SHAPES_MAP[tile])

    HTML += "</tr>"

  await dom.inner("board", HTML)

  if hasWon(board):
    await notify(dom, "You have won!")
  elif movesLeft == 0:
    await notify(dom, "You have run out of moves!")
  else:
    await notify(dom, "Moves left: {}.".format(movesLeft))


def changeTile(tileType, board, x, y, charToChange=None):
  """Change the color/shape of a tile using the recursive flood fill
  algorithm."""
  if x == 0 and y == 0:
    charToChange = board[(x, y)]
    if tileType == charToChange:
      return  # Base Case: Already is the same tile.

  board[(x, y)] = tileType

  if x > 0 and board[(x - 1, y)] == charToChange:
    # Recursive Case: Change the left neighbor's tile:
    changeTile(tileType, board, x - 1, y, charToChange)
  if y > 0 and board[(x, y - 1)] == charToChange:
    # Recursive Case: Change the top neighbor's tile:
    changeTile(tileType, board, x, y - 1, charToChange)
  if x < BOARD_WIDTH - 1 and board[(x + 1, y)] == charToChange:
    # Recursive Case: Change the right neighbor's tile:
    changeTile(tileType, board, x + 1, y, charToChange)
  if y < BOARD_HEIGHT - 1 and board[(x, y + 1)] == charToChange:
    # Recursive Case: Change the bottom neighbor's tile:
    changeTile(tileType, board, x, y + 1, charToChange)    


def hasWon(board):
  """Return True if the entire board is one color/shape."""
  tile = board[(0, 0)]

  for x in range(BOARD_WIDTH):
    for y in range(BOARD_HEIGHT):
      if board[(x, y)] != tile:
        return False

  return True


async def notify(dom, text):
  """ Displays a text with a little animation to attract attention."""
  await dom.inner("output", '<output class="fade-in">{}</output>'.format(text))


async def acConnect(dom):
  await dom.inner("", BODY)
  await displayBoard(gameBoard, dom)


async def acSubmit(dom,id):
  global movesLeft

  if not hasWon(gameBoard) and movesLeft != 0:
    changeTile(int(await dom.getAttribute(id, "data-tile")), gameBoard, 0, 0)
    movesLeft -= 1

  atlastk.broadcastAction("Display")


def acNew(dom):
  newGame()
  atlastk.broadcastAction("Display")


async def acDisplay(dom):
  await displayBoard(gameBoard, dom)


CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit,
  "New": acNew,
  "Display": acDisplay,
}

HEAD = """
<title>Flooder</title>
<style>
  td {
    text-align: center;
    height: 3ex;
    font-size; x-large;
    cursor: pointer;
    width: 1em;
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
  <fieldset>
    <table style="border-collapse: collapse;" id="board"></table>
  </fieldset>
  <fieldset id="output"></fieldset>
  </fieldset>
   <button style="display: flex; margin: 5px auto 0px;" xdh:onevent="New">New game</button>
</fieldset>
"""

main()