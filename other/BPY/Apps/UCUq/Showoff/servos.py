import random

import ucuq

STEP_MIN_ = 100
STEP_MAX_ = 250
DURATION_ = 10
DELAY_ = 1 / 10
COMMIT_DELAY_ = 1 / 8
MAX_ = ucuq.ravel.SERVO_MAX
WIDTH_ = ucuq.ravel.PANEL_WIDTH * 5
COLOR_MAX_ = ucuq.ravel.RING_MAX // 7
SPEED_COLORS_ = ((0, COLOR_MAX_, 0), (COLOR_MAX_, COLOR_MAX_, 0), (COLOR_MAX_, COLOR_MAX_ // 3, 0), (COLOR_MAX_, 0, 0))

def setRing_(ring, step, list):
  pos = len(list) * (step - STEP_MIN_) // (STEP_MAX_ + 1 - STEP_MIN_)

  for i in range(0, pos + 1):
    ring.setValue(list[i][0], list[i][1])

  if pos < len(list):
    for i in range(pos + 1, len(list)):
      ring.setValue(list[i][0], (0,0,0))

  ring.write()


def setScreenDots_(screen, value1, value2, pos, col):
  pos = ucuq.ravel.SCREEN_WIDTH - 1 - pos

  return screen\
    .pixel(pos, value1 * ( ucuq.ravel.SCREEN_HEIGHT // 2  - 1 ) // ( MAX_ - 1 ), col )\
    .pixel(pos, ucuq.ravel.SCREEN_HEIGHT // 2 + value2 * ( ucuq.ravel.SCREEN_HEIGHT // 2  - 1 ) // ( MAX_ - 1 ), col )


def setScreen_(screen, data0, data1, pos):
  if pos == 0:
    setScreenDots_(screen, data0[0], data1[0], pos, 1).show()
  else:
    max = min(pos, ucuq.ravel.SCREEN_WIDTH - 1)
    for i in range(max+1):
      p = pos - i
      setScreenDots_(screen, data0[p-1], data1[p-1], i ,0)
      setScreenDots_(screen, data0[p], data1[p], i ,1)

    screen.show()


def getServosEvents_(servo, panel):
  elapsed = 0
  current = park = servo.get()
  rising = current == 0
  target = random.randrange(MAX_)
  events = []
  step = random.randrange(STEP_MIN_, STEP_MAX_ + 1)
  parking = False
  ringData = []
  screenData = []
  ringDelay = 0

  while True:
    if elapsed > DURATION_:
      if parking and current == park:
        break
      target = park
      rising = park != 0
      parking = True
      ringData.append((step, ringDelay))
      ringDelay = 0
      step = STEP_MAX_
      
    if rising:
      current = min(current + step, target)
      if not parking and current >= target:
        rising = False
        target = random.randrange(0, current + 1)
        ringData.append((step, ringDelay))
        ringDelay = 0
        step = random.randrange(STEP_MIN_, STEP_MAX_ + 1)
    else:
      current = max(current - step, target)
      if  not parking and current <= target:
        rising = True
        target = random.randrange(current + 1, MAX_)
        ringData.append((step, ringDelay))
        ringDelay = 0
        step = random.randrange(STEP_MIN_, STEP_MAX_ + 1)

    screenData.append(current)
    events.append((lambda pos = current, step = step: (servo.set(pos), panel[0].moveTo(0, panel[1]).putString(panel[0].getForwardPeak(WIDTH_ * pos // (MAX_ + 1), WIDTH_))), DELAY_))

    elapsed += DELAY_
    ringDelay += DELAY_

  ringData.append((step, ringDelay))

  return events, ringData, screenData


def getRingEvents_(ring, data, list):
  events = []

  for item in data:
    events.append((lambda item = item: setRing_(ring, item[0], list), item[1]))

  return events


def getScreenEvents_(screen, data0, data1):
  events = []

  for i in range(len(data0)):
    events.append((lambda i = i: setScreen_(screen, data0, data1, i), DELAY_))

  return events


def getCommitEvents_():
  events = []
  elapsed = 0

  while elapsed <= DURATION_:
    events.append((lambda: ucuq.commit(), COMMIT_DELAY_))
    elapsed += COMMIT_DELAY_

  return events


def extend_(array, n):
  return array + [array[-1]] * (n - len(array)) if len(array) < n else array


def launch():
  screen, ring, panel, upper, lower = ucuq.ravel.get("SRPUL")

  ringEvents= []
  screenEvents = []

  ledUpper = tuple((i, SPEED_COLORS_[i]) for i in range(4))
  ledLower = tuple((7 - i, SPEED_COLORS_[i]) for i in range(4))

  
  upperEvents, ringData, screenData0 = getServosEvents_(upper, (panel, 0))
  ringEvents.append(getRingEvents_(ring, ringData, ledUpper))

  lowerEvents, ringData, screenData1 = getServosEvents_(lower, (panel, 1))
  ringEvents.append(getRingEvents_(ring, ringData, ledLower))

  maxAmountOfScreenData= max(len(screenData0), len(screenData1))

  screenData0 = extend_(screenData0, maxAmountOfScreenData)
  screenData1 = extend_(screenData1, maxAmountOfScreenData)
  
#  screenEvents.append(tuple((lambda: screen.scroll(-1, 0).vLine(ucuq.ravel.SCREEN_WIDTH - 1, 0, ucuq.ravel.SCREEN_HEIGHT, 0).show(), DELAY_) for _ in range(maxAmountOfScreenEvents)))

  screenEvents = getScreenEvents_(screen, screenData0, screenData1)

  eventList = (upperEvents, lowerEvents, *ringEvents, screenEvents, getCommitEvents_())

  panel.uploadHPeakChars().backlightOn()

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  ucuq.sleepStart()
  ucuq.playEvents(eventList, lambda tracking: ucuq.sleepWait(tracking.cumul))
  
  upper.park()
  lower.park()

  ucuq.setCommitBehavior(cb)
  ucuq.commit()
