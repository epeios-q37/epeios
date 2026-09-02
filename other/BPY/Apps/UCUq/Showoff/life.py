import random

import ucuq

from show import sleepUntil as sleepUntil_


GRID_WIDTH_ = 32 * 3
GRID_HEIGHT_ = 16
CELL_SIZE_ = 4
FILL_PROBABILITY_ = 0.25
TARGET_DURATION_ = 0.15
MAX_GENERATIONS_ = 500
STAGNATION_WINDOW_ = 4
MASS_EVENT_THRESHOLD_ = 0.15


def createRandomGrid_():
  return [[random.random() < FILL_PROBABILITY_ for _ in range(GRID_WIDTH_)] for _ in range(GRID_HEIGHT_)]


def countAliveNeighbors_(grid, row, col):
  count = 0
  for deltaRow in (-1, 0, 1):
    for deltaCol in (-1, 0, 1):
      if deltaRow == 0 and deltaCol == 0:
        continue
      neighborRow = (row + deltaRow) % GRID_HEIGHT_
      neighborCol = (col + deltaCol) % GRID_WIDTH_
      if grid[neighborRow][neighborCol]:
        count += 1
  return count


def nextGeneration_(grid):
  newGrid = [[False] * GRID_WIDTH_ for _ in range(GRID_HEIGHT_)]
  for row in range(GRID_HEIGHT_):
    for col in range(GRID_WIDTH_):
      alive = grid[row][col]
      neighbors = countAliveNeighbors_(grid, row, col)
      newGrid[row][col] = neighbors == 3 or (alive and neighbors == 2)
  return newGrid


def countPopulation_(grid):
  return sum(1 for row in grid for cell in row if cell)


def gridSignature_(grid):
  return tuple(tuple(row) for row in grid)


def drawGrid_(oled, grid):
  oled.fill(0)
  for row in range(GRID_HEIGHT_):
    for col in range(GRID_WIDTH_):
      if grid[row][col]:
        oled.rect(col * CELL_SIZE_, row * CELL_SIZE_, CELL_SIZE_, CELL_SIZE_, 1)
  oled.show()


def hsvToRGB_(hue, saturation, value):
  hue = hue % 360
  chroma = value * saturation
  xComponent = chroma * (1 - abs((hue / 60) % 2 - 1))
  matchValue = value - chroma
  if hue < 60:
    redPrime, greenPrime, bluePrime = chroma, xComponent, 0
  elif hue < 120:
    redPrime, greenPrime, bluePrime = xComponent, chroma, 0
  elif hue < 180:
    redPrime, greenPrime, bluePrime = 0, chroma, xComponent
  elif hue < 240:
    redPrime, greenPrime, bluePrime = 0, xComponent, chroma
  elif hue < 300:
    redPrime, greenPrime, bluePrime = xComponent, 0, chroma
  else:
    redPrime, greenPrime, bluePrime = chroma, 0, xComponent
  return (
    int((redPrime + matchValue) * 10),
    int((greenPrime + matchValue) * 10),
    int((bluePrime + matchValue) * 10),
  )


def setRingFromPopulation_(ring, population, referencePopulation, generation):
  fraction = min(population / referencePopulation, 1.0) if referencePopulation else 0
  hue = 120 - 150 * fraction
  pulseIndex = generation % 8
  for pixelIndex in range(8):
    value = 1.0 if pixelIndex == pulseIndex else 0.4
    ring.setValue(pixelIndex, hsvToRGB_(hue, 1.0, value))
  ring.write()


def updateLCD_(lcd, generation, population):
  lcd.moveTo(0,0).putString(f"Gen: {str(generation).rjust(3)}".center(16))
  lcd.moveTo(0,1).putString(f"Pop: {str(population).rjust(3)}".center(16))


def runDemo_(oled, ring, lcd, timestamp):
  grid = createRandomGrid_()
  generation = 0
  previousPopulation = countPopulation_(grid)
  recentSignatures = []
  observedMaxPopulation = previousPopulation

  timestamp += 1

  sleepUntil_(timestamp, 0)

  while True:
    drawGrid_(oled, grid)
    population = countPopulation_(grid)
    observedMaxPopulation = max(observedMaxPopulation, population)
    setRingFromPopulation_(ring, population, observedMaxPopulation, generation)
    updateLCD_(lcd, generation, population)

    signature = gridSignature_(grid)
    isStagnant = signature in recentSignatures
    recentSignatures.append(signature)
    if len(recentSignatures) > STAGNATION_WINDOW_:
      recentSignatures.pop(0)

    isExtinct = population == 0
    isExhausted = generation >= MAX_GENERATIONS_

    if isExtinct or isStagnant or isExhausted:
      timestamp += 1
      sleepUntil_(timestamp, 0)
      grid = createRandomGrid_()
      generation = 0
      previousPopulation = countPopulation_(grid)
      recentSignatures = []
      observedMaxPopulation = previousPopulation
      continue

    previousPopulation = population
    grid = nextGeneration_(grid)
    generation += 1

    timestamp += TARGET_DURATION_
    sleepUntil_(timestamp, 0)

  return timestamp


def launch(timestamp, devices):
  oleds = devices.oleds
  runDemo_(ucuq.OLEDS_Wall(((oleds[0], oleds[1], oleds[2]),)), devices.rings, devices.lcds.backlightOn(), timestamp)