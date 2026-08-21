import random

import ucuq

STEP_MIN_ = 100
STEP_MAX_ = 250
DURATION_ = 10
DELAY_ = 1 / 10
COMMIT_DELAY_ = 1 / 8
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


def setOLEDDots_(oled, value1, value2, pos, col):
  pos = ucuq.ravel.OLED_WIDTH - 1 - pos

  return oled\
    .pixel(pos, value1 * ( ucuq.ravel.OLED_HEIGHT // 2  - 1 ) // ( MAX_ - 1 ), col )\
    .pixel(pos, ucuq.ravel.OLED_HEIGHT // 2 + value2 * ( ucuq.ravel.OLED_HEIGHT // 2  - 1 ) // ( MAX_ - 1 ), col )


def setOLED_(oled, data0, data1, pos):
  if pos == 0:
    setOLEDDots_(oled, data0[0], data1[0], pos, 1).show()
  else:
    max = min(pos, ucuq.ravel.OLED_WIDTH - 1)
    for i in range(max+1):
      p = pos - i
      setOLEDDots_(oled, data0[p-1], data1[p-1], i ,0)
      setOLEDDots_(oled, data0[p], data1[p], i ,1)

    oled.show()


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


def getOLEDEvents_(oled, data0, data1):
  events = []

  for i in range(len(data0)):
    events.append((lambda i = i: setOLED_(oled, data0, data1, i), DELAY_))

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

  
  upperEvents, ringData, oledData0 = getServosEvents_(upper, (lcd, 0))
  ringEvents.append(getRingEvents_(ring, ringData, ledUpper))

  lowerEvents, ringData, oledData1 = getServosEvents_(lower, (lcd, 1))
  ringEvents.append(getRingEvents_(ring, ringData, ledLower))

  maxAmountOfOLEDData= max(len(oledData0), len(oledData1))

  oledData0 = extend_(oledData0, maxAmountOfOLEDData)
  oledData1 = extend_(oledData1, maxAmountOfOLEDData)
  
#  oledEvents.append(tuple((lambda: oled.scroll(-1, 0).vline(ucuq.ravel.OLED_WIDTH - 1, 0, ucuq.ravel.OLED_HEIGHT, 0).show(), DELAY_) for _ in range(maxAmountOfOLEDEvents)))

  oledEvents = getOLEDEvents_(oled, oledData0, oledData1)

  eventList = (upperEvents, lowerEvents, *ringEvents, oledEvents, getCommitEvents_())

  lcd.uploadHPeakChars().backlightOn()

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  ucuq.sleepStart()
  ucuq.playEvents(eventList, lambda _, cumul: ucuq.sleepWait(cumul))
  
  upper.park()
  lower.park()

  ucuq.setCommitBehavior(cb)
  ucuq.commit()
