import ucuq

LINE1_ = "En route pour".center(16)
#        "1234567890123456"
LINE2_ = "l'aventure !".center(16)

DELAY_TTY_WRITE_ = .2
DELAY_SCROLL_WRITE_ = .1
DELAY_WAVE_ = .05


def scrollToLeftEvents_(lcd, text, x, y, delay):
  text = " " * 16 + text

  events = []

  for i in range(len(text) - 15):
    events.append((
      lambda i = i: lcd.moveTo(x,y).putString(text[i:][:16]),
      delay))

  return events


def scrollToRightEvents_(lcd, text, x, y, delay):
  text += " " * 16

  events = []

  for i in range(len(text) - 15):
    events.append((
      lambda i = i: lcd.moveTo(x,y).putString(text[len(text) - i - 16:][:16]),
      delay))

  return events


def mixedScrollWrite_(lcd):
  line1 = LINE1_
  line2 = LINE2_
  ucuq.sleepStart()
  ucuq.playEvents((
      scrollToLeftEvents_(lcd, line1, 0, 0, DELAY_SCROLL_WRITE_),
      scrollToRightEvents_(lcd, line2, 0, 1, DELAY_SCROLL_WRITE_)
    ),
    lambda tracking: ucuq.sleepWait(tracking.cumul)
  )


def spacesMerging_(s1: str, s2: str) -> str:
  i = 0
  while i < len(s2) and s2[i] == " ":
    i += 1

  if i >= len(s1):
    return s1 + s2[len(s1) :]
  else:
    return s1 + s2.lstrip()


def waves_(lcd):
  wave2 = ""

  for i in range(8):
    wave2 = chr(i) + wave2
    lcd.moveTo(0, 1).putString(spacesMerging_(wave2, LINE2_)[:16])
    ucuq.sleep(DELAY_WAVE_)

  wave1 = ""

  for i in range(8):
    wave1 = chr(i) + wave1
    wave2 = chr(7) + wave2
    lcd.putString(
      spacesMerging_(wave1, LINE1_)[:16] + spacesMerging_(wave2, LINE2_)[:16]
    )
    ucuq.sleep(DELAY_WAVE_)

  for i in range(7, -1, -1):
    wave1 = chr(i) + wave1
    wave2 = chr(7) + wave2
    lcd.putString(spacesMerging_(wave1, LINE1_)[:16] + wave2[:16])
    ucuq.sleep(DELAY_WAVE_)

  for i in range(7, -1, -1):
    wave1 = " " + wave1
    wave2 = chr(i) + wave2
    lcd.putString(wave1[:16] + wave2[:16])
    ucuq.sleep(DELAY_WAVE_)

  for i in range(16):
    wave1 = " " + wave1
    wave2 = " " + wave2
    lcd.putString(wave1[:16] + wave2[:16])
    ucuq.sleep(DELAY_WAVE_)


def launch(length):
  lcd = ucuq.ravel.LCD()

  lcd.uploadUpwardGaugeChars().backlightOn()

  if length:
    lcd.showCursor().moveTo(0, 0)
    lcd.ttyWrite(LINE1_ + LINE2_, DELAY_TTY_WRITE_)
  else:
    mixedScrollWrite_(lcd)
    ucuq.sleep(1)

  waves_(lcd)

  lcd.backlightOff()
