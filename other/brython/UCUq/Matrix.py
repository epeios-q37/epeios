import ucuq, atlastk, binascii

pattern = "0" * 32

async def drawOnGUI(dom, motif = pattern):
  html = ""

  for i, c in enumerate(motif.ljust(32,"0")):
    for o in range(4):
      on = int(c, 16) & (1 << (3 - o)) != 0
      html += f"<div class='led{ '' if on else ' off'}' xdh:onevent='Toggle' data-state='{'on' if on else 'off'}' xdh:mark='{(i % 4) * 4 + o} {i >> 2}'></div>"

  await dom.inner("Matrix", html)


def drawLittleMatrix(motif):
  html = ""

  for i, c in enumerate(motif.ljust(32,"0")):
    for o in range(4):
      on = int(c, 16) & (1 << (3 - o)) != 0
      html += f"<div class='little-led{ '' if on else ' little-off'}'></div>"

  return html


async def drawLittleMatrixes(dom, matrixes):
  html = ""

  for i, matrix in enumerate(matrixes):
    html += f"<fieldset xdh:mark=\"{i}\" style=\"cursor: pointer;\" class=\"little-matrix\" xdh:onevent=\"Draw\">"\
      + drawLittleMatrix(matrix)\
      +"</fieldset>"

  await dom.inner("LittleMatrixes", html)


async def setHexa(dom, motif = pattern):
  await dom.setValue("Hexa", motif)


def drawOnMatrix(motif = pattern):
  matrix.draw(motif)

async def draw(dom, motif = pattern):
  global pattern

  pattern = motif

  drawOnMatrix(motif)

  await drawOnGUI(dom, motif)

  await setHexa(dom, motif)


async def acConnect(dom):
  await dom.inner("", BODY)

  await draw(dom, "")

  await dom.executeVoid("patchHexaInput();")

  await drawLittleMatrixes(dom,MATRIXES)


async def acTest():
  for y in range(8):
    for x in range(16):
      matrix.plot(x,y)
    matrix.render()
    # time.sleep(.06)
    matrix.clear()

  for x in range(16):
    for y in range(8):
      matrix.plot(x,y)
    matrix.render()
    # time.sleep(.06)
    matrix.clear()

  for x in range(16):
    for y in range(8):
      matrix.plot(x,y)

  matrix.render()

  for b in range(0, 16):
    matrix.setBrightness(b)
    ucuq.render()
    # time.sleep(0.05)

  for b in range(15, -1, -1):
    matrix.setBrightness(b)
    ucuq.render()
    # time.sleep(0.05)

  matrix.clear()


def plot(x,y,ink=True):
  matrix.plot(x,y)
  matrix.render()

def clear():
  matrix.clear()


async def acToggle(dom, id):
  global pattern

  [x, y] = list(map(lambda v: int(v), (await dom.getMark(id)).split()))

  pos = y * 16 + ( 4 * int(x / 4) + (3 - x % 4))

  bin = binascii.unhexlify(pattern.ljust(32,"0")[::-1].encode())[::-1]

  offset = int(pos/8)

  bin = bin[:offset] + bytearray([bin[offset] ^ (1 << (pos % 8))]) + bin[offset+1:]

  pattern = (binascii.hexlify(bin[::-1]).decode()[::-1])

  plot(x, y,  bin[offset] & (1 << (pos % 8)))

  await draw(dom, pattern)


async def acHexa(dom):
  global pattern

  drawOnMatrix(motif := await dom.getValue("Hexa"))

  await drawOnGUI(dom, motif)

  pattern = motif


async def acAll(dom):
  for matrix in MATRIXES:
    await draw(dom, matrix)
    await ucuq.sleepAwait(1000)


async def acBrightness(dom, id):
  matrix.setBrightness(int(await dom.getValue(id)))
  ucuq.render()

async def acBlinkRate(dom, id):
  matrix.setBlinkRate(float(await dom.getValue(id)))
  ucuq.render()

async def acDraw(dom, id):
  await draw(dom,MATRIXES[int(await dom.getMark(id))])

MATRIXES = (
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


HEAD = """
<script>
  function patchHexaInput() {
    function isHex(c) {
      return (
      c !== undefined &&
      ((c >= 97 /* a */ && c <= 102) /* f */ ||
      (c >= 65 /* A */ && c <= 70) /* F */ ||
      (c >= 48 /* 0 */ && c <= 57)) /* 9 */
      )
    }

    document.getElementById('Hexa').addEventListener('keypress', function (e) {
      const key = e.which || e.keyCode;

      if (!isHex(key)) {
          e.preventDefault();
      }
    })
  }
</script>
<style>
  .matrix {
    width: 480px;
    height: 240px;
    background-color: black;
    border: 5px ridge gray;
    border-bottom: 5px groove gray;
    border-left: 5px groove gray;
  }

  .led {
    cursor:pointer;
    display: inline-block;
    margin: 5px;
    margin-bottom: 0px;
    width: 20px;
    height: 20px;
    border-radius: 10px;
    background-color: red;
    -webkit-box-shadow: 0px 0px 15px 5px rgba(255, 0, 0, .75);
    -moz-box-shadow: 0px 0px 15px 5px rgba(255, 0, 0, .75);
    box-shadow: 0px 0px 15px 5px rgba(255, 0, 0, .75);
  }

  .off{
    background-color: #222222;
    -webkit-box-shadow: 0px 0px 0px 0px rgba(255, 255, 190, .75);
    -moz-box-shadow: 0px 0px 0px 0px rgba(255, 255, 190, .75);
    box-shadow: 0px 0px 0px 0px rgba(255, 255, 190, .75);
  }

  .little-matrix {
    width: 96px;
    background-color: black;
    line-height: 1px;
    height: 52px;
  }

  .little-led {
    display: inline-block;
    margin-bottom: 0px;
    width: 6px;
    height: 4px;
    border-radius: 10px;
    background-color: red;
  }

  .little-off {
    background-color: #222222;
  }
</style>
"""

BODY = """
<fieldset>
  <fieldset style="display: flex; justify-content: center;;">
    <div class="matrix" id="Matrix"></div>
  </fieldset>
  <fieldset style="display: flex; justify-content: center;">
    <input xdh:onevent="input|Hexa" style="font-family: monospace;" id="Hexa" type="text" maxlength="32" minlength="32" size="32" pattern="[0-9a-fA-F]+">
  </fieldset>
  <fieldset style="display: flex; justify-content: space-evenly">
    <label style="display: flex; align-items: center;">
      <span>Brightness:&nbsp;</span>
      <input xdh:onevent="Brightness" type="range" min="0" max="15" value="0">
    </label>
    <label>
      <span>Blink:</span>
      <select xdh:onevent="Blink">
        <option value="0">None</option>
        <option value="0.5">0.5 Hz</option>
        <option value="1">1 Hz</option>
        <option value="2">2 Hz</option>
      </select>
    </label>
  </fieldset>
  <fieldset>
    <button xdh:onevent="Test">Test</button>
    <button xdh:onevent="All">All</button>
  </fieldset>
  <fieldset id="LittleMatrixes" style="display: grid; grid-template-columns: auto auto auto auto;">
  </fieldset>
</fieldset>
"""

CALLBACKS = {
  "": acConnect,
  "Test": acTest,
  "All": acAll,
  "Toggle": acToggle,
  "Brightness": acBrightness,
  "Blink": acBlinkRate,
  "Hexa": acHexa,
  "Draw": acDraw
}

ucuq.launch()

matrix = ucuq.HT16K33(4, 5)
matrix.clear()
matrix.setBrightness(0)
matrix.setBlinkRate(0)
ucuq.render()


atlastk.launch(CALLBACKS, headContent=HEAD)
