import random
import show
import ucuq
import time

from types import SimpleNamespace

import shared

from show import devices, sleep
from shared import RAINBOW

prev = 0

def callback_(helper, events, duration):
  global prev
  sleep(helper.timestamp)

  helper.timestamp += duration
  
  for event in events:
    if event[1] == 0:
      devices.buzzers.off()
    elif event[1] > 0:
      devices.buzzers.on(event[1])
      if prev != event[1]:
          prev = event[1]
          helper.led += 1    
          devices.rgbs.setValue(helper.led, RAINBOW[helper.led % len(RAINBOW)]).write()
          devices.rgbs.setValue(helper.led + 1,(0,0,0)).write()
  
  
def launch(timestamp):
  devices.oleds.draw(INDY_, 128).show()
  helper = SimpleNamespace(pantherPict = 0, led = random.randrange(len(RAINBOW)))
  
  helper.start = helper.timestamp = timestamp + 1
  helper.gcTimestamp = None
  
  shared.polyphonicPlay(VOICES_, 260, helper, callback_)

  TEXT = " " * 14 + "That's all folks!" + " " * 16

  devices.lcds.backlightOn()
  
  devices.oleds.hline(0, 0, 128, 0)

  for i in range(64):
    devices.rgbs.setValue(((helper.led + (i // 8)) % 8),(0,0,0)).write()
    devices.oleds.scroll(0, 1).show()
    devices.lcds.moveTo(0,0).putString(TEXT[i//2:i//2+16])
    helper.timestamp += 0.07
    sleep(helper.timestamp)

  devices.oleds.fill(0).show()
  devices.lcds.backlightOff()
  devices.rgbs.fill((0, 0, 0)).write()
  
  return helper.timestamp


INDY_ = "00000000000001a011416b3fb01ffffb00000000000011804403feef603ffff70000000000000164108aabbf802fd7fd00000000000002b04500fdde8002f7fd000000000000005a1081ffbe00004bfe00000000000014bc040f76d100000fff000000000000412f92805fda00002fff00000000000016bde800bfd800002bff000000000004a82df50003e2009637bf00000000000957fcf00001f401873fff00000000000000000000007e81eebfff00000000000000000000003747eddfff00000000000000000000000ffa0b7fff00000000000000000000001d782fffff00000000000000000000002dbc0fffff00000000000000000000019ed4ffffff000000000000000000000116ed7fffff00000000000000000000018f7abfffff000000000000000000002217bf57ff7f0000000009444000000032176fde7fff0000000bffffffc00300014fbbf1ff7d00000021ff5dfff00000021f6eaffdfb000000005a800ff8000000cfd7ffff7d000000002c000bfc0000011f79fffadf00000000140001fc0000024fd47fff7b000000002e0002fe0000085ffe7ffddf000000000f0201fe000000affd1ffbb70000001d1f8a5cff4000013ffb1ffeef0000001f8fd73eff2010122fe04fffaf000001be97e3ffff900c081f8067ff7f000000f98bfdffff670210800e71ffdf0000214e2bffffffef8005001afbfbff000010bf91ffffffff8002801ffabfff000005fe15ffffffff8005801dfc6fff000052bd92ffffffff8000801f7fbfff000004ea28ffffffff8001c08cdaffff002013db14ffffffff80026004455fff001805ae78ffffffff8001c004407fff00080a7e3c7fffffff80006000203fff0018111830ffffffff80215007f00fff00180278007bffffff80908074020fff00180aa0003cffffff800020a1ffc7ff001c0070001effffff80500007fdf7ff001804c403fd7fffff8504007fd2fbff0014014203febfffff005000e00bffff001002a912ff7fffffa484000007ffff000c00540affbfffff001200022fffff001a02c023ffffffff2140800a9fffff00040150097fdfffbe041540007ffffd001a02c0a3ffffffdc41006015fffffb0000016015ffffff900822a300fffff000000180003fffff85028827cbffffc0000000800007ffff90502247edffffe0000001a00001ffff84040027fbffff800000008001387fff0112a947ffffff8000000114adffbfff10400017fdfffc00400000402fffffff000a494bffffff000000008adffffffe4140000bfffff00000000010003ffffe040aa955fffff8000000004a001ffffc01000003ffffc00280000020000ffffc00555554fff600010000001255f7fffc240000017ff8000b400000289ffffffc80aaaaaa96f0000b000000022ffffff8000000004a080007"

VOICES_ = ("""
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
""",)
