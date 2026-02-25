import ucuq, zlib, base64, time

from shared import polyphonicPlay, RAINBOW

ring = None
buzzer = None
oled = None
lcd = None


def isConnected():
  return ring is not None


def connect(device):
  global ring, buzzer, oled, lcd
  ucuq.setDevice(device)

  ring = ucuq.Ravel.Ring()
  buzzer = ucuq.Ravel.Buzzer()
  oled = ucuq.Ravel.OLED()
  lcd = ucuq.Ravel.LCD()


SONG_ = """
E44. F43
G44 C55. -C54 R3 D44. E43
F46 F44 R4 G44. A43
B44 F55. -F54 R3 A44. B43
C55 D55 E54 -E53 R3 E44. F43
G44 C55. -C54 R3 D54. E53
F56 R55 G44 -G42. R1 G43
E55 D54 R3 G43 E55 D54 R3 G43
E55 D54 R3 G43 F55 E54. D53
C56
"""
LINE1_ = "Un monde nouveau"
#       "1234567890123456"
LINE2_ = "pour nos enfants"

GIRL_ = """000000000000018000000000000003e000000000000007f0000000000001e7e0000000000007fef000000000001ffc7800000000001ffe7800000000003fff3c00000000007fffbc0000000000fffff80000000001fffff80000000001fffff80000000000bffff80000000000bff7f800000000001ff7f800000000001ff7f800000000000ffe7800000000000fff7800000000000fff3c000000000007ff9c000000000003ffce000000000001dfce0000000000000fcf00000000000007ff0000000000000fff0000000000001fff0000000000003fff0000000000007fff0000000000007fff0000000000007fff000000000000dfff000000000000bfff000000000000bfff0000000400007fff0000001f0000ffff000000078000ffff00000001e0019fff00000001f801dfff00000000fe01ffff0000003cffc1ffff0000007ffdc1dfff0000007ffe40dfff000000ffff02dfff0000007fffc3dffd0000007ffffbdfff0000003ffffffdfe0000003fffffcffb0000001fffdfcffb0000000fffefcffd00000007fff3cefe00000003fffbfffd00000001fffdfffb00000000fffefff3000000007fff7ff1000000003fff7ff9000000003bff7ff1000000007dfffff00000001ffeffffe00000003fff7fffe00000007fffbfffc00000007fffdfffc00000003fff8fff800000000fff03ff00000000000000c000"""

BOY_ = """0000000000000000000000000000000001f800000000000003fc0000000000000ffe0000000000001fffe000000000001ffff000000000001ffff000000000003ffff000000000003fffc000000000003fffe000000000003fff8000000000003fff8000000000001fff8000000000001fff8000000000001fff0000000000001fff0000000000001fff0000000000007ffe0000000000007ffe000000000000fffc000000000000ff98000000000000ff80000000000000ffc0000000000000ffc0000000000000ffe0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000f7f0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000fff0000000000000f3f0000000000000f3f0000000000000f7f0000000000000fff8000200000000fbf8000700000000fff0001f80000000fff8003f00000000fffc007e000000007ffe01f800000000bfff03f000000000feff87e000000000ffffdfe000000000ffffffc000000000ffffffc000000000ffffff8000000000fffffff800000000fffffffff0000000fffffffffc000000fffffffffe000000fffffffffe0000007fffffffff0000003fffffffff0000001ffffffffe0000000ffffffff800000007e1ff00000000000f00300000000000"""

def hexImageToBytearray_(hex_string, width=128, height=64):
  bits = []
  for c in hex_string:
    nibble = int(c, 16)
    bits.append((nibble >> 3) & 1)
    bits.append((nibble >> 2) & 1)
    bits.append((nibble >> 1) & 1)
    bits.append(nibble & 1)

  pages = height // 8
  out = bytearray(width * pages)

  for page in range(pages):
    for x in range(width):
      byte = 0
      for bit in range(8):
        y = page * 8 + bit
        pixel = bits[y * width + x]
        byte |= pixel << bit
      out[page * width + x] = byte

  return out


def concatHEXImages_(img1: str, img2: str) -> str:
  result_lines = []

  for row in range(64):
    line1 = img1[row * 16 : (row + 1) * 16]
    line2 = img2[row * 16 : (row + 1) * 16]
    result_lines.append(line1 + line2)

  return "".join(result_lines)


def compressToString_(data: bytearray) -> str:
  compressed = zlib.compress(bytes(data), level=9, wbits=9)
  return base64.b64encode(compressed).decode("ascii")


def getDuration(events):
  duration  = 0
  
  for event in events:
    duration += event[1]
    
  return duration


def callback_(_, events, duration):
  ucuq.sleepStart()
  
  for event in events:
    if event[0] == 0:
      
      if event[1] == 0:
        buzzer.off()
      elif event[1] > 0:
        buzzer.on(event[1])
    elif event[0] == 1:
      if event[1][1] == "":
        lcd.showCursor()
      lcd.moveTo(*event[1][0]).putString(event[1][1])
    elif False and event[0] == 2:
      ucuq.addCommand(f'{oled.getObject()}.buffer = ubinascii.a2b_base64("{event[1]}")')
      oled.show()
    elif event[0] == 3:
      ring.setValue(event[1][0], event[1][2]).setValue(event[1][1], event[1][2]).write()
      
  if duration > .05:
    ucuq.commit()

  ucuq.sleepWait(duration)
  
SCRIPT_ = """
import _thread
import time

class MelodyPlayer:
    def __init__(self, pwm):
        self.pwm = pwm
        self._thread_id = None
        self._stop_flag = False
        self.on_ = False

    def _play_melody(self, melody):
        for freq, duration in melody:
            if self._stop_flag:
                break

            if freq <= 0:
                if self.on_:
                  self.pwm.duty_u16(0)
                  self.on_ = False
            else:
                self.pwm.freq(freq)
                if not self.on_:
                  self.pwm.duty_u16(32768)  # 50% duty cycle
                  self.on_ = True

            time.sleep(duration)

        # Arrêt propre du PWM
        self.pwm.duty_u16(0)
        self._thread_id = None
        self._stop_flag = False

    def play(self, melody):
        if self._thread_id is not None:
            self.stop()
            time.sleep(0.05)

        self._stop_flag = False
        self._thread_id = _thread.start_new_thread(self._play_melody, (melody,))

    def stop(self):
        self._stop_flag = True
        
player = MelodyPlayer({})
"""

def oledAnim():
  ucuq.addCommand("import ubinascii")
  oled.powerOn()
  for c in range(64):
    toDraw = concatHEXImages_(
      ("0" * 16 * (63 - c) + GIRL_)[:1024],
      (BOY_[16 * (63 - c) :] + "0" * 1024)[:1024],
    )
    
    ucuq.addCommand(f'{oled.getObject()}.buffer = ubinascii.a2b_base64("{base64.b64encode(hexImageToBytearray_(toDraw)).decode("ascii")}")')
    oled.show()
    
def launch(withSound):
  ringOffset = int(time.time()) % len(RAINBOW)
  ring.flash()
  lcd.clear().backlightOff()
  oled.powerOff()

  if withSound:
    polyEvents = ucuq.polyPhonicToEvents((SONG_,), 260)
    duration = getDuration(polyEvents[0])
  else:
    polyEvents = [[(0,0)]]
    duration = 5
  
#  ucuq.addCommand(SCRIPT_.format(buzzer.PWM().getObject()))
  
  
  line1 = 15 * " " + LINE1_.center(16)
  line2 = 15 * " " + LINE2_.center(16)
  
  lcdEvents = []
  
  for l in range(64):
    if l // 16 == 0:
      event = ((0,0), line1[l % 16 :][:16])
    elif l // 16 == 1:
      event = ((0,1), line2[l % 16 :][:16])
    elif withSound and l // 16 == 2:
      event = ((l %16 ,0), "")
    elif withSound and l // 16 == 3:
      event = ((l % 16,1), "")

    if withSound or l < 32:
      lcdEvents.append((event, duration / ( 32 * ( 1 + withSound))))
      
  polyEvents.append(lcdEvents)
  
  ringEvents = []
  
  ringCount = 200 if withSound else 50

  for c in range(ringCount):
    ringEvent = (c, ringCount - c, RAINBOW[(c + ringOffset) % len(RAINBOW)])
    ringEvents.append((ringEvent, duration / ringCount))
  
  oledEvents = []

  for c in range(64):
    toDraw = concatHEXImages_(
      ("0" * 16 * (63 - c) + GIRL_)[:1024],
      (BOY_[16 * (63 - c) :] + "0" * 1024)[:1024],
    )
    
#    oledEvent = compressToString_(hexImageToBytearray_(toDraw))
    oledEvent = base64.b64encode(hexImageToBytearray_(toDraw)).decode("ascii")
    oledEvents.append((oledEvent, duration / 64))

  polyEvents.append(oledEvents)
  polyEvents.append(ringEvents)

  ringOffset = int(time.time()) % len(RAINBOW)
      
#  ucuq.addCommand(f"player.play({polyEvents[0]})")

  oledAnim()
  
  ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  lcd.backlightOn()

  ucuq.polyeventPlay(polyEvents, callback_)
  
  ucuq.setCommitBehavior(ucuq.CB_AUTO)
  
  lcd.hideCursor()
  
  for l in range(8):
    ring.setValue(
      l, RAINBOW[(ringOffset + l * (len(RAINBOW) - 1) // 7) % len(RAINBOW)]
    ).write()
  