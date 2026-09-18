import copy
import math
import random
import types

import ucuq

from show import sleepUntil as sleepUntil_

MAX_ = ucuq.ravel.SERVO_MAX
STEP_ = 50
DELAY_ = 4/110
PANEL_DELAY_MULTIPLIER_ = 11
REMAINDER_ = ucuq.ravel.PANEL_WIDTH * 3
AMOUNT_ = REMAINDER_ * PANEL_DELAY_MULTIPLIER_
TOTAL_ITERATION_COUNT_ = 100
PROLOG_ITERATION_COUNT_ = 14
PROLOG_ACCELERATION_COEFF_ = 0.5

class Level_:
  def __init__(self, rest):
    self.rest = rest

    if rest == 0:
      self.up = random.randrange(0, MAX_ + 1)
      self.down = 0
      self.step = STEP_
    else:
      self.up = rest
      self.down = random.randrange(0, rest)
      self.step = -STEP_

    self.value = -1

  def update(self):
    if self.value == -1:
      self.value = self.rest
    else:
      self.value = max(min(self.value + self.step, MAX_), 0)
      if self.step > 0 and self.value >= self.up:
        self.step = -STEP_
        self.up = random.randrange(self.down + 1, MAX_ + 1)
      elif self.step < 0 and self.value <= self.down:
        self.step = STEP_
        self.down = random.randrange(0, self.up)

    return self

  def ending(self):
    if self.rest == 0:
      if self.value > 0:
        self.value = max(self.value - STEP_, 0)
    else:
      if self.value < self.rest:
        self.value = min(self.value + STEP_, MAX_)

    return self

  def epilog(self):
    self.value = -1
    return self

  def __repr__(self):
    return str(self.value)


def handleLevels_(levels, method):
  levels.append(method(copy.copy(levels[-1])))
  levels.pop(0)


def getLevelEvents__(tracking):
  for i in range(TOTAL_ITERATION_COUNT_ * PANEL_DELAY_MULTIPLIER_):
    handleLevels_(tracking.tops, Level_.update)
    handleLevels_(tracking.bottoms, Level_.update)

    yield tracking.getDelay(tracking)

  while (tracking.tops[-1].value != 0 or tracking.bottoms[-1].value != MAX_):
    handleLevels_(tracking.tops, Level_.ending)
    handleLevels_(tracking.bottoms, Level_.ending)

    yield tracking.getDelay(tracking)

  for _ in range(REMAINDER_ * PANEL_DELAY_MULTIPLIER_):
    handleLevels_(tracking.tops, Level_.epilog)
    handleLevels_(tracking.bottoms, Level_.epilog)

    yield tracking.getDelay(tracking)

  tracking.stop = True


def getServoEvents_(tracking, levels, index, servo):
  while (True):
    if levels[index].value != levels[index+1].value:
      if levels[index].value == -1:
        servo.park()
      else:
        servo.setSmooth(MAX_ - levels[index].value)

    yield tracking.getDelay(tracking)


def levelTo8_(level):
  return math.ceil(8 * level // (MAX_ +1 ) - .5) + 1


def getLevelChar_(level):
  if level == -1:
    return " "
  
  return ucuq.ravel.panel.getVPeakChar(levelTo8_(level))


def getPanelEvents_(tracking, panels):
  while (True):
    topGauges = ""
    bottomGauges = ""
    for x in range(ucuq.ravel.PANEL_WIDTH * 3):
      topGauges += getLevelChar_(tracking.tops[(x + 1) * PANEL_DELAY_MULTIPLIER_ - 1].value)
      bottomGauges += getLevelChar_(tracking.bottoms[(x + 1) * PANEL_DELAY_MULTIPLIER_ - 1].value)

    panels.moveTo(0,0).putString(topGauges)
    panels.moveTo(0,1).putString(bottomGauges)
    tracking.counter += 1

    yield tracking.getDelay(tracking) * PANEL_DELAY_MULTIPLIER_


def getColorSplit_(level):
  if level == -1:
    return 0
  else:
    return levelTo8_(level)


def getRingEvents_(tracking, index, ring):
  while (True):
    top = getColorSplit_(tracking.tops[index].value)
    bottom = ( 9 - getColorSplit_(tracking.bottoms[index].value) ) % 9

    for i in range(8):
      color = [0] * 3
      if all( i + 1 <= v for v in (top, bottom)):
        color[0] = 10
      elif i + 1 <= top:
        color[1] = 10
      elif i + 1 <= bottom:
        color[2] = 10

      ring.setValue(i - 2, color)

    ring.write()

    yield tracking.getDelay(tracking)


def launch(timestamp, parts):
  tracking = types.SimpleNamespace(
    tops = [Level_(0) for _ in range(AMOUNT_)],
    bottoms = [Level_(MAX_) for _ in range(AMOUNT_)],
    stop = False,
    counter = 0,
    getDelay = lambda tracking: DELAY_ * ( PROLOG_ACCELERATION_COEFF_ if tracking.counter < PROLOG_ITERATION_COUNT_ else 1 )
    )

  timestamp += 1
  sleepUntil_(timestamp, 0)

  uppers = parts.uppers
  lowers = parts.lowers
  panels = ucuq.PanelStrip(parts.panels.uploadVPeakChars().backlightOn())
  rings = parts.rings

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  ucuq.dispatchEvents(
    (
      getLevelEvents__(tracking),
      *(
        events for i in range(3) for events in (
          getServoEvents_(tracking, tracking.tops, i * AMOUNT_ // 3, uppers[i]),
          getServoEvents_(tracking, tracking.bottoms,  i * AMOUNT_ // 3, lowers[i]),
          getRingEvents_(tracking, i * AMOUNT_ // 3, rings[i]),
        )
      ),
      getPanelEvents_(tracking, panels),
    ),
    lambda tracking, user: (sleepUntil_(timestamp + tracking.cumul, 1/3),  not user.tracking.stop)[-1],
    tracking = tracking,
    timestamp = 0
  )

  ucuq.setCommitBehavior(cb)

  uppers.park()
  lowers.park()
  panels.backlightOff()
