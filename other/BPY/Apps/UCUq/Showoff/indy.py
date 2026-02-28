import random
import types

import shared

from shared import RAINBOW as RAINBOW_
from show import devices as devices_, sleep as sleep_

prev = 0

def callback_(helper, events, duration):
  global prev
  sleep_(helper.timestamp)

  helper.timestamp += duration
  
  for event in events:
    if event[1] == 0:
      devices_.buzzers.off()
      prev = 0
    elif event[1] > 0:
      devices_.buzzers.on(event[1])
      if prev != event[1]:
        prev = event[1]
        helper.led += 1    
        devices_.rgbs.setValue(helper.led, RAINBOW_[helper.led % len(RAINBOW_)]).write()
        devices_.rgbs.setValue(helper.led + 1,(0,0,0)).write()
  
  
def launch(timestamp):
  devices_.oleds.draw(INDY_, 128).show()
  helper = types.SimpleNamespace(pantherPict = 0, led = random.randrange(len(RAINBOW_)))
  
  helper.start = helper.timestamp = timestamp + 1
  helper.gcTimestamp = None
  
  shared.playVoices(shared.INDY_VOICES, shared.INDY_TEMPO, helper, callback_)

  TEXT = " " * 14 + "That's all folks!" + " " * 16

  devices_.lcds.backlightOn()
  
  devices_.oleds.hline(0, 0, 128, 0)

  for i in range(64):
    devices_.rgbs.setValue(((helper.led + (i // 8)) % 8),(0,0,0)).write()
    devices_.oleds.scroll(0, 1).show()
    devices_.lcds.moveTo(0,0).putString(TEXT[i//2:i//2+16])
    helper.timestamp += 0.07
    sleep_(helper.timestamp)

  devices_.oleds.fill(0).show()
  devices_.lcds.backlightOff()
  devices_.rgbs.fill((0, 0, 0)).write()
  
  return helper.timestamp


INDY_ = "000000000004001101d5b7e0107ff22f00000000000c0082057d5ec07ffffd6e00000000000340080bd5bd01ffffc6dc0000000000018082055afa003f3bebf9000000000002d00801eb380005d7f7f900000000000160820dfef400023ff7ff000000000002b8280aa94000001ffbff000000000010b602017f4800007ff9ff00000000000abbc8005b0000008fffff0000000005e952a0000f800411aafbf800000000100abbc00005e8061cffffff00000000000000000000f80feafeffff00000000000000000000dd1a36ffffff0000000000000000000036c0abfdffff0000000000000000000035f01effffff0000000000000000000274a0bf7fffff000000000000000000045f55fdfdffff0000000000000000000439a2ff7ffffc000000000000000000062eeabffdffff000000000000000000883afc5ffdffff000000d7dba0000400411ebff1f7ffff000017ffffff80060004756d0ffddfff000000b6013fc00000011dbaffeb67ff000000600017f00000047eafffd5ffff00000008000bf00000093d53ffb6bfff000000380007f8000010bea9ffebdfff0000000e0001f80000027fe8fdd6dfff0000103e0433fc000000bff47f753fff00005e1f2c79fd004044bb823fdadfff00003e2f8ffffe4020107e012ef57fff00037917e3fffe881840081297feffff00008617fffffe9e000a0075cfdeffff00215d23fffffefe0008006bebf77fff00057c2bfffffffe0006007fe2ffffff00437541fffffffe000a006dfbb7ffff0008d411ffffffff000302336affffff0003a429fffffffe00050032157fffff20055c61fffffffe0003800001ffffff10145c71fffffffe00054001017fffff1002b061f7fffffe0002001f807fffff10083000f7fffffe00408090007fffff3002e000fbfffffe010003817e3ffffb380040007cfffffe0000001fff9fffff3005480629fffffe012000bf4adffff710009407fd7ffffe080003800defffff10028005fcfffffe812000002ffeffef0800a815ff3ffffc000000005fffffbf18028047ff7ffffc024a000abfffff7f10008001ffbffff8080100217ffffd7f08034046bfffff7000098047ffffe17f00008013ffffff0020828803ffff807f000300007ffffe0804009e2ffffe007f000080000dfffe0200209fb7ffff00ff0001000003fffe0011041faffffe00ff0001800020fffe0040011feffff801ff00000957fe7ffc0000405fffffe801ff0001002fffbffc0012092ff7fff003ff0000215ffffff80040000fffff8003ff000004007ffff800008257fff7c007ff000040003ffff002040007ffbf000fff000028002ffff8005124abfff0002fff00000055dffff0000000017bc0004fe70000249fffffb000254a4aad40001c000000003feffff0000000002000003800"

VOICES_ = ("""
E43. F42
G43 C54. -C53 R2 D43. E42
F45 F43 R3 G43. A42
B43 F54. -F53 R2 A43. B42
C54 D54 E53 -E52 R2 E43. F42
G43 C54. -C53 R2 D53. E52
F55 R54 G43 -G41. R0 G42
E54 D53 R2 G42 E54 D53 R2 G42
E54 D53 R2 G42 F54 E53. D52
C55
""",)
