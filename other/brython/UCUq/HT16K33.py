import ucuq, atlastk, binascii

onDuty = False
ht16k33 = None

pattern = "0" * 32

TEST_DELAY = 0.05

def test():
  if ht16k33:
    for y in range(8):
      for x in range(16):
        ht16k33.plot(x,y)
      ht16k33.show()
      ucuq.sleep(TEST_DELAY)
      ht16k33.clear()

    for x in range(16):
      for y in range(8):
        ht16k33.plot(x,y)
      ht16k33.show()
      ucuq.sleep(TEST_DELAY)
      ht16k33.clear()

    for x in range(16):
      for y in range(8):
        ht16k33.plot(x,y)

    ht16k33.show()

    for b in range(0, 16):
      ht16k33.setBrightness(b)
      ucuq.sleep(TEST_DELAY)

    for b in range(15, -1, -1):
      ht16k33.setBrightness(b)
      ucuq.sleep(TEST_DELAY)

    ht16k33.clear().show()
    ucuq.commit()


async def drawOnGUIAwait(dom, motif = pattern):
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


async def drawLittleMatricesAwait(dom, matrices):
  html = ""

  for i, matrix in enumerate(matrices):
    html += f"<fieldset xdh:mark=\"{i}\" style=\"cursor: pointer;\" class=\"little-matrix\" xdh:onevent=\"Draw\">"\
      + drawLittleMatrix(matrix)\
      +"</fieldset>"

  await dom.inner("MatricesBox", html)


async def setHexaAwait(dom, motif = pattern):
  await dom.setValue("Hexa", motif)


def drawOnMatrix(motif = pattern):
  if ht16k33:
    ht16k33.draw(motif).show()

    ucuq.commit()

async def drawAwait(dom, motif = pattern):
  global pattern

  pattern = motif
  
  drawOnMatrix(motif)

  await drawOnGUIAwait(dom, motif)

  await setHexaAwait(dom, motif)


async def updateUIAwait(dom, onDuty):
  ids = ["MatrixBox", "HexaBox", "MiscBox", "MatricesBox"]

  if onDuty:
    await dom.enableElements(ids)
    await dom.disableElement("HardwareBox")
    await dom.setValue("Switch", "true")
  else:
    await dom.disableElements(ids)
    await dom.enableElement("HardwareBox")
    await dom.setValue("Switch", "false")

    match await dom.getValue("Preset"):
      case "User":
        await dom.enableElements(["SDA", "SCL"])
      case "Bipedal":
        await dom.setValues({
          "SDA": 4,
          "SCL": 5
        })
        await dom.disableElements(["SDA", "SCL"])
      case _:
        raise Exception("Unknown preset!")
        

async def acConnect(dom):
  label = await ucuq.handleATKAwait(dom)

  await dom.inner("", BODY)

  await drawAwait(dom, "")

  dom.executeVoid("patchHexaInput();")

  await drawLittleMatricesAwait(dom,MATRICES)

  if not onDuty:
    match label:
      case "Freenove.Robot.Bipedal.RPIPicoW":
        await dom.setValue("Preset", "Bipedal")

  await updateUIAwait(dom, onDuty)

async def acPreset(dom, id):
  match await dom.getValue("Preset"):
    case "User":
      await dom.setValues({
        "SDA": "",
        "SCL": ""
      })
    case "Bipedal":
      pass
    case _:
      raise Exception("Unknown preset!")
    
  await updateUIAwait(dom, False)


async def launchAwait(dom, sda, scl):
  global ht16k33, onDuty

  try:
    ht16k33 = ucuq.HT16K33(ucuq.I2C(sda, scl))
    ht16k33.clear().show()
    ht16k33.setBrightness(0)
    ht16k33.setBlinkRate(0)
    ucuq.commit()
  except Exception as err:
    await dom.alert(err)
    onDuty = False
  else:
    onDuty = True


async def acSwitch(dom, id):
  global onDuty

  state = (await dom.getValue(id)) == "true"

  if state:
    await updateUIAwait(dom, state)

    try:
      sda, scl = (int(value.strip()) for value in (await dom.getValues(["SDA", "SCL"])).values())
    except:
      await dom.alert("No or bad value for SDA/SCL!")
      await updateUIAwait(dom, False)
    else:
      await launchAwait(dom, sda, scl)
  else:
    onDuty = False

  await updateUIAwait(dom, onDuty)


async def acTest():
  test()


def plot(x,y,ink=True):
  if ht16k33:
    ht16k33.plot(x,y)
    ht16k33.show()


def clear():
  if ht16k33:
    ht16k33.clear()


async def acToggle(dom, id):
  if not onDuty:
    return

  global pattern

  [x, y] = list(map(lambda v: int(v), (await dom.getMark(id)).split()))

  pos = y * 16 + ( 4 * int(x / 4) + (3 - x % 4)) 

  bin = binascii.unhexlify(pattern.ljust(32,"0")[::-1].encode())[::-1]

  offset = int(pos/8)

  bin = bin[:offset] + bytearray([bin[offset] ^ (1 << (pos % 8))]) + bin[offset+1:]

  pattern = (binascii.hexlify(bin[::-1]).decode()[::-1])

  plot(x, y,  bin[offset] & (1 << (pos % 8)))

  await drawAwait(dom, pattern)


async def acHexa(dom):
  global pattern

  drawOnMatrix(motif := await dom.getValue("Hexa"))

  await drawOnGUIAwait(dom, motif)

  pattern = motif


async def acAll(dom):
  for matrix in MATRICES:
    await drawAwait(dom, matrix)
    await ucuq.sleepAwait(0.5)


async def acBrightness(dom, id):
  ht16k33.setBrightness(int(await dom.getValue(id)))
  ucuq.commit()

async def acBlinkRate(dom, id):
  ht16k33.setBlinkRate(float(await dom.getValue(id)))
  ucuq.commit()

async def acDraw(dom, id):
  await drawAwait(dom, MATRICES[int(await dom.getMark(id))])

CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Test": acTest,
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
    cursor: pointer;
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

  .off {
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
<style>
  .switch-container {
    margin: auto;
    display: flex;
  }

  .switch {
    position: relative;
    display: inline-block;
    width: 30px;
    height: 17px;
    margin: auto;
  }

  .switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    -webkit-transition: .4s;
    transition: .4s cubic-bezier(0, 1, 0.5, 1);
    border-radius: 4px;
  }

  .slider:before {
    position: absolute;
    content: "";
    height: 13px;
    width: 13px;
    left: 3px;
    bottom: 2px;
    background-color: white;
    -webkit-transition: .4s;
    transition: .4s cubic-bezier(0, 1, 0.5, 1);
    border-radius: 3px;
  }

  input:checked+.slider {
    background-color: #52c944;
  }

  input:focus+.slider {
    box-shadow: 0 0 4px #7efa70;
  }

  input:checked+.slider:before {
    -webkit-transform: translateX(10px);
    -ms-transform: translateX(10px);
    transform: translateX(10px);
  }

  /* Rounded sliders */
  .slider.round {
    border-radius: 17px;
  }

  .slider.round:before {
    border-radius: 50%;
  }
</style>
"""

BODY = """
<fieldset>
  <fieldset style="display: flex;">
    <fieldset id="HardwareBox">
      <select id="Preset" xdh:onevent="Preset">
        <option value="User">User defined</option>
        <optgroup label="Freenove">
          <option value="Bipedal">Bipedal</option>
        </optgroup>
      </select>
      <label>
        <span>SDA:</span>
        <input id="SDA" size="2" type="number">
      </label>
      <label>
        <span>SCL:</span>
        <input id="SCL" size="2" type="number">
      </label>
    </fieldset>
    <span class="switch-container">
      <label class="switch">
        <input id="Switch" type="checkbox" xdh:onevent="Switch">
        <span class="slider round"></span>
      </label>
    </span>
  </fieldset>
  <fieldset id="MatrixBox" style="display: flex; justify-content: center;">
    <div class="matrix" id="Matrix"></div>
  </fieldset>
  <fieldset id="HexaBox" style="display: flex; justify-content: center;">
    <input xdh:onevent="input|Hexa" style="font-family: monospace;" id="Hexa" type="text" maxlength="32" minlength="32"
      size="32" pattern="[0-9a-fA-F]+">
  </fieldset>
  <fieldset id="MiscBox" style="display: flex; justify-content: space-evenly">
    <button xdh:onevent="Test">Test</button>
    <button xdh:onevent="All">All</button>
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
  <fieldset id="MatricesBox" style="display: grid; grid-template-columns: auto auto auto auto;">
  </fieldset>
</fieldset>
"""

atlastk.launch(CALLBACKS, headContent=HEAD)
