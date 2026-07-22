import random

import ucuq

STEP_MIN_ = 50
STEP_MAX_ = 300
DURATION_ = 15
DELAY_ = 1 / 15
COMMIT_DELAY_ = 1 / 10
MAX_ = ucuq.ravel.SERVO_MAX
WIDTH_ = ucuq.ravel.LCD_WIDTH * 5
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

def setOLED_(oled, pos, base):
  oled.pixel(ucuq.ravel.OLED_WIDTH - 1, base + pos * ( ucuq.ravel.OLED_HEIGHT // 2  - 1 ) // ( MAX_ - 1 ) )


def getServosEvents_(servo, lcd):
  elapsed = 0
  current = park = servo.get()
  rising = current == 0
  target = random.randrange(MAX_)
  events = []
  step = random.randrange(STEP_MIN_, STEP_MAX_ + 1)
  parking = False
  ringData = []
  oledData = []
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

    oledData.append(current)
    events.append((lambda pos = current, step = step: (servo.set(pos), lcd[0].moveTo(0, lcd[1]).putString(lcd[0].getForwardPeak(WIDTH_ * pos // (MAX_ + 1), WIDTH_))), DELAY_))

    elapsed += DELAY_
    ringDelay += DELAY_

  ringData.append((step, ringDelay))

  return events, ringData, oledData


def getRingEvents_(ring, data, list):
  events = []

  for item in data:
    events.append((lambda item = item: setRing_(ring, item[0], list), item[1]))

  return events


def getOLEDEvents_(oled, data, base):
  events = []

  for item in data:
    events.append((lambda item = item: setOLED_(oled, item, base), DELAY_))

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
  oled, ring, lcd, upper, lower = ucuq.ravel.get("ORLS")

  ringEvents= []
  oledEvents = []

  ledUpper = tuple((i, SPEED_COLORS_[i]) for i in range(4))
  ledLower = tuple((7 - i, SPEED_COLORS_[i]) for i in range(4))

  upperEvents, ringData, oledData = getServosEvents_(upper, (lcd, 0))
  ringEvents.append(getRingEvents_(ring, ringData, ledUpper))
  oledEvents.append(getOLEDEvents_(oled, oledData, 0))

  lowerEvents, ringData, oledData = getServosEvents_(lower, (lcd, 1))
  ringEvents.append(getRingEvents_(ring, ringData, ledLower))
  oledEvents.append(getOLEDEvents_(oled, oledData, ucuq.ravel.OLED_HEIGHT // 2))

  maxAmountOfOLEDEvents= max(len(oledEvents[0]), len(oledEvents[1]))

  oledEvents[0] = extend_(oledEvents[0], maxAmountOfOLEDEvents)
  oledEvents[1] = extend_(oledEvents[1], maxAmountOfOLEDEvents)

  oledEvents.append(tuple((lambda: oled.scroll(-1, 0).vline(ucuq.ravel.OLED_WIDTH - 1, 0, ucuq.ravel.OLED_HEIGHT, 0).show(), DELAY_) for _ in range(maxAmountOfOLEDEvents)))

  eventList = (upperEvents, lowerEvents, *ringEvents, *oledEvents, getCommitEvents_())

  lcd.uploadHPeakChars().backlightOn()

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  ucuq.sleepStart()
  ucuq.playEvents(eventList, lambda _, cumul: ucuq.sleepWait(cumul))
  
  upper.park()
  lower.park()

  ucuq.setCommitBehavior(cb)
  ucuq.commit()
