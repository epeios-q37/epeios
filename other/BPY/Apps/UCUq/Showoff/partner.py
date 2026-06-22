import json
import time

import ucuq

import cube
import matrix
import oled
import shared

from shared import (
  RAINBOW as RAINBOW_,
  RGB_MAX as RGB_MAX_,
  getRainbowColor as getRainbowColor_,
)

ring_ = None
buzzer_ = None
oled_ = None
lcd_ = None
ravel_ = None

spokenColorLed_ = 0


def connect(device):
  global ring_, buzzer_, oled_, lcd_, ravel_, spokenColorLed_

  spokenColorLed_ = 0

  ucuq.setDevice(shared.handleDeviceInput(device))

  ravel_ = ucuq.Ravel()

  ring_ = ravel_.ring()
  buzzer_ = ravel_.buzzer()
  oled_ = ravel_.oled()
  lcd_ = ravel_.lcd()

  lcd_.uploadGaugeChars()


LINE1_ = "En route vers".center(16)
#        "1234567890123456"
LINE2_ = "l'aventure !".center(16)

JUNIOR_ = """000000000004001100000000000c008200000000000340080000000000018082000000000002d0080000000000016082000000000002b828000000000010b60200000000000abbc80000000005e952a000000000100abbc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000d7dba00004000017ffffff8006000000b6013fc000000000600017f00000000008000bf000000000380007f8000000000e0001f8000000103e0433fc0000005e1f2c79fd0000003e2f8ffffe4000037917e3fffe8800008617fffffe9e00215d23fffffefe00057c2bfffffffe00437541fffffffe0008d411ffffffff0003a429fffffffe20055c61fffffffe10145c71fffffffe1002b061f7fffffe10083000f7fffffe3002e000fbfffffe380040007cfffffe3005480629fffffe10009407fd7ffffe10028005fcfffffe0800a815ff3ffffc18028047ff7ffffc10008001ffbffff808034046bfffff7000008013ffffff00000300007ffffe08000080000dfffe020001000003fffe000001800020fffe0000000957fe7ffc000001002fffbffc000000215ffffff800000004007ffff800000040003ffff002000028002ffff80000000055dffff0000000249fffffb0000000003feffff000"""

SENIOR_ = """01d5b7e0107ff22f057d5ec07ffffd6e0bd5bd01ffffc6dc055afa003f3bebf901eb380005d7f7f90dfef400023ff7ff0aa94000001ffbff017f4800007ff9ff005b0000008fffff000f800411aafbf80005e8061cffffff0000f80feafeffff0000dd1a36ffffff000036c0abfdffff000035f01effffff000274a0bf7fffff00045f55fdfdffff000439a2ff7ffffc00062eeabffdffff00883afc5ffdffff00411ebff1f7ffff0004756d0ffddfff00011dbaffeb67ff00047eafffd5ffff00093d53ffb6bfff0010bea9ffebdfff00027fe8fdd6dfff0000bff47f753fff4044bb823fdadfff20107e012ef57fff1840081297feffff000a0075cfdeffff0008006bebf77fff0006007fe2ffffff000a006dfbb7ffff000302336affffff00050032157fffff0003800001ffffff00054001017fffff0002001f807fffff00408090007fffff010003817e3ffffb0000001fff9fffff012000bf4adffff7080003800defffff812000002ffeffef000000005fffffbf024a000abfffff7f080100217ffffd7f00098047ffffe17f20828803ffff807f04009e2ffffe007f00209fb7ffff00ff11041faffffe00ff40011feffff801ff00405fffffe801ff12092ff7fff003ff40000fffff8003ff008257fff7c007ff040007ffbf000fff5124abfff0002fff0000017bc0004fe7254a4aad40001c000000002000003800"""


cumulativeSleepDelay_ = 0
relativeSleepDelay_ = 0


def sleepStart_():
  global cumulativeSleepDelay_, relativeSleepDelay_

  ucuq.sleepStart()
  cumulativeSleepDelay_ = relativeSleepDelay_ = 0


def sleepWait_(delay):
  global cumulativeSleepDelay_, relativeSleepDelay_

  relativeSleepDelay_ += delay

  if relativeSleepDelay_ >= 0.3:
    ucuq.commit()

  cumulativeSleepDelay_ += delay
  ucuq.sleepWait(cumulativeSleepDelay_)


def concatHEXImages_(img1: str, img2: str) -> str:
  result_lines = []

  for row in range(64):
    line1 = img1[row * 16 : (row + 1) * 16]
    line2 = img2[row * 16 : (row + 1) * 16]
    result_lines.append(line1 + line2)

  return "".join(result_lines)


def getDuration_(events):
  duration = 0

  for event in events:
    duration += event[1]

  return duration


def oledAnimation_():
  oled_.powerOn()

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  sleepStart_()

  for c in range(64):
    toDraw = concatHEXImages_(
      ("0" * 16 * (63 - c) + JUNIOR_)[:1024],
      (SENIOR_[16 * (63 - c) :] + "0" * 1024)[:1024],
    )

    oled_.draw(toDraw, 128)
    oled_.show()
    sleepWait_(0.05)

  ucuq.setCommitBehavior(cb)


def indy(withSound=True):
  ringOffset = int(time.time())
  ring_.flash()
  lcd_.clear().backlightOff()
  oled_.powerOff()

  if withSound:
    polyEvents = ucuq.voicesToEvents(
      shared.INDY_VOICES,
      shared.INDY_TEMPO,
      lambda freq: (
        buzzer_.off() if freq == 0 else buzzer_.on(freq) if freq > 0 else None
      ),
    )
    duration = getDuration_(polyEvents[0])
  else:
    polyEvents = [[(lambda: buzzer_.off(), 0)]]
    duration = 5

  ringEvents = []

  ringCount = 200 if withSound else 50

  for c in range(ringCount):
    ringEvents.append(
      (
        lambda c=c, color=getRainbowColor_(
          c + ringOffset
        ), ringCount=ringCount: (
          ring_.setValue(c, color).setValue(ringCount - c, color).write(),
          ravel_.displayRingGauges(),
        ),
        duration / ringCount,
      )
    )

  polyEvents.append(ringEvents)

  ringOffset = int(time.time())

  oledAnimation_()

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  lcd_.backlightOn()

  ucuq.sleepStart()

  ucuq.playEvents(
    polyEvents,
    lambda duration: (
      ucuq.sleepWait(duration),
      ucuq.sleepStart(),
      ucuq.commit() if duration > 0.05 else None,
    ),
  )

  ucuq.setCommitBehavior(cb)

  lcd_.hideCursor()

  for i in range(8):
    ring_.setValue(i, getRainbowColor_(ringOffset + i, 7)).write()

  ravel_.displayRingGauges()

  return True


def Buzzer():
  coeff = 2 ** (1 / 12)

  freq = 220
  
  for n in range(-12, 13):
    buzzer_.on(int(freq))
    
    if n < 0:
      freq *= coeff
    else:
      freq /= coeff
      
    ucuq.sleep(0.1)
    
  buzzer_.off()


def OLED(field):
  oled.launch(oled_, field)
  
  
def matrixSimulation():
  matrix.launch(oled_, buzzer_, ring_, lcd_)


def Ring():
  count = len(RAINBOW_) // 8

  delay = 5 / (count * 8)

  for i in range(count):
    for led in range(8):
      ring_[led] = getRainbowColor_(i * 8 + led)
      ring_.write()
      ucuq.sleep(delay)

  for led in range(8):
    ring_[led] = getRainbowColor_(led, 7)
    ring_.write()
    ucuq.sleep(delay)

  ucuq.sleep(1)

  ring_.fill((0, 0, 0)).write()


SPOKEN_COLORS_ = {
  "rouge": [255, 0, 0],
  "vert": [0, 255, 0],
  "verre": [0, 255, 0],
  "verte": [0, 255, 0],
  "bleu": [0, 0, 255],
  "jaune": [255, 255, 0],
  "cyan": [0, 255, 255],
  "magenta": [255, 0, 255],
  "orange": [255, 127, 0],
  "violet": [127, 0, 255],
  "rose": [255, 127, 127],
  "gris": [127, 127, 127],
  "noir": [0, 0, 0],
  "blanc": [255, 255, 255],
  "marron": [127, 59, 0],
  "turquoise": [0, 127, 127],
  "beige": [255, 212, 170],
}


def DisplaySpokenColor(dom):
  global spokenColorLed_

  colors = json.loads(dom.getValue("PartnerColors"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS_:
      ucuq.sleepStart()
      ring_.setValue(spokenColorLed_, ((255, 255, 255))).write()
      r, g, b = map(
        lambda c: RGB_MAX_ * int(c) // 255, [c for c in SPOKEN_COLORS_[color]]
      )
      ucuq.sleepWait(0.05)
      ring_.setValue(spokenColorLed_, (r, g, b)).write()
      ravel_.displayRingGauges()
      y = spokenColorLed_ % 8 * 8
      oled_.rect(0, y, 128, 8, 0, True).rect(0, 0, 8, 64, 0, True).text(
        color, 64 - 8 * len(color) // 2, y
      )
      if spokenColorLed_ >= 8:
        oled_.text(">", 0, y).show()
      oled_.show()
      spokenColorLed_ += 1
      break


def DisplayOrientation(values):
  x, y, z = (float(value) for value in values.split(","))
  
  ring_.fill((0,0,0)).write()

  lcd_.backlightOn().moveTo(0, 0).putString(f"{f"{int(z):+3d} {int(x):4d} {int(y):+4d}".center(16)}".ljust(32))

  oled_.draw(cube.draw3DCube(x, y, z), 128).show()


def Listen(dom):
  if spokenColorLed_ == 0:
    lcd_.backlightOn()
    ring_.fill((0, 0, 0)).write()
    oled_.fill(0).show()
  dom.executeVoid("partnerListen()")


def fusion_espaces(s1: str, s2: str) -> str:
  i = 0
  while i < len(s2) and s2[i] == " ":
    i += 1

  if i >= len(s1):
    return s1 + s2[len(s1) :]
  else:
    return s1 + s2.lstrip()


DELAY_TEXT_ = 0.2
DELAY_WAVE_ = 0.1


def LCD():
  lcd_.uploadGaugeChars().backlightOn().showCursor().moveTo(0, 0)

  lcd_.ttyWrite(LINE1_ + LINE2_, DELAY_TEXT_)

  wave2 = ""

  for i in range(8):
    wave2 = chr(i) + wave2
    lcd_.moveTo(0, 1).putString(fusion_espaces(wave2, LINE2_)[:16])
    ucuq.sleep(DELAY_WAVE_)

  wave1 = ""

  for i in range(8):
    wave1 = chr(i) + wave1
    wave2 = chr(7) + wave2
    lcd_.putString(
      fusion_espaces(wave1, LINE1_)[:16] + fusion_espaces(wave2, LINE2_)[:16]
    )
    ucuq.sleep(DELAY_WAVE_)

  for i in range(7, -1, -1):
    wave1 = chr(i) + wave1
    wave2 = chr(7) + wave2
    lcd_.putString(fusion_espaces(wave1, LINE1_)[:16] + wave2[:16])
    ucuq.sleep(DELAY_WAVE_)

  for i in range(7, -1, -1):
    wave1 = " " + wave1
    wave2 = chr(i) + wave2
    lcd_.putString(wave1[:16] + wave2[:16])
    ucuq.sleep(DELAY_WAVE_)

  for i in range(16):
    wave1 = " " + wave1
    wave2 = " " + wave2
    lcd_.putString(wave1[:16] + wave2[:16])
    ucuq.sleep(DELAY_WAVE_)

  lcd_.backlightOff()
