import os, sys, time, io, json, datetime, binascii

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("..","../../atlastk"))

import mcrcq, atlastk

pattern = "0" * 32

with open('Head.html', 'r') as file:
  HEAD = file.read()

with open('Body.html', 'r') as file:
  BODY = file.read()

with open('mc_init.py', 'r') as file:
  INIT = file.read()


def drawMatrix(dom, motif = pattern):
  html = ""

  for i, c in enumerate(motif.ljust(32,"0")):
    for o in range(4):
      on = int(c, 16) & (1 << (3 - o)) != 0
      html += f"<div class='led{ '' if on else ' off'}' xdh:onevent='Toggle' data-state='{'on' if on else 'off'}' xdh:mark='{(i % 4) * 4 + o} {i >> 2}'></div>"

  dom.inner("Matrix", html)


def setHexa(dom, motif = pattern):
  dom.setValue("Hexa", motif)


def drawOnDevice(dom, motif = pattern):
  mcrcq.execute(f"matrix.clear().draw('{motif}').render()")



def draw(dom, motif = pattern):
  global pattern

  pattern = motif
  
  drawOnDevice(dom, motif)

  drawMatrix(dom, motif)

  setHexa(dom, motif)


def acConnect(dom):
  dom.inner("", BODY)

  draw(dom, "")

  dom.executeVoid("patchHexaInput();")


def plot(x,y,ink=True):
  mcrcq.execute(f"matrix.plot({x},{y},{1 if ink else 0}).render()")


def clear():
  mcrcq.execute(f"matrix.clear()")


def acToggle(dom, id):
  global pattern

  [x, y] = list(map(lambda v: int(v), dom.getMark(id).split()))

  pos = y * 16 + ( 4 * int(x / 4) + (3 - x % 4)) 

  bin = binascii.unhexlify(pattern.ljust(32,"0")[::-1].encode())[::-1]

  offset = int(pos/8)

  bin = bin[:offset] + bytearray([bin[offset] ^ (1 << (pos % 8))]) + bin[offset+1:]

  pattern = (binascii.hexlify(bin[::-1]).decode()[::-1])

  plot(x, y,  bin[offset] & (1 << (pos % 8)))

  draw(dom, pattern)


def acHexa(dom):
  global pattern

  drawOnDevice(dom, motif := dom.getValue("Hexa"))

  drawMatrix(dom, motif)

  pattern = motif


def acMotif(dom):
  draw(dom, "0FF0300C4002866186614002300C0FF")
  time.sleep(1)
  draw(dom, "000006000300FFFFFFFF030006")
  time.sleep(1)
  draw(dom, "00004002200410080810042003c")
  time.sleep(1)
  draw(dom, "0000283810282838000000400040078")
  time.sleep(1)
  draw(dom, "081004200ff01bd83ffc2ff428140c3")
  time.sleep(1)
  draw(dom, "042003c004200c300ff007e00db0")
  time.sleep(1)
  draw(dom, "0420024027e42db43ffc18180a50042")
  time.sleep(1)
  draw(dom, "0420024007e00ff02bd41ff824241bd8")
  time.sleep(1)
  draw(dom, "0300030009c007a0018002600fc00480")
  time.sleep(1)
  draw(dom, "08800f800a8007100210079007d00be0")
  time.sleep(1)
  draw(dom, "02000e000e1003e003e003e002200660")
  time.sleep(1)
  draw(dom, "06001a000e000f000ff00fe00f800200")
  time.sleep(1)
  draw(dom, "024001800fe01850187018500ff00fe0")
  time.sleep(1)
  draw(dom, "038004400960041004180408021001e0")
  time.sleep(1)
  draw(dom, "000003c0042005a005a0042003c")
  time.sleep(1)
  draw(dom, "00003ffc40025ffa2ff417e8081007e")
  return
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")
  time.sleep(1)
  draw(dom, "")



CALLBACKS = {
  "": acConnect,
  "Test": lambda: mcrcq.execute("test()"),
  "Motif": acMotif,
  "Toggle": acToggle,
  "Brightness": lambda dom, id: mcrcq.execute(f"matrix.set_brightness({dom.getValue(id)})"),
  "Blink": lambda dom, id: mcrcq.execute(f"matrix.set_blink_rate({dom.getValue(id)})"),
  "Hexa": acHexa
}

mcrcq.connect()

mcrcq.execute(INIT)

atlastk.launch(CALLBACKS, headContent=HEAD)
