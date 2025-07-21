import ucuq, atlastk, binascii

hw = None

class OLED:
  def __init__(self, oled):
    self.oled = oled

  def plot(self, x, y):
    # return self.oled.rect(x*8, y*8, 8, 8, 1)
    return self.oled.ellipse(x*8+3, y*8+3, 3, 3, 1)
  
  def show(self):
    return self.oled.show()
  
  def clear(self):
    return self.oled.fill(0).show()

  def rect(self, x0, y0, x1, y1):
    for x in range(x0, x1+1):
      for y in range(y0, y1+1):
        self.plot(x,y)
  
  def draw(self, motif):
    self.oled.fill(0)
    for pos in range(len(motif)):
      char = int(motif[pos],16) 
      y = pos >> 2
      px = ( pos << 2 ) % 16
      for offset in range(4):
        if char & ( 1 << ( 3 - offset) ):
          self.plot(px + offset, y)

    return self
  
  def setBrightness(self, b):
    return self
  
  def setBlinkRate(self, b):
    return self
  

class HW(ucuq.Multi):
  def __init__(self, infos, device=None):
    self.device, matrix, oled = ucuq.getBits(infos, ucuq.B_MATRIX, ucuq.B_OLED, device=device)

    super().__init__(matrix)
    super().add(OLED(oled))

    self.clear().show().setBrightness(0).setBlinkRate(0)


pattern = "0" * 32

TEST_DELAY = 0.05

def test():
  for y in range(8):
    for x in range(16):
      hw.plot(x,y)
    hw.show()
    ucuq.sleep(TEST_DELAY)
    hw.clear()

  for x in range(16):
    for y in range(8):
      hw.plot(x,y)
    hw.show()
    ucuq.sleep(TEST_DELAY)
    hw.clear()

  hw.rect(0, 0, 15, 7).show()

  for b in range(0, 16):
    hw.setBrightness(b)
    ucuq.sleep(TEST_DELAY)

  for b in range(15, -1, -1):
    hw.setBrightness(b)
    ucuq.sleep(TEST_DELAY)

#  matrix.clear().show()


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
  if hw:
    hw.draw(motif).show()


async def drawAwait(dom, motif = pattern):
  global pattern

  pattern = motif
  
  drawOnMatrix(motif)

  await drawOnGUIAwait(dom, motif)

  await setHexaAwait(dom, motif)


async def atk(dom):
  global hw

  if not hw:
    hw = ucuq.Multi(HW(await ucuq.ATKConnectAwait(dom, BODY)))

  await drawAwait(dom, "")

  dom.executeVoid("patchHexaInput();")

  await drawLittleMatricesAwait(dom, MATRICES)


async def atkTest():
  test()


async def atkToggle(dom, id):
  global pattern

  [x, y] = list(map(lambda v: int(v), (await dom.getMark(id)).split()))

  pos = y * 16 + ( 4 * int(x / 4) + (3 - x % 4)) 

  bin = binascii.unhexlify(pattern.ljust(32,"0")[::-1].encode())[::-1]

  offset = int(pos/8)

  bin = bin[:offset] + bytearray([bin[offset] ^ (1 << (pos % 8))]) + bin[offset+1:]

  pattern = (binascii.hexlify(bin[::-1]).decode()[::-1])

  await drawAwait(dom, pattern)


async def atkHexa(dom):
  global pattern

  drawOnMatrix(motif := await dom.getValue("Hexa"))

  await drawOnGUIAwait(dom, motif)

  pattern = motif


async def atkAll(dom):
  for matrix in MATRICES:
    await drawAwait(dom, matrix)
    await ucuq.sleepAwait(0.5)


async def atkBrightness(dom, id):
  hw.setBrightness(int(await dom.getValue(id)))


async def atkBlinkRate(dom, id):
  hw.setBlinkRate(float(await dom.getValue(id)))


async def atkDraw(dom, id):
  await drawAwait(dom, MATRICES[int(await dom.getMark(id))])


async def atkMirror(dom, id):
  if  (await dom.getValue(id)) == "true":
    if ( await dom.confirm("Please do not confirm unless you know exactly what you are doing!") ):
      device = ucuq.Device(id="Hotel")

      hw.add(OLED(ucuq.SH1106_I2C(128, 64, ucuq.I2C(*ucuq.getHardware(ucuq.getKitHardware(await ucuq.getInfosAwait(device)), "OLED", ["SDA", "SCL", "Soft"]), device=device ))))
    else:
      await dom.setValue(id, "false")
  
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

async def UCUqXDevice(dom, device):
  hw.add(HW(await ucuq.getInfosAwait(device), device))
