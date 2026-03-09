import time

import ucuq

import shared

from shared import RAINBOW as RAINBOW_, getRainbowColor as getRainbowColor_

ring_ = None
buzzer_ = None
oled_ = None
lcd_ = None


def connect(device):
  global ring_, buzzer_, oled_, lcd_
  ucuq.setDevice(shared.handleDeviceInput(device))

  ring_ = ucuq.Ravel.Ring()
  buzzer_ = ucuq.Ravel.Buzzer()
  oled_ = ucuq.Ravel.OLED()
  lcd_ = ucuq.Ravel.LCD()
  
  lcd_.uploadJaugeChars()


LINE1_ = "Un smartphone"
#        "1234567890123456"
LINE2_ = "et c'est parti !"

GIRL_ = """000000000000018000000000000003e000000000000007f0000000000001e7e0000000000007fef000000000001ffc7800000000001ffe7800000000003fff3c00000000007fffbc0000000000fffff80000000001fffff80000000001fffff80000000000bffff80000000000bff7f800000000001ff7f800000000001ff7f800000000000ffe7800000000000fff7800000000000fff3c000000000007ff9c000000000003ffce000000000001dfce0000000000000fcf00000000000007ff0000000000000fff0000000000001fff0000000000003fff0000000000007fff0000000000007fff0000000000007fff000000000000dfff000000000000bfff000000000000bfff0000000400007fff0000001f0000ffff000000078000ffff00000001e0019fff00000001f801dfff00000000fe01ffff0000003cffc1ffff0000007ffdc1dfff0000007ffe40dfff000000ffff02dfff0000007fffc3dffd0000007ffffbdfff0000003ffffffdfe0000003fffffcffb0000001fffdfcffb0000000fffefcffd00000007fff3cefe00000003fffbfffd00000001fffdfffb00000000fffefff3000000007fff7ff1000000003fff7ff9000000003bff7ff1000000007dfffff00000001ffeffffe00000003fff7fffe00000007fffbfffc00000007fffdfffc00000003fff8fff800000000fff03ff00000000000000c000"""

BOY_ = """0000000000000000000000000000000001f800000000000003fc0000000000000ffe0000000000001fffe000000000001ffff000000000001ffff000000000003ffff000000000003fffc000000000003fffe000000000003fff8000000000003fff8000000000001fff8000000000001fff8000000000001fff0000000000001fff0000000000001fff0000000000007ffe0000000000007ffe000000000000fffc000000000000ff98000000000000ff80000000000000ffc0000000000000ffc0000000000000ffe0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000f7f0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000f3f0000000000000f3f0000000000000f7f0000000000000fff8000200000000fbf8000700000000fff0001f80000000fff8003f00000000fffc007e000000007ffe01f800000000bfff03f000000000feff87e000000000ffffdfe000000000ffffffc000000000ffffffc000000000ffffff8000000000fffffff800000000fffffffff0000000fffffffffc000000fffffffffe000000fffffffffe0000007fffffffff0000003fffffffff0000001ffffffffe0000000ffffffff800000007e1ff00000000000f00300000000000"""

INDY_ = """000000000004001100000000000c008200000000000340080000000000018082000000000002d0080000000000016082000000000002b828000000000010b60200000000000abbc80000000005e952a000000000100abbc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000d7dba00004000017ffffff8006000000b6013fc000000000600017f00000000008000bf000000000380007f8000000000e0001f8000000103e0433fc0000005e1f2c79fd0000003e2f8ffffe4000037917e3fffe8800008617fffffe9e00215d23fffffefe00057c2bfffffffe00437541fffffffe0008d411ffffffff0003a429fffffffe20055c61fffffffe10145c71fffffffe1002b061f7fffffe10083000f7fffffe3002e000fbfffffe380040007cfffffe3005480629fffffe10009407fd7ffffe10028005fcfffffe0800a815ff3ffffc18028047ff7ffffc10008001ffbffff808034046bfffff7000008013ffffff00000300007ffffe08000080000dfffe020001000003fffe000001800020fffe0000000957fe7ffc000001002fffbffc000000215ffffff800000004007ffff800000040003ffff002000028002ffff80000000055dffff0000000249fffffb0000000003feffff000"""

FATHER_ = """01d5b7e0107ff22f057d5ec07ffffd6e0bd5bd01ffffc6dc055afa003f3bebf901eb380005d7f7f90dfef400023ff7ff0aa94000001ffbff017f4800007ff9ff005b0000008fffff000f800411aafbf80005e8061cffffff0000f80feafeffff0000dd1a36ffffff000036c0abfdffff000035f01effffff000274a0bf7fffff00045f55fdfdffff000439a2ff7ffffc00062eeabffdffff00883afc5ffdffff00411ebff1f7ffff0004756d0ffddfff00011dbaffeb67ff00047eafffd5ffff00093d53ffb6bfff0010bea9ffebdfff00027fe8fdd6dfff0000bff47f753fff4044bb823fdadfff20107e012ef57fff1840081297feffff000a0075cfdeffff0008006bebf77fff0006007fe2ffffff000a006dfbb7ffff000302336affffff00050032157fffff0003800001ffffff00054001017fffff0002001f807fffff00408090007fffff010003817e3ffffb0000001fff9fffff012000bf4adffff7080003800defffff812000002ffeffef000000005fffffbf024a000abfffff7f080100217ffffd7f00098047ffffe17f20828803ffff807f04009e2ffffe007f00209fb7ffff00ff11041faffffe00ff40011feffff801ff00405fffffe801ff12092ff7fff003ff40000fffff8003ff008257fff7c007ff040007ffbf000fff5124abfff0002fff0000017bc0004fe7254a4aad40001c000000002000003800"""


def concatHEXImages_(img1: str, img2: str) -> str:
  result_lines = []

  for row in range(64):
    line1 = img1[row * 16 : (row + 1) * 16]
    line2 = img2[row * 16 : (row + 1) * 16]
    result_lines.append(line1 + line2)

  return "".join(result_lines)


def getDuration_(events):
  duration  = 0
  
  for event in events:
    duration += event[1]
    
  return duration


def lcdsDisplayRings(lcdsAndRings):
  for lcdAndRing in lcdsAndRings:
    lcdAndRing[0].displayRing(lcdAndRing[1], shared.RGB_MAX)


def oledAnimation_():
  oled_.powerOn()
  for c in range(64):
    toDraw = concatHEXImages_(
      ("0" * 16 * (63 - c) + INDY_)[:1024],
      (FATHER_[16 * (63 - c) :] + "0" * 1024)[:1024],
    )
    
    oled_.draw(toDraw, 128)
    oled_.show()
    

def indy(withSound = True):
  ringOffset = int(time.time())
  ring_.flash()
  lcd_.clear().backlightOff()
  oled_.powerOff()
  
  if withSound:
    polyEvents = ucuq.voicesToEvents(shared.INDY_VOICES, shared.INDY_TEMPO, lambda freq: buzzer_.off() if freq == 0 else buzzer_.on(freq) if freq > 0 else None)
    duration = getDuration_(polyEvents[0])
  else:
    polyEvents = [[(lambda: buzzer_.off(),0)]]
    duration = 5
  
  ringEvents = []
  
  ringCount = 200 if withSound else 50

  lcdsAndRings = []
  
  if isinstance(lcd_, ucuq.Multi ):
    for lcd, ring in zip(lcd_, ring_):
      lcdsAndRings.append((lcd, ring))  
  else:
    lcdsAndRings.append((lcd_, ring_))    

  for c in range(ringCount):
    ringEvents.append((
      lambda c=c, color=getRainbowColor_(c + ringOffset), ringCount=ringCount:
        (ring_.setValue(c, color).setValue(ringCount - c, color).write(), lcdsDisplayRings(lcdsAndRings)),
      duration / ringCount))
  
  polyEvents.append(ringEvents)

  ringOffset = int(time.time())
      
  oledAnimation_()
  
  commitBehavior = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  lcd_.backlightOn()
  
  ucuq.sleepStart()  

  ucuq.playEvents(polyEvents, lambda duration: (ucuq.sleepWait(duration), ucuq.sleepStart(),  ucuq.commit() if duration > .05 else None))
  
  ucuq.setCommitBehavior(commitBehavior)
  
  lcd_.hideCursor()
  
  for i in range(8):
    ring_.setValue(i, getRainbowColor_(ringOffset + i, 7)).write()
    
  lcdsDisplayRings(lcdsAndRings)
  
  return True

  
BUZZER_VOICE = "C44 D43 E43 F43 G43 A43 B43 C55"
  

def Buzzer():
  buzzer = ucuq.Ravel.Buzzer()
  ucuq.playVoices((BUZZER_VOICE,), 170, lambda freq: buzzer.on(freq), lambda duration: ucuq.sleep(duration))
  
  
EYES_ = "0" * 32 * 64 + shared.unpack("""eJztUkG2wyAIvBLGRPQ4UeH+R/hjrETbLrr8i8yrqTIIOKD64ME/hvzg4yt/uGWBqWpf7bywk1EYa2W1Sme5/TkVojiuvFDcjk/bcaULCx2bRbxchXSe5/Dd5K9T35Obao+zqWC3YZ3GJ9Szg+4hJYJ28U4gguNO5RXxLCDx2+7iCYZ6huHvkcJHZyJE8EcxSUtGjU5oKJDPI1JIdSSEetJ4ex5xoYPr8JcE3pd95As4kKZkBdfGi1i8gAqTbqY4dCaWOhQKHnxWb/XiJnG1FkdYSOUWvDDHqclILA6vMofsWnfDCNiE8C3KFECXIckt5zwQ19utQQL/+Xqrh5dRZtJpHsY+mGEdtm9YBz7nd57fDQ8efOIPyTYK6w==""")
  
  
def OLED():
  oled = ucuq.Ravel.OLED()
  

  for y in range(64):
    oled.draw(EYES_[y * 32:][:2048], 128).show()
  

def Ring():
  ring = ucuq.Ravel.Ring()
  
  count = len(RAINBOW_) // 8
  
  delay = 5 / (count * 8)

  for i in range(count):
    for led in range(8):
      ring[led] = getRainbowColor_(i * 8 + led)
      ring.write()
      ucuq.sleep(delay)

  for led in range(8):
    ring[led] = getRainbowColor_(led, 7)
    ring.write()
    ucuq.sleep(delay)

      
  ucuq.sleep(1)

  ring.fill((0, 0, 0)).write()  
  
LINE1_ = "Surfez vers".center(16)  
#       "1234567890123456"
LINE2_ = "le futur !".center(16)

  
def fusion_espaces(s1: str, s2: str) -> str:
    i = 0
    while i < len(s2) and s2[i] == ' ':
        i += 1

    if i >= len(s1):
      return s1 + s2[len(s1):]
    else:
      return s1 + s2.lstrip()
    
    
DELAY_TEXT_ = 0.2
DELAY_WAVE_ = 0.1
    
def LCD():
  lcd = ucuq.Ravel.LCD().backlightOn()
  
  lcd.uploadJaugeChars()
  
  lcd.showCursor().ttyWrite(LINE1_ + LINE2_, DELAY_TEXT_)
  
  ucuq.sleep(0.5)
  
  wave2 = ""
  for i in range(8):
    wave2 = chr(i) + wave2
    lcd.moveTo(0,1).putString(fusion_espaces(wave2, LINE2_)[:16])
    ucuq.sleep(DELAY_WAVE_)
    
  wave1 = ""
    
  for i in range(8):
    wave1 = chr(i) + wave1
    wave2 = chr(7) + wave2
    lcd.putString(fusion_espaces(wave1, LINE1_)[:16] + fusion_espaces(wave2, LINE2_)[:16])
    ucuq.sleep(DELAY_WAVE_)
    
  for i in range(7, -1, -1):
    wave1 = chr(i) + wave1
    wave2 = chr(7) + wave2
    lcd.putString(fusion_espaces(wave1, LINE1_)[:16] + wave2[:16])
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
    
  lcd.backlightOff()
                