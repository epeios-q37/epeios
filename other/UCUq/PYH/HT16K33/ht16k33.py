import os, sys, time, binascii

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("../..","../../atlastk.zip"))

import ucuq, atlastk

onDuty = False
matrix = None

pattern = "0" * 32

with open('Head.html', 'r') as file:
  HEAD = file.read()

with open('Body.html', 'r') as file:
  BODY = file.read()

TEST_DELAY = 0.05

def test():
  if matrix:
    for y in range(8):
      for x in range(16):
        matrix.plot(x,y)
      matrix.commit()
      ucuq.sleep(TEST_DELAY)
      matrix.clear()

    for x in range(16):
      for y in range(8):
        matrix.plot(x,y)
      matrix.commit()
      ucuq.sleep(TEST_DELAY)
      matrix.clear()

    for x in range(16):
      for y in range(8):
        matrix.plot(x,y)

    matrix.commit()

    for b in range(0, 16):
      matrix.setBrightness(b)
      ucuq.sleep(TEST_DELAY)

    for b in range(15, -1, -1):
      matrix.setBrightness(b)
      ucuq.sleep(TEST_DELAY)

    matrix.clear().commit()
    ucuq.commit()


def drawOnGUI(dom, motif = pattern):
  html = ""

  for i, c in enumerate(motif.ljust(32,"0")):
    for o in range(4):
      on = int(c, 16) & (1 << (3 - o)) != 0
      html += f"<div class='led{ '' if on else ' off'}' xdh:onevent='Toggle' data-state='{'on' if on else 'off'}' xdh:mark='{(i % 4) * 4 + o} {i >> 2}'></div>"

  dom.inner("Matrix", html)


def drawLittleMatrix(motif):
  html = ""

  for i, c in enumerate(motif.ljust(32,"0")):
    for o in range(4):
      on = int(c, 16) & (1 << (3 - o)) != 0
      html += f"<div class='little-led{ '' if on else ' little-off'}'></div>"

  return html


def drawLittleMatrices(dom, matrices):
  html = ""

  for i, matrix in enumerate(matrices):
    html += f"<fieldset xdh:mark=\"{i}\" style=\"cursor: pointer;\" class=\"little-matrix\" xdh:onevent=\"Draw\">"\
      + drawLittleMatrix(matrix)\
      +"</fieldset>"

  dom.inner("MatricesBox", html)


def setHexa(dom, motif = pattern):
  dom.setValue("Hexa", motif)


def drawOnMatrix(motif = pattern):
  if matrix:
    matrix.draw(motif).commit()

    ucuq.commit()

def draw(dom, motif = pattern):
  global pattern

  pattern = motif
  
  drawOnMatrix(motif)

  drawOnGUI(dom, motif)

  setHexa(dom, motif)


def updateUI(dom, onDuty):
  ids = ["MatrixBox", "HexaBox", "MiscBox", "MatricesBox"]

  if onDuty:
    dom.enableElements(ids)
    dom.disableElement("HardwareBox")
    dom.setValue("Switch", "true")
  else:
    dom.disableElements(ids)
    dom.enableElement("HardwareBox")
    dom.setValue("Switch", "false")

    match dom.getValue("Preset"):
      case "User":
        dom.enableElements(["SDA", "SCL"])
      case "Bipedal":
        dom.setValues({
          "SDA": 4,
          "SCL": 5
        })
        dom.disableElements(["SDA", "SCL"])
      case _:
        raise Exception("Unknown preset!")
        

def acConnect(dom):
  label = ucuq.handleATK(dom)

  dom.inner("", BODY)

  draw(dom, "")

  dom.executeVoid("patchHexaInput();")

  drawLittleMatrices(dom,MATRICES)

  if not onDuty:
    match label:
      case "Freenove.Robot.Bipedal.RPIPicoW":
        dom.setValue("Preset", "Bipedal")

  updateUI(dom, onDuty)

def acPreset(dom, id):
  match dom.getValue("Preset"):
    case "User":
      dom.setValues({
        "SDA": "",
        "SCL": ""
      })
    case "Bipedal":
      pass
    case _:
      raise Exception("Unknown preset!")
    
  updateUI(dom, False)


def launch(dom, sda, scl):
  global matrix, onDuty

  try:
    matrix = ucuq.HT16K33(sda, scl)
    matrix.clear().commit()
    matrix.setBrightness(0)
    matrix.setBlinkRate(0)
    ucuq.commit()
  except Exception as err:
    dom.alert(err)
    onDuty = False
  else:
    onDuty = True


def acSwitch(dom, id):
  global onDuty

  state = dom.getValue(id) == "true"

  if state:
    updateUI(dom, state)

    try:
      sda, scl = (int(value.strip()) for value in dom.getValues(["SDA", "SCL"]).values())
    except:
      dom.alert("No or bad value for SDA/SCL!")
      updateUI(dom, False)
    else:
      launch(dom, sda, scl)
  else:
    onDuty = False

  updateUI(dom, onDuty)


def plot(x,y,ink=True):
  if matrix:
    matrix.plot(x,y)
    matrix.commit()


def clear():
  if matrix:
    matrix.clear()


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

  drawOnMatrix(motif := dom.getValue("Hexa"))

  drawOnGUI(dom, motif)

  pattern = motif


def acAll(dom):
  for matrix in MATRICES:
    draw(dom, matrix)
    time.sleep(0.5)


def acBrightness(dom, id):
  matrix.setBrightness(int(dom.getValue(id)))
  ucuq.commit()

def acBlinkRate(dom, id):
  matrix.setBlinkRate(float(dom.getValue(id)))
  ucuq.commit()

def acDraw(dom, id):
  draw(dom,MATRICES[int(dom.getMark(id))])

CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Test": lambda: test(),
  "All": acAll,
  "Toggle": acToggle,
  "Brightness": acBrightness,
  "Blink": acBlinkRate,
  "Hexa": acHexa,
  "Draw": acDraw
}

MATRICES = (
  "0FF0300C4002866186614002300C0FF",
  "000006000300FFFFFFFF030006",
  "00004002200410080810042003c",
  "0000283810282838000000400040078",
  "081004200ff01bd83ffc2ff428140c3",
  "042003c004200c300ff007e00db",
  "0420024027e42db43ffc18180a50042",
  "0420024007e00ff02bd41ff824241bd8",
  "0300030009c007a0018002600fc0048",
  "08800f800a8007100210079007d00be",
  "02000e000e1003e003e003e00220066",
  "06001a000e000f000ff00fe00f8002",
  "024001800fe01850187018500ff00fe",
  "038004400960041004180408021001e",
  "000003c0042005a005a0042003c",
  "03c0042009900a500a5009e0040803f",
  "239f6441204223862401241177ce",
  "43dc421242124392421242127bdc",
  "00003c3c727272727e7e7e7e3c3c",
  "00003ffc40025ffa2ff417e8081007e",
)

atlastk.launch(CALLBACKS, headContent=HEAD)
