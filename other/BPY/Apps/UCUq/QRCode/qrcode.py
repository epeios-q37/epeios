import atlastk, ucuq, datetime, time

epaper = None

W_TEXT = "Text"

async def atk(dom):
  global epaper

  await ucuq.ATKConnectAwait(dom, BODY)
  epaper = ucuq.SSD1680_SPI(7, 1, 2, 3, ucuq.SPI(1, baudrate=2000000, polarity=0, phase=0, sck=4, mosi=6))
  epaper.fill(0).hText("E-paper ready !", 50).hText(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 75).show()
  await dom.focus(W_TEXT)

# Called from JS!
async def atkDisplay(dom, id):
  epaper.fill(0).draw(id, ox=60, oy=6, width=120).show()


async def atkSubmit(dom):
  await dom.executeVoid(f"generate('{await dom.getValue(W_TEXT)}')")
  await dom.focus(W_TEXT)


async def atkClear(dom):
  await dom.setValue(W_TEXT, "")
  await dom.focus(W_TEXT)


async def atkReset(dom, id):
  global epaper
  epaper = ucuq.SSD1680_SPI(7, 1, 2, 3, ucuq.SPI(1, baudrate=2000000, polarity=0, phase=0, sck=4, mosi=6)).fill(0).show()

